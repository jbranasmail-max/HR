from django.core.management.base import BaseCommand
from datetime import date, datetime, timedelta
import random
from HR.models import (
    Batch,
    Name,
    Address,
    PersonalIDCard,
    Person,
    Specialization,
    University,
    Student,
    Staff,
    Subject,
    StudentSubjectEnrollment,
    Attendance,
    Payment,
    Violation,
    DevelopmentCourse,
    Qualification,
)


class Command(BaseCommand):
    help = "إنشاء بيانات تجريبية للنظام"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="حذف البيانات الموجودة قبل إنشاء بيانات جديدة",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write("جاري حذف البيانات الموجودة...")
            self.clear_existing_data()

        self.stdout.write("جاري إنشاء البيانات التجريبية...")

        # إنشاء البيانات الأساسية
        batches = self.create_batches()
        specializations = self.create_specializations()
        universities = self.create_universities()
        subjects = self.create_subjects()

        # إنشاء الأشخاص والطلاب
        persons = self.create_persons_and_students(
            batches, specializations, universities
        )

        # إنشاء تسجيلات المواد مع الدرجات
        self.create_student_enrollments(persons, subjects)

        # إنشاء الحضور
        self.create_attendance(persons)

        # إنشاء المدفوعات
        self.create_payments(persons)

        # إنشاء بعض المخالفات
        self.create_violations(persons)

        # إنشاء الدورات التطويرية
        self.create_development_courses(persons)

        # إنشاء المؤهلات
        self.create_qualifications(persons)

        self.stdout.write(self.style.SUCCESS("تم إنشاء البيانات التجريبية بنجاح!"))

    def clear_existing_data(self):
        """حذف البيانات الموجودة"""
        models_to_clear = [
            StudentSubjectEnrollment,
            Attendance,
            Payment,
            Violation,
            DevelopmentCourse,
            Qualification,
            Student,
            Staff,
            Person,
            PersonalIDCard,
            Name,
            Address,
            Subject,
            Specialization,
            University,
            Batch,
        ]

        for model in models_to_clear:
            model.objects.all().delete()

    def create_batches(self):
        """إنشاء الدفعات"""
        batch_names = [
            "دفعة 2020 - الأولى",
            "دفعة 2021 - الثانية",
            "دفعة 2022 - الثالثة",
            "دفعة 2023 - الرابعة",
            "دفعة 2024 - الخامسة",
        ]

        batches = []
        for name in batch_names:
            batch, created = Batch.objects.get_or_create(
                name=name, defaults={"notes": f"ملاحظات {name}"}
            )
            batches.append(batch)
            if created:
                self.stdout.write(f"تم إنشاء الدفعة: {name}")

        return batches

    def create_specializations(self):
        """إنشاء التخصصات"""
        specialization_names = [
            "هندسة الحاسوب",
            "هندسة البرمجيات",
            "تقنية المعلومات",
            "علوم الحاسوب",
            "أمن المعلومات",
            "الذكاء الاصطناعي",
            "هندسة الشبكات",
            "تصميم الجرافيك",
        ]

        specializations = []
        for name in specialization_names:
            spec, created = Specialization.objects.get_or_create(name=name)
            specializations.append(spec)
            if created:
                self.stdout.write(f"تم إنشاء التخصص: {name}")

        return specializations

    def create_universities(self):
        """إنشاء الجامعات"""
        university_names = [
            "جامعة صنعاء",
            "جامعة العلوم والتكنولوجيا",
            "جامعة الأندلس للعلوم والتقنية",
            "جامعة الحديدة",
            "جامعة إب",
            "جامعة تعز",
            "جامعة عدن",
        ]

        universities = []
        for name in university_names:
            uni, created = University.objects.get_or_create(name=name)
            universities.append(uni)
            if created:
                self.stdout.write(f"تم إنشاء الجامعة: {name}")

        return universities

    def create_subjects(self):
        """إنشاء المواد الدراسية"""
        subject_names = [
            "مقدمة في البرمجة",
            "هياكل البيانات",
            "خوارزميات",
            "قواعد البيانات",
            "هندسة البرمجيات",
            "الذكاء الاصطناعي",
            "أمن المعلومات",
            "شبكات الحاسوب",
            "تطوير الويب",
            "البرمجة الكائنية",
            "الرياضيات المتقطعة",
            "نظم التشغيل",
            "تفاعل الإنسان والحاسوب",
            "إدارة المشاريع",
            "الحوسبة السحابية",
        ]

        subjects = []
        for name in subject_names:
            subject, created = Subject.objects.get_or_create(
                name=name, defaults={"description": f"وصف مادة {name}"}
            )
            subjects.append(subject)
            if created:
                self.stdout.write(f"تم إنشاء المادة: {name}")

        return subjects

    def create_persons_and_students(self, batches, specializations, universities):
        """إنشاء الأشخاص والطلاب"""
        first_names = [
            "أحمد",
            "محمد",
            "علي",
            "حسن",
            "يوسف",
            "عبدالله",
            "خالد",
            "عمر",
            "فاطمة",
            "عائشة",
            "خديجة",
            "مريم",
            "زينب",
            "أسماء",
            "هند",
            "نور",
        ]

        father_names = [
            "محمد",
            "أحمد",
            "علي",
            "حسن",
            "يوسف",
            "عبدالله",
            "صالح",
            "عبدالرحمن",
        ]

        family_names = [
            "الفلاني",
            "العلوي",
            "الهاشمي",
            "المطري",
            "الشامي",
            "الحميري",
            "الأنصاري",
            "المكي",
            "الزهراني",
            "القحطاني",
        ]

        cities = ["صنعاء", "عدن", "تعز", "الحديدة", "إب", "مأرب"]
        districts = ["التحرير", "السبعين", "الثورة", "شعوب", "معين"]

        persons = []

        for i in range(50):  # إنشاء 50 شخص
            # إنشاء الاسم
            name = Name.objects.create(
                first_name=random.choice(first_names),
                second_name=random.choice(father_names),
                third_name=random.choice(father_names),
                forth_name=random.choice(father_names),
                last_name=random.choice(family_names),
            )

            # إنشاء العنوان
            address = Address.objects.create(
                street=random.choice(cities),
                city=random.choice(districts),
                state=f"عزلة {random.randint(1, 10)}",
                country=f"قرية {random.randint(1, 20)}",
            )

            # إنشاء البطاقة الشخصية
            national_id = PersonalIDCard.objects.create(
                card_number=f"{random.randint(100000000, 999999999)}",
                issue_date=date.today() - timedelta(days=random.randint(365, 3650)),
                expiry_date=date.today() + timedelta(days=random.randint(365, 3650)),
                governorate=random.choice(cities),
                district=random.choice(districts),
                sub_district=f"عزلة {random.randint(1, 10)}",
                village=f"قرية {random.randint(1, 20)}",
                blood_Type=random.choice(
                    ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
                ),
            )

            # إنشاء الشخص
            person = Person.objects.create(
                name=name,
                address=address,
                date_of_birth=date(
                    random.randint(1995, 2005),
                    random.randint(1, 12),
                    random.randint(1, 28),
                ),
                national_id=national_id,
                phone=f"77{random.randint(1000000, 9999999)}",
                email=f"{name.first_name.lower()}.{name.last_name.lower()}{i}@example.com",
                academic_qualification=random.choice(
                    ["ثانوي", "دبلوم جامعي", "بكالوريوس", "ماجستير"]
                ),
                high_school_grade=f"{random.randint(70, 99)}.{random.randint(0, 9)}%",
                entry_date=date.today() - timedelta(days=random.randint(30, 1000)),
                supervisor=f"المشرف {random.randint(1, 5)}",
                status=random.choice(["جيد", "متوسط", "فقير جدًا", "يتيم"]),
                marital_status=random.choice(["أعزب", "متزوج", "مطلق"]),
                health_condition=random.choice(["جيد", "متوسط", "سيئ"]),
                batch=random.choice(batches),
                is_present=random.choice([True, True, True, False]),  # 75% متواجدين
            )

            # إنشاء الطالب
            if random.choice([True, True, False]):  # 66% طلاب
                Student.objects.create(
                    person=person,
                    specialization=random.choice(specializations),
                    university=random.choice(universities),
                    start_date=person.entry_date,
                    stop_date=None
                    if random.choice([True, True, False])
                    else date.today() - timedelta(days=random.randint(1, 365)),
                )
            else:
                # إنشاء موظف
                Staff.objects.create(
                    person=person,
                    position=random.choice(
                        [
                            "مطور برمجيات",
                            "محلل أنظمة",
                            "مدير مشروع",
                            "مصمم جرافيك",
                            "متخصص أمن معلومات",
                        ]
                    ),
                    start_date=person.entry_date,
                    continue_work=random.choice([True, True, True, False]),
                )

            persons.append(person)

            if (i + 1) % 10 == 0:
                self.stdout.write(f"تم إنشاء {i + 1} شخص")

        return persons

    def create_student_enrollments(self, persons, subjects):
        """إنشاء تسجيل الطلاب في المواد مع الدرجات"""
        students = Student.objects.all()
        years = ["السنة الأولى", "السنة الثانية", "السنة الثالثة", "السنة الرابعة"]
        semesters = ["الترم الأول", "الترم الثاني"]

        enrollment_count = 0

        for student in students:
            # كل طالب يدرس في سنوات مختلفة
            student_years = random.sample(years, random.randint(1, 3))

            for year in student_years:
                for semester in semesters:
                    # كل طالب يأخذ بين 3-6 مواد في كل فصل
                    student_subjects = random.sample(subjects, random.randint(3, 6))

                    for subject in student_subjects:
                        # توليد درجة واقعية
                        if random.random() < 0.8:  # 80% ينجحون
                            grade = random.randint(50, 99)
                        else:  # 20% يرسبون
                            grade = random.randint(20, 49)

                        enrollment = StudentSubjectEnrollment.objects.create(
                            student=student,
                            subject=subject,
                            learn_year=year,
                            semester=semester,
                            mrak_of_subject=grade,
                            enrollment_date=date.today()
                            - timedelta(days=random.randint(30, 500)),
                        )
                        enrollment_count += 1

        self.stdout.write(f"تم إنشاء {enrollment_count} تسجيل مادة دراسية")

    def create_attendance(self, persons):
        """إنشاء بيانات الحضور"""
        attendance_count = 0

        # إنشاء حضور للشهر الماضي
        start_date = date.today() - timedelta(days=30)

        for person in persons[:20]:  # حضور لأول 20 شخص فقط
            current_date = start_date
            while current_date <= date.today():
                if current_date.weekday() < 5:  # أيام العمل فقط
                    # 85% نسبة حضور
                    is_present = random.random() < 0.85

                    Attendance.objects.create(
                        person=person, date=current_date, session=is_present
                    )
                    attendance_count += 1

                current_date += timedelta(days=1)

        self.stdout.write(f"تم إنشاء {attendance_count} سجل حضور")

    def create_payments(self, persons):
        """إنشاء المدفوعات المالية"""
        payment_count = 0

        for person in persons[:30]:  # مدفوعات لأول 30 شخص
            # إنشاء مدفوعات للأشهر الثلاثة الماضية
            for month_back in range(3):
                payment_date = date.today() - timedelta(days=30 * month_back)

                Payment.objects.create(
                    person=person,
                    accreditation=random.randint(50000, 200000)
                    if random.choice([True, False])
                    else None,
                    salary=random.randint(30000, 100000)
                    if random.choice([True, False])
                    else None,
                    visit=random.randint(5000, 20000)
                    if random.choice([True, False])
                    else None,
                    expenses=random.randint(10000, 50000)
                    if random.choice([True, False])
                    else None,
                    transfers=random.randint(5000, 15000)
                    if random.choice([True, False])
                    else None,
                    qat=random.randint(2000, 10000)
                    if random.choice([True, False])
                    else None,
                    help=random.randint(20000, 80000)
                    if random.choice([True, False])
                    else None,
                    rent=random.randint(30000, 100000)
                    if random.choice([True, False])
                    else None,
                    date=payment_date,
                    notes=f"مدفوعات شهر {payment_date.month}",
                )
                payment_count += 1

        self.stdout.write(f"تم إنشاء {payment_count} سجل مالي")

    def create_violations(self, persons):
        """إنشاء المخالفات"""
        violation_types = ["إنذار شفوي", "لفت نظر", "إنذار خطي", "إنذار نهائي"]
        descriptions = [
            "تأخر عن الحضور",
            "عدم أداء الواجبات",
            "سلوك غير مناسب",
            "عدم الالتزام بالقوانين",
            "غياب بدون عذر",
        ]

        violation_count = 0

        # بعض الأشخاص لديهم مخالفات
        for person in random.sample(persons, 15):
            # كل شخص قد يكون لديه 1-3 مخالفات
            num_violations = random.randint(1, 3)

            for _ in range(num_violations):
                Violation.objects.create(
                    person=person,
                    date=date.today() - timedelta(days=random.randint(1, 365)),
                    violation_type=random.choice(violation_types),
                    description=random.choice(descriptions),
                    action_taken=f"تم اتخاذ الإجراء المناسب",
                    resolved=random.choice([True, False]),
                )
                violation_count += 1

        self.stdout.write(f"تم إنشاء {violation_count} مخالفة")

    def create_development_courses(self, persons):
        """إنشاء الدورات التطويرية"""
        course_names = [
            "دورة تطوير الويب المتقدمة",
            "دورة الذكاء الاصطناعي",
            "دورة أمن المعلومات",
            "دورة إدارة المشاريع",
            "دورة التصميم الجرافيكي",
            "دورة قواعد البيانات",
            "دورة البرمجة المتقدمة",
        ]

        course_count = 0

        for person in random.sample(persons, 25):
            # كل شخص قد يأخذ 1-3 دورات
            num_courses = random.randint(1, 3)

            for _ in range(num_courses):
                DevelopmentCourse.objects.create(
                    person=person,
                    name=random.choice(course_names),
                    year=random.randint(2020, 2024),
                    result=random.choice(["ممتاز", "جيد جداً", "جيد", "مقبول"]),
                )
                course_count += 1

        self.stdout.write(f"تم إنشاء {course_count} دورة تطويرية")

    def create_qualifications(self, persons):
        """إنشاء المؤهلات الأكاديمية"""
        degrees = ["ثانوية عامة", "دبلوم", "بكالوريوس", "ماجستير", "دكتوراه"]
        institutions = [
            "جامعة صنعاء",
            "جامعة العلوم والتكنولوجيا",
            "جامعة الأندلس",
            "معهد الإدارة العامة",
            "الكلية التقنية",
        ]
        grades = ["ممتاز", "جيد جداً", "جيد", "مقبول"]

        qualification_count = 0

        for person in random.sample(persons, 30):
            # كل شخص قد يكون لديه 1-2 مؤهل
            num_qualifications = random.randint(1, 2)

            for _ in range(num_qualifications):
                Qualification.objects.create(
                    person=person,
                    degree=random.choice(degrees),
                    institution=random.choice(institutions),
                    year=random.randint(2010, 2023),
                    grade=random.choice(grades),
                )
                qualification_count += 1

        self.stdout.write(f"تم إنشاء {qualification_count} مؤهل أكاديمي")
