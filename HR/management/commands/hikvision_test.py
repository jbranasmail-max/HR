from django.core.management.base import BaseCommand
from django.utils import timezone
import requests
from requests.auth import HTTPDigestAuth
import xml.etree.ElementTree as ET

class Command(BaseCommand):
    help = "List Hikvision users and today's attendance events (XML + Digest Auth)"

    def handle(self, *args, **options):
        DEVICE_IP = "192.168.1.2"  # عدّل IP جهازك
        USER = "admin"             # اسم المستخدم
        PASS = "Digt@121"          # كلمة المرور

        # -----------------------
        # 1️⃣ جلب المستخدمين
        # -----------------------
        users_url = f"http://{DEVICE_IP}/ISAPI/AccessControl/UserInfo"
        try:
            r_users = requests.get(users_url, auth=HTTPDigestAuth(USER, PASS), timeout=20)
            self.stdout.write(self.style.SUCCESS(f"Users STATUS: {r_users.status_code}"))
            
            if r_users.status_code != 200:
                self.stdout.write(self.style.ERROR(f"Cannot fetch users. Status code: {r_users.status_code}"))
            else:
                # تحويل XML
                root = ET.fromstring(r_users.content)
                users = root.findall(".//userInfo")
                if not users:
                    self.stdout.write("No users found on the device.")
                else:
                    self.stdout.write("Users on the device:")
                    for u in users:
                        user_id = u.findtext("userID")
                        name = u.findtext("name")
                        self.stdout.write(f"  ID: {user_id}, Name: {name}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error fetching users: {str(e)}"))

        # -----------------------
        # 2️⃣ جلب أحداث اليوم
        # -----------------------
        now = timezone.localtime()
        start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        end   = now.replace(hour=23, minute=59, second=59, microsecond=0).isoformat()

        events_url = f"http://{DEVICE_IP}/ISAPI/AccessControl/AcsEvent"
        body = f"""
        <AcsEventCond>
            <searchID>Search1</searchID>
            <searchResultPosition>0</searchResultPosition>
            <maxResults>50</maxResults>
            <startTime>{start}</startTime>
            <endTime>{end}</endTime>
            <timeReverseOrder>true</timeReverseOrder>
        </AcsEventCond>
        """

        headers = {"Content-Type": "application/xml"}
        try:
            r_events = requests.post(events_url, data=body, headers=headers, auth=HTTPDigestAuth(USER, PASS), timeout=20)
            self.stdout.write(self.style.SUCCESS(f"Events STATUS: {r_events.status_code}"))

            if r_events.status_code != 200:
                self.stdout.write(self.style.ERROR(f"Cannot fetch events. Status code: {r_events.status_code}"))
            else:
                root = ET.fromstring(r_events.content)
                events = root.findall(".//AcsEvent")
                if not events:
                    self.stdout.write("No attendance events found today.")
                else:
                    self.stdout.write("Today's attendance events:")
                    for e in events:
                        user_id = e.findtext("userID") or "N/A"
                        time = e.findtext("time") or "N/A"
                        self.stdout.write(f"  UserID: {user_id}, Time: {time}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error fetching events: {str(e)}"))
