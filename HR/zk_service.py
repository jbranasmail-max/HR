# hr/zk_service.py

from zk import ZK

def get_attendance():
    """
    جلب جميع البصمات من جهاز ZKTeco
    يعيد قائمة من القواميس: [{"user_id": 1, "time": datetime}, ...]
    """
    zk = ZK('192.168.1.201', port=4370)  # ضع هنا IP جهازك
    conn = zk.connect()
    conn.disable_device()

    attendances = conn.get_attendance()
    data = []

    for att in attendances:
        data.append({
            "user_id": att.user_id,
            "time": att.timestamp
        })

    conn.enable_device()
    conn.disconnect()

    return data