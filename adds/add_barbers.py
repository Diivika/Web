from data.barbers import Barber
from data import db_session
from requests import get

db_session.global_init("db/beatyweb.db")
data = [{'name': 'Саня',
         'surname': 'Ровный',
         'email': 'coolbarber@gmail.com',
         'address': 'Большой Гнездниковский переулок д.10',
         'city_from': 'Москва'}]

api_key = '4Ql7cqH7DGHdsQVWKN4Y5rmUFZrW6NgGHd9goJJY'
password = get('https://api.api-ninjas.com/v1/passwordgenerator?length=16', headers={'X-Api-Key': api_key}).json()['random_password']
print('Барбер', password)

def insert_barbers():
    for elem in data:
        barber = Barber()
        barber.name = elem['name']
        barber.surname = elem['surname']
        barber.email = elem['email']
        barber.address = elem['address']
        barber.city_from = elem['city_from']
        barber.set_password(password)
        db_sess = db_session.create_session()
        db_sess.add(barber)
        db_sess.commit()

if __name__ == '__main__':
    insert_barbers()
