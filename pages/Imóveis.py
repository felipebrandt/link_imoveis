import streamlit as st
from pandas import DataFrame
from models import Property, Address, Match, URL
from time import sleep
from settings import start_page, get_actual_session, logout_sidebar_page_permute, login_routines
from streamlit_cookies_controller import CookieController
import pandas as pd
controller = CookieController()
from utils_pagination import *


def format_markdown(type_text, text):
    return f''':blue[**{type_text}**]\n
                {text}'''


def get_percent(range_tuple):
    return 1 + range_tuple[0]/100, 1 + range_tuple[1]/100


def main_page():
    if st.session_state.get("authenticated"):
        query_set_properties = Property.get_user_properties(st.session_state["logged_real_state"],
                                     st.session_state["logged_broker"],
                                     st.session_state['main_offset'],
                                     st.session_state["main_limit"])

        st.markdown("""<hr style="height:3px;border:none;color:#333;background-color:#333;" /> """,
                    unsafe_allow_html=True)
        for property_model in query_set_properties:
            col1, col2 = st.columns(2, vertical_alignment="center")

            col1.metric(f"Propriedade: {property_model.property_id}",
                        f"R$: {round(property_model.value, 2):.2f}", border=True)
            if st.button(label='Ver Match',key=property_model.property_id):
                if st.session_state.get('match_lists'):
                    st.session_state.pop('match_lists')
                st.session_state['match_property_id'] = property_model.property_id
                st.switch_page(page='pages/Permuta.py')

            st.markdown("""<hr style="height:3px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)


def main():
    start_page()
    need_login = True

    if 'main_offset' not in st.session_state:
        st.session_state['main_offset'] = 0

    if "main_limit" not in st.session_state:
        st.session_state["main_limit"] = 20

    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if st.session_state["authenticated"]:
        if not st.session_state['actual_session'].is_timeout():
            main_page()
            need_login = False
        else:
            st.session_state['actual_session'].end_session()
            st.session_state["authenticated"] = False
            st.switch_page("main.py")
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
        st.sidebar.warning('Faça o Login Para ter Acesso')
        sleep(st.session_state.time)
        st.switch_page("main.py")


main()
logout_sidebar_page_permute()

