# service_fingerprint.py
import win32serviceutil
import win32service
import win32event
import subprocess
import time

class FingerprintService(win32serviceutil.ServiceFramework):
    _svc_name_ = "FingerprintService"
    _svc_display_name_ = "Django Fingerprint Reader Service"
    _svc_description_ = "Reads ZKTeco attendance and saves to Django"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.running = True

    def SvcStop(self):
        # عند إيقاف الخدمة
        self.running = False
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        # --- مسارات السكريبت والبايثون ---
        script_path = r"C:\Users\sssss\Desktop\HR\read_zkteco_iface880.py"
        python_path = r"C:\Users\sssss\Desktop\HR\venv\Scripts\python.exe"

        while self.running:
            try:
                # تشغيل السكريبت
                subprocess.call([python_path, script_path])
            except Exception as e:
                # إذا حصل خطأ أثناء التشغيل، تجاهله أو سجل هنا
                pass

            # 🔹 تأخير 60 ثانية لتقليل استهلاك CPU
            time.sleep(60)

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(FingerprintService)