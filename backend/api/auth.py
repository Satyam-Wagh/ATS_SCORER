import streamlit as st
    
st.write("Testing")

##st.session_state.user_id="satyam12345"
#st.session_state.token="48654"
with st.sidebar:
    st.markdown("##navigation")
if st. button("Session"):
    st.write(st.session_state) 
    st.write(print(st.query_params))