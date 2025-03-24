import streamlit as st
from models import Property, URL, RealState, Broker, Address, MatchRequest, PropertyLocation, JobList
from datetime import datetime
from settings import start_page, get_city_id_dict, get_district_id_dict
from time import sleep
from streamlit_cookies_controller import CookieController
from settings import get_actual_session, sidebar_page, login_routines

controller = CookieController()


def get_percent(range_tuple):
    return 1 + range_tuple[0]/100, 1 + range_tuple[1]/100


def main_page():
    if st.session_state.get("authenticated"):
        is_possible_to_save = True
        property_location = None
        register_selected = st.selectbox('Selecione o Tipo de Cadastro', options=("Imóveis", "Corretor"))

        if 'last' not in st.session_state:
            st.session_state['last'] = register_selected

        if register_selected != st.session_state['last']:
            st.session_state['last'] = register_selected
            st.session_state['has_location_data'] = False

        last_register = register_selected

        if register_selected == "Imóveis":
            st.header("Dados do Imóvel")
            if 'new_property' not in st.session_state:
                st.session_state['new_property'] = new_property = Property()
                new_url = URL()
                new_url.url = 'http://127.0.0.1'
                st.session_state['new_property'].url = new_url
                new_url.used = True

            property_type, property_value, property_area = st.columns(3)
            bedrooms, bathrooms, garage = st.columns(3)
            land_taxes, condominium_fee = st.columns(2)

            with property_type:
                property_type_name = st.selectbox("Selecione o Tipo da Propriedade?",
                                                  options=st.session_state["property_types_dict"].keys())
                if property_type_name:
                    st.session_state['new_property'].property_type = st.session_state["property_types_dict"][property_type_name]

            with property_value:
                st.session_state['new_property'].value = st.number_input(label='Valor',
                                             placeholder='Digite o Valor do Imóvel',
                                             step=1000,
                                             min_value=0)
            with property_area:
                st.session_state['new_property'].area = st.number_input(label='Área (m²)',
                                            placeholder='Digite a Área do Imóvel (m²)',
                                            step=5,
                                            min_value=0)
            with bedrooms:
                st.session_state['new_property'].bedrooms = st.number_input(label='Quartos',
                                                placeholder='Digite a Quantidade de Quartos)',
                                                step=1,
                                                min_value=0)

            with bathrooms:
                st.session_state['new_property'].bathrooms = st.number_input(label='Banheiros',
                                                 placeholder='Digite a Quantidade de Banheiros',
                                                 step=1,
                                                 min_value=0)

            with garage:
                st.session_state['new_property'].garage = st.number_input(label='Garagem',
                                              placeholder='Digite a Quantidade de Vagas',
                                              step=1,
                                              min_value=0)
            with land_taxes:
                st.session_state['new_property'].land_taxes = st.number_input(label='IPTU',
                                                  placeholder='Digite o Valor do IPTU do Imóvel',
                                                  step=100,
                                                  min_value=0)
            with condominium_fee:
                st.session_state['new_property'].condominium_fee = st.number_input(label='Taxa de Condomínio',
                                                       placeholder='Digite o Valor do Condomínio do Imóvel',
                                                       step=100,
                                                       min_value=0)

            st.session_state['new_property'].description = st.text_area(label='Descrição',
                                            placeholder='Descreva seu Imóvel',
                                            max_chars=1500)

            st.header('Endereço do Imóvel')
            if not st.session_state['new_property'].address:
                st.session_state['new_property'].address = Address()
            st.session_state['new_property'].address.st_form_model_sell('property')
            broker = st.session_state.get('logged_broker')
            if broker:
                st.session_state['new_property'].broker = broker.user_id

            real_state = st.session_state.get('logged_real_state')
            if real_state:
                st.session_state['new_property'].real_state = real_state.user_id

            number = st.text_input(label='Numero',
                                   placeholder='Digite o Numero do Imóvel')

            complement = st.text_input(label='Complemento',
                                       placeholder='Digite o Complemento do Imóvel')

            st.session_state['new_property'].for_exchange = st.checkbox('Aceita Permuta?')
            if st.session_state['new_property'].for_exchange:
                new_match_request = MatchRequest()
                if 'priority_matc_request' not in st.session_state:
                    st.session_state['priority_matc_request'] = {}

                ck_property_value = st.checkbox('Valor do Imóvel', value=True)
                if ck_property_value:
                    st.session_state['priority_matc_request']['Valor do Imóvel'] = 1
                    new_match_request.property_value_min, \
                    new_match_request.property_value_max = st.slider('Valor do Imóvel Procurado (% em Relação ao seu Imóvel)',
                                  min_value=-49,
                                  max_value=49,
                                  value=(-10, 10))
                elif st.session_state['priority_matc_request'].get('Valor do Imóvel'):

                    st.session_state['priority_matc_request'].pop('Valor do Imóvel')

                ck_property_type = st.checkbox('Tipo de Imóvel')
                if ck_property_type:
                    st.session_state['priority_matc_request']['Tipo de Imóvel'] = 1
                    choose_property_type = st.selectbox('Escolha o Tipo do Imóvel:',
                                                        options=st.session_state['property_types_dict'].keys(),
                                                        index=None,
                                                        placeholder='Escolha o Tipo...')
                    if choose_property_type:
                        new_match_request.property_type = st.session_state['property_types_dict'][choose_property_type]
                elif st.session_state['priority_matc_request'].get('Tipo de Imóvel'):
                    st.session_state['priority_matc_request'].pop('Tipo de Imóvel')

                ck_property_area = st.checkbox('Área Construída do Imóvel')
                if ck_property_area:
                    st.session_state['priority_matc_request']['Área Construída'] = 1
                    new_match_request.property_area_min = st.number_input(
                        'Mínimo de Área Construída do Imóvel Procurado')
                    new_match_request.property_area_max = st.number_input(
                        'Máximo de Área Construída do Imóvel Procurado')

                elif st.session_state['priority_matc_request'].get('Área Construída'):
                    st.session_state['priority_matc_request'].pop('Área Construída')


                ck_property_location = st.checkbox('Localização do Imóvel')

                if ck_property_location:
                    property_location = PropertyLocation()
                    st.session_state['priority_matc_request']['Localização'] = 1
                    location_dict = st.session_state.get('location_dict')
                    name_state = st.selectbox('Escolha o Estado do Imóvel que Deseja:',
                                              options=location_dict.keys(),
                                              index=None,
                                              placeholder='Escolha um Estado...')
                    if name_state:
                        property_location.state = location_dict[name_state]['state_id']
                        if not location_dict[name_state]['cities']:
                            get_city_id_dict(property_location.state, name_state)
                            location_dict = st.session_state.get('location_dict')
                        city_dict = location_dict[name_state]['cities']
                        name_city = st.selectbox('Escolha a Cidade do Imóvel que Deseja:',
                                                 options=city_dict.keys(),
                                                 index=None,
                                                 placeholder='Escolha uma Cidade...')
                        if name_city:
                            property_location.city = city_dict[name_city]['city_id']
                            if not location_dict[name_state]['cities'][name_city]['districts']:
                                get_district_id_dict(property_location.city, name_city, name_state)
                            district_dict = city_dict[name_city]['districts']
                            name_district = st.selectbox('Escolha o Bairro do Imóvel que Deseja:',
                                                                      options=district_dict.keys(),
                                                                      index=None,
                                                                      placeholder='Escolha um Bairro...')
                            if name_district:
                                property_location.district = district_dict[name_district]
                elif st.session_state['priority_matc_request'].get('Localização'):
                    st.session_state['priority_matc_request'].pop('Localização')

                priority_list = st.multiselect('Prioridade de Busca', options=st.session_state['priority_matc_request'])

            if not st.session_state.get('submit'):
                st.session_state.disable = False
            else:
                st.session_state.disable = True
            submit_button = st.button(label='Cadastrar', key='submit', disabled=st.session_state.disable)
            if submit_button:
                if st.session_state['new_property'].for_exchange:
                    if len(st.session_state['priority_matc_request']) > 0:
                        if len(priority_list) == len(st.session_state['priority_matc_request']):
                            priority_value = 1
                            for priority in priority_list:
                                if priority == 'Valor do Imóvel':
                                    new_match_request.pv_priority = priority_value
                                if priority == 'Tipo de Imóvel':
                                    new_match_request.pt_priority = priority_value
                                if priority == 'Área Construída':
                                    new_match_request.pa_priority = priority_value
                                if priority == 'Localização':
                                    new_match_request.pl_priority = priority_value
                                priority_value += 1

                            if property_location:
                                property_location.created_at = datetime.now()
                                property_location.save()
                                new_match_request.property_location = property_location.property_location_id

                            new_match_request.created_at = datetime.now()
                            new_job = JobList()
                            new_job.created_at = datetime.now()
                            new_job.session = st.session_state['actual_session'].session_id
                            new_job.job_status = 0


                        else:
                            st.warning('Selecione Todas as Prioridades')
                            is_possible_to_save = False
                    else:
                        st.warning('Selecione Menos Uma Opção')
                        is_possible_to_save = False

                if is_possible_to_save:
                    st.session_state['new_property'].address.created_at = \
                        st.session_state['new_property'].url.created_at = \
                        st.session_state['new_property'].created_at = datetime.now()
                    st.session_state['new_property'].url.save()
                    st.session_state['new_property'].address.save()

                    if st.session_state['new_property'].address:
                        st.session_state['new_property'].address_description = \
                            st.session_state['new_property'].address.get_address_description(number, complement)

                    st.session_state['new_property'].save()
                    if st.session_state['new_property'].for_exchange:
                        new_match_request.property = st.session_state['new_property'].property_id
                        new_match_request.is_valid = True
                        new_match_request.save()
                        new_job.match_request = new_match_request.match_request_id
                        new_job.save()
                    st.success('Imóvel Cadastrado com Sucesso')
                    st.session_state.disable = True

                    #verificar se ainda necessita desta rotina
                    st.session_state.property = st.session_state['new_property']
                    st.session_state.pop('new_property')

        else:
            broker_register()

    else:

        register_selected = st.selectbox('Selecione o Tipo de Cadastro', options=("Imobiliária", "Corretor"))
        if 'last' not in st.session_state:
            st.session_state['last'] = register_selected

        if register_selected != st.session_state['last']:
            st.session_state['last'] = register_selected
            st.session_state['has_location_data'] = False

        last_register = register_selected
        if register_selected == "Imobiliária":

            if not st.session_state['has_location_data']:
                st.session_state['real_state_address'] = Address()

            st.header('Registrar-se')
            col_username, col_name = st.columns(2)

            with col_username:
                username = st.text_input('Nome de Usuário')

            with col_name:
                name = st.text_input("Nome da Imobiliária")

            col_password, col_confirm = st.columns(2)

            with col_password:
                password = st.text_input("Senha", type="password")

            with col_confirm:
                confirm_password = st.text_input("Confirme a Senha", type="password")

            creci = st.text_input("CRECI")

            st.session_state['real_state_address'].st_form_model_sell('real_state')
            if st.button('Salvar'):
                real_state = RealState()
                real_state.created_at = datetime.now()
                real_state.username = username
                real_state.set_password(password)
                real_state.name = name
                real_state.creci = creci
                real_state.address = st.session_state['real_state_address']
                real_state.save()
                st.session_state['has_location_data'] = False
                st.session_state['all_real_states'] = None
                st.switch_page("main.py")

        else:
            broker_register()


def main():
    start_page()
    need_login = True
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if st.session_state["authenticated"]:
        if not st.session_state['actual_session'].is_timeout():
            main_page()
            need_login = False
        else:
            st.session_state['actual_session'].end_session()
            st.session_state["authenticated"] = False
    else:
        if not st.session_state.get('actual_session'):
            cookie_actual_session_id = controller.get('lk_actual_session_id')
            if cookie_actual_session_id:
                actual_session = get_actual_session(cookie_actual_session_id)
                if actual_session:
                    if actual_session.is_valid:
                        st.session_state['actual_session'] = actual_session
                        login_routines(actual_session)
                        need_login = False
                        main_page()
    if need_login:
        main_page()


def broker_register():
    if not st.session_state['has_location_data']:
        st.session_state['broker_address'] = Address()

    st.header('Registrar-se')

    is_real_state = st.checkbox("Corretor de Imobiliária?")
    if is_real_state:
        real_state = st.selectbox('Qual sua Imobiliária?', options=st.session_state.get("all_real_states"))
        if real_state:
            real_state_broker = st.session_state.get("all_real_states")[real_state].user_id
    else:
        real_state_broker = None
    col_username, col_name = st.columns(2)

    with col_username:
        username = st.text_input('Nome de Usuário', key='b_username')

    with col_name:
        name = st.text_input("Nome do Corretor", key='b_bane')

    col_password, col_confirm = st.columns(2)

    with col_password:
        password = st.text_input("Senha", type="password", key='b_password')

    with col_confirm:
        confirm_password = st.text_input("Confirme a Senha", type="password", key='b_confirm')

    creci = st.text_input("CRECI", key='b_creci')

    st.session_state['broker_address'] = st.session_state['broker_address'].st_form_model_sell('broker')
    if st.button('Salvar', key='b_save'):
        st.session_state['broker_address'].save()
        broker = Broker()
        broker.created_at = datetime.now()
        broker.username = username
        broker.set_password(password)
        broker.name = name
        broker.creci = creci
        broker.real_state = real_state_broker
        broker.address = st.session_state['broker_address']
        broker.save()
        st.session_state['has_location_data'] = False
        st.switch_page("main.py")

main()
sidebar_page()

