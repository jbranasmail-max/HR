from django.db import models
# علاقة تسجيل الطلاب في المواد

# اسماء االاشخاص
class Name(models.Model):
    def __str__(self):
        return f"{self.first_name} {self.second_name or ''} {self.third_name} {self.forth_name} {self.last_name} ".strip()
    first_name = models.CharField("الاسم الأول", max_length=100)
    second_name = models.CharField("اسم الأب", max_length=100, blank=True, null=True)
    third_name = models.CharField("اسم الثالث", max_length=100, blank=True, null=True)
    forth_name = models.CharField("اسم الرابع", max_length=100, blank=True, null=True)
    last_name = models.CharField("اسم العائلة", max_length=100)
    zk_id = models.IntegerField(
        "رقم البصمة",
        null=True,
        blank=True,
        unique=True
    )
    MARITAL_STATUS_CHOICES = [
        ("أعزب", "أعزب"),
        ("متزوج", "متزوج")
    ]
    # هذا الحقل ضروري جداً لتنفيذ شرط (6 أيام للمتزوج و 4 للعازب)
    marital_status = models.CharField(
        "الحالة الاجتماعية", 
        max_length=10, 
        choices=MARITAL_STATUS_CHOICES, 
        default="أعزب"
    )
    @property
    def arabic_full_name(self):
        parts = [
            self.first_name,
            self.second_name,
            self.third_name,
            self.forth_name,
            self.last_name,
        ]
        return " ".join([p for p in parts if p]).strip()

    class Meta:
        verbose_name = "الاسم الكامل"
        verbose_name_plural = "الأسماء الكاملة"
# العناوين
class Address(models.Model):
    def __str__(self):
        return f"{self.street}, {self.city}, {self.state}, {self.country}"
# الترتيب: city (المديرية) ← street (المحافظة) ← state ← country
    street = models.CharField("المحافظة", max_length=255)
    city = models.CharField("المديرية", max_length=100)
    state = models.CharField("العزلة", max_length=100)
    country = models.CharField("القرية", max_length=100)

    class Meta:
        verbose_name = "العنوان"
        verbose_name_plural = "العناوين"


# البطاقات الشخصية
class PersonalIDCard(models.Model):
    def __str__(self):
        return f"{self.card_number}"
    card_number = models.CharField("رقم البطاقة", max_length=50)
    issue_date = models.DateField("تاريخ الإصدار")
    expiry_date = models.DateField("تاريخ الانتهاء")
    governorate = models.CharField("المحافظة", max_length=50, blank=True, null=True)
    district = models.CharField("المديرية", max_length=50, blank=True, null=True)
    sub_district = models.CharField("العزلة", max_length=50, blank=True, null=True)
    village = models.CharField("القرية", max_length=50, blank=True, null=True)
    BLOOD_TYPES_CHOICES = [
        ("A+", "A+"),
        ("A-", "A-"),
        ("B+", "B+"),
        ("B-", "B-"),
        ("AB+", "AB+"),
        ("AB-", "AB-"),
        ("O+", "O+"),
        ("O-", "O-"),
    ]
    blood_Type = models.CharField(
        "فصيلة الدم", choices=BLOOD_TYPES_CHOICES, max_length=10, null=True
    )

    class Meta:
        verbose_name = "بطاقة الهوية الشخصية"
        verbose_name_plural = "بطاقات الهوية الشخصية"

# الاشخاص
from django.db import models
from django.contrib.auth.models import User

from django.utils import timezone
from django.contrib.auth.models import User
from django.db import models

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class LoginHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40, null=True, blank=True)  # لتتبع الجلسة
    login_time = models.DateTimeField("وقت الدخول", auto_now_add=True)
    logout_time = models.DateTimeField("وقت الخروج", null=True, blank=True)

    def session_duration(self):
        end_time = self.logout_time or timezone.now()
        duration = end_time - self.login_time
        return duration.total_seconds() / 60  # بالدقائق

    def __str__(self):
        return f"{self.user.username} - دخول: {self.login_time} - خروج: {self.logout_time or 'لم يخرج بعد'}"

    class Meta:
        verbose_name = "دخول وخروج"
        verbose_name_plural = "الدخول والخروج"

class Person(models.Model):
    @property
    def no_violation_for_six_months(self):
        from datetime import date, timedelta

        six_months_ago = date.today() - timedelta(days=180)
        return not self.violation_set.filter(date__gte=six_months_ago).exists()

    def __str__(self):
        return str(self.name)

    # الحقول الأساسية
    name = models.OneToOneField(Name, on_delete=models.CASCADE, verbose_name="الاسم")

    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="العنوان")
    date_of_birth = models.DateField("تاريخ الميلاد",blank=True, null=True)
    national_id = models.OneToOneField(
        PersonalIDCard,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="person",
        verbose_name="البطاقة الشخصية",
    )
    phone = models.CharField("رقم الجوال", max_length=100, blank=True, null=True)
    email = models.EmailField("البريد الإلكتروني", unique=True, blank=True, null=True)
    STATUS_CHOICES = [
    ("متوقف", "متوقف"),
    ("ليس متوقف", "ليس متوقف"),
    ]
    typestatus = models.CharField("التوقف ", max_length=20, choices=STATUS_CHOICES, default="ليس متوقف")
    stop_reason = models.TextField("سبب التوقف", blank=True, null=True)
    # المؤهل العلمي
    academic_qualification_choices = [
        ("بدون مؤهل", "بدون مؤهل"),
        ("ثانوي", "ثانوي"),
        ("دبلوم مهني", "دبلوم مهني"),
        ("دبلوم جامعي", "دبلوم جامعي"),
        ("بكالوريوس", "بكالوريوس"),
        ("دبلوم عالي", "دبلوم عالي"),
        ("ماجستير", "ماجستير"),
        ("دكتوراه", "دكتوراه"),
        ("أستاذ دكتور", "أستاذ دكتور"),
    ]
    academic_qualification = models.CharField(
        "المؤهل العلمي",
        max_length=50,
        choices=academic_qualification_choices,
        blank=True,
        null=True,
    )
    high_school_grade = models.CharField("معدل الثانوية العامة", max_length=50, blank=True, null=True)
    entry_date = models.DateField("تاريخ الدخول", blank=True, null=True)
   
    exit_date = models.DateField("تاريخ الخروج", blank=True, null=True)
   
    # الحالة المادية والاجتماعية والصحية
    STATUS_CHOICES = [("جيد", "جيد"), ("متوسط", "متوسط"), ("ضعيف", "ضعيف"), ("فقير جدًا", "فقير جدًا"), ("يتيم", "يتيم")]
    status = models.CharField("الحالة المادية", choices=STATUS_CHOICES, max_length=100, blank=True, null=True)

    MARITAL_STATUS_CHOICES = [("أعزب", "أعزب"), ("متزوج", "متزوج")]
    male_children = models.PositiveIntegerField("عدد الأولاد الذكور",blank=True, null=True, default="لايوجد")
    female_children = models.PositiveIntegerField("عدد الأولاد الإناث", blank=True, null=True,default="لايوجد")
    total_children = models.PositiveIntegerField(
        "إجمالي الأولاد", editable=False,blank=True, null=True, default=0
    )

    def save(self, *args, **kwargs):
        self.total_children = (self.male_children or 0) + (self.female_children or 0)
        super().save(*args, **kwargs)

    marital_status = models.CharField("الحالة الاجتماعية", choices=MARITAL_STATUS_CHOICES, max_length=50, blank=True, null=True)
 
    HEALTH_CONDITION_CHOICES = [("جيد", "جيد"), ("متوسط", "متوسط"), ("سيئ", "سيئ"), ("ذو إعاقة", "ذو إعاقة"), ("مريض مزمن", "مريض مزمن")]
    health_condition = models.CharField("الحالة الصحية", choices=HEALTH_CONDITION_CHOICES, max_length=255, blank=True, null=True)

   
    is_present = models.BooleanField("متواجد", default=True)

    class Meta:
        verbose_name = "شخص"
        verbose_name_plural = "الأشخاص"
# التخصصات
class Specialization(models.Model):
    name = models.CharField("التخصص", blank=True, null=True, max_length=50)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = "التخصص"
        verbose_name_plural = "التخصصات"
# الجامعات
class University(models.Model):
    name = models.CharField("اسم الجامعة", blank=True, null=True, max_length=60)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = "الجامعة"
        verbose_name_plural = "الجامعات"
# الطلاب
class Student(models.Model):
    def __str__(self):
        return f"{self.person} - {self.specialization} - {self.university}"
    person = models.OneToOneField(
        Person, on_delete=models.CASCADE, verbose_name="الشخص"
    )
    specialization = models.ForeignKey(
        Specialization, on_delete=models.PROTECT, blank=True, null=True, verbose_name="التخصص"
    )
    university = models.ForeignKey(
        University, on_delete=models.PROTECT, blank=True, null=True, verbose_name="الجامعة"
    )
    YEAR_CHOICES = [
        ("ثانوي", "ثانوي"),
        ('الأولى', 'الأولى'),
        ('الثانية', 'الثانية'),
        ('الثالثة', 'الثالثة'),
        ('الرابعة', 'الرابعة'),
        ("خريج", "خريج"),
    ]
    learnyear = models.CharField(
        max_length=10,
        choices=YEAR_CHOICES,
        verbose_name="السنة"
    )
    start_date = models.DateField("تاريخ البداية")
    stop_date = models.DateField("تاريخ الانتهاء", blank=True, null=True)
    stop_reason = models.TextField(" سبب الانتهاء", blank=True, null=True)

    class Meta:
        verbose_name = "طالب"
        verbose_name_plural = "الطلاب"

# العاملين
class Staff(models.Model):
    def __str__(self):
        return f"{self.person} - {self.position}"

    person = models.OneToOneField(
        Person, on_delete=models.CASCADE, verbose_name="الشخص"
    )
    position = models.CharField("العمل", max_length=100)
    text_notes = models.TextField( "المهام الموكلة ", blank=True, null=True) 
    start_date = models.DateField("تاريخ البداية")
    continue_work = models.BooleanField("استمرار العمل", default=True)
    stop_date = models.DateField("تاريخ الانتهاء", blank=True, null=True)
    stop_reason = models.TextField("سبب الانتهاء", blank=True, null=True)

    class Meta:
        verbose_name = "موظف"
        verbose_name_plural = "الموظف"


# الدورات الاكادمية

# المواد
class Subject(models.Model):
    def __str__(self):
        return f"{self.name}"
    name = models.CharField("اسم المادة", max_length=255)
    description = models.TextField("وصف المادة", blank=True, null=True)
    
    class Meta:
        verbose_name = "مادة دراسية"
        verbose_name_plural = "المواد الدراسية"
        
#السنة
class Year_choices(models.Model):
    name_year = models.CharField(max_length=100,verbose_name='السنة ')
    def __str__(self):
        return f"{self.name_year}" 
    class Meta:
        verbose_name = "السنة الدراسية "
        verbose_name_plural = "السنوات الدراسية "
#الفصل
class Semester_choices(models.Model):
    name_semester = models.CharField(max_length=100,verbose_name=' الفصل')
    def __str__(self):
        return f"{self.name_semester}" 
    class Meta:
        verbose_name = "الفصل الدراسي "
        verbose_name_plural = "الفصول الدراسية "
        
# التسجيل في المواد
class StudentSubjectEnrollment(models.Model):
    student = models.ForeignKey(
        "Student", on_delete=models.CASCADE, verbose_name="الطالب"
    )
    
    YEAR_CHOICES = [
        ('الأولى', 'الأولى'),
        ('الثانية', 'الثانية'),
        ('الثالثة', 'الثالثة'),
        ('الرابعة', 'الرابعة'),
        ("خريج", "خريج"),
    ]

    SEMESTER_CHOICES = [
        ('الأول', 'الأول'),
        ('الثاني', 'الثاني'),
    ]

    learn_year = models.CharField(
        max_length=10,
        choices=YEAR_CHOICES,
        verbose_name="السنة"
    )

    semester = models.CharField(
        max_length=10,
        choices=SEMESTER_CHOICES,
        verbose_name="الترم", blank=True, null=True
    )
    subject = models.ForeignKey(
        "Subject", on_delete=models.CASCADE, verbose_name="المادة الدراسية", blank=True, null=True
    )

    mrak_of_subject = models.DecimalField(
        "الدرجة", max_digits=5, decimal_places=2, blank=True, null=True
    )
    enrollment_date = models.DateField("تاريخ التسجيل", auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"{self.student} - {self.subject} ({self.learn_year}, {self.semester}) - {self.mrak_of_subject} - {self.enrollment_date}  "

    class Meta:
        verbose_name = "إضافة مادة للطالب"
        verbose_name_plural = "إضافة مواد للطالب"

# المالية
class Payment(models.Model):
    def __str__(self):
        return f"{self.person} - {self.accreditation} - {self.salary} - {self.visit} - {self.expenses} - {self.transfers} - {self.qat } - {self.help} - {self.rent} ({self.date})"

    person = models.ForeignKey(Person, on_delete=models.CASCADE, verbose_name="الشخص")
    accreditation = models.IntegerField("الإعتمادية", blank=True, null=True)
    salary = models.IntegerField("رعاية", blank=True, null=True)
    visit = models.IntegerField("مزاورة", blank=True, null=True)
    expenses = models.IntegerField("مصروف جيب", blank=True, null=True)
    transfers = models.IntegerField("تنقلات", blank=True, null=True)
    qat = models.IntegerField("قات", blank=True, null=True)
    help = models.IntegerField("مساعدة", blank=True, null=True)
    rent = models.IntegerField("إيجار", blank=True, null=True)
    date = models.DateField("التاريخ")
    notes = models.TextField("ملاحظات", blank=True, null=True)

    class Meta:
        verbose_name = "إعتماد مالي"
        verbose_name_plural = " الأعتمادية المالية"


# المخالفات
class Violation_name(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, verbose_name="الشخص")

    def __str__(self):
        return str(self.person)

    class Meta:
        verbose_name = "مخالفة"
        verbose_name_plural = "مخالفات"

from django.db import models
from django.utils import timezone
import calendar

class Present_name(models.Model):
    person = models.ForeignKey(Name, on_delete=models.CASCADE, verbose_name="الشخص")
    
    def str(self):
        return str(self.person)

    class Meta:
        verbose_name = "حضور"
        verbose_name_plural = "الحضور"

# قائمة الرموز (المعاني)
DAY_SYMBOLS = [
    ("-","-"),
    ('ح', 'ح'),
    ('م', 'م'),
    ('غ', 'غ'),
    ('د', 'د'),
    ('ذ', 'ذ'),
    ('هـ', 'هـ'),
]

class Present(models.Model):
    # ربط كل سجل بالشخص
    present_name = models.ForeignKey(
        Present_name,
        on_delete=models.CASCADE,
        related_name="presents",
        verbose_name="الشخص"
    )

    year = models.IntegerField(
        choices=[(y, y) for y in range(2020, timezone.now().year + 1)],
        verbose_name="السنة_________"
    )

    month = models.IntegerField(
        choices=[(m, f"{m}") for m in range(1, 13)],
        verbose_name="الشهر______"
    )

    # --- حقول الأيام 1 إلى 31 ----
    Day1  = models.CharField(max_length=2, choices=DAY_SYMBOLS, default='-', verbose_name="اليوم_____ 1")
    Day2  = models.CharField(max_length=2, choices=DAY_SYMBOLS, default='-', verbose_name="اليوم____ 2")
    Day3  = models.CharField(max_length=2, choices=DAY_SYMBOLS, default='-', verbose_name="اليوم____ 3")
    Day4  = models.CharField(max_length=2, choices=DAY_SYMBOLS, default='-', verbose_name="اليوم____ 4")
    Day5  = models.CharField(max_length=2, choices=DAY_SYMBOLS, default='-', verbose_name="اليوم____ 5")
    Day6  = models.CharField(max_length=2, choices=DAY_SYMBOLS, default='-', verbose_name="اليوم____ 6")
    Day7  = models.CharField(max_length=2, choices=DAY_SYMBOLS, default='-', verbose_name="اليوم_____ 7")
    Day8  = models.CharField(max_length=2, choices=DAY_SYMBOLS, default='-', verbose_name="اليوم____ 8")
    Day9  = models.CharField(max_length=2, choices=DAY_SYMBOLS, default='-', verbose_name="اليوم____ 9")
    Day10 = models.CharField(max_length=2, choices=DAY_SYMBOLS, default='-', verbose_name="اليوم___ 10")
    Day11 = models.CharField(max_length=2, choices=DAY_SYMBOLS, default='-', verbose_name="اليوم___ 11")
    Day12 = models.CharField(max_length=2, choices=DAY_SYMBOLS, default='-', verbose_name="اليوم___ 12")
    Day13 = models.CharField(max_length=2, choices=DAY_SYMBOLS, default='-', verbose_name="اليوم___ 13")
    Day14 = models.CharField(max_length=2, choices=DAY_SYMBOLS, default='-', verbose_name="اليوم___ 14")
    Day15 = models.CharField(max_length=2, choices=DAY_SYMBOLS, default='-', verbose_name="اليوم___ 15")
    Day16 = models.CharField(max_length=2, choices=DAY_SYMBOLS, default='-', verbose_name="اليوم___ 16")
    Day17 = models.CharField(max_length=2, choices=DAY_SYMBOLS, default='-', verbose_name="اليوم___ 17")
    Day18 = models.CharField(max_length=2, choices=DAY_SYMBOLS, default='-', verbose_name="اليوم___ 18")
    Day19 = models.CharField(max_length=2, choices=DAY_SYMBOLS, default='-', verbose_name="اليوم___ 19")
    Day20 = models.CharField(max_length=2, choices=DAY_SYMBOLS, default='-', verbose_name="اليوم___ 20")
    Day21 = models.CharField(max_length=2, choices=DAY_SYMBOLS, default='-', verbose_name="اليوم___ 21")
    Day22 = models.CharField(max_length=2, choices=DAY_SYMBOLS, default='-', verbose_name="اليوم___ 22")
    Day23 = models.CharField(max_length=2, choices=DAY_SYMBOLS, default='-', verbose_name="اليوم___ 23")
    Day24 = models.CharField(max_length=2, choices=DAY_SYMBOLS, default='-', verbose_name="اليوم___ 24")
    Day25 = models.CharField(max_length=2, choices=DAY_SYMBOLS, default='-', verbose_name="اليوم___ 25")
    Day26 = models.CharField(max_length=2, choices=DAY_SYMBOLS, default='-', verbose_name="اليوم___ 26")
    Day27 = models.CharField(max_length=2, choices=DAY_SYMBOLS, default='-', verbose_name="اليوم___ 27")
    Day28 = models.CharField(max_length=2, choices=DAY_SYMBOLS, default='-', verbose_name="اليوم___ 28")
    Day29 = models.CharField(max_length=2, choices=DAY_SYMBOLS, default='-', verbose_name="اليوم___ 29")
    Day30 = models.CharField(max_length=2, choices=DAY_SYMBOLS, default='-', verbose_name="اليوم___ 30")
    
    Day31 = models.CharField(max_length=2, choices=DAY_SYMBOLS, default='-', verbose_name="اليوم___ 31")

    class Meta:
        verbose_name = "سجل الشهر"
        verbose_name_plural = "سجلات الأشهر"
        ordering = ["-year", "-month"]

    def str(self):
        return f"{self.present_name} - {self.year}/{self.month}"
    @property
    def last_sick_day(self):
        """هذه ليست حقلاً في قاعدة البيانات بل دالة ذكية"""
        import calendar
        days_in_month = calendar.monthrange(self.year, self.month)[1]
        
        # نبحث من آخر يوم في الشهر (مثلاً 30) رجوعاً إلى يوم 1
        for i in range(days_in_month, 0, -1):
            if getattr(self, f"Day{i}") == 'م':
                return i
        return None
    def count_symbol(self, symbol):
        days_in_month = calendar.monthrange(self.year, self.month)[1]
        fields = [getattr(self, f"Day{i}") for i in range(1, days_in_month + 1)]
        return fields.count(symbol)

    def count_present(self):
        return self.count_symbol('ح')

    def count_sick(self):
        return self.count_symbol('م')

    @property
    def permission(self):
        return self.count_symbol('د') 

    @property
    def excused(self):
        return self.count_symbol('ذ')  

    @property
    def study(self):
        return self.count_symbol('هـ')  

    def count_absent(self):
        return self.count_symbol('غ')
from django.db import models
from django.utils import timezone
from datetime import timedelta

class Violation(models.Model):
    violation_name = models.ForeignKey(Violation_name, on_delete=models.CASCADE, related_name="violations", verbose_name="الاسم")
    date = models.DateField("التاريخ")
    violation_type = models.CharField(
        "نوع المخالفة",
        choices=[
            ("إنذار شفوي", "إنذار شفوي"),
            ("لفت نظر", "لفت نظر"),
            ("إنذار خطي", "إنذار خطي"),
            ("إنذار نهائي", "إنذار نهائي"),
        ],
        max_length=100,
    )
    description = models.TextField("الوصف")
    action_taken = models.CharField("الإجراء المتخذ", max_length=100, blank=True, null=True)
    resolved = models.BooleanField("تم الحل؟", default=False)
    
    def save(self, *args, **kwargs):
    # اليوم ناقص 6 أشهر
         limit_date = timezone.now().date() - timedelta(days=180)

    # إذا تاريخ المخالفة أقدم من 6 أشهر → حل، وإلا لم يُحل
         self.resolved = self.date <= limit_date

         super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.violation_name} - {self.violation_type} ({self.date})"

    class Meta:
        verbose_name = "تفاصيل مخالفة"
        verbose_name_plural = "تفاصيل المخالفات"

# الدورات التطويرية
class DevelopmentCourse(models.Model):
    def __str__(self):
        return f"{self.name} - {self.person}"

    person = models.ForeignKey("Person", on_delete=models.CASCADE, verbose_name="الشخص")
    name = models.CharField("اسم الدورة", max_length=255)
    entity = models.CharField("الجهة", max_length=255, blank=True, null=True)
    year = models.IntegerField("السنة ", blank=True, null=True)
    result = models.CharField("النتيجة", max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "دورة تطويرية"
        verbose_name_plural = "الدورات التطويرية"

#الدورات الاكاديمية
class AcademicCoursePersonal(models.Model):
    def __str__(self):
        return f"{self.name} - {self.person}"

    person = models.ForeignKey("Person", on_delete=models.CASCADE, verbose_name="الشخص")
    name = models.CharField("اسم الدورة", max_length=255)
    entity = models.CharField("الجهة", max_length=255, blank=True, null=True)
    year = models.IntegerField("السنة ", blank=True, null=True)
    result = models.CharField("النتيجة", max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "دورة أكاديمية"
        verbose_name_plural = "الدورات الإكاديمية"

# المؤهلات التعليمية
class Qualification(models.Model):
    def __str__(self):
        return f"{self.degree} - {self.person} ({self.year})"

    person = models.ForeignKey(Person, on_delete=models.CASCADE, verbose_name="الشخص")
    degree = models.CharField("المؤهل", max_length=100, blank=True, null=True)
    institution = models.CharField("المؤسسة التعليمية", max_length=255, blank=True, null=True)
    year = models.IntegerField("سنة التخرج", blank=True, null=True)
    avarg = models.IntegerField("المعدل ", blank=True, null=True)
    grade = models.CharField("التقدير", max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = "مؤهل أكاديمي"
        verbose_name_plural = "المؤهلات الأكاديمية"


# العلاجات
class Medical(models.Model):
    def __str__(self):
        return f"{self.person} - {self.date} - {self.status} - {self.notes}"
    person = models.ForeignKey(Person, on_delete=models.CASCADE,verbose_name="الشخص")

    date = models.DateField("التاريخ")
    status = models.CharField(
        "الحالة الصحية",
        choices=[
            ("سليم", "سليم"),
            ("مريض", "مريض"),
            ("حالة حرجة", "حالة حرجة"),
            ("إصابات أخرى", "إصابات أخرى"),
            ("غير محدد", "غير محدد"),
        ],
        max_length=100,
    )
    notes = models.TextField(verbose_name="خلاصة عن الأمراض", blank=True, null=True)
    type_sex = models.TextField(verbose_name=" نوع المرض", blank=True, null=True)
    
    medicines = models.TextField(verbose_name="العلاجات", blank=True, null=True)

    class Meta:
        verbose_name = "العلاج"
        verbose_name_plural = "العلاجات"

class Covenant(models.Model):
    def __str__(self):
        return f"{self.person}"

    person = models.ForeignKey(Person, on_delete=models.CASCADE, verbose_name="الشخص")
    class Meta:
        verbose_name = "العهدة"
        verbose_name_plural = "العهد"

class Type_covenants(models.Model):
    type_name_covenants = models.CharField(max_length=100, verbose_name="نوع العهدة")

    def __str__(self):
        return self.type_name_covenants

    class Meta:
        verbose_name = "العهدة"
        verbose_name_plural = "أنواع العهد"


class Name_covenants_covenants(models.Model):
    name_covenants_covenant = models.CharField(max_length=100, verbose_name="اسم العهدة")
    def __str__(self):
        return self.name_covenants_covenant
    class Meta:
            verbose_name = "العهدة"
            verbose_name_plural = "أسماء العهد"

class Name_covenants(models.Model):
    def __str__(self):
        return f"{self.covenantor} {self.name_covenants} - {self.type_covenant} {self.quantity} {self.date} {self.notes}"
    covenantor = models.ForeignKey(Covenant, on_delete=models.CASCADE, verbose_name="الشخص")
    
    type_covenant = models.ForeignKey(
        Type_covenants, on_delete=models.CASCADE, verbose_name="نوع العهدة"
    )
    name_covenants = models.ForeignKey(Name_covenants_covenants,on_delete=models.CASCADE, verbose_name="اسم العهدة")
    quantity = models.IntegerField(verbose_name="_____الكمية___")
    CHOICES = (
        ("معه", "معه"),
        ("لم يتم ارجاعها", "لم يتم ارجاعها"),
    )

    name = models.CharField(max_length=50, choices=CHOICES, verbose_name="العهدة")
    

    date = models.DateField(verbose_name="تاريخ الاستلام ", blank=True, null=True)
    return_date = models.DateField(blank=True, null=True, verbose_name="تاريخ الرجوع")

    notes = models.TextField(verbose_name="ملاحظات", blank=True, null=True)

    class Meta:
            verbose_name = "العهدة"
            verbose_name_plural = "أسماء العهد"
class Tutors(models.Model):
    def __str__(self):
        return f"{self.person} - {self.subject} - {self.start_date} - {self.end_date} - {self.mark}"

    person = models.ForeignKey(Name, on_delete=models.CASCADE, verbose_name="المدرب")
    people = models.ManyToManyField(Person, blank=True, verbose_name="المتدربون")
    subject = models.CharField(max_length=50, verbose_name="المادة")
    start_date = models.DateField(verbose_name="تاريخ البداية", blank=True, null=True)
    end_date = models.DateField(verbose_name="تاريخ النهاية", blank=True, null=True)
    mark = models.CharField(max_length=50, verbose_name="النتيجة / التقييم", blank=True, null=True)
    notes = models.TextField(verbose_name="ملاحظات", blank=True, null=True)

    class Meta:
        verbose_name = "المدرب"
        verbose_name_plural = "المدربون"

from django.db import models
# موديل جانب العبادة


from django.db import models
from django.utils import timezone
import datetime

PRIORITY_CHOICES = [
    ('عالي', 'عالي'),
    ('متوسط', 'متوسط'),
    ('منخفض', 'منخفض'),
    ]
class Task(models.Model):
    STATUS_CHOICES = [
        ('تم', 'تم'),
        ('لم يتم', 'لم يتم'),
    ]
    
    TYPE_CHOICES = [
        ('مالية', 'مالية'),
        ('إدارية', 'إدارية'),
        ('تجهيزات', 'تجهيزات'),
        ("لوجستي", "لوجستي"),
    ]
    
    # المكلف
    delegate = models.ForeignKey(
        Name, on_delete=models.CASCADE, verbose_name="المكلف",
        null=True, blank=True, related_name='tasks_as_delegate'
    )
    
    # المتابع
    follower = models.ForeignKey(
        Name, on_delete=models.CASCADE, verbose_name="المتابع",
        null=True, blank=True, related_name='tasks_as_follower'
    )
    
    # المهمة
    name = models.CharField("المهمة", max_length=200)
    

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='متوسط',
        verbose_name="الأولوية"
    )
    # النوع
    type = models.CharField("النوع", max_length=50, choices=TYPE_CHOICES)
    
    # النقاط
    urgency_score = models.IntegerField("النقاط", default=0)
    
    # الحالة
    status = models.CharField("الحالة", max_length=20, choices=STATUS_CHOICES, default='لم يتم')
    
    # التاريخ
    date = models.DateField("التاريخ", default=timezone.now)
    
    # الوقت
    time = models.TimeField("الوقت", default=timezone.now)
    
    # النتيجة (تظهر فقط إذا تمت المهمة)
    result = models.CharField("النتيجة", max_length=200, blank=True, null=True)
    
    # تاريخ ووقت الإنشاء
    created_at = models.DateTimeField("تاريخ ووقت الإنشاء", auto_now_add=True)
    
    class Meta:
        verbose_name = "مهمة"
        verbose_name_plural = "المهام"
        ordering = ['-created_at']
    
    def __str__(self):
        try:
            delegate_name = self.delegate.name if self.delegate else "غير محدد"
        except AttributeError:
            delegate_name = "غير محدد"
        return f"{self.name} - {delegate_name}"
    
    @property
    def datetime(self):
        return datetime.datetime.combine(self.date, self.time)
    
    @property
    def is_overdue(self):
        if self.status == 'تم':
            return False
        now = timezone.now()
        task_datetime = timezone.make_aware(self.datetime)
        return task_datetime < now
    
    @property
    def time_12h(self):
        hour = self.time.hour
        minute = self.time.minute
        period = "صباحاً" if hour < 12 else "مساءً"
        hour_12 = hour % 12
        if hour_12 == 0:
            hour_12 = 12
        return f"{hour_12:02d}:{minute:02d} {period}"
    
    def save(self, *args, **kwargs):
        # حساب النقاط تلقائياً قبل الحفظ
        self.calculate_urgency_score()
        super().save(*args, **kwargs)
    
    def calculate_urgency_score(self):
        score = 0
        
        # حساب نقاط الأولوية حسب النوع
        if self.type == 'مالية':
            score += 100
        elif self.type == 'إدارية':
            score += 80
        elif self.type == 'لوجستي':
            score += 60
        else:  # تجهيزات
            score += 40
            
        # حساب نقاط التأخير
        if self.is_overdue:
            now = timezone.now()
            task_datetime = timezone.make_aware(self.datetime)
            hours_overdue = (now - task_datetime).total_seconds() / 3600
            score += min(int(hours_overdue * 5), 200)
            
        # حساب نقاط الاستعجال للمهام غير المكتملة
        if self.status == 'لم يتم':
            now = timezone.now()
            task_datetime = timezone.make_aware(self.datetime)
            hours_until_due = (task_datetime - now).total_seconds() / 3600
            
            if hours_until_due <= 24:
                score += 80
            elif hours_until_due <= 48:
                score += 40
            elif hours_until_due <= 168:
                score += 20
                
        self.urgency_score = score
# قائمة أيام الأسبوع
DAY_OF_WEEK_CHOICES = [
    ('السبت', 'السبت'),
    ('الأحد', 'الأحد'),
    ('الاثنين', 'الاثنين'),
    ('الثلاثاء', 'الثلاثاء'),
    ('الأربعاء', 'الأربعاء'),
    ('الخميس', 'الخميس'),
    ('الجمعة', 'الجمعة'),
]

class DailyAttendance_name(models.Model):
    person = models.ForeignKey('Name', on_delete=models.CASCADE, verbose_name="الشخص")
    
    def __str__(self):
        return str(self.person)

    class Meta:
        verbose_name = "حضور يومي"
        verbose_name_plural = "الحضور اليومي"
        ordering = ['person__first_name']

class DailyAttendance(models.Model):
    attendance_parent = models.ForeignKey(DailyAttendance_name, on_delete=models.CASCADE, verbose_name="سجل الشخص")
    
    date = models.DateField(verbose_name="التاريخ")
    
    day_name = models.CharField(
        max_length=10,
        choices=DAY_OF_WEEK_CHOICES,
        verbose_name="اليوم",
        blank=True  # جعلناه اختياري ليتم تعبئته تلقائياً
    )
    
    check_in = models.TimeField(verbose_name="وقت الدخول")
    check_out = models.TimeField(verbose_name="وقت الخروج")
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "سجل الحضور اليومي"
        verbose_name_plural = "سجلات الحضور اليومية"
        ordering = ["-date"]

    def save(self, *args, **kwargs):
        # حساب اسم اليوم تلقائياً بناءً على التاريخ
        # ترتيب weekday في بايثون يبدأ من الاثنين=0 وينتهي بالأحد=6
        days = ["الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]
        if self.date:
            self.day_name = days[self.date.weekday()]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.attendance_parent} - {self.date}"