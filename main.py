import telebot
import requests
import re
import os
from flask import Flask, request

# Tokens
BOT_TOKEN = os.getenv("BOT_TOKEN")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
bot = telebot.TeleBot(BOT_TOKEN)

# Flask app
app = Flask(__name__)

CHANNEL_LINK = "https://t.me/+EAo5RTrXbnliZDM1"

# YouTube title fetch
def get_youtube_title(video_url):
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

# Title parsing
def parse_title(title):
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

# /start command
@bot.message_handler(commands=["start"])
def start_cmd(message):
    bot.reply_to(message, "👋 Namaste! Mujhe YouTube link bhejo, main uska title tod kar deta hoon 📚")

# YouTube link handler
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

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("📺 Watch Now", url=url))
    markup.add(telebot.types.InlineKeyboardButton("📢 Join Our Channel", url=CHANNEL_LINK))

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
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
