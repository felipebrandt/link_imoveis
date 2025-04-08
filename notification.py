from datetime import datetime

from models import Notification, Message
import streamlit as st


all_notifications = []
if st.session_state.get("logged_broker"):
    all_notifications = Notification.select().where(
        (Notification.user_broker == st.session_state.get("logged_broker")) & (Notification.is_notified == True))
elif st.session_state.get("logged_real_state"):
    all_notifications = Notification.select().where(
        (Notification.user_real_state == st.session_state.get("logged_real_state")) &
        (Notification.is_notified == True))

for notification in all_notifications:
    col1, col2, col3 = st.columns((1, 3, 1), vertical_alignment="center")
    with col1:
        st.write(notification.created_at)

    if notification.match_notification:
        with col2:
            st.write('Sua Propriedade Recebeu Match')
        with col3:
            if st.button('Ver Match', key=notification.notification_id):
                if st.session_state.get('match_lists'):
                    st.session_state.pop('match_lists')
                st.session_state['match_property_id'] = notification.match_notification_id
                st.switch_page(page='pages/Permuta.py')

    if notification.message_notification:
        with col2:
            st.write(notification.message_notification.message)
        with col3:
            if st.button('Responder', key=notification.notification_id):
                message = st.text_area('Escreva Sua Mensagem')
                if message:
                    send_button = True
                else:
                    send_button = False

                if st.button('Enviar', key=str(notification.notification_id) + 'message', disabled=send_button):
                    new_message = Message()
                    new_message.message = message
                    new_message.created_at = datetime.now()
                    new_message.sender_property = notification.message_notification.receiver_property_id
                    new_message.receiver_property = notification.message_notification.sender_property_id
                    new_message.send_massage()
