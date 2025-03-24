from models import PropertyType, Session, RealState, State, City, District, Match, Property
from uuid import uuid4
from streamlit_cookies_controller import CookieController
import streamlit as st

controller = CookieController()


def get_property_type_id_dict():
    all_property_type = PropertyType.get_all_property_type()
    property_type_id_dict = {}
    for property_type in all_property_type:
        property_type_id_dict[property_type.type_name] = property_type.property_type_id
    return property_type_id_dict


def get_location_dict():
    all_location = State.select()
    location_dict = {}
    for data_location in all_location:
        location_dict[data_location.name] = {'state_id': data_location.state_id,
                                             'cities': {}}
    return location_dict


def get_city_id_dict(state, name_state):
    all_cities = City.get_all_cities(state)
    city_id_dict = {}
    for city in all_cities:
        city_id_dict[city.name] = {'city_id': city.city_id, 'districts': {}}
    st.session_state['location_dict'][name_state]['cities'] = city_id_dict


def get_district_id_dict(city, name_city, name_state):
    all_district = District.get_all_districts(city)
    district_id_dict = {}
    for district in all_district:
        district_id_dict[district.name] = district.district_id
    st.session_state['location_dict'][name_state]['cities'][name_city]['districts'] = district_id_dict


def get_uuid():
    return int(uuid4())


def get_actual_session(session_uuid):
    has_session = Session.get_status_session(session_uuid)
    if has_session:
        return has_session.get()
    return None


def get_all_real_states():
    real_state_id_dict = {}
    real_states = RealState.get_all_real_states()
    for real_state in real_states:
        real_state_id_dict[real_state.name] = real_state
    return real_state_id_dict


def start_page():
    st.session_state["time"] = 2
    if 'actual_session' not in st.session_state:
        st.session_state['actual_session'] = None
    elif st.session_state['actual_session']:
        controller.set('lk_actual_session_id', st.session_state['actual_session'].session_uuid)

    if "logged_real_state" not in st.session_state:
        st.session_state["logged_real_state"] = None

    if "logged_broker" not in st.session_state:
        st.session_state["logged_broker"] = None

    if 'all_real_states' not in st.session_state:
        st.session_state['all_real_states'] = get_all_real_states()

    if 'has_location_data' not in st.session_state:
        st.session_state['has_location_data'] = False

    if 'property_types_dict' not in st.session_state:
        st.session_state['property_types_dict'] = get_property_type_id_dict()

    if 'location_dict' not in st.session_state:
        st.session_state['location_dict'] = get_location_dict()

    if "notificacoes" not in st.session_state:
        st.session_state.notificacoes = 0
        get_notifications()

    if "uuid" not in st.session_state:
        if controller.get('lk_actual_session_id'):
            st.session_state["uuid"] = controller.get('lk_actual_session_id')
        else:
            st.session_state["uuid"] = get_uuid()


def sidebar_page():
    if st.session_state["authenticated"]:
        st.sidebar.header("Notificações 📢")
        get_notifications()
        if st.sidebar.button(f'🔔:{st.session_state.notificacoes}', type="primary"):
            st.switch_page('pages/Imóveis.py')

        user = st.session_state.get('logged_broker')
        if not user:
            user = st.session_state.get('logged_real_state')

        st.sidebar.title(user.name)
        if st.sidebar.button("Sair"):
            st.session_state["actual_session"].end_session()
            st.session_state["authenticated"] = False
            st.switch_page("main.py")


def logout_sidebar_page_permute():
    if st.session_state["authenticated"]:
        user = st.session_state.get('logged_broker')
        if not user:
            user = st.session_state.get('logged_real_state')

        st.sidebar.title(user.name)
        if st.sidebar.button("Sair"):
            st.session_state["actual_session"].end_session()
            st.session_state["authenticated"] = False
            st.switch_page("main.py")


def login_routines(session):
    controller.set('lk_actual_session_id', str(session.session_uuid))
    st.session_state["authenticated"] = True
    st.session_state["logged_real_state"] = session.logged_user_real_state
    st.session_state["logged_broker"] = session.logged_user_broker
    st.session_state['match_property_id'] = None


def get_notifications():
    if st.session_state.get("logged_broker"):
        st.session_state.notificacoes = Match.select(Property.property_id).join(
            Property, on=(Property.property_id == Match.property_match_a)).where(
            (Match.notified == False) & (Property.broker == st.session_state.get("logged_broker"))).distinct().count()

    if st.session_state.get("logged_real_state"):
        st.session_state.notificacoes = Match.select(Property.property_id).join(
            Property, on=(Property.property_id == Match.property_match_a)).where(
            (Match.notified == False) & (Property.real_state == st.session_state.get("logged_real_state"))).distinct().count()

get_location_dict()