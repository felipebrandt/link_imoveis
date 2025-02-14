from datetime import datetime
import time
from settings import *
import streamlit as st

from models import RealState, Broker


def start_session():
    new_session = Session()
    new_session.session_uuid = st.session_state["uuid"]
    new_session.logged_user_real_state = st.session_state["logged_real_state"]
    new_session.logged_user_broker = st.session_state["logged_broker"]
    new_session.valid_datetime = new_session.created_at = datetime.now()
    new_session.is_valid = True
    new_session.save()
    return new_session


def login_page():
    tab_real_state, tab_broker = st.tabs(["Imobiliária", "Corretor"])

    with tab_real_state:
        st.title("Login")
        username = st.text_input("Usuário", key='rs_username')
        password = st.text_input("Senha", type="password", key='rs_password')
        credentials = {'username': username,
                       'password': password}
        col_login, col_register = st.columns(2)
        with col_login:
            if st.button("Entrar", key='rs_login'):
                real_state = RealState.check_login(credentials)
                if real_state:
                    st.session_state["logged_real_state"] = real_state
                    st.session_state['actual_session'] = start_session()
                    login_routines(st.session_state['actual_session'])
                    st.rerun()
                else:
                    st.error("Imobiliária ou senha Invalidos!")

        with col_register:
            if st.button('Registrar', key='rs_register'):
                st.switch_page('pages/Cadastro.py')

    with tab_broker:
        st.title("Login")
        username = st.text_input("Usuário", key='b_username')
        password = st.text_input("Senha", type="password", key='b_password')
        is_real_state_broker = st.checkbox('Corretor de Imobiliária?')
        if is_real_state_broker:
            real_state = st.selectbox('Nome da Imobiliária', options=st.session_state.get('all_real_states'))
        else:
            real_state = None
        col_login, col_register = st.columns(2)
        credentials = {'username': username,
                       'password': password,
                       'real_state': real_state}
        with col_login:
            if st.button("Entrar", key='b_login'):
                broker = Broker.check_login(credentials)
                if broker:
                    st.session_state["logged_broker"] = broker
                    st.session_state['actual_session'] = start_session()
                    login_routines(st.session_state['actual_session'])
                    st.switch_page('main.py')
                else:
                    st.error("Usuário ou senha incorretos!")

        with col_register:
            if st.button('Registrar', key='b_register'):
                st.switch_page('pages/Cadastro.py')


def main():
    need_login = True
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if st.session_state["authenticated"]:
        if not st.session_state['actual_session'].is_timeout():
            need_login = False
        else:
            st.session_state['actual_session'].timeout()
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
    if need_login:
        login_page()


if __name__ == "__main__":
    start_page()
    st.image("linkimovel.png")
    main()
    logout_sidebar_page()

    nova_notificacao = st.text_input("Digite uma notificação:")

    if st.button("Adicionar Notificação"):
        if nova_notificacao:
            st.session_state.notificacoes.append(nova_notificacao)
            st.toast(f"Notificação adicionada: {nova_notificacao}")
            time.sleep(1)
            st.rerun()


