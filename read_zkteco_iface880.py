# read_zkteco_iface880.py
import os
import django

# 🔹 إعداد Django قبل استدعاء أي موديلات
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "HR.settings")
django.setup()

from datetime import datetime, time
from collections import defaultdict
from zk import ZK
from HR.models import Name, Present_name, Present  # الآن آمن الاستدعاء بعد django.setup()

# إعدادات الجهاز
ZK_IP = "192.168.1.201"
ZK_PORT = 4370

MORNING_START = time(7, 0)
MORNING_END   = time(8, 30)
EVENING_START = time(18, 30)
EVENING_END   = time(19, 30)

def classify_time(t):
    if MORNING_START <= t <= MORNING_END:
        return "morning"
    elif EVENING_START <= t <= EVENING_END:
        return "evening"
    return None

def main():
    zk = ZK(ZK_IP, port=ZK_PORT, timeout=5)
    conn = None
    try:
        conn = zk.connect()
        conn.disable_device()
        logs = conn.get_attendance()

        data = defaultdict(lambda: defaultdict(list))
        for log in logs:
            data[int(log.user_id)][log.timestamp.date()].append(log.timestamp.time())

        for user_id, days in data.items():
            try:
                person = Name.objects.get(zk_id=user_id)
            except Name.DoesNotExist:
                continue

            present_name, _ = Present_name.objects.get_or_create(person=person)

            for day_date, times in days.items():
                year, month = day_date.year, day_date.month
                present, _ = Present.objects.get_or_create(
                    present_name=present_name, year=year, month=month
                )
                day_field = f"Day{day_date.day}"

                first_punches = {"morning": None, "evening": None}
                for t in sorted(times):
                    period = classify_time(t)
                    if period and not first_punches[period]:
                        first_punches[period] = t

                if first_punches["morning"] or first_punches["evening"]:
                    setattr(present, day_field, "ح")
                    present.save()
                    
                    # 🔹 تعديل: طباعة تقرير أول بصمة صباحية ومسائية
                    print(f"✅ الموظف: {person.name} | اليوم: {day_date} | "
                          f"صباح: {first_punches['morning']} | مساء: {first_punches['evening']}")

    finally:
        if conn:
            conn.enable_device()
            conn.disconnect()

if __name__ == "__main__":
    main()