import datetime
import random
from data import db_session
from data.records import Record
from data.category import Category

db_session.global_init("db/beatyweb.db")

price_map = {
    'Мужские': 800,
    'Женские': 1500,
    'Детские': 600,
    'Ножницы': 1000,
    'Машинка': 600,
    'Филировка': 300,
    'Текстурирование': 500,
    'Классика': 700,
    'Европейский': 800,
    'Бразильский': 900,
    'Комби': 750,
    'SPA': 1200,
    'Гигиена': 500,
    'Лечение': 1000,
    'Моделирование': 1100,
    'Косметика': 400,
    'Гель-лак': 800,
    'Акрил': 1200,
    'Гель': 1000,
    'Биогель': 900,
    'Дипинг': 1100,
    'Ламинация': 1500,
    'Ботокс': 2000,
    'Комплекс': 2500,
    'Ногтевая': 700,
    'Мобильные': 1300,
    'Брови': 600,
    'Депиляция': 800,
    'Косметология': 1800,
}

def add_records():
    session = db_session.create_session()
    user_id = 1
    categories = session.query(Category).all()
    start_date = datetime.datetime(2026, 4, datetime.date.today().day, 10, 0, 0)
    for i, cat in enumerate(categories):
        price = price_map.get(cat.name, 500)
        record_date = start_date + datetime.timedelta(days=i % 20, hours=random.randint(0, 12))
        record = Record(
            date_time=record_date,
            price=price,
            user_id=user_id
        )
        record.category.append(cat)
        session.add(record)
    session.commit()

if __name__ == '__main__':
    add_records()