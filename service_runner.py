import os
import sys
import time
import socket
import logging
import threading
import win32serviceutil
import win32service
import win32event
import servicemanager
from waitress import serve  # استخدم Daphne إذا كنت تريد ASGI

# إعداد اللوج
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'django_service.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('DjangoService')

class DjangoWindowsService(win32serviceutil.ServiceFramework):
    _svc_name_ = "DjangoService"
    _svc_display_name_ = "Django Web Service"
    _svc_description_ = "Runs Django project as a Windows service"

    def __init__(self, args):
        super().__init__(args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_running = False
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_running = False
        logger.info("Service stop requested")

    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        self.main()

    def main(self):
        logger.info("Service starting")
        self.is_running = True

        # تغيير المسار لمجلد المشروع
        project_path = r"C:\Users\Administrator\Desktop\HR"  # ضع هنا مسار مشروعك
        os.chdir(project_path)
        sys.path.insert(0, project_path)

        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HR.settings')  # ضع اسم المشروع و settings.py

        try:
            from django.core.wsgi import get_wsgi_application
            application = get_wsgi_application()

            # تشغيل السيرفر في Thread منفصل
            server_thread = threading.Thread(target=self.run_server, args=(application,))
            server_thread.daemon = True
            server_thread.start()

            while self.is_running:
                if win32event.WaitForSingleObject(self.hWaitStop, 1000) == win32event.WAIT_OBJECT_0:
                    break
                time.sleep(1)

        except Exception as e:
            logger.error(f"Error starting Django service: {str(e)}")
            self.is_running = False

        logger.info("Service stopped")

    def run_server(self, application):
        host = '0.0.0.0'
        port = 8000
        logger.info(f"Starting Waitress server on {host}:{port}")
        serve(application, host=host, port=port, threads=10)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(DjangoWindowsService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(DjangoWindowsService)
