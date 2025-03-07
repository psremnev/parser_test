from math import trunc
from lxml import html
from Modules.BaseParser import BaseParser


class SiriustParser(BaseParser):
    """ Парсер для сайта https://siriust.ru """

    link = 'https://siriust.ru'
    is_auth = False

    def __get_product_html_element(self, res):
        """ Получить html элемент карточки продукта """

        return self.get_html_element(res).xpath('//div[@class="ty-product-block ty-product-detail"]')[0]

    def __check_is_auth(self):
        """ Проверка что авторизован """

        if not self.is_auth:
            raise Exception('Для получения данных авторизуйтесь. Для этого нужно вызвать метод auth')

    def auth(self):
        """ Авторизация """

        login = input("Введите логин: ")
        password = input("Введите пароль: ")

        res = self.session.post(
            url=self.link,
            data={
                'return_url': 'index.php?dispatch=auth.login_form',
                'redirect_url': 'index.php?dispatch=auth.login_form',
                'user_login': login,
                'password': password,
                'dispatch[auth.login]': True
            },
            headers=self.headers
        )

        error_elem = self.get_html_element(res).xpath('//div[contains(@class,"alert-error")]/text()')
        if error_elem:
            error_text = error_elem[2].strip()
            raise Exception(f'Ошибка авторизации: {error_text}')

        self.is_auth = True

    def get_person_info(self):
        """ Получить информацию о персоне """

        self.__check_is_auth()
        res = self.session.get(f'{self.link}/profiles-update', headers=self.headers)
        page = self.get_html_element(res)

        return {
            'id': self.__get_person_id(page),
            'email': page.xpath('//input[@id="email"]')[0].value,
            'name': page.xpath('//input[@id="elm_15"]')[0].value,
            'surname': page.xpath('//input[@id="elm_17"]')[0].value,
            'city': page.xpath('//input[@id="elm_23"]')[0].value
        }

    def get_wish_products(self):
        """ Получить информацию о избранных продуктах """

        self.__check_is_auth()
        res = self.session.get(f'{self.link}/wishlist', headers=self.headers)
        page = self.get_html_element(res)

        # берем элемент рейтинг для каждого избранного элемента
        pages_rating = page.xpath('//span[contains(@class, "ty-stars")]/a')

        # получаем страницы каждого товара из ссылки названия
        wishlist_pages = [self.__get_product_html_element(self.session.get(x.attrib.get("href"))) for x in
                          page.xpath('//a[@class="product-title"]')]

        # получаем страницы каждого товара из ссылки рейтинга для того чтобы извлечь отзывы
        wishlist_pages_discussion = [
            self.__get_product_html_element(self.session.get(a.attrib.get("href")))
            for a in pages_rating]

        return [{
            'id': f'{self.get_product_name(product)}_{self.get_product_price(product)}',
            'name': self.get_product_name(product),
            'price': self.get_product_price(product),
            'rating': self.get_product_rating(product),
            'stores_number': self.get_product_stores_number(product),
            'reviews_number': self.get_product_reviews_number(wishlist_pages_discussion[index]),
            'reviews': self.get_product_reviews(wishlist_pages_discussion[index])
        } for index, product in enumerate(wishlist_pages)]

    @staticmethod
    def get_html_element(res):
        """ Получить html элемент из строки запроса """

        return html.fromstring(res.text)

    @staticmethod
    def __get_person_id(page):
        """ Получить id персоны """

        name = page.xpath('//input[@id="elm_15"]')[0].value
        surname = page.xpath('//input[@id="elm_17"]')[0].value
        return f'{name}_{surname}'

    @staticmethod
    def get_product_name(product):
        """ Получить имя продукта """

        return product.xpath('//h1[@class="ty-product-block-title"]/bdi/text()')[0]

    @staticmethod
    def get_product_price(product):
        """ Получить цену продукта """

        return product.xpath('//span[contains(@id,"sec_discounted_price")]/text()')[0].replace(u'\xa0', ' ')

    @staticmethod
    def get_product_rating(product):
        """ Получить рейтинг продукта """

        half_stars = product.xpath(
            'count(//div[@class="ty-product-block__rating"]//i[@class="ty-stars__icon ty-icon-star-half"])')
        one_stars = product.xpath(
            'count(//div[@class="ty-product-block__rating"]//i[@class="ty-stars__icon ty-icon-star"])')
        return half_stars * 0.5 + one_stars

    @staticmethod
    def get_product_reviews(product):
        """ Получить комментарии продукта """

        return [{
            'name': review.xpath('//span[@class="ty-discussion-post__author"]/text()')[0],
            'comment': review.xpath('//div[@class="ty-discussion-post__message"]/text()')[0]
        } for review in product.xpath('//div[contains(@class, "ty-discussion-post__content")]')]

    @staticmethod
    def get_product_reviews_number(product):
        """ Получить количество комментариев продукта """

        return trunc(product.xpath('count(//div[contains(@class, "ty-discussion-post__content")])'))

    @staticmethod
    def get_product_stores_number(product):
        """ Получить количество магазинов где товар есть в наличии """

        return trunc(product.xpath(
            'count(//div[@class="ty-product-feature__value"]/img[not(@src="images/addons/mws_feature_tab/zero_cross.png")])'))
