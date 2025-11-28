from django.db import models
from django.contrib.auth.models import User
import uuid
import secrets

class Agent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='agents')
    name = models.CharField(max_length=100)
    api_key = models.CharField(max_length=255, unique=True, editable=False)
    is_active = models.BooleanField(default=True)
    last_seen = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.api_key:
            self.api_key = secrets.token_urlsafe(48)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.user.username})"

class ConnectionToken(models.Model):
    code = models.CharField(max_length=10, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = secrets.token_hex(4).upper() # 8 chars
        super().save(*args, **kwargs)

class Scan(models.Model):
    SCAN_TYPES = (
        ('network', 'Network Scan'),
        ('router', 'Router Scan'),
        ('camera', 'Camera Scan'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='scans')
    scan_type = models.CharField(max_length=20, choices=SCAN_TYPES)
    data = models.JSONField() # Stores the full JSON report
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.scan_type} - {self.agent.name} - {self.created_at}"

class Device(models.Model):
    # This model can be populated from Scan data for easier querying
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='devices')
    ip_address = models.GenericIPAddressField()
    mac_address = models.CharField(max_length=17, null=True, blank=True)
    hostname = models.CharField(max_length=255, null=True, blank=True)
    vendor = models.CharField(max_length=255, null=True, blank=True)
    device_type = models.CharField(max_length=50, default='Unknown')
    risk_score = models.IntegerField(default=0)
    os = models.CharField(max_length=100, null=True, blank=True)
    firmware = models.CharField(max_length=100, null=True, blank=True)
    ports = models.JSONField(default=list, blank=True)
    vulnerabilities = models.JSONField(default=list, blank=True)
    timeline = models.JSONField(default=list, blank=True) # For storing recent events
    last_seen = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('agent', 'ip_address')

    def __str__(self):
        return f"{self.ip_address} ({self.hostname})"
