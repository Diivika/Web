from adds.add_administrator import insert_administrators
from adds.add_barbers import insert_barbers
from adds.add_users import insert_users
from adds.add_categories import add_categories
from adds.add_records import add_records

if __name__ == '__main__':
    insert_administrators()
    insert_barbers()
    insert_users()
    add_categories()
    add_records()