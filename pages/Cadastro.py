import streamlit as st
from src.domain.models import Property, URL
from datetime import datetime


property_model, real_estate, broker = st.tabs(["Imóveis", "Imobiliária", "Corretor"])
with property_model:
    st.header("Dados do Imóvel")
    new_property = Property()
    new_url = URL()
    new_url.url = 'local/sem_link'
    new_property.url = new_url
    new_url.used = True
    new_property.st_form_model_sell()
    if not st.session_state.get('submit'):
        st.session_state.disable = False
    else:
        st.session_state.disable = True
    submit_button = st.button(label='Cadastrar', key='submit', disabled=st.session_state.disable)
    if submit_button:
        new_property.address.created_at = new_url.created_at = new_property.created_at = datetime.now()
        new_url.save()
        new_property.address.save()
        new_property.save()
        st.success('Imóvel Cadastrado com Sucesso')
        st.session_state.disable = True
        st.session_state.property = new_property
        st.switch_page('pages/Permuta.py')

with real_estate:
    st.header("Em Construção")

with broker:
    st.header("Em Construção")

