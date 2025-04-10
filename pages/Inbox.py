from datetime import datetime
from settings import logout_sidebar_page_permute
from models import Notification, Message
import streamlit as st


MAX_CHAR = 255

received_message_model = '''<div style="background-color:#f1f1f1; padding:10px 15px; border-radius:12px; max-width:75%; 
margin-right:auto; margin-bottom:5px; font-family:Arial; color:#333;">
    <div style="font-weight:bold; font-size:13px; margin-bottom:5px;">{name}</div>
    <div style="font-size:14px;">{received_message}</div>
    <div style="text-align:right; font-size:11px; color:#999;">{date}</div>
</div>
'''

sent_message_model = '''
<div style="background-color:#d1e9ff; padding:10px 15px; border-radius:12px; max-width:75%; 
margin-left:auto; margin-bottom:5px; font-family:Arial; color:#330066;">
    <div style="font-weight:bold; font-size:13px; margin-bottom:5px;">Você</div>
    <div style="font-size:14px;">{sent_message}</div>
    <div style="text-align:right; font-size:11px; color:#666;">{date}</div>
</div>


'''


def print_message(actual_message: Message, expander):
    if actual_message.sender_property.is_logged_user(st.session_state.get('logged_real_state'),
                                                       st.session_state.get('logged_broker')):
        expander.markdown(sent_message_model.format(sent_message=actual_message.message,
                                              name=actual_message.sender_property.get_user_name(),
                                              date=actual_message.created_at.strftime("%m/%d/%Y, %H:%M")),
                    unsafe_allow_html=True)
    else:
        expander.markdown(received_message_model.format(received_message=actual_message.message,
                                                  name=actual_message.sender_property.get_user_name(),
                                                  date=actual_message.created_at.strftime("%m/%d/%Y, %H:%M")),
                    unsafe_allow_html=True)


def get_all_messages(actual_message: Message):
    expander = st.expander('Histórico de Mensagens')
    all_messages = Message.select().where((Message.root_message == actual_message.root_message) &
                                          (Message.root_message.is_null(False))).order_by(
        Message.created_at)
    if actual_message.root_message:
        print_message(actual_message.root_message, expander)
    else:
        print_message(actual_message, expander)
    for to_print_message in all_messages:
        print_message(to_print_message, expander)


def get_all_chat():
    chat_expander = st.expander('Negociações em Andamento:')
    all_chat = Message.select().distinct(Message.root_message).where(Message.root_message.is_null(False))
    for chat in all_chat:
        col1, col2 = chat_expander.columns((3,1))
        col1.write(f"Mensagens do Match Do Imóvel {chat.sender_property_id} e {chat.receiver_property_id}")
        with col2:
            if st.button('Ver', key=chat.message_id, type="primary"):
                st.session_state['message_notify'] = Notification.select().where(Notification.message_notification ==
                                                                                 chat.message_id).get()
                st.rerun()


def main():
    if st.session_state['message_notify']:
        notification = st.session_state['message_notify']

        get_all_messages(st.session_state['message_notify'].message_notification)

        message = st.text_area('Escreva Sua Mensagem', max_chars=MAX_CHAR)

        if st.button('Enviar', key=str(notification.notification_id) + 'send_message', type="primary"):
            if message:
                new_message = Message()
                new_message.message = message
                if notification.message_notification.root_message:
                    new_message.root_message = notification.message_notification.root_message_id
                else:
                    new_message.root_message = notification.message_notification_id
                new_message.created_at = datetime.now()
                new_message.sender_property = notification.message_notification.receiver_property_id
                new_message.receiver_property = notification.message_notification.sender_property_id
                new_message.send_massage()
                notification.is_notified = True
                notification.save()
                st.session_state['message_notify'] = None
                st.rerun()
            else:
                st.warning('Digite uma mensagem antes de enviar!')
        if st.button('Cancelar', key=str(notification.notification_id) + 'cancel_message'):
            st.session_state['message_notify'] = None
            st.rerun()

    else:
        get_all_chat()
        all_notifications = []
        if st.session_state.get("logged_broker"):
            all_notifications = Notification.select().where(
                (Notification.user_broker == st.session_state.get("logged_broker")) & (Notification.is_notified == False))
        elif st.session_state.get("logged_real_state"):
            all_notifications = Notification.select().where(
                (Notification.user_real_state == st.session_state.get("logged_real_state")) &
                (Notification.is_notified == False))

        notification_expander = st.expander('Notificações')
        for notification in all_notifications:

            col1, col2, col3 = notification_expander.columns((1, 3, 1), vertical_alignment="center")
            col1.write(notification.created_at.strftime("%m/%d/%Y, %H:%M"))

            if notification.match_notification:
                with col2:
                    st.write('Sua Propriedade Recebeu Match')
                with col3:
                    if st.button('Ver Match', key=notification.notification_id, type="primary"):
                        if st.session_state.get('match_lists'):
                            st.session_state.pop('match_lists')
                        st.session_state['match_property_id'] = notification.match_notification_id
                        st.switch_page(page='pages/Permuta.py')

            if notification.message_notification:
                with col2:
                    st.write(notification.message_notification.message)
                with col3:
                    if st.button('Responder', key=notification.notification_id, type="primary"):
                        st.session_state['message_notify'] = notification
                        st.rerun()


main()
logout_sidebar_page_permute()

