from rest_framework import serializers
from .models import Agent, Scan, Device

class ConnectAgentSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=10)

class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = ('id', 'name', 'last_seen', 'is_active')

class ScanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scan
        fields = '__all__'
        read_only_fields = ('agent', 'created_at')

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = '__all__'
