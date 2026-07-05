from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone
from .models import LoginHistory

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    session_key = request.session.session_key  # رقم الجلسة
    if not session_key:
        request.session.create()  # إنشاء جلسة إذا لم تكن موجودة
        session_key = request.session.session_key
    LoginHistory.objects.create(user=user, session_key=session_key)

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    session_key = request.session.session_key
    last = LoginHistory.objects.filter(user=user, session_key=session_key, logout_time__isnull=True).first()
    if last:
        last.logout_time = timezone.now()
        last.save()
