import streamlit as st
from settings import get_actual_session, login_routines, sidebar_page, start_page
from streamlit_cookies_controller import CookieController
from models import Match, URL, Property
import pandas as pd
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

    match_list, interest_list, other_property_list = Match.get_match_properties(first_property_id)

    with match_property:
        other_property_id = []
        property_value = []
        other_property_value = []
        property_list = []
        other_property_url_list = []
        score = []
        for match in match_list:
            print(match.match_id)
            if first_property_id == match.property_match_b_id:
                other_property_id.append(match.property_match_a)
                other_property_url_list.append(match.property_match_a.url.url)
                other_property_value.append(match.property_match_a.value)
                score.append(match.score_ab)
            else:
                other_property_id.append(match.property_match_b)
                other_property_url_list.append(match.property_match_b.url.url)
                other_property_value.append(match.property_match_b.value)
                score.append(match.score_ba)
        df = pd.DataFrame(
            {
                "id": other_property_id,
                "other_property_value": other_property_value,
                "url": other_property_url_list,
                "score": score,

            }
        )
        st.dataframe(
            df,
            column_config={
                "other_property_id": st.column_config.NumberColumn("Imóvel de Interesse"),
                "other_property_value": st.column_config.NumberColumn("Valor do Imóvel de Interesse"),
                "score": st.column_config.NumberColumn(
                    "Score do Imóvel Permutável",
                    help="Score do Imóvel",
                    format="%d 📈​",
                ),
                "url": st.column_config.LinkColumn("Imóvel Permutável",display_text="Veja o Outro Imóvel")
            },
            hide_index=True,
        )

    with interest_property:
        other_property_id = []
        property_value = []
        other_property_value = []
        property_list = []
        other_property_url_list = []
        score = []
        for match in interest_list:
            other_property_id.append(match.property_match_b)
            other_property_url_list.append(match.property_match_b.url.url)
            other_property_value.append(match.property_match_b.value)
            score.append(match.score_ba)
        df = pd.DataFrame(
            {
                "id": other_property_id,
                "other_property_value": other_property_value,
                "url": other_property_url_list,
                "score": score,

            }
        )
        st.dataframe(
            df,
            column_config={
                "other_property_id": st.column_config.NumberColumn("Imóvel de Interesse"),
                "other_property_value": st.column_config.NumberColumn("Valor do Imóvel de Interesse"),
                "score": st.column_config.NumberColumn(
                    "Score do Imóvel Permutável",
                    help="Score do Imóvel",
                    format="%d 📈​",
                ),
                "url": st.column_config.LinkColumn("Imóvel Permutável", display_text="Veja o Outro Imóvel")
            },
            hide_index=True,
        )

    with other_property_tab:
        other_property_id = []
        property_value = []
        other_property_value = []
        property_list = []
        other_property_url_list = []
        score = []
        for match in other_property_list:
            other_property_id.append(match.property_match_a)
            other_property_url_list.append(match.property_match_a.url.url)
            other_property_value.append(match.property_match_a.value)
            score.append(match.score_ba)
        df = pd.DataFrame(
            {
                "id": other_property_id,
                "other_property_value": other_property_value,
                "url": other_property_url_list,
                "score": score,

            }
        )
        st.dataframe(
            df,
            column_config={
                "other_property_id": st.column_config.NumberColumn("Imóvel de Interesse"),
                "other_property_value": st.column_config.NumberColumn("Valor do Imóvel de Interesse"),
                "score": st.column_config.NumberColumn(
                    "Score do Imóvel Permutável",
                    help="Score do Imóvel",
                    format="%d 📈​",
                ),
                "url": st.column_config.LinkColumn("Imóvel Permutável",display_text="Veja o Outro Imóvel")
            },
            hide_index=True,
        )


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
