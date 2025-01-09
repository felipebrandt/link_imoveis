from datetime import datetime
from peewee import *
from db_connection import db
from address_utils import get_json_address_by_cep, get_cep_by_olx_address
import streamlit as st


class BaseModel(Model):
    created_at = DateTimeField()
    updated_at = DateTimeField(null=True)

    class Meta:
        database = db

    def save_model(self, data_model):
        self.save()


class Address(BaseModel):
    address_id = AutoField(primary_key=True, help_text='Id do endereço do Imóvel')
    street = CharField(max_length=255, help_text='Rua do Imóvel')
    district = CharField(max_length=255, help_text='Bairro do Imóvel')
    city = CharField(max_length=255, help_text='Cidade do Imóvel')
    state = CharField(max_length=255, help_text='Unidade Federativa do Imóvel')
    zipcode = CharField(max_length=255, help_text='ZipCode da Região do Imóvel')
    latitude = FloatField(null=True)
    longitude = FloatField(null=True)

    def save_model(self, cep):
        json_address = get_json_address_by_cep(cep)
        if json_address['status'] == 200:
            self.created_at = datetime.now()
            self.street = json_address.get('street')
            self.city = json_address.get('city')
            self.state = json_address.get('uf')
            self.district = json_address.get('district')
            self.zipcode = json_address.get('cep')
            self.latitude = json_address.get('latitude')
            self.longitude = json_address.get('longitude')
            self.save()

    @staticmethod
    def get_address_by_cep(cep):
        return Address.select().where(Address.zipcode == cep)

    def st_form_model_sell(self):
        zip_code, street = st.columns(2)
        district, city, state = st.columns(3)
        latitude, longitude = st.columns(2)

        with zip_code:
            self.zipcode = st.text_input(label='CEP',
                                 placeholder='Digite o CEP do Imóvel')
            if self.zipcode:
                has_address = Address.get_address_by_cep(self.zipcode)
                if has_address:
                    self = has_address.get()
                else:
                    json_address = get_json_address_by_cep(self.zipcode)
                    if json_address['status'] == 200:
                        self.created_at = datetime.now()
                        self.street = json_address.get('street')
                        self.city = json_address.get('city')
                        self.state = json_address.get('uf')
                        self.district = json_address.get('district')
                        self.zipcode = json_address.get('cep')
                        self.latitude = json_address.get('latitude')
                        self.longitude = json_address.get('longitude')
                    else:
                        st.warning('CEP NÃO ENCONTRADO')

        with street:
            if self.zipcode:
                st.text_input(label='Rua',
                                              disabled=True,
                                              value=self.street)
            else:
                self.street = st.text_input(label='Rua',
                                              placeholder='Digite a Rua do Imóvel')

        with district:
            if self.zipcode:
                st.text_input(label='Bairro',
                                                disabled=True,
                                                value=self.district)
            else:
                self.district = st.text_input(label='Bairro',
                                              placeholder='Digite a Bairro do Imóvel')

        with city:
            if self.zipcode:
                st.text_input(label='Cidade',
                                            disabled=True,
                                            value=self.city)
            else:
                self.city = st.text_input(label='Cidade',
                                              placeholder='Digite a Cidade do Imóvel')

        with state:
            if self.zipcode:
                st.text_input(label='Estado',
                                             disabled=True,
                                             value=self.state)
            else:
                self.state = st.text_input(label='Estado',
                                              placeholder='Digite a Estado do Imóvel')

        with latitude:
            if self.latitude:
                float(st.text_input(label='Latitude',
                                                disabled=True,
                                                value=self.latitude))
            else:
                self.latitude = st.text_input(label='Latitude',
                                                placeholder='Campo Automático',
                                                disabled=True)

        with longitude:
            if self.longitude:
                float(st.text_input(label='Longitude',
                                                 disabled=True,
                                                 value=self.longitude))
            else:
                self.longitude = st.text_input(label='Longitude',
                                                 placeholder='Campo Automático',
                                                 disabled=True)

        if self.zipcode:
            return self

    def get_address_description(self, number, complement):
        return f'{self.street} {number},{complement} {self.district}, {self.city} - {self.state} - {self.zipcode}'

    def get_address_soft_description(self):
        return f'{self.district}, {self.city} - {self.zipcode}'


class URL(BaseModel):
    url_id = AutoField(primary_key=True, help_text='Id da URL')
    property_type = CharField(null=True)
    url = TextField()
    used = BooleanField()

    @staticmethod
    def has_url(ad_url):
        url = URL.select().where(URL.url == ad_url)
        if url:
            return True
        return False

    def validate_url(self):
        pass

    def get_image_url(self):
        pass


class Property(BaseModel):
    property_id = AutoField(primary_key=True, help_text='Id do Imovel')
    value = FloatField(null=True)
    address_description = TextField(null=True)
    address = ForeignKeyField(Address, to_field='address_id', null=True)
    area = CharField(null=True)
    bedrooms = IntegerField(null=True)
    bathrooms = IntegerField(null=True)
    garage = IntegerField(null=True)
    land_taxes = FloatField(null=True)
    condominium_fee = FloatField(null=True)
    description = TextField(null=True)
    url = ForeignKeyField(URL, to_field='url_id', null=True)

    def save_model(self, data_model):
        self.created_at = datetime.now()
        if self.address_description:
            cep = get_cep_by_olx_address(self.address_description)
            has_address = Address.get_address_by_cep(cep)
            if not has_address:
                self.address = Address()
                self.address.save_model(cep)
            else:
                self.address = has_address
        self.save()

    def st_form_model_sell(self):
        property_value, property_area = st.columns(2)
        bedrooms, bathrooms, garage = st.columns(3)
        land_taxes, condominium_fee = st.columns(2)

        with property_value:
            self.value = st.number_input(label='Valor',
                                         placeholder='Digite o Valor do Imóvel',
                                         step=1000,
                                         min_value=0)
        with property_area:
            self.area = st.number_input(label='Área (m²)',
                                        placeholder='Digite a Área do Imóvel (m²)',
                                        step=5,
                                        min_value=0)
        with bedrooms:
            self.bedrooms = st.number_input(label='Quartos',
                                        placeholder='Digite a Quantidade de Quartos)',
                                        step=1,
                                        min_value=0)

        with bathrooms:
            self.bathrooms = st.number_input(label='Banheiros',
                                        placeholder='Digite a Quantidade de Banheiros',
                                        step=1,
                                        min_value=0)

        with garage:
            self.garage = st.number_input(label='Garagem',
                                        placeholder='Digite a Quantidade de Vagas',
                                        step=1,
                                        min_value=0)
        with land_taxes:
            self.land_taxes = st.number_input(label='IPTU',
                                        placeholder='Digite o Valor do IPTU do Imóvel',
                                        step=100,
                                        min_value=0)
        with condominium_fee:
            self.condominium_fee = st.number_input(label='Taxa de Condomínio',
                                        placeholder='Digite o Valor do Condomínio do Imóvel',
                                        step=100,
                                        min_value=0)

        self.description = st.text_area(label='Descrição',
                                        placeholder='Descreva seu Imóvel',
                                        max_chars=1500)

        st.header('Endereço do Imóvel')
        self.address = Address()
        self.address = self.address.st_form_model_sell()

        number = st.text_input(label='Numero',
                               placeholder='Digite o Numero do Imóvel')

        complement = st.text_input(label='Complemento',
                               placeholder='Digite o Complemento do Imóvel')
        if self.address:
            self.address_description = self.address.get_address_description(number, complement)

    def st_form_model_search(self):
        pass

    def get_similar_property(self, value):
        if value > self.value:
            return Property.select().where((Property.value.between(self.value, value)) &
                                            (Property.url.is_null(False)) &
                                            (Property.property_id != self.property_id)).limit(10)
        return Property.select().where((Property.value.between(value, self.value)) &
                                       (Property.url.is_null(False)) &
                                       (Property.property_id != self.property_id)).limit(10)

    @staticmethod
    def get_property_by_id(property_id):
        return Property.select().where(Property.property_id == property_id)

if __name__ == '__main__':
    db.create_tables([Address, URL, Property])
