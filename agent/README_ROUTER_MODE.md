# Router Interface Mode

قابلیت جدید Eriska Agent برای اسکن امنیتی از طریق وب اینترفیس روتر

## 🚀 استفاده

### 1. حالت Router Interface (پیشنهادی)
```bash
# اسکن از طریق روتر TP-Link
python main.py --mode router --router-ip 192.168.1.1 --router-user admin --router-pass 123456

# اسکن با مشخص کردن نوع روتر
python main.py --mode router --router-ip 192.168.1.1 --router-user admin --router-pass password --router-type tp-link

# اسکن روترهای دیگر
python main.py --mode router --router-ip 192.168.0.1 --router-user admin --router-pass admin123 --router-type d-link
```

### 2. حالت‌های قبلی (بدون تغییر)
```bash
# اسکن فعال شبکه
python main.py --mode active

# اسکن غیرفعال (شنود)
python main.py --mode passive

# تست credential
python main.py --mode active --test-creds
```

## 🎯 مزایای Router Mode

### ✅ **پوشش کامل شبکه:**
- تمام دستگاه‌های متصل به روتر (شامل دستگاه‌های مخفی)
- دستگاه‌های بی‌سیم و سیمی
- دستگاه‌های VLANهای مختلف
- Guest networks و subnet های جداگانه

### ✅ **اطلاعات غنی‌تر:**
- لیست کامل DHCP clients
- جدول ARP دقیق
- اطلاعاتی که فقط از روتر قابل دسترسه
- تاریخچه اتصال دستگاه‌ها

### ✅ **امنیت بالاتر:**
- احراز هویت قانونی از طریق روتر
- نیاز به دسترسی sudo نداره
- برای محیط‌های سازمانی مناسب‌تر

## 📊 خروجی نمونه

```
    ███████╗██████╗ ██╗███████╗██╗  ██╗ █████╗
    ██╔════╝██╔══██╗██║██╔════╝██║ ██╔╝██╔══██╗
    █████╗  ██████╔╝██║███████╗█████╔╝ ███████║
    ██╔══╝  ██╔══██╗██║╚════██║██╔═██╗ ██╔══██║
    ███████╗██║  ██║██║███████║██║  ██╗██║  ██║
    ╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝
          IoT Security Agent - v0.2.0

[INFO] 🚀 Starting Router Interface Mode
[INFO] Target Router: 192.168.1.1
[INFO] Router Username: admin
[INFO] 🔐 Attempting authentication to 192.168.1.1
[INFO] 🔍 Detected router type: tp-link
[INFO] 🔄 Trying authentication method 1/3...
[INFO] ✅ Authentication successful!
[INFO] 📡 Gathering router information...
[INFO] 🔍 Scanning for connected devices...
[INFO] ✓ Found 8 devices via _get_dhcp_devices
[INFO] ✓ Found 12 devices via _get_arp_devices
[INFO] ✓ Found 6 devices via _get_wireless_devices
[INFO] 🎯 Total unique devices found: 15
[INFO] 📄 Reports saved: router_scan_report_1703123456.json, router_scan_report_1703123456.html
[INFO] ✅ Router interface scan completed successfully!

============================================================
🔍 ROUTER INTERFACE SECURITY SCAN RESULTS
============================================================

📡 Router Information:
   IP: 192.168.1.1
   Type: tp-link
   Model: Archer C60
   Firmware: 0.9.1 4.0 v0032.0

📊 Network Summary:
   Total Devices: 15
   Wireless Devices: 8
   Wired Devices: 7
   High Risk Devices: 3

⚠️  High Risk Devices:
   - 192.168.1.50    00:12:15:XX:XX:XX  Hikvision-DS-2CD         (Risk: 85)
   - 192.168.1.88    e0:50:8b:XX:XX:XX  Dahua-IPC-HFW           (Risk: 78)
   - 192.168.1.100   dc:a6:32:XX:XX:XX  Raspberry-Pi             (Risk: 72)

============================================================
```

## 📋 روترهای پشتیبانی شده

### ✅ **کامل پشتیبانی می‌شه:**
- **TP-Link:** Archer series, Deco series
- **D-Link:** DIR series, DSL series
- **ASUS:** RT-series, ZenWiFi
- **Netgear:** Nighthawk, Orbi

### 🔄 **پشتیبانی عمومی:**
- روترهای با Web interface استاندارد
- فرآیند احراز هویت Basic Auth
- فرآیند احراز هویت Form-based

## 🔒 نکات امنیتی

- **قانونی است:** اسکن از طریق روتر کاملاً قانونی و امنه
- **بدون تغییر:** هیچ تغییری در تنظیمات روتر ایجاد نمی‌شه
- **Privileged:** نیاز به credentials معتبر داره
- **Non-invasive:** هیچ آسیبی به شبکه وارد نمی‌کنه

## 🚨 قابلیت‌های آینده

- ✅ Auto-discovery روتر در شبکه
- ✅ Real-time monitoring از طریق WebSocket
- ✅ پشتیبانی از NVR/DVR های دوربین
- ✅ Integration با dashboard وب

---

**نکته:** این قابلیت agent شما رو از یک "اسکنر شبکه ساده" به یک "پلتفرم مدیریت امنیت شبکه" تبدیل می‌کنه! 🚀