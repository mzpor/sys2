from balethon import Client
from balethon.conditions import private, text

BOT_TOKEN = "1778171143:vD6rjJXAYidLL7hQyQkBeu5TJ9KpRd4zAKegqUt3"
# توکن بات رو اینجا بذار
#BOT_TOKEN = "BOTFATHER_TOKEN"

# ساخت بات
bot = Client(BOT_TOKEN)

# تابع برای پاسخ به پیام‌های متنی خصوصی
@bot.on_message(private & text)
async def echo(message):
    await message.reply(message.text)

# اجرای بات
if __name__ == "__main__":
    bot.run()