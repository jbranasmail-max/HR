"""
URL configuration for HR project.

The urlpatterns list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path ,include
from . import views
from django.contrib.auth.views import LogoutView
# from django.urls import path
# from .views import hikvision_webhook


urlpatterns = [
  path('logout/', views.logout_view, name='logout'),
 path("login/", views.login_view, name="login"),
    path("logout/", LogoutView.as_view(next_page='login'), name="logout"),
   
    path("reports/", views.reports_home, name="reports_home"),

    path("admin/", admin.site.urls),
  path("", views.login_view, name="login"),
 
    path("reports/", views.reports_home, name="reports_home"),
    path(
        "reports/person/<int:person_id>/",
        views.person_detail_report,
        name="person_detail_report",
    ),
    path(
        "reports/person/<int:person_id>/print/",
        views.person_print_simple,
        name="person_print_simple",
    ),
    path("api/person/<int:person_id>/", views.person_data_api, name="person_data_api"),
    path("i18n/", include("django.conf.urls.i18n")),  # Add this line
    path("term-chart/<int:student_id>/", views.term_chart, name="term_chart"),
     path('api/term-chart-data/<int:student_id>/', views.api_term_chart_data, name='api_term_chart_data'),

    # مخطط درجات السنة
    path("year-chart/<int:student_id>/", views.year_chart, name="year_chart"),
path("full-progress/<int:student_id>/", views.full_academic_progress, name="full_academic_progress"),

    # مخطط كل السنوات
   # مخطط كل السنوات
    path("summary_chart/<int:student_id>/", views.summary_chart, name="summary_chart"),
   path('monthly_report/<int:person_id>/', views.monthly_report, name='monthly_report'),
path('spiritual_report/<int:person_id>/', views.spiritual_report, name='spiritual_report'),
   
path('For_every_year/<int:person_id>/', views.For_every_year, name='For_every_year'),
 
#   path('tasks/', views.Attendance, name=' Attendance'),
path('tasks/', views.task_list, name='task_list'),
 path('tasks/', views.task_list, name='task_manager'),
# urls.py

    # path("hikvision/webhook/", hikvision_webhook),


]