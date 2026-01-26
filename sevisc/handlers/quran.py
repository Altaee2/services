from telebot import types
import json, os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QURAN_INDEX = os.path.join(BASE_DIR, "data", "quran_index.json")
USER_PAGES = os.path.join(BASE_DIR, "data", "user_pages.json")

with open(QURAN_INDEX, "r", encoding="utf-8") as f:
    quran = json.load(f)

if not os.path.exists(USER_PAGES):
    with open(USER_PAGES, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False)


# ========= حفظ الصفحة =========
def load_pages():
    with open(USER_PAGES, "r", encoding="utf-8") as f:
        return json.load(f)

def save_page(uid, page):
    data = load_pages()
    data[str(uid)] = int(page)
    with open(USER_PAGES, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_saved_page(uid):
    return int(load_pages().get(str(uid), 1))


# ========= أدوات =========
def get_info(page):
    page = int(page)
    i = next((x for x in quran if int(x.get("page", 0)) == page), None)
    if not i:
        return "غير معروف", "—", "—"
    return (
        i.get("sura_name", "—"),
        i.get("juz", "—"),
        i.get("hizb", "—")
    )

def first_page(key, val):
    i = next((x for x in quran if x.get(key) == val), None)
    return int(i["page"]) if i else 1


# ========= إرسال الصفحة =========
def send_page(bot, chat_id, page, msg_id=None):
    page = int(page)
    sura, juz, hizb = get_info(page)
    save_page(chat_id, page)

    img = f"https://quran.ksu.edu.sa/png_big/{page}.png"

    kb = types.InlineKeyboardMarkup()
    kb.row(
        types.InlineKeyboardButton("⬅️", callback_data="prev"),
        types.InlineKeyboardButton("➡️", callback_data="next")
    )
    kb.add(
        types.InlineKeyboardButton("📘 السور", callback_data="list_sura"),
        types.InlineKeyboardButton("📗 الأجزاء", callback_data="list_juz")
    )
    kb.add(
        types.InlineKeyboardButton("📕 الأحزاب", callback_data="list_hizb")
    )

    cap = (
        f"📖 <b>القرآن الكريم</b>\n\n"
        f"📄 الصفحة: <b>{page}</b>\n"
        f"📘 السورة: <b>{sura}</b>\n"
        f"📗 الجزء: <b>{juz}</b>\n"
        f"📕 الحزب: <b>{hizb}</b>"
    )

    media = types.InputMediaPhoto(img, caption=cap, parse_mode="HTML")

    if msg_id:
        bot.edit_message_media(
            media=media,
            chat_id=chat_id,
            message_id=msg_id,
            reply_markup=kb
        )
    else:
        bot.send_photo(chat_id, img, caption=cap, parse_mode="HTML", reply_markup=kb)


# ========= القوائم =========
def sura_list():
    kb = types.InlineKeyboardMarkup(row_width=2)
    seen = set()
    for i in quran:
        name = i.get("sura_name")
        if name and name not in seen:
            seen.add(name)
            kb.add(types.InlineKeyboardButton(name, callback_data=f"sura_{name}"))
    return kb

def juz_list():
    kb = types.InlineKeyboardMarkup(row_width=5)
    for j in range(1, 31):
        kb.add(types.InlineKeyboardButton(str(j), callback_data=f"juz_{j}"))
    return kb

def hizb_list():
    kb = types.InlineKeyboardMarkup(row_width=5)
    for h in range(1, 61):
        kb.add(types.InlineKeyboardButton(str(h), callback_data=f"hizb_{h}"))
    return kb


# ========= الهاندلر =========
def quran_handler(bot):

    @bot.callback_query_handler(func=lambda c: c.data == "go_quran")
    def start(call):
        page = get_saved_page(call.from_user.id)
        send_page(bot, call.message.chat.id, page)

    @bot.callback_query_handler(func=lambda c: c.data in ["next", "prev"])
    def nav(call):
        page = get_saved_page(call.from_user.id)
        page = page + 1 if call.data == "next" else page - 1

        if not 1 <= page <= 604:
            bot.answer_callback_query(call.id, "📖 لا توجد صفحات أخرى")
            return

        send_page(bot, call.message.chat.id, page, call.message.message_id)

    @bot.callback_query_handler(func=lambda c: c.data == "list_sura")
    def list_s(call):
        bot.send_message(call.message.chat.id, "📘 اختر سورة:", reply_markup=sura_list())

    @bot.callback_query_handler(func=lambda c: c.data == "list_juz")
    def list_j(call):
        bot.send_message(call.message.chat.id, "📗 اختر جزء:", reply_markup=juz_list())

    @bot.callback_query_handler(func=lambda c: c.data == "list_hizb")
    def list_h(call):
        bot.send_message(call.message.chat.id, "📕 اختر حزب:", reply_markup=hizb_list())

    @bot.callback_query_handler(func=lambda c: c.data.startswith(("sura_", "juz_", "hizb_")))
    def select(call):
        if call.data.startswith("sura_"):
            page = first_page("sura_name", call.data[5:])
        elif call.data.startswith("juz_"):
            page = first_page("juz", int(call.data[4:]))
        else:
            page = first_page("hizb", int(call.data[5:]))

        send_page(bot, call.message.chat.id, page)