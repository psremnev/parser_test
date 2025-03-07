import sqlite3


class DataBase:

    def __init__(self):
        self.connection = sqlite3.connect('database.db')
        self.cursor = self.connection.cursor()
        self.__create_tables()

    def __del__(self):
        # Сохраняем изменения и закрываем соединение
        self.connection.commit()
        self.connection.close()

    def __create_tables(self):
        # Создаем таблицу PersonalInfo
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS PersonalInfo (
        id INTEGER PRIMARY KEY,
        person_id TEXT NOT NULL,
        email TEXT NOT NULL,
        name TEXT NOT NULL,
        surname TEXT NOT NULL,
        city TEXT NOT NULL
        )
        ''')

        # Создаем таблицу WishlistInfo
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Wishlist (
        id INTEGER PRIMARY KEY,
        product_id TEXT NOT NULL,
        name TEXT NOT NULL,
        price TEXT NOT NULL,
        rating REAL,
        stores_number INTEGER,
        reviews_number INTEGER
        )
        ''')

        # Создаем таблицу WishComments, комментарии по товару
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS WishComments (
        id INTEGER PRIMARY KEY,
        product_id TEXT NOT NULL,
        name TEXT NOT NULL,
        comment TEXT NOT NULL
        )
        ''')

    def add_person_info(self, person_info):
        # Добавляем персональную информацию о персоне PersonalInfo
        self.cursor.execute(
            'INSERT INTO PersonalInfo (person_id, email, name, surname, city) VALUES (?, ?, ?, ?, ?)',
            (person_info['id'], person_info['email'], person_info['name'],
             person_info['surname'], person_info['city']))

    def add_wishlist(self, wishlist):
        # Добавляем товары из избранных WishlistInfo
        for product in wishlist:
            self.cursor.execute(
                'INSERT INTO Wishlist (product_id, name, price, rating, stores_number, reviews_number) VALUES (?, ?, ?, ?, ?, ?)',
                (product['id'], product['name'], product['price'], product['rating'],
                 product['stores_number'], product['reviews_number']))

    def add_wish_product_comments(self, wishlist):
        # Добавляем комментарии по товару WishComments

        for product in wishlist:
            for review in product['reviews']:
                self.cursor.execute('INSERT INTO WishComments (product_id, name, comment) VALUES (?, ?, ?)',
                                    (product['id'], review['name'], review['comment']))
