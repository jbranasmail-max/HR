#!/bin/bash

echo "=========================================="
echo "إنشاء البيانات التجريبية لنظام الموارد البشرية"
echo "=========================================="

# التحقق من وجود Python و Django
if ! command -v python3 &> /dev/null; then
    echo "خطأ: Python 3 غير مثبت"
    exit 1
fi

# الانتقال لمجلد المشروع
cd "$(dirname "$0")"

echo "1. جاري إنشاء قاعدة البيانات والجداول..."
python3 manage.py makemigrations
python3 manage.py migrate

echo ""
echo "2. جاري إنشاء البيانات الأساسية..."
python3 manage.py create_sample_data --clear

echo ""
echo "3. جاري إنشاء بيانات التقدم الأكاديمي المحسنة..."
python3 manage.py create_academic_progress_data

echo ""
echo "=========================================="
echo "تم الانتهاء من إنشاء البيانات التجريبية!"
echo "=========================================="

echo ""
echo "يمكنك الآن تشغيل الخادم باستخدام:"
echo "python3 manage.py runserver"

echo ""
echo "أو تشغيل:"
echo "./run_local_server.sh"