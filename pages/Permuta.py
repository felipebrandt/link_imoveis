import streamlit as st
from pandas import DataFrame
from models import Property, Address


def format_markdown(type_text, text):
    return f''':blue[**{type_text}**]\n
                {text}'''


def get_percent(range_tuple):
    return 1 + range_tuple[0]/100, 1 + range_tuple[1]/100


if st.session_state.get('percent'):
    st_dataframe = []
    st.header('Imóveis com Possibilidade de Permuta')
    property_to_permute = st.session_state.property
    similar_property_list = property_to_permute.get_similar_property(st.session_state.percent,
                                                                     st.session_state.property_type,
                                                                     st.session_state.city)
    for similar_property in similar_property_list:
        st_dataframe.append({'id': similar_property.property_id,
                             'address': similar_property.address.get_address_soft_description(),
                             'value': 'R$ ' + str(similar_property.value),
                             'url': similar_property.url.url})

    df = DataFrame(st_dataframe)
    edited_df = st.data_editor(
        df,
        column_config=
        {
            'id': 'ID do Imóvel',
            'address': 'Endereço',
            'value': 'Valor',
            'url': st.column_config.LinkColumn(
                'Link',
                display_text='ir para a pagina'
            )
        },
        disabled=['id','address','value','url'],
        hide_index=True
    )
    if st.button('Limpar Busca'):
        st.session_state.percent = None

elif st.session_state.get('property'):
    property_id = int(st.number_input('ID do Imóvel',
                                      disabled=True,
                                      value=st.session_state.get('property').property_id))
    min_percent, max_percent = get_percent(st.slider('Valor do Imóvel Procurado (% em Relação ao seu Imóvel)',
                                                     min_value=-49,
                                                     max_value=49,
                                                     value=(-10,10)))
    has_property_type, property_type_col = st.columns(2)
    searched_property_type = searched_location = None
    with has_property_type:
        is_property_type = st.checkbox("Buscar por Tipo de Imóvel?", False)

        if is_property_type:
            with property_type_col:
                searched_property_type = st.selectbox("Selecione o Tipo da Propriedade?",
                                                      ("Apartamento", "Casa", "Terreno","Casa Geminada", "Studio",
                                                       "Sobrado","Kitnet", "Flat","Loft"))

    has_property_location, property_location_col = st.columns(2)

    with has_property_location:
        is_property_location = st.checkbox("Buscar Pela Cidade do Imóvel?", False)

        if is_property_location:
            with property_location_col:
                searched_location = st.selectbox("Selecione a Cidade de Interesse para Permuta",
                                                 options=Address.get_all_cities())

    if property_id:
        has_property = Property.get_property_by_id(property_id)
        if has_property:
            property_model = has_property.get()

            if st.button('Buscar'):
                st.session_state.property = property_model
                st.session_state.percent = (min_percent, max_percent)
                st.session_state.property_type = searched_property_type
                st.session_state.city = searched_location

            st.header('Valor: ' + str(property_model.value))
            st.markdown(format_markdown(':red[Tipo de Imóvel]', property_model.url.property_type))
            st.markdown(format_markdown('Descrição', property_model.description))
            area, bedrooms, bathrooms = st.columns(3)

            with area:
                st.markdown(format_markdown('Área', property_model.area))

            with bedrooms:
                st.markdown(format_markdown('Quartos', property_model.bedrooms))

            with bathrooms:
                st.markdown(format_markdown('Banheiros', property_model.bathrooms))

            garage, land_taxes, condominium_fee = st.columns(3)

            with garage:
                st.markdown(format_markdown('Garagem', property_model.garage))

            with land_taxes:
                st.markdown(format_markdown('IPTU', property_model.land_taxes))

            with condominium_fee:
                st.markdown(format_markdown('Taxa de Comdomnínio', property_model.condominium_fee))

        else:
            st.warning('Propriedade Não Encontrada')

# else:
#     property_id = int(st.number_input('ID do Imóvel',
#                                       placeholder='Digite o ID do seu Imóvel',
#                                       step=1))
#     if property_id:
#         has_property = Property.get_property_by_id(property_id)
#         if has_property:
#             property_model = has_property.get()
#             st.switch_page('pages/Permuta.py')

