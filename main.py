import datetime
import time

from scraper import SeleniumOLX
from models import URL, Property
import streamlit as st


def get_url():
    print(f'{datetime.datetime.now()} -- Extracting Datas From Data Files')
    lines_read = 0
    with open('src/domain/url_data.csv') as file:
        file_array = file.readlines()
        total_lines = len(file_array)
        for line in file_array:
            lines_read += 1
            array_line_data = line.split('¬')
            new_url = URL()
            new_url.url = array_line_data[-1]
            new_url.property_type = array_line_data[6]
            new_url.used = False
            new_url.created_at = datetime.datetime.now()
            new_url.save(force_insert=True)
            print(f'{datetime.datetime.now()} -- URL Save Success! --> {(1 - lines_read/total_lines)*100}% to Finish')

    with open('src/domain/url_data.csv', 'w') as file:
        file.close()


def get_url_property():
    for url in URL.select().where(URL.used == False):
        scraper = SeleniumOLX()
        try:
            scraper.search_in_url(url=url)
            time.sleep(2)
            url.used = True
            url.updated_at = datetime.datetime.now()
            url.save()
            print(f'{datetime.datetime.now()} -- URL {url.url_id} Processada com sucesso!')
        except Exception:
            print(f'{datetime.datetime.now()} -- Erro ao processar a URL: {url.url_id}')


def get_property():
    for property_model in Property.select():
        scraper = SeleniumOLX(property_model)
        try:
            if property_model.url:
                scraper.get_image(url=property_model.url.url)
            time.sleep(2)
            print(f'{datetime.datetime.now()} -- Imagem {property_model.property_id} Processada com sucesso!')
        except Exception:
            print(f'{datetime.datetime.now()} -- Erro ao processar a Imagem: {property_model.property_id}')


if __name__ == '__main__':
    st.image("C:\\Users\\pfsb2\\PycharmProjects\\link_imoveis\\linkimovel.png")
    # from src.adapters.address_utils import *
    # get_address_by_cep('123456')

    # get_url()
    # get_property()
    # scraper = SeleniumOLX().get_url_property_sell('sc')

