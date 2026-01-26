from datetime import datetime, timedelta
from telebot import types
from utils.dates import get_hijri_date
from keyboards.main_keyboard import get_start_keyboard

def start_handler(bot):

    @bot.message_handler(commands=['start'])
    def start(message):
        # معلومات المستخدم
        user_name = message.from_user.first_name
        user_id = message.from_user.id
        username = f"@{message.from_user.username}" if message.from_user.username else "لا يوجد"

        # توقيت بغداد
        now = datetime.utcnow() + timedelta(hours=3)

        time_24 = now.strftime("%H:%M:%S")
        time_12 = now.strftime("%I:%M:%S %p").replace("AM", "صباحاً").replace("PM", "مساءً")
        day_name_en = now.strftime("%A")

        # مصفوفات
        days_ar = {
            "Monday": "الأثنين", "Tuesday": "الثلاثاء", "Wednesday": "الأربعاء",
            "Thursday": "الخميس", "Friday": "الجمعة",
            "Saturday": "السبت", "Sunday": "الأحد"
        }

        months_miladi = [
            "", "كانون الثاني", "شباط", "آذار", "نيسان", "أيار",
            "حزيران", "تموز", "آب", "أيلول",
            "تشرين الأول", "تشرين الثاني", "كانون الأول"
        ]

        months_hijri = [
            "", "محرم", "صفر", "ربيع الأول", "ربيع الثاني",
            "جمادى الأولى", "جمادى الآخرة", "رجب", "شعبان",
            "رمضان", "شوال", "ذو القعدة", "ذو الحجة"
        ]

        # التاريخ الميلادي
        date_miladi_str = f"{now.day} {months_miladi[now.month]} {now.year}"

        # التاريخ الهجري
        raw_hijri = get_hijri_date(now.strftime("%Y/%m/%d"))
        h_day, h_month, h_year = raw_hijri.split("/")
        h_month = int(h_month)

        date_hijri_str = f"{int(h_day)} {months_hijri[h_month]} ({h_month}) {h_year}"

        # مناسبات
        occasions = {
            "1/1": "رأس السنة الهجرية",
            "10/1": "يوم عاشوراء",
            "12/3": "مولد النبي (ص)",
            "1/10": "عيد الفطر المبارك",
            "10/12": "عيد الأضحى المبارك",
            "13/1": "استشهاد الزهراء (ع)"
        }

        current_occ = occasions.get(f"{h_day}/{h_month}", "لا توجد مناسبة مسجلة اليوم")

        # رسالة البدء
        welcome_html = (
            f"<b>✨ أهلاً بك يا {user_name} في بوت الخدمات الشامل</b>\n\n"
            f"<b>👤 معلوماتك:</b>\n"
            f"• اليوزر: {username}\n"
            f"• الأيدي: <code>{user_id}</code>\n\n"
            f"<b>📅 تاريخ اليوم:</b>\n"
            f"• اليوم: <b>{days_ar.get(day_name_en)}</b>\n"
            f"• ميلادي: <b>{date_miladi_str}</b>\n"
            f"• هجري: <b>{date_hijri_str}</b>\n"
            f"• المناسبة: <i>{current_occ}</i>\n\n"
            f"<b>⏰ الوقت الحالي (بتوقيت بغداد):</b>\n"
            f"• نظام 12H: <code>{time_12}</code>\n"
            f"• نظام 24H: <code>{time_24}</code>\n\n"
            f"<b>🛠 ماذا يقدم البوت؟</b>\n"
            f"يقدم البوت خدمات دينية، تقنية، وخدمات صور متقدمة.\n\n"
            f"👨🏻‍💻 مطور البوت: <a href='https://t.me/altaee_z'>علي الطائي</a>\n"
            f"📦 إصدار البوت: <a href='https://www.ali-altaee.free.nf/'><b>V2.5.0</b></a>"
        )

        bot.send_message(
            message.chat.id,
            welcome_html,
            reply_markup=get_start_keyboard(),
            parse_mode="HTML",
            disable_web_page_preview=True
        )