
import streamlit as st
from supabase import create_client, Client
from datetime import datetime
import pandas as pd
import os

# ML Imports
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- Page Config ---
st.set_page_config(layout="wide", page_title="CO:LAB - Project Partner Finder")

# --- Supabase Connection ---
try:
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error("Could not connect to Supabase. Please check your .streamlit/secrets.toml file.")
    st.stop()


# --- "PRO" CSS - FINAL VERSION ---
def inject_custom_css():
    st.markdown("""
        <style>
            /* --- Import "Tech" Font --- */
            @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&display=swap');

            /* --- Base & Font --- */
            * {
                font-family: 'Space+Grotesk', sans-serif;
            }

            /* --- Animated Gradient Background --- */
            @keyframes gradientBG {
                0% {background-position: 0% 50%;}
                50% {background-position: 100% 50%;}
                100% {background-position: 0% 50%;}
            }
            .stApp {
                background: linear-gradient(-45deg, #0a0a10, #0f2027, #203a43, #2c5364);
                background-size: 400% 400%;
                animation: gradientBG 15s ease infinite;
                color: #FFFFFF;
            }

            /* --- Titles --- */
            h1, h2, h3 {
                color: #FFFFFF;
                text-shadow: 0 0 10px rgba(0, 240, 255, 0.3);
            }
            h1 {
                font-weight: 700;
            }
            h3 {
                color: #00F0FF; /* Neon Blue Accent */
                display: flex; /* Aligns header text with icon */
                align-items: center;
            }

            /* --- Glassmorphism Containers --- */
            .glass-container {
                background: rgba(26, 26, 38, 0.7);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 16px;
                padding: 2em;
                margin-bottom: 2em;
                box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
            }

            /* --- Tab Navigation (UI FIX) --- */
            .stTabs {
                border: none;
            }
            .stTabs [data-baseweb="tab-list"] {
                gap: 12px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
            .stTabs [data-baseweb="tab"] {
                height: 50px;
                background: transparent;
                border: none;
                border-bottom: 3px solid transparent;
                color: #E0E0E0;
                font-weight: 500;
                transition: all 0.3s ease;
            }
            .stTabs [data-baseweb="tab"]:hover {
                background: rgba(40, 40, 55, 0.8);
                color: #FFFFFF;
            }
            .stTabs [aria-selected="true"] {
                background: transparent;
                border-bottom: 3px solid #00F0FF;
                color: #00F0FF;
                font-weight: 700;
            }
            .stTabs [data-baseweb="tab-panel"] {
                background: transparent;
                padding-top: 2em;
            }
            
            /* --- Animated Icons (now used in headers) --- */
            lord-icon {
                width: 40px;
                height: 40px;
                margin-right: 10px;
                filter: drop-shadow(0 0 8px rgba(0, 240, 255, 0.7));
            }
            
            /* --- Form Inputs (Text, Select) --- */
            .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
                background: rgba(0, 0, 0, 0.3);
                border: 1px solid #00F0FF;
                box-shadow: 0 0 10px rgba(0, 240, 255, 0.3);
                color: #FFFFFF !important;
                border-radius: 8px;
                font-weight: 500;
            }
            .stTextInput label, .stTextArea label, .stSelectbox label {
                color: #E0E0E0 !important;
                font-weight: 500;
            }
            ::placeholder {
                color: #707080 !important;
                opacity: 1;
            }

            /* --- Buttons --- */
            .stButton > button {
                background: linear-gradient(90deg, #00F0FF, #00A3FF);
                color: #0a0a10;
                border: none;
                border-radius: 8px;
                font-weight: 700;
                font-size: 1.1em;
                padding: 0.7em 1.5em;
                transition: all 0.3s ease;
                box-shadow: 0 0 15px rgba(0, 240, 255, 0.5);
            }
            .stButton > button:hover {
                box-shadow: 0 0 25px rgba(0, 240, 255, 1);
                transform: scale(1.03);
            }

            /* --- Match Card Styling --- */
            .match-card {
                background: rgba(26, 26, 38, 0.7);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 1.5em;
                margin-bottom: 1.5em;
            }
            .match-card .score {
                font-size: 2em;
                font-weight: 700;
                color: #00F0FF;
                text-align: right;
                text-shadow: 0 0 10px #00F0FF;
            }
            
            /* --- Profile Mini-Card (Replaces DataFrame) --- */
            .profile-mini-card {
                background: rgba(26, 26, 38, 0.7);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 1.5em;
                margin-bottom: 1em;
                transition: all 0.3s ease;
            }
            .profile-mini-card:hover {
                border-color: #00F0FF;
                box-shadow: 0 0 15px rgba(0, 240, 255, 0.3);
                transform: translateY(-3px);
            }
            .profile-mini-card h4 {
                color: #00F0FF;
                margin: 0 0 0.5em 0;
            }
            .profile-mini-card p {
                color: #E0E0E0;
                font-size: 0.9em;
                margin: 0.2em 0;
            }
            
            /* --- Chat Message Styling --- */
            div[data-testid="chat-message-container"] {
                background: rgba(0, 0, 0, 0.2);
                border-radius: 10px;
                padding: 0.5em 1em;
                margin-bottom: 0.5em;
            }
        </style>
    """, unsafe_allow_html=True)


# --- DATA FUNCTIONS (Supabase) ---

@st.cache_data(ttl=300) 
def get_all_profiles():
    try:
        response = supabase.table('profiles').select("*").execute()
        return response.data
    except Exception as e:
        st.error(f"Error fetching profiles: {e}")
        return []

def upsert_profile(email, name, subject, skills, goals):
    try:
        data, count = supabase.table('profiles').upsert({
            'email': email,
            'name': name,
            'class': subject,
            'skills': skills,
            'goals': goals
        }).execute()
        st.cache_data.clear() 
        return data
    except Exception as e:
        st.error(f"Error saving profile: {e}")
        return None

@st.cache_data(ttl=5) 
def get_chat_history(user_email, match_email):
    try:
        response1 = supabase.table('messages').select("*").eq('sender_email', user_email).eq('receiver_email', match_email).execute()
        response2 = supabase.table('messages').select("*").eq('sender_email', match_email).eq('receiver_email', user_email).execute()
        
        all_messages = response1.data + response2.data
        all_messages.sort(key=lambda x: x['created_at'])
        return all_messages
    except Exception as e:
        st.error(f"Error fetching chat history: {e}")
        return []

def send_message(sender, receiver, message):
    try:
        data, count = supabase.table('messages').insert({
            'sender_email': sender,
            'receiver_email': receiver,
            'message': message
        }).execute()
        st.cache_data.clear() 
        return data
    except Exception as e:
        st.error(f"Error sending message: {e}")
        return None

# --- ML Matchmaker Function (Now uses Supabase data) ---

def get_matches(current_user_email, all_profiles_data):
    if not all_profiles_data or len(all_profiles_data) < 2:
        return []
        
    df = pd.DataFrame(all_profiles_data)
    
    df['combined_text'] = df['skills'].fillna('') + " " + df['goals'].fillna('')
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(df['combined_text'])
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    
    try:
        user_index_series = df.index[df['email'] == current_user_email]
        if user_index_series.empty:
            st.error(f"Error: Your email '{current_user_email}' not found.")
            return []
        user_index = user_index_series[0]
        
    except Exception as e:
        st.error(f"Error finding user index: {e}")
        return []

    sim_scores = list(enumerate(cosine_sim[user_index]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    top_matches = []
    for i, score in sim_scores:
        if i == user_index:
            continue
            
        match_details = {
            'Name': df.iloc[i]['name'],
            'Email': df.iloc[i]['email'],
            'Class': df.iloc[i]['class'],
            'Skills': df.iloc[i]['skills'],
            'Goals': df.iloc[i]['goals'],
            'Match_Score': f"{score*100:.2f}%" 
        }
        top_matches.append(match_details)
        
        if len(top_matches) == 3:
            break
            
    return top_matches

# --- Initialize CSS ---
inject_custom_css()

# --- NEW: Inject the Lordicon SCRIPT (This is the fix) ---
st.markdown('<script src="https://cdn.lordicon.com/lordicon.js"></script>', unsafe_allow_html=True)


# --- Main App ---
st.title("CO:LAB 🚀")
st.header("Find Your Perfect Project Partner")
st.write("Create your profile, find smart matches, and start collaborating. (v6.1 Stable Build)")
st.divider()

# --- Initialize Session State for Chat ---
if 'current_chat' not in st.session_state:
    st.session_state.current_chat = None
    st.session_state.current_chat_name = None
    st.session_state.current_user_email = None

# --- NEW: Animated Icon HTML ---
icon_matches = """
<lord-icon
    src="https://cdn.lordicon.com/lthGlgqe.json"
    trigger="loop"
    delay="1000"
    colors="primary:#ffffff,secondary:#00a3ff">
</lord-icon>
"""

icon_profile = """
<lord-icon
    src="https://cdn.lordicon.com/kthelypq.json"
    trigger="loop"
    delay="1000"
    colors="primary:#ffffff,secondary:#00a3ff">
</lord-icon>
"""

icon_members = """
<lord-icon
    src="https://cdn.lordicon.com/yxyampms.json"
    trigger="loop"
    delay="1000"
    colors="primary:#ffffff,secondary:#00a3ff">
</lord-icon>
"""

# --- NEW: TAB LAYOUT with EMOJI labels (This is the fix) ---
tab_matches, tab_profile, tab_all_members = st.tabs(["🧠 Find Matches", "👤 My Profile", "🌐 All Members"])


# --- Tab 1: Find Matches & Chat ---
with tab_matches:
    # --- NEW: Header with animated icon ---
    st.markdown(f"<h3>{icon_matches} Find & Chat With Your Matches</h3>", unsafe_allow_html=True)
    
    all_profiles = get_all_profiles()
    
    if not all_profiles:
        st.info("Create your profile in the 'My Profile' tab to find matches!")
    else:
        try:
            if len(all_profiles) < 2:
                st.info("We need at least two profiles to find matches. Ask a friend to join!")
            else:
                all_emails = [p['email'] for p in all_profiles]
                user_email_to_match = st.selectbox("Select your profile (by email):", all_emails, key="profile_selector")

                if st.button("Find My Top 3 Matches", use_container_width=True):
                    st.session_state.current_user_email = user_email_to_match
                    st.session_state.current_chat = None 
                    
                    with st.spinner("Calculating your matches..."):
                        matches = get_matches(user_email_to_match, all_profiles)
                        
                        if not matches:
                            st.warning("Could not find any matches. Try updating your skills or goals!")
                        else:
                            st.success("Here are your top matches! 👇")
                            
                            cols = st.columns(3)
                            for i, match in enumerate(matches):
                                with cols[i]:
                                    st.markdown(f"""
                                        <div class="match-card">
                                            <div style="display: flex; justify-content: space-between;">
                                                <h3>{match['Name']}</h3>
                                                <div class="score">{match['Match_Score']}</div>
                                            </div>
                                            <p><strong>Email:</strong> {match['Email']}</p>
                                            <p><strong>Class:</strong> {match['Class']}</p>
                                            <hr style="border-color: rgba(255, 255, 255, 0.1);">
                                            <p><strong>Skills:</strong> {match['Skills'].replace('\\n', ', ')}</p>
                                        </div>
                                    """, unsafe_allow_html=True)
                                    
                                    if st.button(f"Chat with {match['Name']}", key=f"chat_{match['Email']}", use_container_width=True):
                                        st.session_state.current_chat = match['Email']
                                        st.session_state.current_chat_name = match['Name']
                                        st.session_state.current_user_email = user_email_to_match
                                        st.rerun()

        except Exception as e:
            st.error(f"An error occurred during matching: {e}")

    # --- DEDICATED CHAT INTERFACE ---
    st.divider()
    if st.session_state.current_chat:
        st.header(f"Chat with {st.session_state.current_chat_name}")
        st.markdown("---")
        
        chat_history = get_chat_history(st.session_state.current_user_email, st.session_state.current_chat)
        
        for msg in chat_history:
            is_me = (msg['sender_email'] == st.session_state.current_user_email)
            name = "Me" if is_me else st.session_state.current_chat_name
            with st.chat_message(name=name, avatar="🧑‍💻" if is_me else "🤖"):
                st.write(msg['message'])
                ts = datetime.fromisoformat(msg['created_at']).strftime('%Y-%m-%d %I:%M %p')
                st.caption(f"_{ts}_")
    
# --- Tab 2: Profile Creation ---
with tab_profile:
    # --- NEW: Header with animated icon ---
    st.markdown(f"<h3>{icon_profile} Create or Update Your Profile</h3>", unsafe_allow_html=True)
    
    st.markdown('<div class="glass-container">', unsafe_allow_html=True) 
    
    with st.form(key='profile_form'):
        email = st.text_input("My Email (This is your unique ID)", help="Required. Used to identify you and for chat.")
        name = st.text_input("My Full Name", help="Enter your real name for better collaboration.")
        subject = st.selectbox(
            "My Class/Subject",
            ("Computer Science", "Information Technology", "Electronics", "Mechanical", "Civil", "Biotechnology", "Business", "Design", "Other"),
            help="Choose your main class or subject area."
        )
        skills = st.text_area(
            "My Skills",
            placeholder="e.g., Python, UI/UX Design, Data Analysis...",
            help="List your main technical and soft skills."
        )
        goals = st.text_area(
            "My Goals",
            placeholder="e.g., Build a ML app, Find a strong coder...",
            help="Describe what you want to achieve or the type of partner you seek."
        )
        submit_button = st.form_submit_button(label="Create / Update My Profile", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True) 

    # --- Form Submission Logic (NEW) ---
    if submit_button:
        if not email or not name or not subject or not skills or not goals:
            st.warning("Please fill out all the fields before submitting.")
        else:
            with st.spinner("Saving your profile to the cloud..."):
                data = upsert_profile(email.strip(), name.strip(), subject, skills, goals)
                if data:
                    st.success("Profile saved successfully! 🎉")
                    st.balloons()
                else:
                    st.error("There was an error saving your profile.")

# --- Tab 3: All Members (NEW CUSTOM GRID) ---
with tab_all_members:
    # --- NEW: Header with animated icon ---
    st.markdown(f"<h3>{icon_members} All Members in CO:LAB</h3>", unsafe_allow_html=True)
    
    all_profiles_data = get_all_profiles()
    
    if not all_profiles_data:
        st.info("Database is empty. Create a profile to get started!")
    else:
        st.write(f"Showing {len(all_profiles_data)} members.")
        st.divider()
        
        cols = st.columns(3)
        for i, profile in enumerate(all_profiles_data):
            skills = profile['skills'].replace('\\n', ', ') if profile['skills'] else "No skills listed"
            goals = profile['goals'].replace('\\n', ', ') if profile['goals'] else "No goals listed"
            
            with cols[i % 3]:
                st.markdown(f"""
                <div class="profile-mini-card">
                    <h4>{profile['name']}</h4>
                    <p><strong>Email:</strong> {profile['email']}</p>
                    <p><strong>Class:</strong> {profile['class']}</p>
                    <hr style="border-color: rgba(255, 255, 255, 0.1); margin: 0.5em 0;">
                    <p><strong>Skills:</strong> {skills}</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.divider()
        st.download_button(
            label="Download All Profiles (CSV)",
            data=pd.DataFrame(all_profiles_data).to_csv(index=False).encode('utf-8'),
            file_name='all_profiles.csv',
            mime='text/csv',
            use_container_width=True
        )


# --- MAIN CHAT INPUT (Stays at the bottom) ---
if st.session_state.current_chat:
    if prompt := st.chat_input(f"Message {st.session_state.current_chat_name}..."):
        send_message(st.session_state.current_user_email, st.session_state.current_chat, prompt)
        st.rerun()