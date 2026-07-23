import time
import requests
from bs4 import BeautifulSoup

TOKEN = "8661679728:AAGiOHFWxzzIlSwof9yocKz4cbi_SqqvG2Q"
CHAT_ID = "1182541467"
URL = "https://avito.ru"
INTERVAL = 10

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def send_telegram(text):
    api_url = f"https://tgproxy.today{TOKEN}/sendMessage"
    try:
        res = requests.post(api_url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}, timeout=10)
        if res.status_code != 200:
            print(f"Ошибка доставки: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"Ошибка сети: {e}")

def parse_avito():
    try:
        response = requests.get(URL, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            print(f"Авито временно недоступен. Код: {response.status_code}")
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
    except:
        return []

def main():
    print("Бот успешно запущен на вашем ПК.")
    send_telegram("🚀 Робот-мониторинг Котов-Воителей успешно запущен на вашем ПК!")
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
    main()
