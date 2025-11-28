from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from datetime import timedelta
from .models import Agent, ConnectionToken, Scan, Device
from .serializers import ConnectAgentSerializer, AgentSerializer, ScanSerializer, DeviceSerializer
import secrets

class GenerateTokenView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Expire old tokens
        ConnectionToken.objects.filter(user=request.user, expires_at__lt=timezone.now()).delete()
        
        # Create new token
        token = ConnectionToken.objects.create(
            user=request.user,
            expires_at=timezone.now() + timedelta(hours=1)
        )
        return Response({'token': token.code, 'expires_at': token.expires_at})

class ConnectAgentView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ConnectAgentSerializer(data=request.data)
        if serializer.is_valid():
            code = serializer.validated_data['token']
            try:
                token = ConnectionToken.objects.get(
                    code=code, 
                    is_used=False, 
                    expires_at__gt=timezone.now()
                )
                
                # Create Agent
                agent_name = request.data.get('name', f"Agent-{secrets.token_hex(2)}")
                agent = Agent.objects.create(
                    user=token.user,
                    name=agent_name
                )
                
                # Invalidate token
                token.is_used = True
                token.save()
                
                return Response({
                    'api_key': agent.api_key,
                    'agent_id': agent.id,
                    'name': agent.name
                })
                
            except ConnectionToken.DoesNotExist:
                return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AgentUploadView(APIView):
    permission_classes = [permissions.AllowAny]  # Custom API key authentication
    def post(self, request):
        api_key = request.headers.get('X-Agent-Key')
        if not api_key:
            return Response({'error': 'Missing API Key'}, status=status.HTTP_401_UNAUTHORIZED)
            
        try:
            agent = Agent.objects.get(api_key=api_key)
        except Agent.DoesNotExist:
            return Response({'error': 'Invalid API Key'}, status=status.HTTP_401_UNAUTHORIZED)
            
        # Update agent status
        agent.last_seen = timezone.now()
        agent.save()
        
        # Save Scan
        scan_type = request.data.get('scan_type', 'network')
        scan_data = request.data.get('data', {})
        
        scan = Scan.objects.create(
            agent=agent,
            scan_type=scan_type,
            data=scan_data
        )
        
        # Process Devices (Optional: Extract from JSON and save to Device model)
        # This is a simplified version. In production, we'd parse the JSON deeply.
        if isinstance(scan_data, dict):
             # Handle network scan format {ip: {data}}
            for ip, info in scan_data.items():
                if ip == 'scan_info' or ip == 'summary' or ip == 'devices': continue # Skip metadata

                # Make sure info is a dict before using .get()
                if isinstance(info, dict):
                    Device.objects.update_or_create(
                        agent=agent,
                        ip_address=ip,
                        defaults={
                            'mac_address': info.get('mac'),
                            'hostname': info.get('hostname'),
                            'vendor': info.get('vendor'),
                            'device_type': info.get('type', 'Unknown'),
                            'risk_score': info.get('risk_score', 0),
                            'os': info.get('os_guess', [None])[0] if isinstance(info.get('os_guess'), list) and info.get('os_guess') else None,
                            'ports': info.get('ports', []),
                            'vulnerabilities': info.get('risk_issues', []), # Mapping risk_issues to vulnerabilities
                            # Timeline could be updated here based on status changes, but for now we leave it empty or append 'Last Seen'
                        }
                    )
        
        return Response({'status': 'success', 'scan_id': scan.id})

class DeviceViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DeviceSerializer

    def get_queryset(self):
        return Device.objects.filter(agent__user=self.request.user)

class AgentViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AgentSerializer

    def get_queryset(self):
        return Agent.objects.filter(user=self.request.user)

class ScanViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ScanSerializer

    def get_queryset(self):
        return Scan.objects.filter(agent__user=self.request.user).order_by('-created_at')

from django.db.models import Avg

class StatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user_agents = Agent.objects.filter(user=request.user)
        user_devices = Device.objects.filter(agent__in=user_agents)
        
        total_devices = user_devices.count()
        high_risk = user_devices.filter(risk_score__gte=70).count()
        online_devices = user_devices.filter(last_seen__gte=timezone.now() - timedelta(minutes=10)).count()
        
        # Agent Status
        agent_count = user_agents.count()
        is_connected = user_agents.filter(last_seen__gte=timezone.now() - timedelta(minutes=5)).exists()
        
        # Calculate Real Average Risk Score
        avg_risk_score = user_devices.aggregate(Avg('risk_score'))['risk_score__avg'] or 0
        avg_risk_score = round(avg_risk_score, 1)

        # Helper to calc avg from scan data
        def get_scan_stats(scan_data):
            stats = {
                'avg_risk': 0,
                'total_count': 0,
                'high_risk_count': 0,
                'online_count': 0 # Hard to get historical online count accurately without more data, will approximate
            }
            
            total_score = 0
            count = 0
            high_risk = 0
            
            if isinstance(scan_data, dict):
                # Check if it's the list format (from router/camera scan) or dict format (network scan)
                if 'devices' in scan_data and isinstance(scan_data['devices'], list):
                    for device in scan_data['devices']:
                        score = device.get('risk_score', 0)
                        total_score += score
                        if score >= 70:
                            high_risk += 1
                        count += 1
                else:
                    # Network scan dict format {ip: data}
                    for key, val in scan_data.items():
                        if isinstance(val, dict) and 'risk_score' in val:
                            score = val['risk_score']
                            total_score += score
                            if score >= 70:
                                high_risk += 1
                            count += 1
            
            stats['avg_risk'] = total_score / count if count > 0 else 0
            stats['total_count'] = count
            stats['high_risk_count'] = high_risk
            # For online count, in a scan report, all devices listed are technically "online" at that time
            stats['online_count'] = count 
            
            return stats



        # Calculate Risk Trend (Compare last 2 scans for percentage)
        risk_trend_value = 0
        total_devices_trend = 0
        high_risk_trend = 0
        online_devices_trend = 0

        last_scans = Scan.objects.filter(agent__user=request.user).order_by('-created_at')[:2]
        
        if len(last_scans) >= 2:


            current_stats = get_scan_stats(last_scans[0].data)
            prev_stats = get_scan_stats(last_scans[1].data)
            
            # Risk Trend
            if prev_stats['avg_risk'] > 0:
                risk_trend_value = ((current_stats['avg_risk'] - prev_stats['avg_risk']) / prev_stats['avg_risk']) * 100
                risk_trend_value = round(risk_trend_value, 1)

            # Total Devices Trend
            if prev_stats['total_count'] > 0:
                total_devices_trend = ((current_stats['total_count'] - prev_stats['total_count']) / prev_stats['total_count']) * 100
                total_devices_trend = round(total_devices_trend, 1)
            
            # High Risk Trend
            if prev_stats['high_risk_count'] > 0:
                high_risk_trend = ((current_stats['high_risk_count'] - prev_stats['high_risk_count']) / prev_stats['high_risk_count']) * 100
                high_risk_trend = round(high_risk_trend, 1)

            # Online Devices Trend (Approximated by total count in scan)
            if prev_stats['online_count'] > 0:
                online_devices_trend = ((current_stats['online_count'] - prev_stats['online_count']) / prev_stats['online_count']) * 100
                online_devices_trend = round(online_devices_trend, 1)

        # 1. Device Distribution
        from django.db.models import Count
        device_counts = user_devices.values('device_type').annotate(count=Count('id'))
        device_distribution = []
        colors = ["#10b981", "#3b82f6", "#8b5cf6", "#f59e0b", "#ef4444", "#ec4899"]
        
        for i, item in enumerate(device_counts):
            device_distribution.append({
                "name": item['device_type'],
                "value": item['count'],
                "color": colors[i % len(colors)]
            })
            
        # If empty, add placeholder
        if not device_distribution:
             device_distribution = [
                { "name": "ناشناخته", "value": 100, "color": "#94a3b8" }
             ]

        # 2. Risk Trend Chart (Last 7 Days)
        risk_trend = []
        today = timezone.now().date()
        days_map = {0: "دوشنبه", 1: "سه‌شنبه", 2: "چهارشنبه", 3: "پنج‌شنبه", 4: "جمعه", 5: "شنبه", 6: "یکشنبه"}

        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            # Find scans for this day
            scans = Scan.objects.filter(
                agent__user=request.user,
                created_at__date=day
            )
            
            day_risk = 0
            if scans.exists():
                total_day_risk = 0
                scan_count = 0
                for scan in scans:
                    stats = get_scan_stats(scan.data)
                    avg = stats['avg_risk']
                    if avg > 0:
                        total_day_risk += avg
                        scan_count += 1
                
                if scan_count > 0:
                    day_risk = round(total_day_risk / scan_count)
            else:
                # If no scan today, use previous day's risk (or 0 if first day)
                if risk_trend:
                    day_risk = risk_trend[-1]['risk']
                else:
                    day_risk = 0

            weekday = day.weekday()
            day_name = days_map.get(weekday, str(day))

            risk_trend.append({
                "name": day_name,
                "risk": day_risk
            })

        return Response({
            "total_devices": total_devices,
            "high_risk_devices": high_risk,
            "online_devices": online_devices,
            "avg_risk_score": avg_risk_score,
            "risk_trend_value": risk_trend_value,
            "total_devices_trend": total_devices_trend,
            "high_risk_trend": high_risk_trend,
            "online_devices_trend": online_devices_trend,
            "risk_trend": risk_trend,
            "device_distribution": device_distribution,
            "agent_count": agent_count,
            "is_connected": is_connected
        })
