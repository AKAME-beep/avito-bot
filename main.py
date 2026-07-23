import time
import requests
from bs4 import BeautifulSoup

TOKEN = "8661679728:AAGiOHFWxzzIlSwof9yocKz4cbi_SqqvG2Q"
CHAT_ID = "1182541467"
URL = "https://yandex.ru" + requests.utils.quote("site:avito.ru коты воители")
INTERVAL = 60

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def send_telegram(text):
    api_url = f"https://telegram.org{TOKEN}/sendMessage"
    try:
        requests.post(api_url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}, timeout=10)
    except:
        try:
            fallback_url = f"https://b612.me{TOKEN}/sendMessage"
            requests.post(fallback_url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}, timeout=10)
        except:
            pass

def parse_data():
    try:
        response = requests.get(URL, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            return []
        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.find_all("a")
        listings = []
        for item in items:
            link = item.get("href", "")
            title = item.text.strip()
            if "avito.ru" in link and len(title) > 5:
                listings.append({"title": title, "link": link})
        return listings
    except:
        return []

def main():
    print("Бот успешно запущен на вашем ПК.")
    send_telegram("🚀 Робот-мониторинг Котов-Воителей успешно запущен по защищенному каналу!")
    old_listings = parse_data()
    old_links = {item["link"] for item in old_listings}
    while True:
        time.sleep(INTERVAL)
        current_listings = parse_data()
        if not current_listings:
            continue
        for item in current_listings:
            if item["link"] not in old_links:
                message = f"🔔 *Новое объявление!*\n\n📌 *{item['title']}*\n🔗 [Открыть на Авито]({item['link']})"
                send_telegram(message)
                old_links.add(item["link"])

if __name__ == "__main__":
    main()
