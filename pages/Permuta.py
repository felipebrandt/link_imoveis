import streamlit as st
from pandas import DataFrame
from models import Property, Address
from time import sleep
from settings import start_page, get_actual_session, logout_sidebar_page_permute, login_routines
from streamlit_cookies_controller import CookieController

controller = CookieController()


def format_markdown(type_text, text):
    return f''':blue[**{type_text}**]\n
                {text}'''


def get_percent(range_tuple):
    return 1 + range_tuple[0]/100, 1 + range_tuple[1]/100


def main_page():
    if st.session_state.get("authenticated"):
        pass


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
            st.session_state['actual_session'].timeout()
            st.session_state["authenticated"] = False
            st.switch_page("main.py")
    else:
        if not st.session_state.get('actual_session'):
            cookie_actual_session_id = controller.get('lk_actual_session_id')
            if cookie_actual_session_id:
                actual_session = get_actual_session(cookie_actual_session_id)
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

