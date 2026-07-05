import os
import sys
import django
from zk import ZK
from datetime import datetime, time, timedelta

# 1. إعداد بيئة Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "HR.settings")
django.setup()

from HR.models import Name, Present_name, Present

# --- الإعدادات الدقيقة (حسب توقيتك) ---
NIGHT_IN_START, NIGHT_IN_END = time(21, 0), time(22, 10)    # دخول: 9:00 م - 10:10 م
NIGHT_OUT_START, NIGHT_OUT_END = time(5, 0), time(6, 40)   # خروج: 5:00 ص - 6:40 ص
DECISION_TIME = time(6, 45)  # ساعة الحسم (لا يتم وضع م أو غ إلا بعد 6:45 صباحاً)

DEVICE_IP = '192.168.10.4'
DEVICE_PORT = 4371

def sync_attendance():
    zk = ZK(DEVICE_IP, port=DEVICE_PORT, timeout=30, password=0, force_udp=False)
    conn = None
    
    try:
        print(f"🔄 جاري سحب البيانات... الوقت الحالي: {datetime.now().strftime('%H:%M')}")
        conn = zk.connect()
        conn.disable_device()
        
        attendance_records = conn.get_attendance()
        device_users = conn.get_users()
        
        now = datetime.now()
        current_time = now.time()
        today_date = now.date()
        yesterday_date = today_date - timedelta(days=1)

        # 1. بناء خريطة البصمات (Punches Map)
        punches_map = {}
        if attendance_records:
            for att in attendance_records:
                u_id = str(att.user_id)
                att_time = att.timestamp.time()
                att_date = att.timestamp.date()

                # --- التعديل المضاف للموظفين 50 و 51 ---
                if u_id in ['50', '51']:
                    is_in_time = (time(21, 0) <= att_time <= time(23, 59, 59))
                else:
                    is_in_time = (NIGHT_IN_START <= att_time <= NIGHT_IN_END)

                # تسجيل بصمات الدخول (الليلة)
                if is_in_time:
                    key = (u_id, att_date)
                    if key not in punches_map: punches_map[key] = {'in': False, 'out': False}
                    punches_map[key]['in'] = True
                
                # تسجيل بصمات الخروج (الفجر) - تُنسب لليوم المالي السابق
                elif NIGHT_OUT_START <= att_time <= NIGHT_OUT_END:
                    work_day_date = att_date - timedelta(days=1)
                    key = (u_id, work_day_date)
                    if key not in punches_map: punches_map[key] = {'in': False, 'out': False}
                    punches_map[key]['out'] = True

        # 2. تحديث قاعدة البيانات لكل موظف
        for user in device_users:
            u_id = str(user.user_id)
            try:
                person = Name.objects.get(zk_id=u_id)
                p_name, _ = Present_name.objects.get_or_create(person=person)
                
                # --- معالجة يوم أمس (الوردية المستهدفة) ---
                p_month_y, _ = Present.objects.get_or_create(
                    present_name=p_name, year=yesterday_date.year, month=yesterday_date.month
                )
                y_day_attr = f'Day{yesterday_date.day}'
                y_punches = punches_map.get((u_id, yesterday_date), {'in': False, 'out': False})
                
                current_val_y = getattr(p_month_y, y_day_attr)

                # الحالة الأولى: بصم دخول وخروج -> حاضر حتماً
                if y_punches['in'] and y_punches['out']:
                    setattr(p_month_y, y_day_attr, 'ح')
                
                # الحالة الثانية: الحسم (فقط بعد انتهاء الدوام 6:45 صباحاً)
                elif current_time >= DECISION_TIME:
                    # لا نغير الحالة إذا كانت مسجلة مسبقاً (ح، م، غ)
                    
                    if current_val_y not in ['ح', 'م', 'غ', 'د', 'ذ', 'هـ']:
                        limit = 6 if person.marital_status == "متزوج" else 4
                        used_m = sum(1 for d in range(1, 32) if getattr(p_month_y, f'Day{d}', '-') == 'م')
                        
                        symbol = 'م' if used_m < limit else 'غ'
                        setattr(p_month_y, y_day_attr, symbol)
                
                p_month_y.save()

                # --- معالجة اليوم الحالي (إظهار بصمة الدخول الآن) ---
                p_month_t, _ = Present.objects.get_or_create(
                    present_name=p_name, year=today_date.year, month=today_date.month
                )
                t_day_attr = f'Day{today_date.day}'
                t_punches = punches_map.get((u_id, today_date), {'in': False, 'out': False})
                
                if t_punches['in'] and not t_punches['out']:
                    if getattr(p_month_t, t_day_attr) not in ['ح', 'م', 'غ']:
                        setattr(p_month_t, t_day_attr, 'ب') # ب تعني بصم دخول
                
                p_month_t.save()

            except Name.DoesNotExist:
                continue

        print("✅ تم سحب البيانات بنجاح ")

    except Exception as e:
        print(f"❌ حدث خطأ غير متوقع: {e}")
    finally:
        if conn:
            conn.enable_device()
            conn.disconnect()
            print("🔌 تم فصل الاتصال بجهاز البصمة.")

if __name__ == "__main__":
    sync_attendance()