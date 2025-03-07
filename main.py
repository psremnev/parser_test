from Modules.Database import DataBase
from Modules.SiriustParser import SiriustParser

parser = SiriustParser()

# Авторизуемся
parser.auth()

# Получаем персональную информацию
person_info = parser.get_person_info()
print(person_info)

# Получаем информацию по избранным товарам
wishlist = parser.get_wish_products()
print(wishlist)

# Создаем базу данных и добавляем данные
database = DataBase()
database.add_person_info(person_info)
database.add_wishlist(wishlist)
database.add_wish_product_comments(wishlist)