from data import db_session
from data.category import Category

db_session.global_init("db/beatyweb.db")


def add_categories():
    categories = [
        'Мужская стрижка',
        'Женская стрижка',
        'Детская стрижка',
        'Стрижка ножницами',
        'Стрижка машинкой',
        'Стрижка с филировкой',
        'Текстурирование волос',
        'Классическая стрижка',
        'Европейская стрижка',
        'Бразильская стрижка',
        'Комбинированная стрижка',
    ]
    for elem in categories:
        category = Category()
        category.name = elem
        db_sess = db_session.create_session()
        db_sess.add(category)
        db_sess.commit()

if __name__ == '__main__':
    add_categories()
