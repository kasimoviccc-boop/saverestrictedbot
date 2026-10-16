import os
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from pyrogram import Client, filters, idle

# 1. Render port talabini qondirish uchun HTTP server
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot faol ishlayapti!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

server_thread = threading.Thread(target=run_server)
server_thread.daemon = True
server_thread.start()

# O'zgaruvchilarni olish
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
STRING_SESSION = os.getenv("STRING_SESSION", "")

# 2. Bot klienti (foydalanuvchi bilan yozishish uchun)
bot = Client(
    "my_bot_client",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# 3. Userbot klienti (yopiq kanallardan fayl yuklab olish uchun)
userbot = Client(
    "my_user_client",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=STRING_SESSION
)

@bot.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply(
        "Salom! Menga yopiq yoki cheklangan kanaldagi post havolasini yuboring "
        "(masalan: https://t.me/c/123456789/10), men sizga videoni yuklab beraman."
    )

@bot.on_message(filters.text & ~filters.command(["start"]))
async def download_media(client, message):
    url = message.text.strip()
    
    if "t.me/c/" in url:
        status_msg = await message.reply("⏳ Fayl yuklanmoqda, biroz kuting...")
        try:
            parts = url.split("/")
            chat_id = int("-100" + parts[-2])
            msg_id = int(parts[-1])
            
            # Userbot yopiq kanaldan xabarni oladi
            msg = await userbot.get_messages(chat_id, msg_id)
            if msg and msg.media:
                path = await userbot.download_media(msg)
                await message.reply_video(video=path, caption="Mana siz so'ragan video! 🚀")
                if os.path.exists(path):
                    os.remove(path)
                await status_msg.delete()
            else:
                await status_msg.edit("❌ Bu havolada video topilmadi yoki userbot bu kanalga a'zo emas.")
        except Exception as e:
            await status_msg.edit(f"❌ Xatolik yuz berdi: {str(e)}")
    else:
        await message.reply("⚠️ Iltimos, faqat yopiq kanaldagi post havolasini yuboring (masalan: https://t.me/c/...)")

async main():
    await bot.start()
    await userbot.start()
    print("Bot va Userbot muvaffaqiyatli ishga tushdi!")
    await idle()
    await bot.stop()
    await userbot.stop()

if __name__ == "__main__":
    asyncio.run(main())
        
