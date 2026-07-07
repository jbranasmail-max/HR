# Admin for PersonalIDCard
from django import forms
from django.db import models
from import_export.admin import ImportExportModelAdmin
from django_daisy.mixins import NavTabMixin
from django.contrib import admin
from .models import *

@admin.register(PersonalIDCard)
class PersonalIDCardAdmin(ImportExportModelAdmin):
    def has_module_permission(self, request):
        return False

    list_display = ("card_number", "issue_date", "expiry_date", "governorate")
    search_fields = ("person__name__first_name", "card_number")
    list_filter = ("issue_date", "expiry_date", "governorate")

    fieldsets = (
        ("معلومات البطاقة", {"fields": ("card_number", "issue_date", "expiry_date")}),
        (
            "مكان الميلاد",
            {"fields": ("governorate", "district", "sub_district", "village")},
        ),
        ("فصيلة الدم:", {"fields": ("blood_Type",)}),
    )


@admin.register(University)
class UniversityAdmin(ImportExportModelAdmin):
    def has_module_permission(self, request):
        return False

    list_display = ("name",)
    search_fields = ("name",)
    list_filter = ("name",)


@admin.register(Specialization)
class SpecializationAdmin(ImportExportModelAdmin):
    def has_module_permission(self, request):
        return False

    list_display = ("name",)
    search_fields = ("name",)
    list_filter = ("name",)


@admin.register(DevelopmentCourse)
class DevelopmentCourseAdmin(ImportExportModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = ("name", "person", "year", "result","entity")
    search_fields = ("name", "person__name__first_name", "person__name__last_name")
    list_filter = ("year",)
    autocomplete_fields = ["person"]

class DevelopmentCourseInline(NavTabMixin,admin.TabularInline):
    model = DevelopmentCourse
    extra = 1


class QualificationInline(NavTabMixin, admin.TabularInline):
    model = Qualification
    extra = 1   

@admin.register(AcademicCoursePersonal)
class AcademicCoursePersonalAdmin(ImportExportModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = ("name", "person", "year", "result" ,"entity")
    search_fields = ("name", "person__name__first_name", "person__name__last_name")
    list_filter = ("year",)
    autocomplete_fields = ["person"]

class AcademicCoursePersonalInline(NavTabMixin,admin.TabularInline):
    model = AcademicCoursePersonal
    extra = 1
# Admin for Person
@admin.register(Person)
class PersonAdmin(ImportExportModelAdmin):
    list_display = (
        "name",
        "typestatus"

        
    )

    list_display_links  = (
        "name",

    )

    search_fields = (
    "name__first_name",
    "name__second_name",
    "name__third_name",
    "name__forth_name",
    "name__last_name",
    "phone",
    )

    list_filter = [
        "address__city",
     
        "is_present",
        "marital_status",
        "health_condition",
     
    ]

    autocomplete_fields = ["name", "address", "national_id"]

    actions = ["export_as_excel"]
    inlines = [QualificationInline,DevelopmentCourseInline,AcademicCoursePersonalInline]

    fieldsets = (
    (
        "المعلومات الشخصية",
        {
            "fields": (
                "name",
                "address",
                "date_of_birth",
                "national_id",
                "marital_status",
                "male_children",
                "female_children",
                "health_condition",
                "status",
            )
        },
        ),
        (
        "معلومات التواصل",
        {
            "fields": (
                "phone",
                "email",
            )
        },
        ),
           )
    (
            "معلومات التواصل",
            {
                "fields": (
                    "phone",
                    "email",
                )
            },
        ),
    (
            "المؤهل والدراسة",
            {
                "fields": (
                    "academic_qualification",
                    "high_school_grade",
                    "entry_date",
              
                )
            },
        ),
    
            
    (
            "التوقف",
            {
                "fields": (
                    
                    "typestatus",
                    "stop_reason",
                    "exit_date",
                    
                )
            },
        ),
      
    
    
     # داخل كلاس PersonAdmin
    def get_fieldsets(self, request, obj=None):
       restricted_users = ["abas", "sadiq", "mjad", "taloot"] 
       if request.user.username in restricted_users:
          return (
            ("المعلومات الشخصية", {"fields": ("name",)}),
          )
  
       return super().get_fieldsets(request, obj)


    def export_as_excel(self, request, queryset):
        import openpyxl
        from django.http import HttpResponse

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Persons"
        headers = [
            "الاسم",
            "رقم الجوال",
            "متواجد",
            "البريد الإلكتروني",
            "العنوان",
            "تاريخ الميلاد",
            "رقم البطاقة",
            "المؤهل العلمي",
            "معدل الثانوية العامة",
            "تأريخ الدخول",
          
            "الحالة المادية",
            "الحالة الأجتماعية",
       
        ]
        ws.append(headers)
        for obj in queryset:
            ws.append(
                [
                    str(obj.name),
                    obj.phone,
                    obj.is_present,
                    obj.email,
                    str(obj.address),
                    obj.date_of_birth,
                    str(obj.national_id),
                    obj.academic_qualification,
                    obj.high_school_grade,
                    obj.entry_date,
     
                    obj.status,
                    obj.marital_status,
                    obj.health_condition,
               
                ]
            )

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = "attachment; filename=persons.xlsx"
        wb.save(response)
        return response
    def delete_link(self, obj):
        from django.utils.html import format_html
        return format_html('<a href="/admin/HR/person/{}/delete/">ازاله</a>', obj.id)
    
    delete_link.short_description = "حذف"

    export_as_excel.short_description = "تصدير إلى Excel"


class StudentSubjectEnrollmentInline(NavTabMixin,admin.TabularInline):
    model = StudentSubjectEnrollment
    extra = 1
@admin.register(Subject)
class SubjectAdmin(ImportExportModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name", "description")

    def has_module_permission(self, request):
        return False


# Admin for StudentSubjectEnrollment
@admin.register(StudentSubjectEnrollment)
class StudentSubjectEnrollmentAdmin(ImportExportModelAdmin):
    list_display = (
        "student",
        "subject",
        "learn_year",
        "semester",
        "mrak_of_subject",
        "enrollment_date",
    )
    
    search_fields = (
        "student__person__name__first_name",
        "student__person__name__last_name",
        "subject__name",
    )
    list_filter = ("student", "learn_year", "semester", "enrollment_date")
    autocomplete_fields = ["student", "subject"]
    list_per_page = 25
    ordering = ("-enrollment_date",)
    date_hierarchy = "enrollment_date"
    def has_module_permission(self, request):
        return False




# Admin for Name
@admin.register(Name)
class NameAdmin(ImportExportModelAdmin):
    list_display = (
        "first_name",
        "second_name",
        "third_name",
        "forth_name",
        "last_name",
        "arabic_full_name",
    )
    
    search_fields = (
        "first_name",
        "second_name",
        "third_name",
        "forth_name",
        "last_name",
        "arabic_full_name",
    )

    def has_module_permission(self, request):
        return False


# Admin for Address
@admin.register(Address)
class AddressAdmin(ImportExportModelAdmin):
    list_display = ("street", "city", "state", "country")
    search_fields = ("street", "city", "state", "country")

    def has_module_permission(self, request):
        return False


@admin.register(Year_choices)
class Year_choicesAdmin(ImportExportModelAdmin):
    list_display = ["name_year",]
    def has_module_permission(self, request):
        return False
    
@admin.register(Semester_choices)
class Semester_choicesAdmin(ImportExportModelAdmin):
    list_display = ["name_semester",]
    def has_module_permission(self, request):
        return False

# Admin for Student
@admin.register(Student)
class StudentAdmin(ImportExportModelAdmin):
    list_display = (
        "person",
        "specialization",
        "university",
        "start_date",
        "stop_date",
        "stop_reason",
    )

    list_display_links = (
        "person",
        "specialization",
        "university",
        "start_date",
        "stop_date",
        "stop_reason",
    )
    
    search_fields = (
        "person__name__first_name",
        "person__name__last_name",
        "specialization__name",
    )
    list_filter = (
        "specialization",
        "university",
    )
    autocomplete_fields = ["person"]
    inlines = [StudentSubjectEnrollmentInline]



# Admin for Staff
@admin.register(Staff)
class StaffAdmin(ImportExportModelAdmin):
    list_display = (
        "person",
        "position",
        "start_date",
        "continue_work",
        "stop_date",
        "stop_reason",
        "text_notes",
    )
    search_fields = ("person__name__first_name", "person__name__last_name", "position")
    list_filter = ("position", "start_date", "stop_date")
    autocomplete_fields = ["person"]


# Admin for AcademicCourse


# Admin for Subject




# Admin for Attendance
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from django.contrib import admin
from import_export.admin import ImportExportModelAdmin


# تسجيل موديل Attendance في الأدمين

# Admin for Payment
@admin.register(Payment)
class PaymentAdmin(ImportExportModelAdmin):
    list_display = (
        "person",
        "accreditation",
        "salary",
        "visit",
        "expenses",
        "transfers",
        "qat",
        "help",
        "rent",
        "date",
    )

    search_fields = (
    "person__name__first_name",
    "person__name__second_name",
    "person__name__third_name",
    "person__name__forth_name",
    "person__name__last_name",
    )

    list_filter = ("date", "accreditation")
    autocomplete_fields = ["person"]


# Admin for Violationclass ViolationInline(admin.TabularInline):  # أو StackedInline لو تحب عمودي
class ViolationInline(NavTabMixin,admin.StackedInline):
    model = Violation
    extra = 1


@admin.register(Violation_name)
class ViolationNameAdmin(ImportExportModelAdmin):
    list_display = ("person", "get_violation_type", "get_violation_date","get_violation_status",)
    list_display_links = ("person", "get_violation_type", "get_violation_date","get_violation_status",)
    search_fields = ("person__name__first_name", "person__name__last_name")
    list_filter = ("violations__resolved","violations__violation_type")
    autocomplete_fields = ["person"]
    inlines = [ViolationInline]

    def get_violation_type(self, obj):
        # يجيب أول نوع مخالفة مرتبط بالاسم
        violation = obj.violations.first()
        return violation.violation_type if violation else "-"
    get_violation_type.short_description = "نوع المخالفة"

    def get_violation_date(self, obj):
        violation = obj.violations.first()
        return violation.date if violation else "-"
    get_violation_date.short_description = "تاريخ المخالفة"

    def get_violation_status(self, obj):
        violation = obj.violations.first()
        if violation:
            return "✅ تم الحل" if violation.resolved else "❌ لم يُحل"
        return "-"
    get_violation_status.short_description = "حالة الحل"

# Admin for DevelopmentCourse


# Admin for Qualification

@admin.register(Medical)
class MedicalAdmin(ImportExportModelAdmin):
    list_display = ("person", "date", "status", "type_sex", "medicines", "notes")
    search_fields = (
    "person__name__first_name",
    "person__name__second_name",
    "person__name__third_name",
    "person__name__forth_name",
    "person__name__last_name",
    "notes",
    )

    list_filter = ("date", "status")
    autocomplete_fields = ["person"]

    
@admin.register(Type_covenants)
class Type_covenantsAdmin(ImportExportModelAdmin):
    def has_module_permission(self, request):
        return False

    list_display = ("type_name_covenants",)
    search_fields = ("type_name_covenants",)
    list_filter = ("type_name_covenants",)

@admin.register(Name_covenants_covenants)
class name_covenants_covenantsAdmin(ImportExportModelAdmin):
    def has_module_permission(self, request):
        return False

    list_display = ("name_covenants_covenant",)
    search_fields = ("name_covenants_covenant",)
    list_filter = ("name_covenants_covenant",)
@admin.register(Name_covenants)
class AdminName_covenants(ImportExportModelAdmin):
    list_display = ["covenantor", "type_covenant", "quantity", "date", "notes"]
    list_filter = ["type_covenant", "date"]
    search_fields = ["covenantor"]

    formfield_overrides = {
        models.TextField: {"widget": forms.Textarea(attrs={"rows": 1, "cols": 40})},
    }

    def has_module_permission(self, request):
        return False

class CovenantsInlin(NavTabMixin,admin.TabularInline):
    model = Name_covenants
    extra = 1
    tab_name = 'العهد'

@admin.register(Covenant)
class CovenantAdmin(ImportExportModelAdmin):
    list_display = (
        "person",
        "get_name",
        "get_type_covenant",
        "get_quantity",
    )
    list_filter = (
        "name_covenants__type_covenant",
        "name_covenants__name_covenants",
    )
    list_display_links = (
        "person",
        "get_type_covenant",
        "get_name",
        "get_quantity",
    )
    search_fields = (
    "person__name__first_name",
    "person__name__second_name",
    "person__name__third_name",
    "person__name__forth_name",
    "person__name__last_name",
  
    )
 

    autocomplete_fields = ["person"]
    inlines = [CovenantsInlin]
    def get_name(self, obj):
        names = obj.name_covenants_set.values_list(
        "name_covenants__name_covenants_covenant", flat=True
    )
        return ", ".join(str(n) for n in names if n) if names else "-"
    get_name.short_description = "أسم العهدة"

    def get_type_covenant(self, obj):
        types = obj.name_covenants_set.values_list("type_covenant__type_name_covenants", flat=True)
        return ", ".join(types) if types else "-"
    get_type_covenant.short_description = "نوع العهدة"

    def get_quantity(self, obj):
        quantities = obj.name_covenants_set.values_list("quantity", flat=True)
        return ", ".join(str(q) for q in quantities) if quantities else "-"
    get_quantity.short_description = "الكمية"

@admin.register(Tutors)
class TutorsAdmin(ImportExportModelAdmin):
    list_display = ("person", "subject", "start_date", "end_date", "mark", "notes")
    list_filter = ("subject", "start_date", "end_date", "mark")
    search_fields = ("person__first_name", "person__last_name", "subject")
    autocomplete_fields = ["person"]
    filter_vertical = ("people",)

    fieldsets = (
        ("المعلومات الأساسية", {
            "fields": ("person", "subject", "start_date", "end_date", "mark")
        }),
        ("الملاحظات", {
            "fields": ("notes",)
        }),
        ("المتدربون", {
            "fields": ("people",)
        }),
    )
from django.contrib import admin
from .models import Task, Name

class PresentInline(admin.TabularInline):
    model = Present
    extra = 0

    
    # السر هنا: يجب أن تكون الدالة في الـ readonly_fields حصراً

    fields = ['year', 'month'] + [f'Day{i}' for i in range(1, 32)]+ ['show_last_m_day']
    readonly_fields = ['show_last_m_day']
    can_delete = True
    show_change_link = True
    def show_last_m_day(self, obj):
        # التأكد أن السجل محفوظ وله بيانات
        if obj and obj.id:
            day = obj.last_sick_day # ينادي الـ property من الموديل
            return f"يوم {day}" if day else "لا يوجد"
        return "-"
    
    show_last_m_day.short_description = "آخر يوم (م)"

@admin.register(Present_name)
class PresentNameAdmin(ImportExportModelAdmin):
    autocomplete_fields = ["person"]
    inlines = [PresentInline] 

    list_display = (
        "person",
        "count_h", "count_m", "count_g", "count_d", "count_th", "count_holiday"
    )
    search_fields = (
    "person__first_name",
    "person__second_name",
    "person__third_name",
    "person__forth_name",
    "person__last_name",
    )

    def count_h(self, obj):
        return sum(p.count_symbol('ح') for p in obj.presents.all())
    count_h.short_description = "حضور"

    def count_m(self, obj):
        return sum(p.count_symbol('م') for p in obj.presents.all())
    count_m.short_description = "مزاوره"

    def count_g(self, obj):
        return sum(p.count_symbol('غ') for p in obj.presents.all())
    count_g.short_description = "غياب"

    def count_d(self, obj):
        return sum(p.count_symbol('د') for p in obj.presents.all())
    count_d.short_description = "دوره"

    def count_th(self, obj):
        return sum(p.count_symbol('ذ') for p in obj.presents.all())
    count_th.short_description = "مذاكره"

    def count_holiday(self, obj):
       return sum(p.count_symbol('هـ') for p in obj.presents.all())
    count_holiday.short_description = "مهمه"
from django.db.models import Case, When
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    # تعديل الحقول الخاصة بالـ ForeignKey
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ['delegate', 'follower']:
            # جلب جميع الموظفين النشطين
            active_staff = Staff.objects.filter(continue_work=True)
            # جلب الأشخاص المرتبطين بالموظفين النشطين فقط
            active_person_ids = active_staff.values_list('person_id', flat=True)
            # جلب الأسماء المرتبطة بالموظفين النشطين
            active_names = Name.objects.filter(person__id__in=active_person_ids).order_by(
                'first_name', 'second_name', 'third_name', 'forth_name', 'last_name'
            )
            kwargs["queryset"] = active_names
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # عرض الاسم الكامل في الـ Admin
    list_display = (
        'name_display', 
        'delegate_display', 
        'follower_display', 
        'type', 
        'status', 
        'date', 
        'time', 
        'urgency_score',
        'result',
        "priority"
    )

    # وظائف مساعدة لعرض الاسم الكامل بأمان
    def name_display(self, obj):
        if hasattr(obj.name, 'arabic_full_name'):
            return obj.name.arabic_full_name
        return str(obj.name)
    name_display.short_description = "اسم المهمة"

    def delegate_display(self, obj):
        if hasattr(obj.delegate, 'arabic_full_name'):
            return obj.delegate.arabic_full_name
        return str(obj.delegate) if obj.delegate else "-"
    delegate_display.short_description = "المكلف "

    def follower_display(self, obj):
        if hasattr(obj.follower, 'arabic_full_name'):
            return obj.follower.arabic_full_name
        return str(obj.follower) if obj.follower else "-"
    follower_display.short_description = "المتابع"

    list_display_links = ('name_display', 'delegate_display')

    list_filter = (
        'status', 
        'type', 
        'delegate', 
        'follower',
        'date'
    )
    
    search_fields = (
    "delegate__first_name",
    "delegate__second_name",
    "delegate__third_name",
    "delegate__forth_name",
    "delegate__last_name",
    "follower__first_name",
    "follower__second_name",
    "follower__third_name",
    "follower__forth_name",
    "follower__last_name",
)

    
    ordering = ('-created_at',)
    list_per_page = 20
    
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': (
                'name', 
                'delegate', 
                'follower'
            )
        }),
        ('تفاصيل المهمة', {
            'fields': (
                "priority",
                'type', 
                'status', 
                'urgency_score'
            )
        }),
        ('التاريخ والوقت', {
            'fields': (
                'date', 
                'time', 
                'created_at'
            )
        }),
        ('النتيجة', {
            'fields': ('result',),
            'classes': ('collapse',),
            'description': 'املأ حقل النتيجة فقط عند إتمام المهمة'
        })
    )
    
    readonly_fields = ('created_at', 'urgency_score')

# @admin.register(Task)
# class TaskAdmin(admin.ModelAdmin):
#     list_display = (
#         'name', 
#         'delegate', 
#         'follower', 
#         'type', 
#         'status', 
#         'date', 
#         'time', 
#         'urgency_score',
#         'result',
#         "priority"
#     )
    
#     list_display_links = ('name', 'delegate')
#     list_filter = ('status', 'type', 'delegate', 'follower', 'date')
#     search_fields = ('name', 'result', 'delegate__first_name', 'follower__first_name')
#     ordering = ('-created_at',)
#     list_per_page = 20
#     readonly_fields = ('created_at', 'urgency_score')

#     # ==============================
#     # IDs المخصصة التي تريد ظهورها فقط وبالترتيب الذي تريد
#     allowed_ids = [1, 71, 174, 42, 173, 181, 20, 175, 177, 30, 5, 18]
#     # ==============================

#     # استخدام autocomplete لتسهيل البحث بين هؤلاء الأشخاص فقط
#     autocomplete_fields = ['delegate', 'follower']

#     def formfield_for_foreignkey(self, db_field, request, **kwargs):
#         """
#         هذه الدالة تعرض فقط الأشخاص الموجودين في allowed_ids
#         وبالترتيب الذي حددته في allowed_ids
#         """
#         if db_field.name in ('delegate', 'follower'):
#             preserved_order = Case(*[When(id=pk, then=pos) for pos, pk in enumerate(self.allowed_ids)])
#             kwargs["queryset"] = Name.objects.filter(id__in=self.allowed_ids).order_by(preserved_order)
#         return super().formfield_for_foreignkey(db_field, request, **kwargs)

from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.utils import timezone
import pytz
from .models import LoginHistory

# -------------------------------
# دوال مساعدة للتنسيق بالعربية
# -------------------------------
def to_arabic_numbers(number_str):
    arabic_numbers = "٠١٢٣٤٥٦٧٨٩"
    return "".join(arabic_numbers[int(ch)] if ch.isdigit() else ch for ch in number_str)

def format_time_arabic(dt):
    hour_str = dt.strftime("%I:%M:%S %p")
    time_part, am_pm = hour_str[:-3], hour_str[-2:]
    am_pm_ar = "صباحًا" if am_pm.upper() == "AM" else "مساءً"
    return f"{to_arabic_numbers(time_part)} {am_pm_ar}"

def arabic_weekday(dt):
    weekdays = ["الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]
    return weekdays[dt.weekday()]


# -------------------------------
# لوحة إدارة سجل الدخول والخروج
# -------------------------------
@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        
        'login_time_only','login_day_name', 'login_day', 'login_month', 'login_year', 
        'logout_time_only','logout_day_name', 'logout_day', 'logout_month', 'logout_year', 
        'session_duration_display','status_display'
    )
    ordering = ('-login_time',)
    search_fields = ('user__username',)

    # عرض حالة المستخدم (نشط / مسجل خروج)
    def status_display(self, obj):
        if obj.logout_time:
            return mark_safe('<span style="color:red; font-weight:bold;">مسجل خروج ❌</span>')
        else:
            return mark_safe('<span style="color:green; font-weight:bold;">نشط حاليًا ✅</span>')
    status_display.short_description = "نوع الحالة"

    # ✅ هنا نضيف عدد وأسماء المستخدمين النشطين
    def changelist_view(self, request, extra_context=None):
        # المستخدمين الذين لم يسجلوا خروج بعد (نشطين حاليًا)
        active_users_qs = LoginHistory.objects.filter(logout_time__isnull=True).order_by('-login_time').values_list('user__username', flat=True).distinct()

        active_count = active_users_qs.count()
        active_count_ar = to_arabic_numbers(str(active_count))

        # تحويل الأسماء إلى عربية (إظهارها بشكل منسق)
        if active_users_qs:
            user_list_html = "<br>".join([f"👤 <b>{u}</b>" for u in active_users_qs])
        else:
            user_list_html = "<i>لا يوجد مستخدمين نشطين الآن</i>"

        message = format_html(
            '<div style="background-color:#eef7ff; padding:12px; border-radius:10px; margin-bottom:15px; font-size:16px; line-height:1.8;">'
            '👥 عدد المستخدمين داخل النظام حاليًا: <span style="color:blue; font-weight:bold;">{}</span><br>{}'
            '</div>', active_count_ar, mark_safe(user_list_html)
        )

        extra_context = extra_context or {}
        extra_context['title'] = mark_safe(message + "سجل الدخول والخروج للمستخدمين")
        return super().changelist_view(request, extra_context=extra_context)

    # ---------- أعمدة التاريخ والوقت ----------
    def login_day_name(self, obj):
        return arabic_weekday(obj.login_time)
    login_day_name.short_description = "يوم الأسبوع الدخول"

    def login_day(self, obj):
        return obj.login_time.day
    login_day.short_description = "يوم الدخول"

    def login_month(self, obj):
        return obj.login_time.month
    login_month.short_description = "شهر الدخول"

    def login_year(self, obj):
        return obj.login_time.year
    login_year.short_description = "سنة الدخول"

    def login_time_only(self, obj):
        if not obj.login_time:
            return "-"
        local_tz = pytz.timezone("Asia/Aden")
        local_time = timezone.localtime(obj.login_time, local_tz)
        return format_time_arabic(local_time)
    login_time_only.short_description = "وقت الدخول الفعلي"

    # ---------- الخروج ----------
    def logout_day_name(self, obj):
        return arabic_weekday(obj.logout_time) if obj.logout_time else "-"
    logout_day_name.short_description = "يوم الأسبوع الخروج"

    def logout_day(self, obj):
        return obj.logout_time.day if obj.logout_time else "-"
    logout_day.short_description = "يوم الخروج"

    def logout_month(self, obj):
        return obj.logout_time.month if obj.logout_time else "-"
    logout_month.short_description = "شهر الخروج"

    def logout_year(self, obj):
        return obj.logout_time.year if obj.logout_time else "-"
    logout_year.short_description = "سنة الخروج"

    def logout_time_only(self, obj):
        if not obj.logout_time:
            return "-"
        local_tz = pytz.timezone("Asia/Aden")
        local_time = timezone.localtime(obj.logout_time, local_tz)
        return format_time_arabic(local_time)
    logout_time_only.short_description = "وقت الخروج الفعلي"

    # ---------- مدة الجلسة ----------
    def session_duration_display(self, obj):
        if not obj.logout_time or not obj.login_time:
            return "-"
        diff = obj.logout_time - obj.login_time
        total_seconds = int(diff.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{to_arabic_numbers(str(hours))} س {to_arabic_numbers(str(minutes))} د {to_arabic_numbers(str(seconds))} ث"
    session_duration_display.short_description = "مدة الجلسة الفعلية"
from django.contrib import admin
from django import forms
from .models import DailyAttendance_name, DailyAttendance, DAY_OF_WEEK_CHOICES
from import_export.admin import ImportExportModelAdmin

# إنشاء فورم مخصص لفرض شكل الحقول
class DailyAttendanceForm(forms.ModelForm):
    day_name = forms.ChoiceField(choices=DAY_OF_WEEK_CHOICES, label="اليوم", required=False)
    
    class Meta:
        model = DailyAttendance
        fields = '__all__'
        widgets = {
            'date': admin.widgets.AdminDateWidget(),
            'check_in': admin.widgets.AdminTimeWidget(),
            'check_out': admin.widgets.AdminTimeWidget(),
        }

class DailyAttendanceInline(admin.TabularInline):
    model = DailyAttendance
    form = DailyAttendanceForm # ربط الفورم المخصص
    extra = 1 # اجعلها 1 ليظهر سطر جديد دائماً
    fields = ['date', 'day_name', 'check_in', 'check_out', 'notes']
    
    # لا تضع day_name في readonly_fields حتى يظهر كقائمة منسدلة
    # readonly_fields = ['day_name'] 
    
    can_delete = True

@admin.register(DailyAttendance_name)
class DailyAttendanceNameAdmin(ImportExportModelAdmin):
    autocomplete_fields = ["person"]
    inlines = [DailyAttendanceInline] 
    list_display = ("person",)
    search_fields = ("person__first_name", "person__second_name", "person__third_name", "person__forth_name", "person__last_name")