# Camera Interface Mode - Examples & Documentation

## 🎥 **فوق‌العاده! حالت Camera Interface به agent اضافه شد!**

این قابلیت به شما اجازه می‌دهد به طور مستقیم به وب اینترفیس دوربین‌های مداربسته متصل بشید و تحلیل امنیتی کاملی انجام دهید.

---

## 🚀 **نحوه استفاده**

### **1. حالت Camera Interface (جدید):**

```bash
# اسکن دوربین Hikvision
python main.py --mode camera --camera-ip 192.168.1.50 --camera-user admin --camera-pass 123456 --camera-type hikvision

# اسکن خودکار (تشخیص نوع دوربین)
python main.py --mode camera --camera-ip 192.168.1.50 --camera-user admin --camera-pass 123456

# اسکن دوربین Dahua
python main.py --mode camera --camera-ip 192.168.1.51 --camera-user admin --camera-pass admin123 --camera-type dahua

# اسکن دوربین Axis
python main.py --mode camera --camera-ip 192.168.1.52 --camera-user root --camera-pass pass --camera-type axis
```

### **2. تمام حالت‌های موجود:**

```bash
# حالت شبکه (فعال/غیرفعال)
python main.py --mode active
python main.py --mode passive

# حالت روتر
python main.py --mode router --router-ip 192.168.1.1 --router-user admin --router-pass 123456

# حالت دوربین (جدید!)
python main.py --mode camera --camera-ip 192.168.1.50 --camera-user admin --camera-pass 123456
```

---

## 📊 **خروجی نمونه**

### **کنسول:**
```
    ███████╗██████╗ ██╗███████╗██╗  ██╗ █████╗
    ██╔════╝██╔══██╗██║██╔════╝██║ ██╔╝██╔══██╗
    █████╗  ██████╔╝██║███████╗█████╔╝ ███████║
    ██╔══╝  ██╔══██╗██║╚════██║██╔═██╗ ██╔══██║
    ███████╗██║  ██║██║███████║██║  ██╗██║  ██║
    ╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝
          IoT Security Agent - v0.3.0

[INFO] 🎥 Starting Camera Interface Mode
[INFO] Target Camera: 192.168.1.50
[INFO] Camera Username: admin
[INFO] 🔐 Attempting authentication to camera 192.168.1.50
[INFO] 🔍 Detected camera type: hikvision
[INFO] 🔄 Trying camera auth method 1/3...
[INFO] ✅ Camera authentication successful!
[INFO] 📷 Gathering camera information...
[INFO] 🔒 Analyzing camera security...
[INFO] 📄 Reports saved: camera_scan_report_1703123456.json, camera_scan_report_1703123456.html
[INFO] ✅ Camera interface scan completed successfully!

============================================================
🎥 CAMERA INTERFACE SECURITY SCAN RESULTS
============================================================

📷 Camera Information:
   IP: 192.168.1.50
   Type: hikvision
   Model: DS-2CD2142FWD-I
   Firmware: v5.5.800

🔒 Security Analysis:
   Risk Score: 85/100
   Total Issues: 5

⚠️  Security Issues:
   🔴 CRITICAL: default_credentials
      Camera using default credentials
   🔴 CRITICAL: firmware_vulnerability
      CVE-2017-7921 detected in firmware v5.5.800
   🟡 HIGH: insecure_protocols
      Camera allows unencrypted access
   🟠 MEDIUM: exposed_admin
      Admin interface accessible from WAN
   🟠 MEDIUM: default_ports
      Using default HTTP/RTSP ports

============================================================
```

---

## 🔍 **قابلیت‌های پیشرفته Camera Scanner**

### **1. Detection & Authentication:**
```python
# Auto-detection supported brands
supported_cameras = [
    "Hikvision",      # #1 در بازار ایران
    "Dahua",         # #2 در بازار ایران
    "Axis",          # برند اروپایی
    "Vivotek",       # برند تایوانی
    "Foscam",        # دوربین‌های ارزان
    "TP-Link Tapo",  # دوربین‌های خانگی
    "D-Link",        # برند قدیمی
    "ONVIF Compatible" # استاندارد صنعتی
]

# Multi-method authentication
auth_methods = [
    "Web Form Login",     # لاگین از طریق فرم
    "HTTP Basic Auth",    # احراز هویت ساده
    "ONVIF SOAP",         # استاندارد ONVIF
    "REST API"            # API مدرن
]
```

### **2. Information Extraction:**
```python
camera_info = {
    # 基本信息
    "ip": "192.168.1.50",
    "model": "DS-2CD2142FWD-I",
    "firmware": "v5.5.800",
    "serial_number": "DS-2CD2142FWD-I20201201AACH123456789",
    "mac_address": "00:12:15:AA:BB:CC",

    # Video capabilities
    "resolution": "1920x1080",
    "max_fps": 30,
    "codec_support": ["H.264", "H.265"],
    "streams": ["Main", "Sub"],

    # Network settings
    "ports": [80, 443, 554, 8080],
    "protocols": ["HTTP", "HTTPS", "RTSP", "ONVIF"],
    "encryption": ["Available", "Enabled"],

    # Security features
    "user_accounts": ["admin", "operator", "viewer"],
    "access_levels": ["Admin", "User", "Guest"],
    "privacy_zones": "Configured",
    "motion_detection": "Enabled"
}
```

### **3. Security Analysis:**
```python
security_checks = [
    {
        "check": "Default Credentials",
        "severity": "CRITICAL",
        "detection": "Common passwords check",
        "recommendation": "Change default username/password"
    },
    {
        "check": "Firmware Vulnerabilities",
        "severity": "HIGH",
        "detection": "CVE database matching",
        "recommendation": "Update firmware immediately"
    },
    {
        "check": "Insecure Protocols",
        "severity": "HIGH",
        "detection": "HTTP without SSL, RTSP without encryption",
        "recommendation": "Enable HTTPS and RTSPS"
    },
    {
        "check": "Default Ports",
        "severity": "MEDIUM",
        "detection": "Port 80, 554, 8080 detected",
        "recommendation": "Change default ports for security"
    },
    {
        "check": "Exposed Admin Interface",
        "severity": "MEDIUM",
        "detection": "Admin accessible from WAN",
        "recommendation": "Restrict to local network only"
    }
]
```

---

## 🎯 **مزایای استراتژیک Camera Mode**

### **مقایسه حالت‌ها:**

| ویژگی | Active/Passive | Router Mode | **Camera Mode** |
|--------|----------------|-------------|-----------------|
| پوشش دوربین‌ها | ✅ محدود | ✅ غیرمستقیم | **✅ مستقیم و عمیق** |
| اطلاعات دقیق | ❌ محدود | ❌ کلی | **✅ کامل و دقیق** |
| ریسک‌های خاص دوربین | ❌ None | ❌ غیرمستقیم | **✅ Camera-specific** |
| تنظیمات امنیتی | ❌ None | ❌ None | **✅ مستقیم قابل دسترس** |
| آسیب‌پذیری‌های فریمور | ❌ None | ❌ None | **✅ CVE detection** |
| پیکربندی ویدیو | ❌ None | ❌ None | **✅ Stream settings** |

---

## 💡 **Use Cases کاربردی**

### **1. Enterprise Security Audit:**
```bash
# اسکن تمام دوربین‌های شبکه
for camera_ip in $(cat camera_list.txt); do
    python main.py --mode camera --camera-ip $camera_ip --camera-user admin --camera-pass $PASSWORD --camera-type auto
done

# تولید گزارش واحد
python combine_camera_reports.py *.json
```

### **2. Security Monitoring:**
```bash
# مانیتورینگ مداوم از ناحیه crontab
echo "0 */6 * * * python /path/to/agent/main.py --mode camera --camera-ip 192.168.1.50 --camera-user admin --camera-pass secure123" | crontab -
```

### **3. Incident Response:**
```bash
# بررسی سریع دوربین‌های مشکوک در شبکه
python main.py --mode camera --camera-ip $SUSPICIOUS_IP --camera-user admin --camera-pass $PASSWORD
```

---

## 📋 **دوربین‌های پشتیبانی شده**

### **✅ کامل پشتیبانی:**

#### **Hikvision (هیکن ویژن):**
```python
hikvision_endpoints = [
    "/ISAPI/System/deviceInfo",      # اطلاعات دستگاه
    "/ISAPI/Security/users",        # کاربران امنیتی
    "/ISAPI/ContentMgmt/InputProxy/channels", # کانال‌های ویدیو
    "/ISAPI/Streaming/channels",    # تنظیمات استریم
    "/doc/page/login.asp"           # صفحه لاگین قدیمی
]

vulnerabilities_covered = [
    "CVE-2017-7921", # Command injection
    "CVE-2021-36260", # Critical RCE
    "Default credentials", # admin/12345, admin/admin
    "Backdoor accounts" # Hidden user accounts
]
```

#### **Dahua (دهوا):**
```python
dahua_endpoints = [
    "/cgi-bin/global.cgi",          # اطلاعات عمومی
    "/cgi-bin/magicBox.cgi",       # اطلاعات جعبه جادویی
    "/cgi-bin/configManager.cgi",   # مدیریت کانفیگ
    "/web/index.html"              # رابط وب مدرن
]

vulnerabilities_covered = [
    "CVE-2019-10939", # Hardcoded credentials
    "CVE-2018-10088", # Remote code execution
    "CVE-2017-7925", # Information disclosure
    "Default telnet access"
]
```

### **✅ پشتیبانی عمومی:**
- **ONVIF compatible cameras** (استاندارد صنعتی)
- **HTTP Basic Auth** دوربین‌ها
- **Form-based authentication** دوربین‌ها
- **REST API** دوربین‌های مدرن

---

## 🚨 **Security Intelligence**

### **Camera-Specific Vulnerabilities:**
```python
camera_vulnerability_db = {
    "hikvision_v5.5.0": {
        "cve": "CVE-2017-7921",
        "type": "Command Injection",
        "severity": "CRITICAL",
        "description": "Buffer overflow in web server",
        "exploitability": "High",
        "patch_available": True
    },
    "dahua_v2.400": {
        "cve": "CVE-2019-10939",
        "type": "Hardcoded Credentials",
        "severity": "CRITICAL",
        "description": "Hardcoded backdoor credentials",
        "exploitability": "Critical",
        "patch_available": True
    }
}
```

### **Default Credential Database:**
```python
default_credentials = {
    "hikvision": [
        ("admin", "12345"),
        ("admin", "admin"),
        ("admin", "888888"),
        ("service", "service")
    ],
    "dahua": [
        ("admin", "admin"),
        ("admin", "888888"),
        ("default", "default")
    ],
    "axis": [
        ("root", "pass"),
        ("admin", "pass"),
        ("admin", "admin")
    ]
}
```

---

## 📱 **HTML Report Features**

### **گزارش تولید شده شامل:**

1. **📷 Camera Information Card:**
   - Model, Firmware, Serial Number
   - MAC Address, IP Configuration
   - Video specifications

2. **🔒 Security Analysis Dashboard:**
   - Risk Score (0-100)
   - Visual risk meter
   - Severity breakdown

3. **⚠️ Security Issues List:**
   - Critical vulnerabilities in red
   - High risk issues in yellow
   - Actionable recommendations

4. **💡 Remediation Recommendations:**
   - Prioritized action items
   - Step-by-step fix instructions
   - Security best practices

---

## 🔮 **قابلیت‌های آینده:**

### **برای نسخه‌های بعدی:**
- ✅ **Video Stream Analysis** - تست RTSP streams
- ✅ **Configuration Backup** - بکاپ از تنظیمات امنیتی
- ✅ **Batch Camera Scanning** - اسکن همزمان چند دوربین
- ✅ **Real-time Monitoring** - مانیتورینگ زنده تغییرات
- ✅ **Integration with NVRs** - اتصال به دستگاه‌های ضبط

---

**نتیجه نهایی:** این قابلیت agent شما رو به یک **ابزار حرفه‌ای دوربین مداربسته** تبدیل می‌کنه که در بازار ایران نیاز بسیار زیادی بهش هست! 🚀