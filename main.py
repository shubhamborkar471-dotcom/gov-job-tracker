import os
import sys
import requests
import feedparser
from datetime import datetime

# Retrieve credentials from GitHub Secrets
BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Sources: RSS feeds and structured feeds for government recruitment updates
JOB_FEEDS = [
    {"name": "Free Job Alert", "url": "https://www.freejobalert.com/feed/"},
    {"name": "Sarkari Result Updates", "url": "https://www.sarkariresult.com/feed/"}
]

def send_telegram_message(text: str) -> bool:
    """Sends a formatted Markdown message to your Telegram Chat/Bot."""
    if not BOT_TOKEN or not CHAT_ID:
        print("Error: Missing TELEGRAM_TOKEN or TELEGRAM_CHAT_ID environment variables.")
        return False

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print("Notification sent successfully to Telegram!")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Failed to send message via Telegram: {e}")
        return False

def scrape_job_updates():
    """Scrapes top recruitment updates from specified feeds."""
    all_updates = []

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for feed_info in JOB_FEEDS:
        print(f"Fetching updates from: {feed_info['name']}...")
        try:
            # Fetch feed content with explicit headers to avoid 403 blocks
            resp = requests.get(feed_info['url'], headers=headers, timeout=15)
            feed = feedparser.parse(resp.content)

            # Retrieve top 4 posts per source
            for entry in feed.entries[:4]:
                title = entry.get("title", "No Title").strip()
                link = entry.get("link", "#")
                
                # Format bullet point item
                all_updates.append(f"• *{title}*\n  🔗 [Apply / View Notification]({link})")
        except Exception as e:
            print(f"Error fetching {feed_info['name']}: {e}")

    # Build final message payload
    today_str = datetime.now().strftime("%d %b %Y")
    
    if all_updates:
        # Telegram messages have a 4096 character limit; slice top 8 updates
        formatted_list = "\n\n".join(all_updates[:8])
        message = (
            f"📢 *Daily Govt Job Recruitment Updates*\n"
            f"🗓 *Date:* {today_str}\n\n"
            f"{formatted_list}\n\n"
            f"───────────────\n"
            f"🤖 _Automated via GitHub Actions_"
        )
    else:
        message = f"ℹ️ *Govt Job Tracker ({today_str})*\n\nNo new recruitment updates found today."

    # Dispatch to Telegram
    send_telegram_message(message)

if __name__ == "__main__":
    scrape_job_updates()
      
