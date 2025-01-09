import time
from image_utils import base64_to_png
from selenium import webdriver
from selenium.webdriver.common.by import By
import base64
from models import *
import locale

locale.setlocale(locale.LC_TIME, "pt_BR")


class SeleniumOLX:
    components = {'value': (By.CSS_SELECTOR, '#price-box-container > div.ad__sc-q5xder-1.hoJpM > div.olx-d-flex.olx-fd-column > span'),
    'title': (By.CSS_SELECTOR, '#description-title'),
    'img': (By.CSS_SELECTOR, '#gallery > div.ad__sc-xbkr7e-1.inLQmf > button:nth-child(1) > picture > img'),
    'address': (By.CSS_SELECTOR, '#location > div > div.ad__sc-r24bmj-0.gqiLfK > div > div > div'),
    'land_tax': (By.CSS_SELECTOR,
                '#price-box-container > div.ad__sc-q5xder-1.hoJpM > div:nth-child(3) > div > span:nth-child(2)'),
    'condominium_fee': (By.CSS_SELECTOR,
                        '#price-box-container > div.ad__sc-q5xder-1.hoJpM > div:nth-child(4) > div > span:nth-child(2)'),
    'details': (By.CSS_SELECTOR, '#details'),
    'phone': (By.CSS_SELECTOR, '#price-box-container > div:nth-child(2) > div.ad__sc-14mcmsd-0.cAceya > span')}
    data = {}

    def __init__(self, property_model=None):
        self.driver = webdriver.Chrome()
        if property_model:
            self.new_property = property_model
        else:
            self.new_property = Property()
        self.image = None

    def search_in_url(self, url):
        self.driver.get(url.url)
        self.new_property.url = url
        try:
            self.get_property_in_page()
            self.driver.close()
        except Exception as e:
           print(e)

        return True

    def get_property_in_page(self):
        for next_element_name, css in self.components.items():
            try:
                for self.element in self.driver.find_elements(*css):
                    self.get_value(next_element_name, self.element)
            except:
                pass
        if self.new_property.value:
            self.new_property.save_model(self.new_property)
            self.save_image()

    def save_image(self):
        if self.image:
            base64_to_png(self.new_property.property_id, self.image)

    @staticmethod
    def currency_converter(currency_string):
        try:
            currency_value = float(currency_string.removeprefix('R$ ').replace('.', ''))
            return currency_value
        except Exception as e:
            return 0.0

    def get_value(self, element_name, raw_element):
        element = raw_element.text
        if element_name == 'value':
            self.new_property.value = self.currency_converter(element)
            return True
        if element_name == 'img':
            self.image = base64.b64decode(raw_element.screenshot_as_base64.encode())
        if element_name == 'title':
            self.new_property.description = element
            return True
        if element_name == 'address':
            self.new_property.address_description = element
            return True
        if element_name == 'land_tax':
            self.new_property.land_taxes = self.currency_converter(element)
            return True
        if element_name == 'condominium_fee':
            self.new_property.condominium_fee = self.currency_converter(element.split('/')[0])
            return True
        if element_name == 'details':
            self.convert_details(element)
            return True
        return False

    def convert_details(self, detail_element):
        detail_list = detail_element.split('\n')
        for detail_index in range(len(detail_list)):
            if detail_list[detail_index].lower() == 'Área construída'.lower():
                self.new_property.area = detail_list[detail_index + 1]
            if detail_list[detail_index].lower() == 'Quartos'.lower():
                self.new_property.bedrooms = int(self.currency_converter(detail_list[detail_index + 1]))
            if detail_list[detail_index].lower() == 'Banheiros'.lower():
                self.new_property.bathrooms = int(self.currency_converter(detail_list[detail_index + 1]))
            if detail_list[detail_index].lower() == 'Vagas na garagem'.lower():
                self.new_property.garage = int(self.currency_converter(detail_list[detail_index + 1]))

    def get_url_property_sell(self, state):
        for page in range(1, 2):
            url_base = f'https://www.olx.com.br/imoveis/venda/estado-{state}'
            if page > 1:
                next_pages = f'?o={page}'
                url_base = url_base + next_pages
            self.driver.get(url_base)

            for element in self.driver.find_elements(By.CSS_SELECTOR, '#main-content > div.sc-c70b81f6-0.cUgHyT [href]'):
                ad_url = element.get_attribute('href')
                property_type = self.get_property_type(element)
                if ad_url:
                    if not URL.has_url(ad_url):
                        new_url = URL()
                        new_url.url = ad_url
                        new_url.used = False
                        new_url.property_type = property_type
                        new_url.created_at = datetime.now()
                        new_url.save(force_insert=True)
            time.sleep(10)

    def get_property_type(self, element):
        if element.accessible_name.lower().find('apto') != -1:
            return 'Apartamento'
        if element.accessible_name.lower().find('apartamento') != -1:
            return 'Apartamento'
        if element.accessible_name.lower().find('casa') != -1:
            return 'Casa'
        if element.accessible_name.lower().find('terreno') != -1:
            return 'Terreno'
        return 'Imóvel'

    def get_image(self, url):
        self.driver.get(url)
        try:
            css = self.components['img']
            for self.element in self.driver.find_elements(*css):
                self.get_value('img', self.element)
            self.save_image()
            self.driver.close()
        except Exception as e:
            print(e)

        return True
