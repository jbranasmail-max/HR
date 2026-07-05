from django.core.management.base import BaseCommand
from datetime import date, timedelta
import random
from HR.models import Student, Subject, StudentSubjectEnrollment


class Command(BaseCommand):
    help = "إنشاء بيانات مخطط التقدم الأكاديمي للطلاب"

    def handle(self, *args, **options):
        self.stdout.write("جاري إنشاء بيانات مخطط التقدم الأكاديمي...")

        # التأكد من وجود طلاب ومواد
        students = Student.objects.all()
        subjects = Subject.objects.all()

        if not students.exists():
            self.stdout.write(
                self.style.ERROR(
                    "لا توجد طلاب في النظام. يرجى تشغيل create_sample_data أولاً"
                )
            )
            return

        if not subjects.exists():
            self.stdout.write(
                self.style.ERROR(
                    "لا توجد مواد في النظام. يرجى تشغيل create_sample_data أولاً"
                )
            )
            return

        # حذف التسجيلات الموجودة
        StudentSubjectEnrollment.objects.all().delete()

        years = ["السنة الأولى", "السنة الثانية", "السنة الثالثة", "السنة الرابعة"]
        semesters = ["الترم الأول", "الترم الثاني"]

        enrollment_count = 0

        # إنشاء تقدم أكاديمي واقعي لكل طالب
        for student in students:
            self.stdout.write(f"إنشاء البيانات للطالب: {student.person.name}")

            # محاكاة التقدم عبر السنوات
            current_gpa = random.uniform(2.0, 4.0)  # معدل تراكمي أولي

            for year_index, year in enumerate(years):
                # تحسن تدريجي في الأداء (أو تراجع أحياناً)
                if year_index > 0:
                    change = random.uniform(-0.3, 0.5)  # تغيير في المعدل
                    current_gpa = max(1.0, min(4.0, current_gpa + change))

                for semester in semesters:
                    # تقلبات فصلية في الأداء
                    semester_variation = random.uniform(-0.2, 0.3)
                    semester_gpa = max(1.0, min(4.0, current_gpa + semester_variation))

                    # اختيار مواد للفصل (4-6 مواد)
                    semester_subjects = random.sample(
                        list(subjects), random.randint(4, 6)
                    )

                    for subject in semester_subjects:
                        # توليد درجة بناءً على المعدل المطلوب
                        target_grade = (semester_gpa / 4.0) * 100

                        # إضافة تنوع في الدرجات
                        grade_variation = random.uniform(-15, 15)
                        final_grade = max(0, min(99.99, target_grade + grade_variation))

                        # تاريخ التسجيل (محاولة جعله واقعي)
                        base_date = date(
                            2020 + year_index,
                            3 if semester == "الترم الثاني" else 9,
                            random.randint(1, 28),
                        )

                        StudentSubjectEnrollment.objects.create(
                            student=student,
                            subject=subject,
                            learn_year=year,
                            semester=semester,
                            mrak_of_subject=round(final_grade, 2),
                            enrollment_date=base_date,
                        )
                        enrollment_count += 1

            # توقف بعض الطلاب قبل إكمال كل السنوات
            if random.random() < 0.2:  # 20% يتوقفون
                break

        self.stdout.write(
            self.style.SUCCESS(
                f"تم إنشاء {enrollment_count} تسجيل مادة مع بيانات التقدم الأكاديمي"
            )
        )

        # إظهار إحصائيات
        self.show_statistics()

    def show_statistics(self):
        """عرض إحصائيات البيانات المنشأة"""
        students_count = Student.objects.count()
        enrollments_count = StudentSubjectEnrollment.objects.count()

        # حساب متوسط الدرجات
        enrollments = StudentSubjectEnrollment.objects.filter(
            mrak_of_subject__isnull=False
        )
        if enrollments.exists():
            avg_grade = sum(e.mrak_of_subject for e in enrollments) / len(enrollments)
            passed_count = enrollments.filter(mrak_of_subject__gte=50).count()
            failed_count = enrollments.filter(mrak_of_subject__lt=50).count()

            self.stdout.write("\n=== إحصائيات البيانات المنشأة ===")
            self.stdout.write(f"عدد الطلاب: {students_count}")
            self.stdout.write(f"عدد التسجيلات: {enrollments_count}")
            self.stdout.write(f"متوسط الدرجات: {avg_grade:.2f}")
            self.stdout.write(f"المواد المجتازة: {passed_count}")
            self.stdout.write(f"المواد المرسبة: {failed_count}")
            self.stdout.write(
                f"نسبة النجاح: {(passed_count/enrollments_count)*100:.1f}%"
            )
