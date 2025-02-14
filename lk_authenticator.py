from models import *

def login():
    if usermame and password:
        st.session_state['login'] = True
        st.session_state['username'] = username

        return True
    return False


