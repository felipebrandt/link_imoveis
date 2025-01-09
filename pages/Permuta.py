import streamlit as st
from pandas import DataFrame
from src.domain.models import Property


def format_markdown(type_text, text):
    return f''':blue[**{type_text}**]\n
                {text}'''


if st.session_state.get('property'):
    st_dataframe = []
    st.header('Imóveis com Possibilidade de Permuta')
    property_to_permute = st.session_state.property
    similar_property_list = property_to_permute.get_similar_property(st.session_state.property.value *
                                                                     st.session_state.percent)
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
        st.session_state.property = None

else:
    property_id = int(st.number_input('ID do Imóvel',
                                      placeholder='Digite o ID do seu Imóvel',
                                      step=1))
    percent = 1 + st.slider('Valor do Imóvel Procurado (% em Relação ao seu Imóvel)',
                        min_value=-49,
                        max_value=49,
                        value=0)/100
    if property_id:
        has_property = Property.get_property_by_id(property_id)
        if has_property:
            property_model = has_property.get()

            if st.button('Buscar'):
                st.session_state.property = property_model
                st.session_state.percent = percent

            st.header('Valor: ' + str(property_model.value))
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


