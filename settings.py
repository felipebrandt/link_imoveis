from models import PropertyType, Session, RealState, State, City, District
from uuid import getnode
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
    all_state = State.get_all_states()
    location_dict = {}
    for state in all_state:
        location_dict[state.name] = {'state_id': state.state_id, 'cities': get_city_id_dict(state)}
    return location_dict


def get_city_id_dict(state):
    all_cities = City.get_all_cities(state)
    city_id_dict = {}
    for city in all_cities:
        city_id_dict[city.name] = {'city_id': city.city_id, 'districts': get_district_id_dict(city)}
    return city_id_dict


def get_district_id_dict(city):
    all_district = District.get_all_districts(city)
    district_id_dict = {}
    for district in all_district:
        district_id_dict[district.name] = district.district_id
    return district_id_dict


def get_uuid():
    return getnode()


def get_actual_session(session_id):
    has_session = Session.get_status_session(session_id)
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
        controller.set('lk_actual_session_id', st.session_state['actual_session'].session_id)

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
        st.session_state.notificacoes = []

    if "uuid" not in st.session_state:
        st.session_state["uuid"] = get_uuid()


def logout_sidebar_page():
    if st.session_state["authenticated"]:
        st.sidebar.header("Notificações 📢")
        if st.session_state.notificacoes:
            st.sidebar.markdown(f'🔔:red-background[[{len(st.session_state.notificacoes)}](page/Permuta.py)]')

        user = st.session_state.get('logged_broker')
        if not user:
            user = st.session_state.get('logged_real_state')

        st.sidebar.title(user.name)
        if st.sidebar.button("Sair"):
            st.session_state["authenticated"] = False
            st.session_state["actual_session"].end_session()
            st.switch_page("main.py")


def logout_sidebar_page_permute():
    if st.session_state["authenticated"]:
        st.session_state.notificacoes = []
        user = st.session_state.get('logged_broker')
        if not user:
            user = st.session_state.get('logged_real_state')

        st.sidebar.title(user.name)
        if st.sidebar.button("Sair"):
            st.session_state["authenticated"] = False
            st.session_state["actual_session"].end_session()
            st.switch_page("main.py")


def login_routines(session):
    controller.set('lk_actual_session_id', session.session_id)
    st.session_state["authenticated"] = True
    st.session_state["logged_real_state"] = session.logged_user_real_state
    st.session_state["logged_broker"] = session.logged_user_broker
    print(session.logged_user_real_state)