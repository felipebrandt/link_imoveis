import streamlit as st
from settings import get_actual_session, login_routines, sidebar_page, start_page
from streamlit_cookies_controller import CookieController
from models import Match, URL, Property, Notification, Message
import pandas as pd
from datetime import datetime

controller = CookieController()

if st.session_state.get('match_property_id'):
    first_property_id = st.session_state.get('match_property_id')
    property_model = Property.get_property_by_id(first_property_id)

    st.markdown("""<hr style="height:3px;border:none;color:#333;background-color:#333;" /> """,
                unsafe_allow_html=True)
    col1, col2 = st.columns(2, vertical_alignment="center")

    col1.metric(f"Propriedade: {property_model.property_id}",
                f"R$: {int(property_model.value)}", border=True)

    with col2:
        st.page_link(label='Seu Imóvel', page=property_model.url.url)

    st.markdown("""<hr style="height:3px;border:none;color:#333;background-color:#333;" /> """,
                unsafe_allow_html=True)

    match_property, interest_property, other_property_tab = st.tabs(
        ["Match", "Imóveis de Interesse", "Interessados em Permuta"])

    if st.session_state.get('match_lists'):
        match_list, interest_list, other_property_list = st.session_state.get('match_lists').values()

    else:
        match_list, interest_list, other_property_list = Match.get_match_properties(first_property_id)
        st.session_state['match_lists'] = {'match': match_list,
                                           'interests': interest_list,
                                           'other': other_property_list}

    with match_property:
        for match in match_list:
            if first_property_id == match.property_match_b_id:
                region_mean_value = match.property_match_a.address.get_mean_value()
                propriety_mean_value = int(match.property_match_a.value) / \
                                       (int(match.property_match_a.area) if match.property_match_a.area else 100)

                col1, col2, col3, col4 = st.columns((3, 3, 2, 1), vertical_alignment="center")
                col1.metric(f"Propriedade: {match.property_match_a}",
                            f"Score: {int(match.score_ab)}",
                            delta=f"R$: {int(match.property_match_a.value)}", delta_color='off', border=True)
                col2.metric(f"M² na Região R$: {int(region_mean_value)}",
                            f"R$: {int(propriety_mean_value)}/ M²",
                            delta=int(propriety_mean_value - region_mean_value),
                            delta_color='inverse', border=True)
                col3.metric(match.property_match_a.address.city.name, match.property_match_a.address.state.uf,
                            delta=match.property_match_a.address.district.name, delta_color='off', border=True)
                with col4:
                    if st.button(label='Falar', key=match.match_id, type="primary"):
                        new_message = Message()
                        new_message.created_at = datetime.now()
                        new_message.message = f"Olá, me interessei pelo seu Imóvel: {match.property_match_a}"
                        new_message.sender_property = first_property_id
                        new_message.receiver_property = match.property_match_a_id
                        new_message.send_massage()
                        st.toast(f"Mensagem Enviada com Sucesso!")
            else:
                region_mean_value = match.property_match_b.address.get_mean_value()
                propriety_mean_value = int(match.property_match_b.value) / \
                                       (int(match.property_match_b.area) if match.property_match_b.area else 100)

                col1, col2, col3, col4 = st.columns((3, 3, 2, 1), vertical_alignment="center")
                col1.metric(f"Propriedade: {match.property_match_b}",
                            f"Score: {int(match.score_ba)}",
                            delta=f"R$: {int(match.property_match_b.value)}", delta_color='off', border=True)
                col2.metric(f"M² na Região R$: {int(region_mean_value)}",
                            f"R$: {int(propriety_mean_value)}/ M²",
                            delta=int(propriety_mean_value - region_mean_value),
                            delta_color='inverse', border=True)
                col3.metric(match.property_match_b.address.city.name, match.property_match_b.address.state.uf,
                            delta=match.property_match_b.address.district.name, delta_color='off', border=True)
                with col4:
                    if st.button(label='Falar', key=match.match_id, type="primary"):
                        new_message = Message()
                        new_message.created_at = datetime.now()
                        new_message.message = f"Olá, me interessei pelo seu Imóvel: {match.property_match_b}"
                        new_message.sender_property = first_property_id
                        new_message.receiver_property = match.property_match_b_id
                        new_message.send_massage()
                        st.toast(f"Mensagem Enviada com Sucesso!")

    with interest_property:
        for match in interest_list:
            region_mean_value = match.property_match_b.address.get_mean_value()
            propriety_mean_value = int(match.property_match_b.value) / \
                                   (int(match.property_match_b.area) if match.property_match_b.area else 100)

            col1, col2, col3, col4 = st.columns((3, 3, 2, 1), vertical_alignment="center")
            col1.metric(f"Propriedade: {match.property_match_b}",
                        f"Score: {int(match.score_ba)}",
                        delta=f"R$: {int(match.property_match_b.value)}", delta_color='off', border=True)
            col2.metric(f"M² na Região R$: {int(region_mean_value)}",
                        f"R$: {int(propriety_mean_value)}/ M²",
                        delta=int(propriety_mean_value - region_mean_value),
                        delta_color='inverse', border=True)
            col3.metric(match.property_match_b.address.city.name, match.property_match_b.address.state.uf,
                        delta=match.property_match_b.address.district.name, delta_color='off', border=True)
            with col4:
                if st.button(label='Falar', key=match.match_id, type="primary"):
                    new_message = Message()
                    new_message.created_at = datetime.now()
                    new_message.message = f"Olá, me interessei pelo seu Imóvel: {match.property_match_b}"
                    new_message.sender_property = first_property_id
                    new_message.receiver_property = match.property_match_b_id
                    new_message.send_massage()
                    st.toast(f"Mensagem Enviada com Sucesso!")

    with other_property_tab:
        for match in other_property_list:
            region_mean_value = match.property_match_a.address.get_mean_value()
            propriety_mean_value = int(match.property_match_a.value) / \
                                   (int(match.property_match_a.area) if match.property_match_a.area else 100)

            col1, col2, col3, col4 = st.columns((3, 3, 2, 1), vertical_alignment="center")
            col1.metric(f"Propriedade: {match.property_match_a}",
                        f"Score: {int(match.score_ba)}",
                        delta=f"R$: {int(match.property_match_a.value)}", delta_color='off', border=True)
            col2.metric(f"M² na Região R$: {int(region_mean_value)}",
                        f"R$: {int(propriety_mean_value)}/ M²",
                        delta=int(propriety_mean_value - region_mean_value),
                        delta_color='inverse', border=True)
            col3.metric(match.property_match_a.address.city.name, match.property_match_a.address.state.uf,
                        delta=match.property_match_a.address.district.name, delta_color='off', border=True)
            with col4:
                if st.button(label='Falar', key=match.match_id, type="primary"):
                    new_message = Message()
                    new_message.created_at = datetime.now()
                    new_message.message = f"Olá, me interessei pelo seu Imóvel: {match.property_match_a}"
                    new_message.sender_property = first_property_id
                    new_message.receiver_property = match.property_match_a_id
                    new_message.send_massage()
                    st.toast(f"Mensagem Enviada com Sucesso!")


def main():
    need_login = True
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if st.session_state["authenticated"]:
        if not st.session_state['actual_session'].is_timeout():
            need_login = False
        else:
            st.session_state['actual_session'].end_session()
            st.session_state["authenticated"] = False
    else:
        if not st.session_state.get('actual_session'):
            cookie_actual_session_id = controller.get('lk_actual_session_id')
            if cookie_actual_session_id:
                print(cookie_actual_session_id)
                actual_session = get_actual_session(cookie_actual_session_id)
                if actual_session:
                    if actual_session.is_valid:
                        st.session_state['actual_session'] = actual_session
                        login_routines(actual_session)
                        need_login = False


start_page()
main()
sidebar_page()
