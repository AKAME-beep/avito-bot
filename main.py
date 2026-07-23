import time
import requests
from bs4 import BeautifulSoup
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import urllib.parse

TOKEN = "8661679728:AAGiOHFWxzzIlSwof9yocKz4cbi_SqqvG2Q"
CHAT_ID = "1182541467"
PRODUCT = "коты воители"
INTERVAL = 60

encoded_product = urllib.parse.quote_plus(PRODUCT)
URL = f"https://avito.ru{encoded_product}&s=104&rss=1"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, Gecko) Chrome/120.0.0.0 Safari/537.36"
}

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
    try:
        api_url = f"https://telegram.org{TOKEN}/sendMessage"
        res = requests.post(api_url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})
        print(f"Ответ Telegram: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"Ошибка сети: {e}")

def parse_avito():
    try:
        response = requests.get(URL, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            print(f"Авито вернул статус: {response.status_code}")
            return []
        soup = BeautifulSoup(response.text, "xml")
        items = soup.find_all("item")
        listings = []
        for item in items:
            title = item.find("title").text if item.find("title") else "Без названия"
            link = item.find("link").text if item.find("link") else ""
            price = item.find("price").text if item.find("price") else "Цена не указана"
            listings.append({"title": title, "link": link, "price": price})
        return listings
    except Exception as e:
        print(f"Ошибка парсинга: {e}")
        return []

def main():
    print("Бот успешно запущен в облаке.")
    send_telegram("🚀 Робот-мониторинг Котов-Воителей успешно запущен в облаке!")
    old_listings = parse_avito()
    old_links = {item["link"] for item in old_listings}
    while True:
        time.sleep(INTERVAL)
        current_listings = parse_avito()
        if not current_listings:
            continue
        for item in current_listings:
            if item["link"] not in old_links:
                message = f"🔔 *Новое объявление!*\n\n📌 *{item['title']}*\n💰 Цена: {item['price']}\n🔗 [Открыть на Авито]({item['link']})"
                send_telegram(message)
                old_links.add(item["link"])

if __name__ == "__main__":
    threading.Thread(target=run_health_server, daemon=True).start()
    main()
