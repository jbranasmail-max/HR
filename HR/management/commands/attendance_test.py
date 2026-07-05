from django.core.management.base import BaseCommand
from datetime import datetime
from management.models import Name, Present_name, Present

class Command(BaseCommand):
    help = "Test Attendance Import"

    def handle(self, *args, **kwargs):
        attendance_data = [
            {"user_id": 1, "timestamp": datetime(2026, 2, 9, 8, 0)},
            {"user_id": 2, "timestamp": datetime(2026, 2, 9, 8, 5)},
        ]

        for record in attendance_data:
            try:
                person = Name.objects.get(zk_id=record["user_id"])
            except Name.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"الموظف غير موجود: {record['user_id']}"))
                continue

            present_name, _ = Present_name.objects.get_or_create(person=person)
            year = record["timestamp"].year
            month = record["timestamp"].month
            day = record["timestamp"].day
            present, _ = Present.objects.get_or_create(
                present_name=present_name,
                year=year,
                month=month
            )
            setattr(present, f"Day{day}", "ح")
            present.save()
            self.stdout.write(self.style.SUCCESS(f"تم تسجيل حضور: {person}"))
