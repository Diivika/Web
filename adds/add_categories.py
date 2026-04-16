from data import db_session
from data.category import Category

db_session.global_init("db/beatyweb.db")


def add_categories():
    categories = [
        'Мужские', 'Женские', 'Детские',
        'Ножницы', 'Машинка', 'Филировка', 'Текстурирование',
        'Классика', 'Европейский', 'Бразильский', 'Комби', 'SPA',
        'Гигиена', 'Лечение', 'Моделирование', 'Косметика',
        'Гель-лак', 'Акрил', 'Гель', 'Биогель', 'Дипинг',
        'Ламинация', 'Ботокс',
        'Комплекс',
        'Ногтевая', 'Мобильные',
        'Брови', 'Депиляция', 'Косметология'
    ]
    for elem in categories:
        category = Category()
        category.name = elem
        db_sess = db_session.create_session()
        db_sess.add(category)
        db_sess.commit()

if __name__ == '__main__':
    add_categories()
