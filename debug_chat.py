import streamlit as st
from supabase import create_client, Client

try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
    st.success("✅ Connected to Supabase!")
    
    st.write("### Testing Tables:")
    
    try:
        profiles = supabase.table('profiles').select("*").execute()
        st.write(f"✅ Profiles table exists. Records: {len(profiles.data)}")
        st.write(profiles.data)
    except Exception as e:
        st.error(f"❌ Profiles table error: {e}")
    
    try:
        messages = supabase.table('messages').select("*").execute()
        st.write(f"✅ Messages table exists. Records: {len(messages.data)}")
        st.write(messages.data)
    except Exception as e:
        st.error(f"❌ Messages table error: {e}")
    
    st.write("### Test Sending a Message:")
    with st.form("test_message"):
        sender = st.text_input("Sender Email")
        receiver = st.text_input("Receiver Email")
        message = st.text_input("Message")
        
        if st.form_submit_button("Send Test Message"):
            try:
                result = supabase.table('messages').insert({
                    'sender_email': sender,
                    'receiver_email': receiver,
                    'message': message
                }).execute()
                st.success(f"✅ Message sent! {result}")
            except Exception as e:
                st.error(f"❌ Error: {e}")
    
except Exception as e:
    st.error(f"Connection Error: {e}")
