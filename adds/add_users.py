from data.users import User
from data import db_session
from requests import get

db_session.global_init("db/beatyweb.db")
data = [{'name': 'Петя',
         'surname': 'Пятиклассный',
         'email': 'petya227@gmail.com',}]

api_key = '4Ql7cqH7DGHdsQVWKN4Y5rmUFZrW6NgGHd9goJJY'
password = get('https://api.api-ninjas.com/v1/passwordgenerator?length=16', headers={'X-Api-Key': api_key}).json()['random_password']
print('Юзер', password)

def insert_users():
    for elem in data:
        user = User()
        user.name = elem['name']
        user.surname = elem['surname']
        user.email = elem['email']
        user.set_password(password)
        db_sess = db_session.create_session()
        db_sess.add(user)
        db_sess.commit()

if __name__ == '__main__':
    insert_users()