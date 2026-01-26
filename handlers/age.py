from datetime import datetime, timedelta

def age_handler(bot, user_states):

    @bot.callback_query_handler(func=lambda c: c.data == "go_age")
    def ask_birth(call):
        user_states[call.from_user.id] = "age"
        bot.edit_message_text(
            "📅 أرسل تاريخ ميلادك:\n<code>YYYY/MM/DD</code>",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )

    @bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "age")
    def calc_age(message):
        try:
            birth = datetime.strptime(message.text, "%Y/%m/%d")
            now = datetime.utcnow() + timedelta(hours=3)
            diff = now - birth
            years = diff.days // 365

            bot.reply_to(
                message,
                f"🎉 عمرك:\n• {years} سنة\n• {diff.days} يوم"
            )
        except:
            bot.reply_to(message, "❌ التاريخ غير صحيح")
        user_states.pop(message.from_user.id, None)