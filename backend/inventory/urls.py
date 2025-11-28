from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GenerateTokenView, ConnectAgentView, AgentUploadView, DeviceViewSet, StatsView, AgentViewSet, ScanViewSet

router = DefaultRouter()
router.register(r'devices', DeviceViewSet, basename='device')
router.register(r'agents', AgentViewSet, basename='agent')
router.register(r'scans', ScanViewSet, basename='scan')

urlpatterns = [
    path('', include(router.urls)),
    path('agent/generate_token/', GenerateTokenView.as_view(), name='generate_token'),
    path('agent/connect/', ConnectAgentView.as_view(), name='connect_agent'),
    path('agent/upload/', AgentUploadView.as_view(), name='agent_upload'),
    path('stats/', StatsView.as_view(), name='dashboard_stats'),
]
