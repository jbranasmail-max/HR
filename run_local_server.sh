#!/bin/bash

# ==============================================================================
# تشغيل خادم Django عبر الشبكة المحلية
# HR Management System - Local Network Server
# ==============================================================================

# ألوان لتحسين الواجهة
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}======================================================${NC}"
echo -e "${CYAN}         نظام إدارة الموارد البشرية - HR System      ${NC}"
echo -e "${CYAN}             تشغيل الخادم عبر الشبكة المحلية           ${NC}"
echo -e "${CYAN}======================================================${NC}"
echo ""

# التحقق من وجود Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}خطأ: Python3 غير مثبت على النظام${NC}"
    exit 1
fi

# الانتقال إلى مجلد المشروع
PROJECT_DIR="/home/mazen/Desktop/HR"
cd "$PROJECT_DIR" || {
    echo -e "${RED}خطأ: لا يمكن الوصول إلى مجلد المشروع: $PROJECT_DIR${NC}"
    exit 1
}

echo -e "${BLUE}📁 مجلد المشروع: $PROJECT_DIR${NC}"

# التحقق من وجود manage.py
if [ ! -f "manage.py" ]; then
    echo -e "${RED}خطأ: ملف manage.py غير موجود${NC}"
    exit 1
fi

# التحقق من وجود البيئة الافتراضية وتفعيلها
if [ -d "venv" ]; then
    echo -e "${YELLOW}🔄 تفعيل البيئة الافتراضية...${NC}"
    source venv/bin/activate
elif [ -d "env" ]; then
    echo -e "${YELLOW}🔄 تفعيل البيئة الافتراضية...${NC}"
    source env/bin/activate
elif [ -d ".venv" ]; then
    echo -e "${YELLOW}🔄 تفعيل البيئة الافتراضية...${NC}"
    source .venv/bin/activate
else
    echo -e "${YELLOW}⚠️  تحذير: لم يتم العثور على بيئة افتراضية${NC}"
    echo -e "${YELLOW}   سيتم استخدام Python النظام${NC}"
fi

# الحصول على عنوان IP المحلي
LOCAL_IP=$(hostname -I | awk '{print $1}' | head -n1)
if [ -z "$LOCAL_IP" ]; then
    LOCAL_IP=$(ip route get 1 | awk '{print $NF;exit}' 2>/dev/null)
fi

if [ -z "$LOCAL_IP" ]; then
    LOCAL_IP="192.168.1.100"  # قيمة افتراضية
    echo -e "${YELLOW}⚠️  تحذير: لم يتم تحديد IP تلقائياً، استخدام: $LOCAL_IP${NC}"
else
    echo -e "${GREEN}🌐 عنوان IP المحلي: $LOCAL_IP${NC}"
fi

# تحديد المنفذ
PORT=${1:-3001}
echo -e "${GREEN}🔗 المنفذ: $PORT${NC}"

echo ""
echo -e "${CYAN}======================================================${NC}"
echo -e "${GREEN}✅ معلومات الاتصال:${NC}"
echo -e "${GREEN}   🖥️  على نفس الجهاز: http://localhost:$PORT${NC}"
echo -e "${GREEN}   🏠 عبر الشبكة المحلية: http://$LOCAL_IP:$PORT${NC}"
echo -e "${GREEN}   📱 للأجهزة المحمولة: http://$LOCAL_IP:$PORT${NC}"
echo -e "${CYAN}======================================================${NC}"
echo ""

echo -e "${YELLOW}📋 تعليمات للوصول من أجهزة أخرى:${NC}"
echo -e "${YELLOW}   1. تأكد من أن جميع الأجهزة على نفس الواي فاي${NC}"
echo -e "${YELLOW}   2. في المتصفح اكتب: http://$LOCAL_IP:$PORT${NC}"
echo -e "${YELLOW}   3. للإيقاف اضغط Ctrl+C${NC}"
echo ""

# إجراء فحص سريع للنظام
echo -e "${BLUE}🔍 إجراء فحص سريع...${NC}"

# فحص قاعدة البيانات
if python3 manage.py check --deploy > /dev/null 2>&1; then
    echo -e "${GREEN}✅ فحص النظام: نجح${NC}"
else
    echo -e "${YELLOW}⚠️  فحص النظام: هناك تحذيرات${NC}"
fi

# تطبيق التحديثات (إذا لزم الأمر)
echo -e "${BLUE}🔄 فحص التحديثات...${NC}"
if python3 manage.py showmigrations --plan | grep -q "\[ \]"; then
    echo -e "${YELLOW}🔄 تطبيق تحديثات قاعدة البيانات...${NC}"
    python3 manage.py migrate
    echo -e "${GREEN}✅ تم تطبيق التحديثات${NC}"
else
    echo -e "${GREEN}✅ قاعدة البيانات محدثة${NC}"
fi

echo ""
echo -e "${GREEN}🚀 بدء تشغيل الخادم...${NC}"
echo -e "${CYAN}======================================================${NC}"

# تشغيل الخادم
python3 manage.py runserver 0.0.0.0:$PORT

# رسالة الإغلاق
echo ""
echo -e "${CYAN}======================================================${NC}"
echo -e "${YELLOW}📴 تم إيقاف الخادم${NC}"
echo -e "${GREEN}شكراً لاستخدام نظام إدارة الموارد البشرية${NC}"
echo -e "${CYAN}======================================================${NC}"