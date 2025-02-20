from datetime import datetime, timedelta
from peewee import *
from db_connection import db
from address_utils import get_json_address_by_cep, get_cep_by_olx_address
import streamlit as st
from hashlib import sha256


class BaseModel(Model):
    created_at = DateTimeField()
    updated_at = DateTimeField(null=True)

    class Meta:
        database = db

    def save_model(self, data_model):
        self.save()


class PropertyType(BaseModel):
    property_type_id = AutoField(primary_key=True, help_text='Id do endereço do Imóvel')
    type_name = CharField(max_length=255, help_text='Rua do Imóvel')
    type_description = TextField(null=True)


    @staticmethod
    def get_all_property_type():
        has_property_type = PropertyType.select()
        if has_property_type:
            return has_property_type


class User(BaseModel):
    user_id = AutoField(primary_key=True, help_text='Id do endereço do Imóvel')
    username = CharField(max_length=255, help_text='Rua do Imóvel')
    password = CharField(max_length=255, help_text='Rua do Imóvel')

    @staticmethod
    def check_login(credentials):
        pass

    def set_password(self, password):
        hash_pass = sha256()
        hash_pass.update(password.encode())
        self.password = hash_pass.hexdigest()


class Country(BaseModel):
    country_id = AutoField(primary_key=True, help_text='Id do endereço do Imóvel')
    name = CharField(max_length=255, help_text='Bairro do Imóvel')


class State(BaseModel):
    state_id = AutoField(primary_key=True, help_text='Id do endereço do Imóvel')
    ibge_id = IntegerField(null=True)
    name = CharField(max_length=255, help_text='Bairro do Imóvel')
    uf = CharField(max_length=2)
    country = ForeignKeyField(Country, to_field='country_id')

    @staticmethod
    def create_new_state(state_data):
        new_state = State()
        new_state.ibge_id = state_data[0]
        new_state.name = state_data[1]
        new_state.uf = state_data[2]
        new_state.country = state_data[3]
        new_state.created_at = datetime.now()
        new_state.save()
        return new_state

    @staticmethod
    def get_all_states():
        has_state = State.select()
        if has_state:
            return has_state
        return ()

    @staticmethod
    def set_get_state(uf):
        has_state = State.select().where(State.uf == uf)
        if has_state:
            return has_state.get().state_id
        else:
            return State.create_new_state((0, uf, uf, 1)).state_id


class City(BaseModel):
    city_id = AutoField(primary_key=True, help_text='Id do endereço do Imóvel')
    ibge_id = IntegerField(null= True)
    name = CharField(max_length=255, help_text='Bairro do Imóvel')
    state = ForeignKeyField(State, to_field='state_id')

    @staticmethod
    def create_new_city(city_data):
        new_city = City()
        new_city.ibge_id = city_data[0]
        new_city.name = city_data[1]
        new_city.state = city_data[2]
        new_city.created_at = datetime.now()
        new_city.save()
        return new_city

    @staticmethod
    def set_get_city(name, state):
        has_city = City.select().where((City.state == state) & (City.name == name))
        if has_city:
            return has_city.get().city_id
        else:
            return City.create_new_city((0, name, state)).city_id

    @staticmethod
    def get_all_cities(state):
        has_city = City.select().where(City.state == state)
        if has_city:
            return has_city
        return ()


class District(BaseModel):
    district_id = AutoField(primary_key=True, help_text='Id do endereço do Imóvel')
    ibge_id = BigIntegerField(null=True)
    name = CharField(max_length=255, help_text='Bairro do Imóvel')
    city = ForeignKeyField(City, to_field='city_id')

    @staticmethod
    def get_all_districts(city):
        has_district = District.select().where(District.city == city)
        if has_district:
            return has_district
        return ()

    @staticmethod
    def create_new_district(district_data):
        new_district = District()
        new_district.ibge_id = district_data[0]
        new_district.name = district_data[1]
        new_district.city = district_data[2]
        new_district.created_at = datetime.now()
        new_district.save()
        return new_district

    @staticmethod
    def set_get_city(name, city):
        has_city = District.select().where((District.city == city) & (District.name == name))
        if has_city:
            return has_city.get().district_id
        else:
            return District.create_new_district((0, name, city)).district_id


class Address(BaseModel):
    address_id = AutoField(primary_key=True, help_text='Id do endereço do Imóvel')
    street = CharField(max_length=255, help_text='Rua do Imóvel')
    district = ForeignKeyField(District, to_field='district_id')
    city = ForeignKeyField(City, to_field='city_id')
    state = ForeignKeyField(State, to_field='state_id')
    zipcode = CharField(max_length=255, help_text='ZipCode da Região do Imóvel')
    latitude = FloatField(null=True)
    longitude = FloatField(null=True)

    def save_model(self, cep):
        json_address = get_json_address_by_cep(cep)
        if json_address['status'] == 200:
            self.created_at = datetime.now()
            self.street = json_address.get('street')
            self.state = State.set_get_state(json_address.get('uf'))
            self.city = City.set_get_city(json_address.get('city'), self.state)
            self.district = District.set_get_city(json_address.get('district'), self.city)
            self.zipcode = json_address.get('cep')
            self.latitude = json_address.get('latitude')
            self.longitude = json_address.get('longitude')
            self.save()

    @staticmethod
    def get_address_by_cep(cep):
        return Address.select().where(Address.zipcode == cep)

    def st_form_model_sell(self, key):
        zip_code, street = st.columns(2)
        district, city, state = st.columns(3)
        latitude, longitude = st.columns(2)

        with zip_code:
            zipcode = st.text_input(label='CEP',
                                    placeholder='Digite o CEP do Imóvel',
                                    key=key+'zip_code')

            if not zipcode:
                st.session_state['has_location_data'] = False
            if zipcode != self.zipcode:
                self.zipcode = None
                st.session_state['has_location_data'] = False
            if zipcode and not st.session_state['has_location_data']:
                self.zipcode = zipcode
                has_address = Address.get_address_by_cep(self.zipcode)
                if has_address:
                    self = has_address.get()
                else:
                    json_address = get_json_address_by_cep(self.zipcode)
                    if json_address['status'] == 200:
                        self.created_at = datetime.now()
                        self.street = json_address.get('street')
                        self.state = State.set_get_state(json_address.get('uf'))
                        self.city = City.set_get_city(json_address.get('city'), self.state)
                        self.district = District.set_get_city(json_address.get('district'), self.city)
                        self.zipcode = json_address.get('cep')
                        self.latitude = json_address.get('latitude')
                        self.longitude = json_address.get('longitude')
                        st.session_state['has_location_data'] = True
                        self.save()
                    else:
                        st.warning('CEP NÃO ENCONTRADO')

        with street:
            if self.zipcode:
                st.text_input(label='Rua',
                              disabled=True,
                              value=self.street,
                              key=key+'street')
            else:
                self.street = st.text_input(label='Rua',
                                              placeholder='Digite a Rua do Imóvel',
                                            key=key+'street')

        with district:
            if self.zipcode:
                st.text_input(label='Bairro',
                                                disabled=True,
                                                value=self.district.name,
                              key=key+'district')
            else:
                self.district = st.text_input(label='Bairro',
                                              placeholder='Digite a Bairro do Imóvel',
                              key=key+'district')

        with city:
            if self.zipcode:
                st.text_input(label='Cidade',
                                            disabled=True,
                                            value=self.city.name,
                              key=key+'city')
            else:
                self.city = st.text_input(label='Cidade',
                                              placeholder='Digite a Cidade do Imóvel',
                                          key=key+'city')

        with state:
            if self.zipcode:
                st.text_input(label='Estado',
                                             disabled=True,
                                             value=self.state.name,
                              key=key+'state')
            else:
                self.state = st.text_input(label='Estado',
                                              placeholder='Digite a Estado do Imóvel',
                              key=key+'state')

        with latitude:
            if self.latitude:
                float(st.text_input(label='Latitude',
                                                disabled=True,
                                                value=self.latitude,
                                    key=key+'latitude'))
            else:
                self.latitude = st.text_input(label='Latitude',
                                                placeholder='Campo Automático',
                                                disabled=True,
                                              key=key+'latitude')

        with longitude:
            if self.longitude:
                float(st.text_input(label='Longitude',
                                                 disabled=True,
                                                 value=self.longitude,
                                    key=key+'longitude'))
            else:
                self.longitude = st.text_input(label='Longitude',
                                                 placeholder='Campo Automático',
                                                 disabled=True,
                                    key=key+'longitude')


    @staticmethod
    def get_all_cities():
        has_address = Address.select(Address.city)
        set_cities = set()
        for address in has_address:
            set_cities.add(address.city)
        return tuple(set_cities)

    def get_address_description(self, number, complement):
        return f'{self.street} {number},{complement} {"" if not self.district else self.district.name}, ' \
               f'{ "" if not self.city else self.city.name} - {"" if not self.state else self.state.name} - {self.zipcode}'

    def get_address_soft_description(self):
        return f'{self.district}, {self.city} - {self.zipcode}'

    @staticmethod
    def get_property_city(city):
        has_address = Address.select(Address.address_id).where(Address.city == city)
        address_ids = []
        for address in has_address:
            address_ids.append(address.address_id)

        return address_ids


class RealState(User):
    name = CharField(max_length=255, help_text='Rua do Imóvel')
    creci = CharField(max_length=255, help_text='Rua do Imóvel')
    address = ForeignKeyField(Address, to_field='address_id', null=True)

    @staticmethod
    def check_login(credentials):
        has_user = RealState.select().where(RealState.username == credentials['username'])
        if has_user:
            user = has_user.get()
            hash_pass = sha256()
            hash_pass.update(credentials['password'].encode())
            if user.password == hash_pass.hexdigest():
                return user
        return None

    @staticmethod
    def get_all_real_states():
        has_real_state = RealState.select()
        if has_real_state:
            return has_real_state
        return ()


class Broker(User):
    real_state = ForeignKeyField(RealState, to_field='user_id', null=True)
    name = CharField(max_length=255, help_text='Rua do Imóvel')
    creci = CharField(max_length=255, help_text='Rua do Imóvel')
    address = ForeignKeyField(Address, to_field='address_id', null=True)

    @staticmethod
    def check_login(credentials):
        has_user = RealState.select().where((Broker.username == credentials['username']) &
                                            (Broker.real_state == credentials['real_state']))
        if has_user:
            user = has_user.get()
            hash_pass = sha256()
            hash_pass.update(credentials['password'].encode())
            if user.password == hash_pass.hexdigest():
                return user
        return None


class URL(BaseModel):
    url_id = AutoField(primary_key=True, help_text='Id da URL')
    property_type = ForeignKeyField(PropertyType, to_field='property_type_id')
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

    # @staticmethod
    # def get_property_type(property_type):
    #     has_url = URL.select(URL.url_id).where(URL.property_type == property_type)
    #     url_ids = []
    #     for url in has_url:
    #         url_ids.append(url.url_id)
    #
    #     return url_ids


class PropertyLocation(BaseModel):
    property_location_id = AutoField(primary_key=True, help_text='Id do Imovel')
    district = ForeignKeyField(District, to_field='district_id', null=True)
    city = ForeignKeyField(City, to_field='city_id', null=True)
    state = ForeignKeyField(State, to_field='state_id', null=True)


class Property(BaseModel):
    property_id = AutoField(primary_key=True, help_text='Id do Imovel')
    value = FloatField(null=True)
    address_description = TextField(null=True)
    address = ForeignKeyField(Address, to_field='address_id', null=True)
    property_type = ForeignKeyField(PropertyType, to_field='property_type_id')
    area = CharField(null=True)
    bedrooms = IntegerField(null=True)
    bathrooms = IntegerField(null=True)
    garage = IntegerField(null=True)
    land_taxes = FloatField(null=True)
    condominium_fee = FloatField(null=True)
    description = TextField(null=True)
    real_state = ForeignKeyField(RealState, to_field='user_id', null=True)
    broker = ForeignKeyField(Broker, to_field='user_id', null=True)
    is_valid = BooleanField(default=True)
    for_exchange = BooleanField(default=True)
    url = ForeignKeyField(URL, to_field='url_id', null=True)

    def save_model(self, data_model):
        self.created_at = datetime.now()
        self.is_valid = True
        if self.address_description:
            cep = get_cep_by_olx_address(self.address_description)
            has_address = Address.get_address_by_cep(cep)
            if not has_address:
                self.address = Address()
                self.address.save_model(cep)
            else:
                self.address = has_address
        self.save()

    def st_form_model_search(self):
        pass

    def get_similar_property(self, percent_range, property_type, city):
        value_min, value_max = self.get_searched_values(percent_range)
        query = Property.select().where((Property.value.between(value_min, value_max)) &
                                        (Property.url.is_null(False)) &
                                        (Property.property_id != self.property_id))

        if property_type:
            query = query.filter((Property.property_type in property_type))
        if city:
            address_ids = Address.get_property_city(city)
            query = query.filter((Property.address << address_ids))

        return query.limit(10)

    def get_searched_values(self, percent_range):
        return percent_range[0] * self.value, percent_range[1] * self.value

    @staticmethod
    def get_property_by_id(property_id):
        return Property.select().where(Property.property_id == property_id)


class MatchRequest(BaseModel):
    match_request_id = AutoField(primary_key=True, help_text='Id do Imovel')
    property = ForeignKeyField(Property, to_field='property_id')
    property_value_min = IntegerField(null=True)
    property_value_max = IntegerField(null=True)
    pv_priority = IntegerField(null=True)
    property_location = ForeignKeyField(PropertyLocation, to_field='property_location_id', null=True)
    pl_priority = IntegerField(null=True)
    property_area_min = IntegerField(null=True)
    property_area_max = IntegerField(null=True)
    pa_priority = IntegerField(null=True)
    property_type = ForeignKeyField(PropertyType, to_field='property_type_id', null=True)
    pt_priority = IntegerField(null=True)
    is_valid = BooleanField()


class Match(BaseModel):
    match_id = AutoField(primary_key=True, help_text='Id do Imovel')
    match_request = ForeignKeyField(MatchRequest, to_field='match_request_id')
    first_property_match = ForeignKeyField(Property, to_field='property_id')
    second_property_match = ForeignKeyField(Property, to_field='property_id')
    match_type = IntegerField()
    score = FloatField()


class Session(BaseModel):
    session_id = AutoField(primary_key=True, help_text='Id do Imovel')
    session_uuid = CharField(max_length=255, index=True)
    logged_user_real_state = ForeignKeyField(RealState, to_field='user_id', null=True)
    logged_user_broker = ForeignKeyField(Broker, to_field='user_id', null=True)
    valid_datetime = DateTimeField()
    is_valid = BooleanField()

    def is_timeout(self):
        elapsed_time = datetime.now() - self.valid_datetime
        if elapsed_time > timedelta(minutes=30):
            return True
        return False

    def timeout(self):
        self.is_valid = False
        self.updated_at = datetime.now()

    def update_session(self):
        self.is_valid = True
        self.valid_datetime = datetime.now()

    def end_session(self):
        self.valid_datetime = datetime.now() - timedelta(minutes=30)
        self.timeout()
        self.save()


    @staticmethod
    def get_status_session(session_uuid):
        return Session.select().where(Session.session_uuid == session_uuid)


class JobList(BaseModel):
    job_list_id = AutoField(primary_key=True, help_text='Id do Imovel')
    session = ForeignKeyField(Session, to_field='session_id')
    match_request = ForeignKeyField(MatchRequest, to_field='match_request_id')
    job_status = IntegerField()

    #job_status: 0 = Waiting, 1 = Processing 2 = Fail


if __name__ == '__main__':
    db.create_tables([PropertyType, Country, State, City, District, Address, URL, Property, RealState,
                      Broker, Match, PropertyLocation, MatchRequest, Session, JobList])
    # property_model = Property.select().where(Property.property_id == 1).get()
    # property_model.get_similar_property((-0.1, 0.2), 'Casa', 'Florianópolis')