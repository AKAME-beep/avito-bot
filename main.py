import time
import requests
from bs4 import BeautifulSoup
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

TOKEN = "8661679728:AAGiOHFWxzzIlSwof9yocKz4cbi_SqqvG2Q"
CHAT_ID = "1182541467"
URL = "https://tgstat.ru"
INTERVAL = 60

class HealthCheckServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")

def run_health_server():
    server = HTTPServer(("0.0.0.0", 10000), HealthCheckServer)
    server.serve_forever()

def send_telegram(text):
    url = f"https://telegram.org{TOKEN}/sendMessage"
    try:
        res = requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}, timeout=10)
        print(f"Ответ Telegram: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"Ошибка сети: {e}")

def parse_data():
    try:
        response = requests.get(URL, timeout=15)
        if response.status_code != 200:
            return []
        soup = BeautifulSoup(response.text, "xml")
        items = soup.find_all("item")
        listings = []
        for item in items:
            title = item.find("title").text if item.find("title") else "Новый лот"
            link = item.find("link").text if item.find("link") else ""
            listings.append({"title": title, "link": link})
        return listings
    except:
        return []

def main():
    print("Бот успешно запущен.")
    send_telegram("🚀 Робот-мониторинг Котов-Воителей успешно запущен в облаке!")
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
    threading.Thread(target=run_health_server, daemon=True).start()
    main()
