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
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; SM-S911B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache"
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
        requests.post(api_url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})
    except:
        pass

def parse_avito():
    try:
        response = requests.get(URL, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            return []
        soup = BeautifulSoup(response.text, "html.parser" if "item" not in response.text else "xml")
        items = soup.find_all("item")
        listings = []
        for item in items:
            title = item.find("title").text if item.find("title") else "Без названия"
            link = item.find("link").text if item.find("link") else ""
            price = item.find("price").text if item.find("price") else "Цена не указана"
            listings.append({"title": title, "link": link, "price": price})
        return listings
    except:
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
