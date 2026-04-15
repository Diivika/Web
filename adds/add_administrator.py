from data.administrators import Administrator
from data import db_session
from requests import get

db_session.global_init("db/beatyweb.db")
data = [{'name': 'Ridley',
         'surname': 'Scott',
         'email': 'administrator@gmail.com',}]

api_key = '4Ql7cqH7DGHdsQVWKN4Y5rmUFZrW6NgGHd9goJJY'
password = get('https://api.api-ninjas.com/v1/passwordgenerator?length=16', headers={'X-Api-Key': api_key}).json()['random_password']
print(password)

def insert_administrators():
    for elem in data:
        administrator = Administrator()
        administrator.name = elem['name']
        administrator.surname = elem['surname']
        administrator.email = elem['email']
        administrator.set_password(password)
        db_sess = db_session.create_session()
        db_sess.add(administrator)
        db_sess.commit()

if __name__ == '__main__':
    insert_administrators()
