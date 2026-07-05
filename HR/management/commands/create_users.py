import os
import django
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Permission, Group
from django.contrib.contenttypes.models import ContentType
from HR.models import *  # غيّر HR.models حسب اسم تطبيقك

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HR.settings')
django.setup()

# -------------------------------
# الأقسام المسموح بها لكل مستخدم
# -------------------------------
USER_SECTIONS = {
    "eshaiq": ["all"],
    "asmail": ["all"],
    "muad": ["all_models_only"],  
    
    "ahmed": [
        "StaffAdmin",
        "PersonAdminExtended",
        "QualificationAdmin",
       
        "AcademicCourseAdmin",
        "ViolationNameAdmin",
        "TaskAdmin",
        "NameAdmin",
        "DevelopmentCourse",
        "ViolationAdmin"
    ],
    "abas": [
        "AcademicCourse",
        "StudentSubjectEnrollmentAdmin",
        "AcademicCoursePersonalAdmin",
        "QualificationAdmin",
        "Type_covenantsAdmin",
        "TutorsAdmin",
        "NameAdmin",
        "ViolationAdmin",
        "CovenantAdmin",
        "TypeCovenantsAdmin",
        "NameCovenantsCovenantsAdmin",
        "NameCovenantsAdmin",
        "StudentAdmin",
        "SubjectAdmin"
    ],
    "mjad": ["MedicalAdmin"],
    "taloot": ["PaymentAdmin"],
}

# -------------------------------
# ربط كل قسم بالموديل
# -------------------------------
SECTION_MODELS = {
    "all_models_only": [
       Person, StudentSubjectEnrollment, Payment, Violation,
        DevelopmentCourse, Qualification,
        Medical, Covenant, Name_covenants, Tutors
    ],

    "StaffAdmin": [Person, Staff],
    "QualificationAdmin": [Person, Qualification],

    "ViolationNameAdmin": [Person, Violation_name],
    "TaskAdmin": [Person, Task, AcademicCoursePersonal],
    "StudentSubjectEnrollmentAdmin": [Person, StudentSubjectEnrollment],
    "TutorsAdmin": [Person, Tutors],
    "MedicalAdmin": [Person, Medical],
    "PaymentAdmin": [Person, Payment],
    "Type_covenantsAdmin": [Person, Type_covenants],
    "DevelopmentCourse": [Person, DevelopmentCourse],
    "NameAdmin": [Person, Name],
    "ViolationAdmin": [Person, Person, Violation],
    "CovenantAdmin": [Person, Covenant],
    "TypeCovenantsAdmin": [Person, Type_covenants],
    "NameCovenantsCovenantsAdmin": [Person, Name_covenants_covenants],
    "NameCovenantsAdmin": [Person, Name_covenants],
    "StudentAdmin": [Person, Student],
    "SubjectAdmin": [Person, Subject],
    "all": [
     Person, StudentSubjectEnrollment, Payment, Violation,
        DevelopmentCourse, AcademicCoursePersonal, Qualification,
        Medical, Covenant, Name_covenants, Tutors
    ],
}

# -------------------------------
# تعريف قسم الحضور
# -------------------------------
SECTION_MODELS["PresentAdmin"] = [Present_name, Present]

# -------------------------------
# إضافة هذا القسم للمستخدمين المحددين
# -------------------------------
for username in ["ahmed", "asmail", "eshaiq"]:
    if "PresentAdmin" not in USER_SECTIONS[username]:
        USER_SECTIONS[username].append("PresentAdmin")
SECTION_MODELS["PersonAdminExtended"] = [Person, Address, PersonalIDCard]
SECTION_MODELS["AcademicCoursePersonalAdmin"] = [AcademicCoursePersonal]


USER_SECTIONS['muad'] = ['all']

SECTION_MODELS["all_models_only"].extend([University, Specialization])
SECTION_MODELS["StudentAdmin"].extend([University, Specialization])
SECTION_MODELS["all"].extend([University, Specialization])

# -------------------------------
# قائمة المستخدمين
# -------------------------------
USERS = [
    {'username': 'eshaiq', 'password': 'eshaiq64839'},
    {'username': 'asmail' , 'password': 'asmail774815916'},
    {'username': 'muad', 'password': 'muad73901'},  
 
    {'username': 'ahmed', 'password': 'ahmed48081'},
    {'username': 'abas', 'password': 'abas60381'},
    {'username': 'mjad', 'password': 'mjad04927'},
    {'username': 'taloot', 'password': 'taloot417'},
]

# -------------------------------
# دالة لتحديد الـ fieldsets
# -------------------------------
def get_fieldsets(self, request, obj=None):
    restricted_users = ["abas",  "mjad", "taloot"]
    if request.user.username in restricted_users:
        return (("المعلومات الشخصية", {"fields": ("name",)}),)
    return super().get_fieldsets(request, obj)

# -------------------------------
# إنشاء أو تحديث المستخدمين
# -------------------------------
class Command(BaseCommand):
    help = "إنشاء أو تحديث المستخدمين مع الصلاحيات المحددة لكل مستخدم"

    def handle(self, *args, **kwargs):
        # إنشاء مجموعة WorshipAdmin وإضافة صلاحيات النماذج الثقافية
        worship_group, created = Group.objects.get_or_create(name="WorshipAdmin")
        cultural_models = [
        ]
        for model in cultural_models:
            content_type = ContentType.objects.get_for_model(model)
            perms = Permission.objects.filter(content_type=content_type)
            for perm in perms:
                worship_group.permissions.add(perm)
        worship_group.save()
        self.stdout.write(self.style.SUCCESS("✅ تم إعداد مجموعة WorshipAdmin مع صلاحيات النماذج الثقافية"))

        # إنشاء المستخدمين وإعطاء الصلاحيات
        for u in USERS:
            user, created = User.objects.get_or_create(username=u['username'])
            user.set_password(u['password'])

            # تحديد صلاحيات خاصة بكل مستخدم
            if u['username'] == 'muad':
                user.is_superuser = False
                user.is_staff = False
                user.is_active = True
            else:
                user.is_superuser = u['username'] in ['eshaiq', 'asmail']
                user.is_staff = True
                user.is_active = True

            user.save()

            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ تم إنشاء المستخدم: {u['username']}"))
            else:
                self.stdout.write(self.style.WARNING(f"⚠️ المستخدم {u['username']} موجود بالفعل، تم تحديث بياناته"))

            # مسح أي صلاحيات موجودة وإعطاء صلاحيات الأقسام لجميع المستخدمين
            user.user_permissions.clear()

            sections = USER_SECTIONS.get(u['username'], [])
            for section in sections:
                models_list = SECTION_MODELS.get(section, [])
                for model in models_list:
                    content_type = ContentType.objects.get_for_model(model)
                    perms = Permission.objects.filter(content_type=content_type)
                    user.user_permissions.add(*perms)

            # ✅ إضافة صلاحية view_person للمستخدمين المحددين (لتظهر خيارات الاسم)
            if u['username'] in ["abas", "mjad", "taloot"]:
                content_type = ContentType.objects.get_for_model(Person)
                view_perm = Permission.objects.get(content_type=content_type, codename="view_person")
                user.user_permissions.add(view_perm)

            # ربط المستخدم بالمجموعة إذا كان cultural
            if 'WorshipSideSecond' in sections:
                user.groups.add(worship_group)

            user.save()

        self.stdout.write(self.style.SUCCESS("🎉 جميع المستخدمين تم إنشاؤهم/تحديثهم بنجاح!"))
