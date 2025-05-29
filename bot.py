import os
import telebot
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

def search_part(article):
    url = f"https://platonservice.com/search/?q={article}"
    response = requests.get(url)
    if article not in response.text:
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    link = soup.select_one(".product__title a")
    if not link:
        return None

    product_url = "https://platonservice.com" + link.get("href")
    product_page = requests.get(product_url)
    psoup = BeautifulSoup(product_page.text, 'html.parser')

    name = psoup.select_one(".product__title").text.strip()
    price_old_tag = psoup.select_one(".product__price--old")
    if not price_old_tag:
        return None
    try:
        old_price = int(price_old_tag.text.replace("₽", "").replace(" ", "").strip())
        discount_price = int(old_price * 0.7)
    except:
        return None

    return {
        "name": name,
        "url": product_url,
        "old_price": old_price,
        "final_price": discount_price
    }

@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "Здравствуйте! Чем могу помочь? Напишите артикул или вопрос.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    article = message.text.strip()
    result = search_part(article)
    if result:
               reply = (
            f"🔹 {result['name']}\n"
            f"🔗 {result['url']}\n"
            f"❌ Старая цена: ~{result['old_price']} ₽~\n"
            f"✅ Скидка 30%\n"
            f"💰 Цена со скидкой: {result['final_price']} ₽"
        )
    else:
        reply = "К сожалению, не нашёл такой товар. Сейчас подключу менеджера..."
    bot.reply_to(message, reply)

bot.infinity_polling()
