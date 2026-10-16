import os
from pyrogram import Client, filters
from flask import Flask
from threading import Thread

# Web Service Render'da o'chib qolmasligi uchun kichik veb-server
web_app = Flask('')

@web_app.route('/')
def home():
    return "Bot faol ishlayapti!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.daemon = True
    t.start()

# Render muhit o'zgaruvchilarini o'qish
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
STRING_SESSION = os.getenv("STRING_SESSION", "")

app = Client(
    "restricted_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    session_string=STRING_SESSION
)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply(
        "Salom! Menga yopiq yoki cheklangan kanaldagi post havolasini yuboring "
        "(masalan: https://t.me/c/123456789/10), men sizga videoni yuklab beraman."
    )

@app.on_message(filters.text & ~filters.command(["start"]))
async def download_media(client, message):
    url = message.text.strip()
    
    if "t.me/c/" in url:
        try:
            status_msg = await message.reply("⏳ Fayl yuklanmoqda, biroz kuting...")
            
            parts = url.split("/")
            chat_id = int("-100" + parts[-2])
            msg_id = int(parts[-1])
            
            msg = await client.get_messages(chat_id, msg_id)
            if msg.media:
                path = await client.download_media(msg)
                await message.reply_video(video=path, caption="Mana siz so'ragan video! 🚀")
                os.remove(path)
                await status_msg.delete()
            else:
                await status_msg.edit("❌ Bu havolada video topilmadi.")
        except Exception as e:
            await message.reply(f"❌ Xatolik yuz berdi: {str(e)}")
    else:
        await message.reply("⚠️ Iltimos, faqat yopiq kanaldagi post havolasini yuboring (masalan: https://t.me/c/...)")

if __name__ == "__main__":
    keep_alive()  # Veb-serverni fonda ishga tushiramiz
    print("Bot ishga tushdi...")
    app.run()
    
