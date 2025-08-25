import telebot
import requests
import re
import os
from flask import Flask, request
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Tokens
BOT_TOKEN = os.getenv("BOT_TOKEN")   # Render me Environment variable set karo
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
bot = telebot.TeleBot(BOT_TOKEN)

# Flask app for Render
app = Flask(__name__)

def get_youtube_title(video_url):
    """ YouTube link se Title nikalta hai """
    try:
        if "watch?v=" in video_url:
            video_id = video_url.split("watch?v=")[1].split("&")[0]
        elif "youtu.be/" in video_url:
            video_id = video_url.split("youtu.be/")[1].split("?")[0]
        elif "live/" in video_url:
            video_id = video_url.split("live/")[1].split("?")[0]
        else:
            return None

        api_url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={YOUTUBE_API_KEY}"
        response = requests.get(api_url).json()
        title = response["items"][0]["snippet"]["title"]
        return title
    except:
        return None

def parse_title(title):
    """ Title ko Subject, Lecture, Topic, Batch me todta hai """
    subject, lecture, topic, batch = "Unknown", "N/A", "N/A", "N/A"

    lecture_match = re.search(r"Lecture\s*(\d+)", title, re.IGNORECASE)
    topic_match = re.search(r"Topic\s*([^\|]+)", title, re.IGNORECASE)
    batch_match = re.search(r"\|\s*(.*)$", title)

    parts = title.split("Lecture")[0].strip().split()
    if parts:
        subject = parts[0]

    if lecture_match:
        lecture = lecture_match.group(1)

    if topic_match:
        topic = topic_match.group(1).strip()

    if batch_match:
        batch = batch_match.group(1).strip()

    return subject, lecture, topic, batch


# ✅ Start command
@bot.message_handler(commands=['start'])
def start_command(message):
    welcome_text = (
        "👋 Namaste! Main ek YouTube Title Extractor Bot hoon.\n\n"
        "📌 Aap mujhe koi bhi YouTube link bhejiye, aur mai uska Title + Details nikal dunga.\n\n"
        "ℹ️ Commands:\n"
        "/start - Bot ko shuru kare\n"
        "/help - Madad aur commands dekhe\n\n"
        "✨ made by Antaryami 🇮🇳"
    )

    markup = InlineKeyboardMarkup()
    channel_button = InlineKeyboardButton("📢 Join Our Channel", url="https://t.me/+EAo5RTrXbnliZDM1")
    markup.add(channel_button)

    bot.reply_to(message, welcome_text, reply_markup=markup)


# ✅ Help command
@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = (
        "📖 *Help Menu*\n\n"
        "1️⃣ Mujhe YouTube ka koi bhi link bhejiye.\n"
        "2️⃣ Main uska Title, Subject, Lecture, Topic, aur Batch nikal dunga.\n\n"
        "💡 Example: https://youtu.be/abcd1234\n\n"
        "✨ made by Antaryami 🇮🇳"
    )
    bot.reply_to(message, help_text, parse_mode="Markdown")


# ✅ YouTube link handler
@bot.message_handler(func=lambda msg: "youtube.com" in msg.text or "youtu.be" in msg.text)
def handle_youtube_link(message):
    url = message.text.strip()
    title = get_youtube_title(url)

    if not title:
        bot.reply_to(message, "❌ Video title fetch nahi ho paaya.")
        return

    subject, lecture, topic, batch = parse_title(title)

    reply_msg = (
        "━━━━━━━━━━━━━━\n"
        f"📚 Subject: {subject}\n"
        f"🎬 Lecture: {lecture}\n"
        f"📝 Topic: {topic}\n"
        f"👨‍🏫 Batch: {batch}\n"
        f"▶️ Watch Now: {url}\n"
        "━━━━━━━━━━━━━━\n"
        "✨ made by Antaryami 🇮🇳"
    )

    # Inline button for channel
    markup = InlineKeyboardMarkup()
    channel_button = InlineKeyboardButton("📢 Join Our Channel", url="https://t.me/+EAo5RTrXbnliZDM1")
    markup.add(channel_button)

    bot.reply_to(message, reply_msg, reply_markup=markup)


# Flask route for webhook
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/")
def index():
    return "🤖 Bot is running with Flask on Render!", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render ke liye port 10000
    app.run(host="0.0.0.0", port=port)
