from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Count, Avg, Sum
from django.core.paginator import Paginator
from .models import Student, StudentSubjectEnrollment, Year_choices, Semester_choices
from collections import defaultdict
from .models import *
import json
from django.db.models import Max

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils import timezone
from .models import Task, Name
import datetime
from .models import Student

from datetime import datetime, timedelta
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login  # أيضًا إذا لم تكن مستوردة
from django.shortcuts import redirect  # إذا لم تكن مستوردة
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

# تسجيل الدخول
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("reports_home")  # بعد تسجيل الدخول اذهب إلى الصفحة الرئيسية
        else:
            # تمرير الرسالة فقط عند إدخال خاطئ
            return render(request, "login.html", {"error": "اسم المستخدم أو كلمة المرور غير صحيحة"})
    # عند GET request لا نمرر أي error
    return render(request, "login.html")


# تسجيل الخروج
def logout_view(request):
    logout(request)
    return redirect('login')  # يعيد المستخدم إلى صفحة تسجيل الدخول بعد الخروج


@login_required(login_url='login')

def reports_home(request):
    """صفحة التقارير الرئيسية مع قائمة الأشخاص"""
    records_type = request.GET.get("records_type", "")

    search_query = request.GET.get("search", "")
    batch_filter = request.GET.get("batch", "")
    person_type = request.GET.get("type", "")  
    specialization_filter = request.GET.get("specialization", "")  
    level_filter = request.GET.get("level", "")  

    persons = Person.objects.select_related(
        "name", "address", "national_id",
    ).all()

    # فلترة حسب نوع الشخص
    if person_type == "student":
        persons = persons.filter(student__isnull=False)
    elif person_type == "student_active_only":  
        persons = persons.filter(student__isnull=False)\
                     .exclude(typestatus="متوقف")\
                     .exclude(staff__isnull=False)

    elif person_type == "staff":
        persons = persons.filter(staff__isnull=False)
    elif person_type == "staff_active_only":  
         persons = persons.filter(
        staff__isnull=False,      
        staff__continue_work=True, 
        student__isnull=True       
    )
    elif person_type == "student_present":
        persons = persons.filter(student__isnull=False).exclude(typestatus="متوقف")
    elif person_type == "staff_present":
        persons = persons.filter(staff__isnull=False, staff__continue_work=True)
    elif person_type == "staff_exit":
        persons = persons.filter(staff__isnull=False, staff__continue_work=False)

    elif person_type == "student_exit":
        persons = persons.filter(student__isnull=False, typestatus="متوقف")
 
    elif person_type == "person_present":
        persons = persons.exclude(typestatus="متوقف")
    elif person_type == "person_exit":
        persons = persons.filter(typestatus="متوقف")

    if search_query:
       search_words = search_query.split()
       if search_words:
          q_objects = Q() 
          for word in search_words:
            q_objects &= (
                Q(name__first_name__icontains=word) |
                Q(name__second_name__icontains=word) |
                Q(name__third_name__icontains=word) |
                Q(name__forth_name__icontains=word) |
                Q(name__last_name__icontains=word) |
                Q(nickname__icontains=word) |
                Q(phone__icontains=word) |
                Q(email__icontains=word)
            )
            persons = persons.filter(q_objects)

    if batch_filter:
        persons = persons.filter(batch=batch_filter)

    if specialization_filter:
        persons = persons.filter(student__specialization_id=specialization_filter)

    if level_filter:
       persons = persons.filter(student__learnyear=level_filter)
    # فلترة المخالفات
# =========================
    if records_type == "violations_all":
        persons = persons.filter(
        violation_name__violations__isnull=False
    ).distinct()

    elif records_type == "violations_unresolved":
        persons = persons.filter(
        violation_name__violations__resolved=False
    ).distinct()

    elif records_type == "violations_resolved":
        persons = persons.filter(
        violation_name__violations__resolved=True
    ).distinct()

# =========================
# فلترة العهد
# =========================
    elif records_type == "covenants_all":
         persons = persons.filter(
        covenant__name_covenants__isnull=False
    ).distinct()

    elif records_type == "covenants_not_returned":
         persons = persons.filter(
        covenant__name_covenants__name="لم يتم ارجاعها"
    ).distinct()

    elif records_type == "covenants_returned":
         persons = persons.filter(
        covenant__name_covenants__name="معه"
    ).distinct()
    # ترتيب وتقسيم الصفحات
    persons = persons.order_by("name__first_name")
    paginator = Paginator(persons,1000)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # إضافة last_level لكل طالب للعرض فقط
    for person in page_obj:
        if hasattr(person, "student") and person.student:
            last_level = person.student.studentsubjectenrollment_set.order_by("-learn_year").first()
            person.last_level = last_level.learn_year if last_level else None

    stats = {
        "total_persons": Person.objects.count(),
        "total_students": Person.objects.filter(student__isnull=False).count(),
        "total_staff": Person.objects.filter(staff__isnull=False).count(),
        "active_persons": Person.objects.exclude(typestatus="متوقف").count(),
    }

    batches = Person.objects.values_list( flat=True).distinct()
    specializations = Specialization.objects.all()
    # levels = StudentSubjectEnrollment.YEAR_CHOICES
    levels = Student.YEAR_CHOICES
    # 🔹 إحصائيات عدد الطلاب حسب التخصص فقط
    student_summary = persons.filter(student__isnull=False).values(
        "student__specialization__name"
    ).annotate(count=Count("id")).order_by("student__specialization__name")

    context = {
        "page_obj": page_obj,
        "records_type": records_type,
        "search_query": search_query,
        "batch_filter": batch_filter,
        "person_type": person_type,
        "specialization_filter": specialization_filter,
        "level_filter": level_filter,
        "batches": batches,
        "specializations": specializations,
        "levels": levels,
        "stats": stats,
        "student_summary": student_summary,
    }

    return render(request, "reports/reports_home_new.html", context)

from collections import defaultdict
from django.shortcuts import render, get_object_or_404

def For_every_year(request, person_id):
    person = get_object_or_404(Person, id=person_id)

    # ====================== الجانب العبادي ======================
    alabadi_qs = AlAbadiSecond.objects.filter(worship_side__name=person.name)
    alabadi_data = defaultdict(dict)
    for rec in alabadi_qs:
        if not rec.hijri_year or not rec.hijri_month:
            continue
        key = f"{rec.hijri_year}-{rec.hijri_month}"
        alabadi_data[key] = rec.total

    # ====================== الجانب الثقافي ======================
    cultural_qs = CulturalSecond.objects.filter(worship_side__name=person.name)
    cultural_data = defaultdict(dict)
    for rec in cultural_qs:
        if not rec.hijri_year or not rec.hijri_month:
            continue
        key = f"{rec.hijri_year}-{rec.hijri_month}"
        cultural_data[key] = rec.total

    # ====================== الجانب السلوكي ======================
    behavioral_qs = BehavioralSecond.objects.filter(worship_side__name=person.name)
    behavioral_data = defaultdict(dict)
    for rec in behavioral_qs:
        if not rec.hijri_year or not rec.hijri_month:
            continue
        key = f"{rec.hijri_year}-{rec.hijri_month}"
        behavioral_data[key] = rec.total

    context = {
        "person": person,
        "alabadi_data": dict(alabadi_data),
        "cultural_data": dict(cultural_data),
        "behavioral_data": dict(behavioral_data),
    }

    return render(request, 'report/For_every_year.html', context)

from collections import defaultdict
from django.db.models import Avg, Sum
from django.shortcuts import get_object_or_404, render
import json
def person_detail_report(request, person_id):
    """تقرير شامل: درجات + أداء أكاديمي + جدول زمني + باقي التفاصيل"""
    person = get_object_or_404(Person, id=person_id)

    context = {
        "person": person,
        "is_student": hasattr(person, "student"),
        "is_staff": hasattr(person, "staff"),
    }

    user = request.user
    visible_sections = []
    enrollments = [] 
    # ===================== معلومات الطالب =====================
    if hasattr(person, "student") and user.has_perm("HR.view_studentsubjectenrollment"):
        student = person.student
        context["student"] = student

        enrollments = (
            StudentSubjectEnrollment.objects.filter(student=student)
            .select_related("subject")
            .order_by("learn_year", "semester", "subject__name")
        )
        context["enrollments"] = enrollments

       # جدول زمني أكاديمي
    year_names = {1: "الأولى", 2: "الثانية", 3: "الثالثة", 4: "الرابعة", 5: "الخامسة"}
    semester_names = {1: "الأول", 2: "الثاني"}
    enrollments_by_year = {}

    for e in enrollments:
       year_name = year_names.get(e.learn_year, str(e.learn_year))
       semester_name = semester_names.get(e.semester, str(e.semester))
       enrollments_by_year.setdefault(year_name, {})
       enrollments_by_year[year_name].setdefault(semester_name, [])
       enrollments_by_year[year_name][semester_name].append(e)

# ترتيب السنوات حسب الأولوية
    year_order = ["الأولى", "الثانية", "الثالثة", "الرابعة", "الخامسة"]

# إنشاء dict مرتب حسب year_order
    sorted_enrollments_by_year = {}
    for y in year_order:
        if y in enrollments_by_year:
        # ترتيب الفصول داخل كل سنة
           sorted_enrollments_by_year[y] = dict(sorted(enrollments_by_year[y].items()))

# إضافة أي سنة غير موجودة في year_order في آخر القائمة
    for y in enrollments_by_year:
        if y not in year_order:
           sorted_enrollments_by_year[y] = dict(sorted(enrollments_by_year[y].items()))

        enrollments_by_year = sorted_enrollments_by_year
        context["enrollments_by_year"] = enrollments_by_year

        # ملخص الأداء الأكاديمي
        performance_data = []
        for year, semesters in enrollments_by_year.items():
            for semester, subjects in semesters.items():
                total_subjects = len(subjects)
                passed_subjects = sum(1 for s in subjects if s.mrak_of_subject and s.mrak_of_subject >= 50)
                if total_subjects == 0:
                    performance_type = "no-data"
                elif passed_subjects == total_subjects:
                    performance_type = "excellent"
                elif passed_subjects == 0:
                    performance_type = "poor"
                elif passed_subjects >= total_subjects * 0.75:
                    performance_type = "good"
                else:
                    performance_type = "fair"

                performance_data.append({
                    "year": year,
                    "semester": semester,
                    "total_subjects": total_subjects,
                    "passed_subjects": passed_subjects,
                    "performance_type": performance_type,
                })
        context["performance_data"] = performance_data

        # إحصائيات الدرجات
        grades = enrollments.filter(mrak_of_subject__isnull=False)
        if grades.exists():
            grade_stats = {
                "average": grades.aggregate(avg=Avg("mrak_of_subject"))["avg"],
                "total_subjects": grades.count(),
                "passed_subjects": grades.filter(mrak_of_subject__gte=50).count(),
            }
        else:
            grade_stats = {
                "average": 0,
                "total_subjects": enrollments.count(),
                "passed_subjects": 0,
            }
        context["grade_stats"] = grade_stats

        # مخطط درجات
        grade_labels = [e.subject.name for e in grades]
        grade_data = [float(e.mrak_of_subject) for e in grades]
        context["chart_data"] = {
            "labels": json.dumps(grade_labels, ensure_ascii=False),
            "data": json.dumps(grade_data),
        }

        visible_sections.append("student_section")

    # ===================== معلومات الموظف =====================
    if hasattr(person, "staff") and user.has_perm("HR.view_staff"):
        context["staff"] = person.staff
        visible_sections.append("staff_section")

    
    # ===================== المدفوعات =====================
    if user.has_perm("HR.view_payment"):
        payments = Payment.objects.filter(person=person).order_by("-date")
        context["payments"] = payments
        context["total_payments"] = payments.aggregate(total=Sum("accreditation"))["total"] or 0
        visible_sections.append("payments_section")

    # ===================== المخالفات =====================
    if user.has_perm("HR.view_violation"):
        violations = Violation.objects.filter(violation_name__person=person).order_by("-date")
        context["violations"] = violations
        context["unresolved_violations"] = violations.filter(resolved=False).count()
        visible_sections.append("violations_section")

    # ===================== الدورات والمؤهلات =====================
    if user.has_perm("HR.view_developmentcourse"):
        context["development_courses"] = DevelopmentCourse.objects.filter(person=person)
        visible_sections.append("development_courses_section")
    if user.has_perm("HR.view_academiccoursepersonal"):
        context["AcademicCoursePersonal_courses"] = AcademicCoursePersonal.objects.filter(person=person)
        visible_sections.append("academic_courses_section")
    if user.has_perm("HR.view_qualification"):
        context["qualifications"] = Qualification.objects.filter(person=person).order_by("-year")
        visible_sections.append("qualifications_section")
    if user.has_perm("HR.view_medical"):
        context["medical_records"] = Medical.objects.filter(person=person).order_by("-date")
        visible_sections.append("medical_section")

    # ===================== العهد =====================
    if user.has_perm("HR.view_covenant"):
        context["covenants"] = Covenant.objects.filter(person=person).order_by("-id")
        context["covenant_details"] = Name_covenants.objects.filter(covenantor__person=person).order_by("-date")
        visible_sections.append("covenant_section")

    # ===================== التدريبات =====================
    if user.has_perm("HR.view_tutors"):
        context["tutors_as_trainer"] = Tutors.objects.filter(person__person=person).order_by("-start_date")
        context["tutors_as_trainee"] = Tutors.objects.filter(people=person).order_by("-start_date")
        visible_sections.append("tutors_section")

    # ===================== الجوانب الثقافية والسلوكية =====================
    if user.has_perm("HR.view_worshipsidesecond"):
        alAbadiSecond = AlAbadiSecond.objects.filter(worship_side__name=person.name).order_by('hijri_year', 'hijri_month')
        culturalSecond = CulturalSecond.objects.filter(worship_side__name=person.name).order_by('hijri_year', 'hijri_month')
        behavioralSecond = BehavioralSecond.objects.filter(worship_side__name=person.name).order_by('hijri_year', 'hijri_month')
        general_notes = GeneralNotesSecond.objects.filter(worship_side__name=person.name).order_by('hijri_year', 'hijri_month')
        strength_weakness = StrengthAndWeaknessSecond.objects.filter(worship_side__name=person.name).order_by('hijri_year', 'hijri_month')
        assessment_opinion = AssessmentMakerOpinionSecond.objects.filter(worship_side__name=person.name).order_by('hijri_year', 'hijri_month')

        total_score = sum(item.total or 0 for item in alAbadiSecond) \
                      + sum(item.total or 0 for item in culturalSecond) \
                      + sum(item.total or 0 for item in behavioralSecond)

        if total_score >= 180:
            final_grade = "ممتاز"
        elif total_score >= 160:
            final_grade = "جيد جدًا"
        elif total_score >= 140:
            final_grade = "جيد"
        elif total_score >= 120:
            final_grade = "متوسط"
        else:
            final_grade = "ضعيف"

        monthly_totals = defaultdict(lambda: {"alAbadi": 0, "cultural": 0, "behavioral": 0})
        for item in alAbadiSecond:
            monthly_totals[(item.hijri_year, item.hijri_month)]["alAbadi"] += item.total or 0
        for item in culturalSecond:
            monthly_totals[(item.hijri_year, item.hijri_month)]["cultural"] += item.total or 0
        for item in behavioralSecond:
            monthly_totals[(item.hijri_year, item.hijri_month)]["behavioral"] += item.total or 0

        HIJRI_MONTHS = ["", "محرم", "صفر", "ربيع الأول", "ربيع الآخر", "جمادى الأولى", "جمادى الآخرة",
                        "رجب", "شعبان", "رمضان", "شوال", "ذو القعدة", "ذو الحجة"]
        monthly_results = []
        for (year, month), scores in sorted(monthly_totals.items()):
    # تأكد أن المفاتيح موجودة
            month_total = (scores.get("alAbadi", 0) or 0) + (scores.get("cultural", 0) or 0) + (scores.get("behavioral", 0) or 0)
    
    # تحديد التقدير
            if month_total >= 180:
               grade = "ممتاز"
            elif month_total >= 160:
               grade = "جيد جدًا"
            elif month_total >= 140:
               grade = "جيد"
            elif month_total >= 120:
               grade = "متوسط"
            else:
               grade = "ضعيف"
    
    # التأكد من صحة الشهر
            month_name = HIJRI_MONTHS[month] if 1 <= month <= 12 else "غير معروف"
    
            monthly_results.append({
            "year": year,
            "month": month_name,
            "total": month_total,
            "grade": grade,
           })


        context.update({
            "alAbadiSecond": alAbadiSecond,
            "culturalSecond": culturalSecond,
            "behavioralSecond": behavioralSecond,
            "total_score": total_score,
            "final_grade": final_grade,
            "monthly_results": monthly_results,
            "GeneralNotesSecond": general_notes,
            "StrengthAndWeaknessSecond": strength_weakness,
            "AssessmentMakerOpinionSecond": assessment_opinion,
        })
        visible_sections.append("cultural_section")
        # ===================== الحضور =====================
    if user.has_perm("HR.view_present"):
    # الحصول على كائن Present_name المرتبط بالـ Person الحالي
      present_name_instance, created = Present_name.objects.get_or_create(person=person.name)

    # جلب سجلات الحضور الخاصة به فقط
    attendance_records = Present.objects.filter(
        present_name=present_name_instance
    ).order_by("-year", "-month")

    # حساب ملخص الحضور لكل شهر
    attendance_summary = []
    for record in attendance_records:
        days_in_month = calendar.monthrange(record.year, record.month)[1]
        attendance_summary.append({
            "year": record.year,
            "month": record.month,
            "record": record,
            "days_in_month": days_in_month,
            "present": record.count_present(),
            "sick": record.count_sick(),
            "absent": record.count_absent(),
            "permission": record.permission,  
            "excused": record.excused,        
            "study": record.study,
            "last_m_day": record.last_sick_day,            
        })

    context["attendance_records"] = attendance_records
    context["attendance_summary"] = attendance_summary
    visible_sections.append("attendance_section")
    # ===================== تمرير الأقسام المرئية للقالب =====================
    # ===================== الحضور اليومي =====================
    if user.has_perm("HR.view_dailyattendance"):
    # الحصول على كائن DailyAttendance_name المرتبط بالشخص (أو إنشاؤه إذا لم يوجد)
        daily_attendance_instance, created = DailyAttendance_name.objects.get_or_create(person=person.name)
    # جلب سجلات الحضور اليومية الخاصة به مرتبة حسب التاريخ (من الأحدث للأقدم)
    daily_records = DailyAttendance.objects.filter(
        attendance_parent=daily_attendance_instance
    ).order_by("-date")

    # تجهيز البيانات للعرض في القالب
    daily_summary = []
    for record in daily_records:
        daily_summary.append({
            "date": record.date,
            "day_name": record.day_name,
            "check_in": record.check_in,
            "check_out": record.check_out,
            "notes": record.notes,
            "record": record,
        })

    context["daily_records"] = daily_records
    context["daily_summary"] = daily_summary
    visible_sections.append("daily_attendance_section")
    context["visible_sections"] = visible_sections

    return render(request, "reports/person_detail_simple.html", context)




def person_print_simple(request, person_id):
    """تقرير مبسط للطباعة"""
    person = get_object_or_404(Person, id=person_id)

    # استخدام نفس منطق person_detail_report ولكن مع قالب مبسط
    context = {
        "person": person,
        "is_student": hasattr(person, "student"),
        "is_staff": hasattr(person, "staff"),
    }

    # معلومات الطالب
    if hasattr(person, "student"):
        student = person.student
        context["student"] = student

        # المواد المسجل بها - مرتبة حسب السنة والترم
        enrollments = (
            StudentSubjectEnrollment.objects.filter(student=student)
            .select_related("subject")
            .order_by("learn_year", "semester", "subject__name")
        )
        context["enrollments"] = enrollments

        # تجميع المواد حسب السنة
        enrollments_by_year = {}
        performance_data = []

        for enrollment in enrollments:
            year = enrollment.learn_year
            if year not in enrollments_by_year:
                enrollments_by_year[year] = {}
            semester = enrollment.semester
            if semester not in enrollments_by_year[year]:
                enrollments_by_year[year][semester] = []
            enrollments_by_year[year][semester].append(enrollment)

        # حساب إحصائيات الأداء لكل ترم
        for year, semesters in enrollments_by_year.items():
            for semester, subjects in semesters.items():
                if subjects:
                    total_subjects = len(subjects)
                    passed_subjects = sum(
                        1
                        for s in subjects
                        if s.mrak_of_subject and s.mrak_of_subject >= 50
                    )

                    # تحديد نوع الأداء
                    if passed_subjects == total_subjects:
                        performance_type = "excellent"
                    elif passed_subjects == 0:
                        performance_type = "poor"
                    elif passed_subjects >= total_subjects * 0.75:
                        performance_type = "good"
                    else:
                        performance_type = "fair"

                    performance_data.append(
                        {
                            "year": year,
                            "semester": semester,
                            "total_subjects": total_subjects,
                            "passed_subjects": passed_subjects,
                            "performance_type": performance_type,
                        }
                    )

        context["enrollments_by_year"] = enrollments_by_year
        context["performance_data"] = performance_data

        # إحصائيات الدرجات
        grades = enrollments.filter(mrak_of_subject__isnull=False)
        if grades.exists():
            context["grade_stats"] = {
                "average": grades.aggregate(avg=Avg("mrak_of_subject"))["avg"],
                "total_subjects": grades.count(),
                "passed_subjects": grades.filter(mrak_of_subject__gte=50).count(),
            }

    # معلومات الموظف
    if hasattr(person, "staff"):
        context["staff"] = person.staff

    # الحضور
    all_attendances = Attendance.objects.filter(person=person).order_by("-date")
    attendances = all_attendances[:30]
    context["recent_attendances"] = attendances

    total_days = all_attendances.count()
    present_days = all_attendances.filter(session=True).count()
    if total_days > 0:
        context["attendance_rate"] = (present_days / total_days) * 100
    else:
        context["attendance_rate"] = 0

    # المدفوعات
    payments = Payment.objects.filter(person=person).order_by("-date")
    context["payments"] = payments
    context["total_payments"] = (
        payments.aggregate(total=Sum("accreditation"))["total"] or 0
    )

    # المخالفات
    violations = Violation.objects.filter(violation_name__person=person).order_by("-date")
    context["violations"] = violations
    context["unresolved_violations"] = violations.filter(resolved=False).count()

  
    return render(request, "reports/person_detail_simple.html", context)


def person_data_api(request, person_id):
    """API لجلب بيانات الشخص بصيغة JSON للمخططات"""
    person = get_object_or_404(Person, id=person_id)

    data = {
        "name": str(person.name),
        "phone": person.phone,
        "email": person.email,
    }

    # إضافة بيانات إضافية حسب الحاجة
    if hasattr(person, "student"):
        enrollments = StudentSubjectEnrollment.objects.filter(
            student=person.student, mrak_of_subject__isnull=False
        )
        data["grades"] = [
            {"subject": e.subject.name, "grade": float(e.mrak_of_subject)}
            for e in enrollments
        ]

    return JsonResponse(data)

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Student, StudentSubjectEnrollment

# دالة لإرجاع البيانات بصيغة JSON للمخطط
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from collections import defaultdict


YEAR_ORDER = ['الأولى', 'الثانية', 'الثالثة', 'الرابعة']
TERM_ORDER = ['الأول', 'الثاني']

def full_academic_progress(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    enrollments = StudentSubjectEnrollment.objects.filter(
        student=student
    ).order_by('learn_year', 'semester')

    yearly_data_raw = defaultdict(lambda: defaultdict(list))

    for e in enrollments:
        year_name = str(e.learn_year).strip()
        term = str(e.semester).strip()

        try:
            mark = float(e.mrak_of_subject)
        except:
            mark = 0

        yearly_data_raw[year_name][term].append(mark)

    labels = []
    grades = []

    for year_name in YEAR_ORDER:
        if year_name not in yearly_data_raw:
            continue

        for term in TERM_ORDER:
            marks = yearly_data_raw[year_name].get(term, [])
            if marks:
                avg = sum(marks) / len(marks)
                grades.append(round(avg, 2))
                labels.append(f"السنة {year_name} - الترم {term}")

    context = {
        'student': student,
        'labels': json.dumps(labels, ensure_ascii=False),
        'grades': json.dumps(grades),
    }

    return render(request, 'Academic_Application_Charts/full_academic_progress.html', context)

# قاموس تحويل السنة والترم إلى الشكل المطلوب
year_names = {
    "الأولى": "السنة الأولى",
    "الثانية": "السنة الثانية",
    "الثالثة": "السنة الثالثة",
    "الرابعة": "السنة الرابعة"
}

semester_names = {
    "الأول": "الترم الأول",
    "الثاني": "الترم الثاني"
}

def term_chart(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    enrollments = StudentSubjectEnrollment.objects.filter(student=student)

    # تجميع المواد حسب الترم
    term_dict = defaultdict(lambda: {'labels': [], 'grades': [], 'avg': 0, 'count': 0})
    for e in enrollments:
        if e.subject:
            key = f"{e.learn_year.strip()} - {e.semester.strip()}"
            term_dict[key]['labels'].append(e.subject.name)
            term_dict[key]['grades'].append(e.mrak_of_subject)
            term_dict[key]['avg'] += e.mrak_of_subject
            term_dict[key]['count'] += 1

    # ترتيب السنوات والترم يدوياً وإظهار المخطط فقط إذا هناك بيانات
    year_order = ["الأولى", "الثانية", "الثالثة", "الرابعة"]
    semester_order = ["الأول", "الثاني"]

    ordered_terms = []
    for year in year_order:
        for semester in semester_order:
            key = f"{year} - {semester}"
            data = term_dict.get(key, {'labels': [], 'grades': [], 'avg': 0, 'count': 0})
            if data['count'] > 0:  # فقط إذا توجد مواد للترم
                avg = data['avg'] / data['count']
                display_name = f"{year_names.get(year, year)} - {semester_names.get(semester, semester)}"
                ordered_terms.append({
                    'display_name': display_name,
                    'labels': data['labels'],
                    'grades': data['grades'],
                    'avg': round(avg, 2)
                })

    context = {
        'student': student,
        'term_list': ordered_terms
    }
    return render(request, 'Academic_Application_Charts/term_chart.html', context)


# نسخة API بنفس الطريقة
def api_term_chart_data(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    enrollments = StudentSubjectEnrollment.objects.filter(student=student)

    term_dict = defaultdict(lambda: {'labels': [], 'grades': [], 'avg': 0, 'count': 0})
    for e in enrollments:
        if e.subject:
            key = f"{e.learn_year.strip()} - {e.semester.strip()}"
            term_dict[key]['labels'].append(e.subject.name)
            term_dict[key]['grades'].append(e.mrak_of_subject)
            term_dict[key]['avg'] += e.mrak_of_subject
            term_dict[key]['count'] += 1

    year_order = ["الأولى", "الثانية", "الثالثة", "الرابعة"]
    semester_order = ["الأول", "الثاني"]

    ordered_terms = []
    for year in year_order:
        for semester in semester_order:
            key = f"{year} - {semester}"
            data = term_dict.get(key, {'labels': [], 'grades': [], 'avg': 0, 'count': 0})
            if data['count'] > 0:  # فقط إذا توجد مواد للترم
                avg = data['avg'] / data['count']
                display_name = f"{year_names.get(year, year)} - {semester_names.get(semester, semester)}"
                ordered_terms.append({
                    'display_name': display_name,
                    'labels': data['labels'],
                    'grades': data['grades'],
                    'avg': round(avg, 2)
                })

    return JsonResponse({'term_list': ordered_terms})
from collections import defaultdict
import json
from django.shortcuts import render, get_object_or_404

from collections import defaultdict
import json
from django.shortcuts import get_object_or_404, render

# ترتيب السنوات العربية
YEAR_ORDER = ['الأولى', 'الثانية', 'الثالثة', 'الرابعة']

def year_chart(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    # جلب كل المواد للطالب
    enrollments = StudentSubjectEnrollment.objects.filter(
        student=student
    ).order_by('learn_year', 'semester')

    yearly_data_raw = defaultdict(lambda: defaultdict(list))
    for e in enrollments:
        year_name = str(e.learn_year).strip()
        term = str(e.semester).strip()
        try:
            mark = float(e.mrak_of_subject)
        except (TypeError, ValueError):
            mark = 0
        yearly_data_raw[year_name][term].append(mark)

    final_data = []
    term_order = ["الأول", "الثاني"]

    for year_name in YEAR_ORDER:
        terms = yearly_data_raw.get(year_name, {})
        if not terms:
            continue

        labels = []
        grades = []
        term_avgs = []

        # ترتيب الترم حسب الأول ثم الثاني
        for term in term_order:
            marks = terms.get(term, [])
            if marks:
                avg_term = sum(marks) / len(marks)
                labels.append(term)
                grades.append(round(avg_term, 2))
                term_avgs.append(avg_term)

        if term_avgs:
            avg_year = sum(term_avgs) / len(term_avgs)
            final_data.append({
                'year': year_name,
                'labels': json.dumps(labels, ensure_ascii=False),
                'grades': json.dumps(grades),
                'avg': round(avg_year, 2),
                'grade_text': get_grade_text(avg_year)
            })

    context = {
        'student': student,
        'yearly_data': final_data
    }
    return render(request, 'Academic_Application_Charts/year_chart.html', context)


def get_grade_text(average):
    if average >= 90:
        return "ممتاز"
    elif average >= 80:
        return "جيد جدًا"
    elif average >= 65:
        return "جيد"
    elif average >= 50:
        return "مقبول"
    else:
        return "راسب"
from collections import defaultdict
import json
from django.shortcuts import get_object_or_404, render

YEAR_ORDER = ['الأولى', 'الثانية', 'الثالثة', 'الرابعة']

def summary_chart(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    # جلب كل تسجيلات الطالب
    enrollments = StudentSubjectEnrollment.objects.filter(student=student)

    # هيكل بيانات لكل سنة وترم
    yearly_data_raw = defaultdict(lambda: defaultdict(list))
    for e in enrollments:
        year = str(e.learn_year).strip()
        term = str(e.semester).strip()
        try:
            mark = float(e.mrak_of_subject)
        except (TypeError, ValueError):
            mark = 0
        yearly_data_raw[year][term].append(mark)

    final_data = []
    chart_data = []
    term_order = ["الأول", "الثاني"]

    for year in YEAR_ORDER:
        terms = yearly_data_raw.get(year, {})
        term_avgs = []

        # حساب متوسط كل ترم
        for term in term_order:
            marks = terms.get(term, [])
            if marks:
                avg_term = sum(marks) / len(marks)
                term_avgs.append(avg_term)

        avg_year = sum(term_avgs) / len(term_avgs) if term_avgs else 0
        grade_text = get_grade_text(avg_year)

        # إضافة كل السنوات للحسابات
        final_data.append({
            'year': year,
            'avg': round(avg_year, 2),
            'grade_text': grade_text
        })

        # إضافة فقط إذا فيه درجات للسنة للرسم
        if term_avgs:
            chart_data.append({
                'year': year,
                'avg': round(avg_year, 2),
                'grade_text': grade_text
            })

    # تحويل البيانات للـ JavaScript
    year_labels_json = json.dumps([y['year'] for y in chart_data], ensure_ascii=False)
    year_avgs_json = json.dumps([y['avg'] for y in chart_data])
    year_grades_text_json = json.dumps([y['grade_text'] for y in chart_data], ensure_ascii=False)

    context = {
        'student': student,
        'yearly_data': final_data,  # كل السنوات للحسابات
        'year_labels_json': year_labels_json,
        'year_avgs_json': year_avgs_json,
        'year_grades_text_json': year_grades_text_json
    }
    return render(request, 'Academic_Application_Charts/summary_chart.html', context)


def get_grade_text(average):
    if average >= 90:
        return "ممتاز"
    elif average >= 80:
        return "جيد جدًا"
    elif average >= 65:
        return "جيد"
    elif average >= 50:
        return "مقبول"
    else:
        return "راسب"

HIJRI_MONTH_NAMES = {
    1: "محرم", 2: "صفر", 3: "ربيع الأول", 4: "ربيع الثاني",
    5: "جمادى الأولى", 6: "جمادى الثانية", 7: "رجب", 8: "شعبان",
    9: "رمضان", 10: "شوال", 11: "ذو القعدة", 12: "ذو الحجة"
}

RATING_VALUES = {"ضعيف": 1, "متوسط": 2, "جيد": 3, "جيد جدًا": 4, "ممتاز": 5}

def get_alabadi_rating(total):
    if total >= 90: return "ممتاز"
    elif total >= 80: return "جيد جدًا"
    elif total >= 65: return "جيد"
    elif total >= 50: return "متوسط"
    return "ضعيف"

def get_cultural_rating(total):
    if total >= 27: return "ممتاز"
    elif total >= 24: return "جيد جدًا"
    elif total >= 21: return "جيد"
    elif total >= 16: return "متوسط"
    return "ضعيف"

def get_behavioral_rating(total):
    if total >= 63: return "ممتاز"
    elif total >= 56: return "جيد جدًا"
    elif total >= 49: return "جيد"
    elif total >= 40: return "متوسط"
    return "ضعيف"

def get_table_data():
    alabadi = [{'hijri': obj.hijri_year, 'month': obj.hijri_month, 'rating': get_alabadi_rating(obj.total)} for obj in AlAbadiSecond.objects.all()]
    cultural = [{'hijri': obj.hijri_year, 'month': obj.hijri_month, 'rating': get_cultural_rating(obj.total)} for obj in CulturalSecond.objects.all()]
    behavioral = [{'hijri': obj.hijri_year, 'month': obj.hijri_month, 'rating': get_behavioral_rating(obj.total)} for obj in BehavioralSecond.objects.all()]
    return alabadi, cultural, behavioral
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from collections import defaultdict
from collections import defaultdict
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse

HIJRI_MONTH_NAMES = {
    1: "محرم", 2: "صفر", 3: "ربيع الأول", 4: "ربيع الآخر",
    5: "جمادى الأولى", 6: "جمادى الآخرة", 7: "رجب", 8: "شعبان",
    9: "رمضان", 10: "شوال", 11: "ذو القعدة", 12: "ذو الحجة"
}

RATING_VALUES = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5}  # أو حسب قاعدة البيانات

from collections import defaultdict
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse

from hijri_converter import Gregorian

from django.shortcuts import get_object_or_404, render
from django.shortcuts import render, get_object_or_404

from hijri_converter import Gregorian

from django.shortcuts import get_object_or_404, render

from collections import defaultdict
from django.shortcuts import get_object_or_404, render

from collections import defaultdict
from django.shortcuts import get_object_or_404, render

def spiritual_report(request, person_id):
    person = get_object_or_404(Person, id=person_id)

    # ====================== الجانب العبادي ======================
    alabadi_qs = AlAbadiSecond.objects.filter(worship_side__name=person.name)
    alabadi_data = defaultdict(dict)
    for rec in alabadi_qs:
        if not rec.hijri_year or not rec.hijri_month:
            continue
        key = f"{rec.hijri_year}-{rec.hijri_month}"
        alabadi_data[key] = rec.total

    # ====================== الجانب الثقافي ======================
    cultural_qs = CulturalSecond.objects.filter(worship_side__name=person.name)
    cultural_data = defaultdict(dict)
    for rec in cultural_qs:
        if not rec.hijri_year or not rec.hijri_month:
            continue
        key = f"{rec.hijri_year}-{rec.hijri_month}"
        cultural_data[key] = rec.total

    # ====================== الجانب السلوكي ======================
    behavioral_qs = BehavioralSecond.objects.filter(worship_side__name=person.name)
    behavioral_data = defaultdict(dict)
    for rec in behavioral_qs:
        if not rec.hijri_year or not rec.hijri_month:
            continue
        key = f"{rec.hijri_year}-{rec.hijri_month}"
        behavioral_data[key] = rec.total

    context = {
        "person": person,
        "alabadi_data": dict(alabadi_data),
        "cultural_data": dict(cultural_data),
        "behavioral_data": dict(behavioral_data),
    }

    return render(request, 'report/spiritual_report.html', context)


from functools import wraps
from django.shortcuts import redirect



def monthly_report(request, person_id):
   
    person = get_object_or_404(Person, id=person_id)

    # ====================== الجانب العبادي ======================
    alabadi_qs = AlAbadiSecond.objects.filter(worship_side__name=person.name)
    alabadi_data = defaultdict(dict)
    for record in alabadi_qs:
        if not record.hijri_year or not record.hijri_month:
            continue
        key = f"{record.hijri_year}-{record.hijri_month}"
        alabadi_data[key] = {
            "الاستيقاظ قبل الفجر": record.waking_up_before_dawn,
            "الاستغفار": record.seeking_forgiveness,
            "صلاة الجماعة": record.congregational_prayer,
            "المحافظة على الصلاة": record.maintaining_prayer,
            "الدعاء": record.the_supplication,
            "تلاوة القرآن": record.recitation_of_the_quran,
            "التسبيح": record.the_glorification,
            "صلاة الجمعة": record.friday_prayer,
            "التعامل مع الملازم": record.interacted_with_the_lieutenant,
            "الحقيقة والأخبار": record.the_truth_and_the_news,
        }

    # ====================== الجانب الثقافي ======================
    cultural_qs = CulturalSecond.objects.filter(worship_side__name=person.name)
    cultural_data = defaultdict(dict)
    for record in cultural_qs:
        if not record.hijri_year or not record.hijri_month:
            continue
        key = f"{record.hijri_year}-{record.hijri_month}"
        cultural_data[key] = {
            "استيعابه لهدى الله": record.seeking_forgi,
            "الوعي الثقافي": record.seeking_forgiveness,
            "تقبله وتفاعله مع هدى الله": record.congregational_prayer,
            "الروحية الجهادية": record.maintaining_prayer,
            "تقبله للتوجيهات ضمن المجموعة": record.the_supplication,
            "تقبله لتوجيهات القائمين": record.recitation_of_the_quran,
        }

    # ====================== الجانب السلوكي ======================
    behavioral_qs = BehavioralSecond.objects.filter(worship_side__name=person.name)
    behavioral_data = defaultdict(dict)
    for record in behavioral_qs:
        if not record.hijri_year or not record.hijri_month:
            continue
        key = f"{record.hijri_year}-{record.hijri_month}"
        behavioral_data[key] = {
            "الإحسان": record.waking_up_before_dawn,
            "الحكمة": record.seeking_forgiveness,
            "الانسجام": record.congregational_prayer,
            "التأثير": record.maintaining_prayer,
            "تحسن التصرف": record.the_supplication,
            "النظافة": record.recitation_of_the_quran,
            "المبادرة": record.the_glorification,
            "الإتقان": record.friday_prayer,
            "المظهر": record.interacted_with_the_lieutenant,
            "الالتزام والانضباط": record.nteracted,
            "الصبر والتحمل": record.Patience_and_endurance,
            "السرية": record.secrecy,
            "الحس الأمني": record.Security_sense,
            "تقدير المسؤولية": record.Appraisal_of_Responsibility,
        }

    context = {
        "person": person,
        "alabadi_data": dict(alabadi_data),
        "cultural_data": dict(cultural_data),
        "behavioral_data": dict(behavioral_data),
    }

    return render(request, 'report/monthly_report.html', context)


from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils import timezone
from .models import Task, Name
import datetime

# قائمة المستخدمين المسموح لهم
ALLOWED_USERS = ["eshaiq", "ahmed", "muad", "asmail"]

def allowed_users_only(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:  # متأكد انه مسجل دخول
            if request.user.username in ALLOWED_USERS:
                return view_func(request, *args, **kwargs)
            else:
                # هنا بدلنا رسالة المنع بتحويل لصفحة ثانية
                return redirect("reports_home")
        else:
            return redirect("login")
    return wrapper
from django.shortcuts import render
from .models import Task # تأكد من استيراد الموديل الصحيح

# def Attendance(request):
#     # جلب البيانات من قاعدة البيانات
#     tasks = Task.objects.all()
    
#     context = {
#         'tasks': tasks,
#     }
    
#     # الإشارة إلى مسار ملف الـ HTML مباشرة
#     return render(request, 'Attendance.html', context)
from django.shortcuts import render
from .models import Task

def الحضور(request):
    tasks = Task.objects.all()
    
    # استقبال قيم البحث والفلترة من الـ URL
    search_query = request.GET.get('q')
    month = request.GET.get('month')
    year = request.GET.get('year')

    # تصفية البيانات
    if search_query:
        tasks = tasks.filter(name__icontains=search_query) # افترضت أن اسم الحقل name
    
    if month:
        tasks = tasks.filter(date__month=month) # افترضت أن الحقل يسمى date
        
    if year and year != 'all':
        tasks = tasks.filter(date__year=year)

    context = {
        'tasks': tasks,
        'years': range(2025, 2036),
    }
    return render(request, 'Attendance.html', context)
@allowed_users_only
def task_list(request):
    # معالجة النموذج عند الإرسال
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        
        # إذا كان هناك task_id فهذا يعني تحديث مهمة موجودة
        if task_id:
            task = get_object_or_404(Task, pk=task_id)
            
            # التحقق من نوع العملية
            action = request.POST.get('action')
            
            if action == 'update':
                # تحديث بيانات المهمة
                task.name = request.POST.get('name')
                
                # تحديث المكلف
                delegate_id = request.POST.get('delegate')
                if delegate_id:
                    task.delegate = get_object_or_404(Name, pk=delegate_id)
                else:
                    task.delegate = None
                
                # تحديث المتابع
                follower_id = request.POST.get('follower')
                if follower_id:
                    task.follower = get_object_or_404(Name, pk=follower_id)
                else:
                    task.follower = None
                
                task.type = request.POST.get('type')
                task.status = request.POST.get('status')
                
                # تحديث التاريخ والوقت
                date_str = request.POST.get('date')
                time_str = request.POST.get('time')
                if date_str and time_str:
                    task.date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                    task.time = datetime.datetime.strptime(time_str, '%H:%M').time()
                
                # تحديث النتيجة إذا كانت المهمة مكتملة
                if task.status == 'تم':
                    task.result = request.POST.get('result', '')
                else:
                    task.result = ''
                
                task.save()
                
            elif action == 'delete':
                # حذف المهمة
                task.delete()
                
            elif action == 'refresh':
                # تحديث القائمة فقط
                pass
        else:
            # إنشاء مهمة جديدة
            delegate_id = request.POST.get('delegate')
            follower_id = request.POST.get('follower')
            
            # تحديث التاريخ والوقت
            date_str = request.POST.get('date')
            time_str = request.POST.get('time')
            task_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else timezone.now().date()
            task_time = datetime.datetime.strptime(time_str, '%H:%M').time() if time_str else timezone.now().time()
            
            Task.objects.create(
                name=request.POST.get('name'),
                delegate=get_object_or_404(Name, pk=delegate_id) if delegate_id else None,
                follower=get_object_or_404(Name, pk=follower_id) if follower_id else None,
                type=request.POST.get('type'),
                status=request.POST.get('status'),
                date=task_date,
                time=task_time,
                result=request.POST.get('result', '') if request.POST.get('status') == 'تم' else ''
            )
        
        # إذا كان طلب AJAX، إرجاع استجابة JSON
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        
        # إعادة التوجيه إلى نفس الصفحة
        return redirect('task_manager')
    
    # الحصول على المهام من قاعدة البيانات
    tasks = Task.objects.all()
    
    # فلترة المهام المتأخرة
    show_overdue = request.GET.get('show_overdue') == 'on'
    if show_overdue:
        tasks = tasks.filter(status='لم يتم')
        overdue_tasks = []
        for task in tasks:
            task_datetime = timezone.make_aware(datetime.datetime.combine(task.date, task.time))
            if task_datetime < timezone.now():
                overdue_tasks.append(task.id)
        tasks = tasks.filter(id__in=overdue_tasks)
    
    # ترتيب المهام
    sort_by = request.GET.get('sort_by', 'ذكي')
    
    if sort_by == 'ذكي':
        tasks = sorted(tasks, key=lambda t: (t.status == 'تم', -t.urgency_score, t.datetime))
    elif sort_by == 'الوقت':
        tasks = sorted(tasks, key=lambda t: (t.status == 'تم', t.datetime))
    elif sort_by == 'النوع':
        type_order = {'مالية': 1, 'إدارية': 2, 'لوجستي': 3, 'تجهيزات': 4}
        tasks = sorted(tasks, key=lambda t: (t.status == 'تم', type_order.get(t.type, 5), t.datetime))
    elif sort_by == 'الحالة':
        tasks = sorted(tasks, key=lambda t: (t.status == 'تم', t.is_overdue, t.datetime))
    elif sort_by == 'التاريخ':
        tasks = sorted(tasks, key=lambda t: (t.status == 'تم', t.date, t.time), reverse=True)
    
    # حساب الإحصائيات
    total_tasks = Task.objects.count()
    completed_tasks = Task.objects.filter(status='تم').count()
    
    # حساب المهام المتأخرة
    overdue_tasks_count = 0
    incomplete_tasks = Task.objects.filter(status='لم يتم')
    for task in incomplete_tasks:
        task_datetime = timezone.make_aware(datetime.datetime.combine(task.date, task.time))
        if task_datetime < timezone.now():
            overdue_tasks_count += 1
    
    # الحصول على جميع الأشخاص لقوائم الاختيار
    persons = Name.objects.all()
    
    # الحصول على المهمة المحددة للتعديل
    edit_task = None
    edit_task_id = request.GET.get('edit')
    if edit_task_id:
        edit_task = get_object_or_404(Task, pk=edit_task_id)
    
    context = {
        'tasks': tasks,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'overdue_tasks': overdue_tasks_count,
        'show_overdue': show_overdue,
        'sort_by': sort_by,
        'edit_task': edit_task,
        'persons': persons,
        'now': timezone.now(),
    }
    
    return render(request, 'tasks/task_list.html', context)
