import os
import sys
import django

from zk import ZK
from datetime import datetime, time, timedelta

# =========================================
# إعداد Django
# =========================================

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "HR.settings")

django.setup()

from HR.models import Name, Present_name, Present


# =========================================
# إعدادات البصمة
# =========================================

NIGHT_IN_START = time(20, 30)
NIGHT_IN_END = time(22, 10)

# تمديد خاص للموظفين 50 و 51
SPECIAL_IDS = ['50', '51']
NIGHT_IN_START_SPECIAL = time(20, 30)
NIGHT_IN_END_SPECIAL = time(23, 59)

NIGHT_OUT_START = time(5, 0)
NIGHT_OUT_END = time(6, 40)

DECISION_TIME = time(6, 45)

DEVICE_IP = '192.168.10.4'
DEVICE_PORT = 4371

# قائمة القيم اليدوية المحمية
PROTECTED_VALUES = ['هـ', 'ذ', 'د', 'ب', 'م', 'غ', 'ح']
# =========================================
# المزامنة
# =========================================

def sync_attendance():

    zk = ZK(
        DEVICE_IP,
        port=DEVICE_PORT,
        timeout=30,
        password=0,
        force_udp=False
    )

    conn = None

    try:

        print(f"🔄 جاري سحب البيانات... {datetime.now().strftime('%H:%M')}")

        conn = zk.connect()

        conn.disable_device()

        attendance_records = conn.get_attendance()

        device_users = conn.get_users()
                # =========================================
        # تثبيت يوم 11 / 6 / السنة = ح لجميع موظفي جهاز البصمة
        # =========================================

        FORCE_YEAR = 2026   # غيّر السنة متى أردت

        for user in device_users:

            u_id = str(user.user_id)

            try:
                person = Name.objects.get(zk_id=u_id)

                p_name, _ = Present_name.objects.get_or_create(
                    person=person
                )

                p_month, _ = Present.objects.get_or_create(
                    present_name=p_name,
                    year=FORCE_YEAR,
                    month=6
                )

                setattr(p_month, "Day11", "ح")
                p_month.save()

            except Name.DoesNotExist:
                continue

        now = datetime.now()

        current_time = now.time()

        today_date = now.date()

        yesterday_date = today_date - timedelta(days=1)

        # =========================================
        # خريطة البصمات
        # =========================================

        punches_map = {}

        if attendance_records:

            for att in attendance_records:

                u_id = str(att.user_id)
                att_time = att.timestamp.time()
                att_date = att.timestamp.date()

                # منطق تحديد الدخول مع التمديد لـ 50 و 51
                is_special = u_id in SPECIAL_IDS
                start_in = NIGHT_IN_START_SPECIAL if is_special else NIGHT_IN_START
                end_in = NIGHT_IN_END_SPECIAL if is_special else NIGHT_IN_END

                if start_in <= att_time <= end_in:

                    key = (u_id, att_date)

                    if key not in punches_map:
                        punches_map[key] = {'in': False, 'out': False}

                    punches_map[key]['in'] = True

                elif NIGHT_OUT_START <= att_time <= NIGHT_OUT_END:

                    work_day_date = att_date - timedelta(days=1)

                    key = (u_id, work_day_date)

                    if key not in punches_map:
                        punches_map[key] = {'in': False, 'out': False}

                    punches_map[key]['out'] = True

        all_dates = sorted({
            att.timestamp.date()
            for att in attendance_records
        }) if attendance_records else []

        # =========================================
        # معالجة الموظفين واحتساب العداد التراكمي
        # =========================================

        for user in device_users:

            u_id = str(user.user_id)

            try:

                person = Name.objects.get(zk_id=u_id)

                p_name, _ = Present_name.objects.get_or_create(
                    person=person
                )

                limit = 6 if person.marital_status == "متزوج" else 4

                past_dates = sorted([
                    d for d in all_dates
                    if d < yesterday_date
                ])

                # دالة لحساب المأذونيات في الشهر الحالي فقط
                def get_month_absent_count(p_name_obj, year, month):
                    p_m = Present.objects.filter(present_name=p_name_obj, year=year, month=month).first()
                    if not p_m: return 0
                    count = 0
                    for d in range(1, 32):
                        if getattr(p_m, f'Day{d}') == 'م':
                            count += 1
                    return count

                # =========================================
                # 1. معالجة الأيام السابقة
                # =========================================

                for work_date in past_dates:

                    p_month_all, _ = Present.objects.get_or_create(
                        present_name=p_name,
                        year=work_date.year,
                        month=work_date.month
                    )

                    day_attr = f'Day{work_date.day}'
                    
                    if getattr(p_month_all, day_attr) in PROTECTED_VALUES:
                        continue

                    absent_counter = get_month_absent_count(p_name, work_date.year, work_date.month)

                    punches = punches_map.get(
                        (u_id, work_date),
                        {'in': False, 'out': False}
                    )

                    if punches['in'] and punches['out']:
                        setattr(p_month_all, day_attr, 'ح')
                    else:
                        # المأذونية تشمل (بصمة واحدة) أو (صفر بصمات)
                        setattr(p_month_all, day_attr, 'م' if absent_counter < limit else 'غ')

                    p_month_all.save()

                # =========================================
                # 2. معالجة يوم أمس
                # =========================================

                p_month_y, _ = Present.objects.get_or_create(
                    present_name=p_name,
                    year=yesterday_date.year,
                    month=yesterday_date.month
                )

                y_day_attr = f'Day{yesterday_date.day}'
                
                if getattr(p_month_y, y_day_attr) not in PROTECTED_VALUES:
                    
                    y_punches = punches_map.get(
                        (u_id, yesterday_date),
                        {'in': False, 'out': False}
                    )
                    
                    absent_counter_y = get_month_absent_count(p_name, yesterday_date.year, yesterday_date.month)

                    if y_punches['out'] or current_time >= DECISION_TIME:
                        if y_punches['in'] and y_punches['out']:
                            setattr(p_month_y, y_day_attr, 'ح')
                        else:
                            # المأذونية تشمل (بصمة واحدة) أو (صفر بصمات)
                            setattr(p_month_y, y_day_attr, 'م' if absent_counter_y < limit else 'غ')
                    else:
                        # قبل وقت القرار إذا لم يكمل البصمتين
                        if y_punches['in']:
                            setattr(p_month_y, y_day_attr, 'ب')
                        else:
                            setattr(p_month_y, y_day_attr, '-')
                    
                    p_month_y.save()

                # =========================================
                # 3. معالجة اليوم الحالي
                # =========================================

                p_month_t, _ = Present.objects.get_or_create(
                    present_name=p_name,
                    year=today_date.year,
                    month=today_date.month
                )

                t_day_attr = f'Day{today_date.day}'

                if getattr(p_month_t, t_day_attr) not in PROTECTED_VALUES:

                    t_punches = punches_map.get(
                        (u_id, today_date),
                        {'in': False, 'out': False}
                    )
                    
                    absent_counter_t = get_month_absent_count(p_name, today_date.year, today_date.month)

                    if t_punches['out']:
                        if t_punches['in'] and t_punches['out']:
                            setattr(p_month_t, t_day_attr, 'ح')
                        else:
                            # المأذونية تشمل (بصمة واحدة) أو (صفر بصمات)
                            setattr(p_month_t, t_day_attr, 'م' if absent_counter_t < limit else 'غ')
                    else:
                        if t_punches['in']:
                            setattr(p_month_t, t_day_attr, 'ب')
                        else:
                            # إذا لم يبصم بعد (صفر بصمات)
                            setattr(p_month_t, t_day_attr, '-')

                    p_month_t.save()

            except Name.DoesNotExist:

                continue

        print("✅ تم سحب البيانات بنجاح ")

    except Exception as e:

        print(f"❌ خطأ في السكربت: {e}")

    finally:

        if conn:

            conn.enable_device()

            conn.disconnect()

            print("🔌 تم فصل الجهاز بأمان")


# =========================================
# تشغيل السكربت
# =========================================

if __name__ == "__main__":

    sync_attendance()