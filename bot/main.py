import time
from datetime import datetime, timedelta
import os
import threading
import schedule
import telebot
from dotenv import load_dotenv
from data import db_session
from data.users import User
from data.records import Record

load_dotenv()
API_TOKEN = os.getenv("API_KEY")
bot = telebot.TeleBot(API_TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    telegram_id = message.chat.id
    bot.send_message(
        telegram_id,
        "Привет! Отправь свой email для привязки аккаунта.\n"
        "Пример: /link your_email@example.com"
    )


@bot.message_handler(commands=['link'])
def link_account(message):
    telegram_id = message.chat.id
    try:
        email = message.text.split()[1]
    except IndexError:
        bot.send_message(telegram_id, "❌ Формат: /link your_email@example.com")
        return

    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.email == email).first()

    if user:
        user.telegram_id = str(telegram_id)
        db_sess.commit()
        bot.send_message(telegram_id, f"✅ Аккаунт привязан! Добро пожаловать, {user.name}!")
    else:
        bot.send_message(telegram_id, "❌ Пользователь с таким email не найден")


@bot.message_handler(commands=['my_bookings'])
def my_bookings(message):
    telegram_id = str(message.chat.id)
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.telegram_id == telegram_id).first()

    if not user:
        bot.send_message(message.chat.id, "❌ Сначала привяжите аккаунт: /link email")
        return

    records = db_sess.query(Record).filter(Record.user_id == user.id).all()

    if not records:
        bot.send_message(message.chat.id, "У вас пока нет записей")
        return

    text = "📋 Ваши записи:\n\n"
    for record in records:
        text += f"📅 {record.date_time}\n"
        text += "➖➖➖➖➖➖➖➖\n"

    bot.send_message(message.chat.id, text)


def send_telegram_notification(telegram_id, message_text):
    try:
        if telegram_id:
            bot.send_message(int(telegram_id), message_text)
            return True
    except Exception as e:
        print(f"Ошибка отправки уведомления: {e}")
        return False


def notify_user_about_booking(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    record = db_sess.query(Record).filter(
        Record.user_id == user_id
    ).order_by(Record.id.desc()).first()

    if user and user.telegram_id and record:
        message = (
            f"🎉 Новая запись!\n\n"
            f"📅 Дата: {record.date_time}\n\n"
            f"Спасибо за доверие!"
        )
        send_telegram_notification(user.telegram_id, message)


def check_and_send_reminders():
    db_sess = db_session.create_session()
    tomorrow = datetime.now() + timedelta(days=1)

    records = db_sess.query(Record).filter(
        Record.date_time >= tomorrow.replace(hour=0, minute=0, second=0),
        Record.date_time <= tomorrow.replace(hour=23, minute=59, second=59)
    ).all()

    for record in records:
        user = db_sess.query(User).filter(User.id == record.user_id).first()
        if user and user.telegram_id:
            message = (
                f"⏰ Напоминание!\n\n"
                f"У вас завтра запись!\n"
                f"📅 {record.date_time}\n\n"
                f"Не забудьте!"
            )
            send_telegram_notification(user.telegram_id, message)
            print(f"Напоминание отправлено пользователю {user.id}")


def schedule_checker():
    schedule.every().hour.do(check_and_send_reminders)

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == '__main__':
    db_session.global_init("../db/beatyweb.db")

    reminder_thread = threading.Thread(target=schedule_checker)
    reminder_thread.daemon = True
    reminder_thread.start()

    print("✅ Бот запущен с напоминаниями")
    bot.polling(none_stop=True, timeout=30)
