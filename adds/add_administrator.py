from data.users import User
from data import db_session
from requests import get

db_session.global_init("db/beatyweb.db")
data = [{'name': 'Ridley',
         'surname': 'Scott',
         'email': 'administrator@gmail.com',}]

api_key = '4Ql7cqH7DGHdsQVWKN4Y5rmUFZrW6NgGHd9goJJY'
password = get('https://api.api-ninjas.com/v1/passwordgenerator?length=16', headers={'X-Api-Key': api_key}).json()['random_password']

def insert_administrators():
    for elem in data:
        administrator = User()
        administrator.name = elem['name']
        administrator.surname = elem['surname']
        administrator.email = elem['email']
        administrator.set_password(password)
        administrator.is_admin = True
        db_sess = db_session.create_session()
        db_sess.add(administrator)
        db_sess.commit()
        print('Admin', password)

if __name__ == '__main__':
    insert_administrators()

