

import streamlit as st
from supabase import create_client, Client
import pandas as pd
import os
import requests
import openai
import json 

st.set_page_config(layout="wide", page_title="CO:LAB - AI Team Builder")

try:
    SUPABASE_URL: str = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY: str = st.secrets["SUPABASE_KEY"]
    OPENAI_API_KEY: str = st.secrets["OPENAI_API_KEY"]
    
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    openai_client = openai.OpenAI(api_key=OPENAI_API_KEY) # Use new v1+ client
    
except Exception as e:
    st.error("Error: Could not find API keys. Did you set up your .streamlit/secrets.toml file?")
    st.stop()

def inject_custom_css():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&display=swap');
            * {font-family: 'Space Grotesk', sans-serif;}
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
            h1, h2, h3 {
                color: #FFFFFF;
                text-shadow: 0 0 10px rgba(0, 240, 255, 0.3);
            }
            h3 {
                color: #00F0FF;
                display: flex;
                align-items: center;
            }
            .glass-container {
                background: rgba(26, 26, 38, 0.7);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 16px;
                padding: 2em;
                margin-bottom: 2em;
            }
            .project-card, .profile-card {
                background: rgba(26, 26, 38, 0.7);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 16px;
                padding: 1.5em;
                margin-bottom: 1.5em;
                transition: all 0.3s ease;
            }
            .project-card:hover, .profile-card:hover {
                border-color: #00F0FF;
                box-shadow: 0 0 15px rgba(0, 240, 255, 0.3);
                transform: translateY(-3px);
            }
            .project-card h4, .profile-card h4 {
                color: #00F0FF;
                margin-bottom: 0.5em;
            }
            .project-card p, .profile-card p {
                color: #E0E0E0;
                font-size: 0.9em;
                margin: 0.2em 0;
            }
            .profile-card .reliability-score {
                font-size: 1.2em;
                font-weight: 700;
                color: #00F0FF;
                text-align: right;
            }
            .project-card .role-tag, .profile-card .tag {
                background-color: rgba(0, 240, 255, 0.1);
                color: #00F0FF;
                padding: 0.2em 0.5em;
                border-radius: 5px;
                font-size: 0.8em;
                margin-right: 5px;
                display: inline-block;
            }
            .github-analysis {
                font-size: 0.9em;
                padding: 0.5em;
                background-color: rgba(0, 0, 0, 0.2);
                border-radius: 8px;
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
            }
            .stTabs [data-baseweb="tab"]:hover {
                background: rgba(40, 40, 55, 0.8);
                color: #FFFFFF;
            }
            .stTabs [aria-selected="true"] {
                background: transparent;
                border-bottom: 3px solid #00F0FF;
                color: #00F0FF;
            }
            .stTabs [data-baseweb="tab-panel"] {
                background: transparent;
                padding-top: 2em;
            }
            .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"], .stMultiSelect div[data-baseweb="select"] {
                background: rgba(0, 0, 0, 0.3);
                border: 1px solid #00F0FF;
                box-shadow: 0 0 10px rgba(0, 240, 255, 0.3);
                color: #FFFFFF !important;
                border-radius: 8px;
            }
            .stTextInput label, .stTextArea label, .stSelectbox label, .stCheckbox label, .stMultiSelect label, .stSlider label {
                color: #E0E0E0 !important;
            }
            .stButton > button {
                background: linear-gradient(90deg, #00F0FF, #00A3FF);
                color: #0a0a10;
                border: none;
                border-radius: 8px;
                font-weight: 700;
                padding: 0.7em 1.5em;
                transition: all 0.3s ease;
                box-shadow: 0 0 15px rgba(0, 240, 255, 0.5);
            }
            .stButton > button:hover {
                box-shadow: 0 0 25px rgba(0, 240, 255, 1);
                transform: scale(1.03);
            }
            .stTabs [data-baseweb="tab-panel"] div[data-testid="chat-message-container"] {
                background: rgba(0, 0, 0, 0.2);
                border-radius: 10px;
                padding: 0.5em 1em;
                margin-bottom: 0.5em;
            }
        </style>
    """, unsafe_allow_html=True)


@st.cache_data(ttl=3600)
def get_embedding(text, model="text-embedding-3-small"):
   try:
       text = text.replace("\n", " ")
       response = openai_client.embeddings.create(input=[text], model=model)
       return response.data[0].embedding
   except Exception as e:
       st.error(f"Error getting embedding from OpenAI: {e}")
       return None

@st.cache_data(ttl=600)
def get_github_analysis(username):
    if not username:
        return "No GitHub username provided."
    api_url = f"https://api.github.com/users/{username}/repos"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        repos = response.json()
        if not repos:
            return "This user has no public repositories."
        lang_counts = {}
        for repo in repos:
            lang = repo.get('language')
            if lang and not repo.get('fork'):
                lang_counts[lang] = lang_counts.get(lang, 0) + 1
        if not lang_counts:
            return "No public, non-forked repositories with a detected language."
        sorted_langs = sorted(lang_counts.items(), key=lambda item: item[1], reverse=True)
        report = f"*GitHub Analysis: {len(repos)} Public Repos*\n"
        for lang, count in sorted_langs[:3]:
            report += f"* *{lang}:* {count} {'repo' if count == 1 else 'repos'}\n"
        return report
    except requests.exceptions.HTTPError as e:
        return f"Error fetching GitHub data: {e.response.status_code}"
    except Exception as e:
        return f"An error occurred: {e}"

def extract_search_intent(query):
    ROLE_OPTIONS_STR = ", ".join(["Developer", "Designer", "Project Manager", "Researcher", "Presenter"])
    system_prompt = f"""
    You are an AI assistant helping a student find project teammates.
    Your job is to extract search criteria from the user's text.
    You must ONLY respond with a single, valid JSON object.
    
    The user is looking for three things:
    1.  role: The specific role they need. Must be one of: {ROLE_OPTIONS_STR}.
    2.  availability: A list of availability slots. Must be one or more of: weekdays, weekends, evenings.
    3.  skills_query: The string of text describing the skills they need.
    
    If the user's text is unclear, return a JSON object with all values as null.
    """
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini", # Switched to gpt-4o-mini
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        
        intent_json = response.choices[0].message.content
        intent_data = json.loads(intent_json)
        return intent_data
        
    except Exception as e:
        st.error(f"Error calling OpenAI for intent extraction: {e}")
        return { "role": None, "availability": [], "skills_query": None }

def generate_team_report(project_title, project_desc, roles_with_matches):
    
    briefing = f"Project Title: {project_title}\n"
    briefing = f"Project Title: {project_title}\n"
    briefing += f"Project Description: {project_desc}\n\n"
    briefing += "Here are the roles to fill and the top candidates found by the AI search:\n\n"

    for role, matches in roles_with_matches.items():
        briefing += f"--- ROLE: {role} ---\n"
        if not matches:
            briefing += "No candidates found.\n\n"
            continue
            
        for i, match in enumerate(matches):
            briefing += f"Candidate {i+1}: {match['name']} (Email: {match['email']})\n"
            briefing += f"Skills: {match['skills']}\n"
            briefing += f"Reliability: {match.get('reliability_score', 'N/A')}\n"
            briefing += f"GitHub Analysis: {match.get('github_analysis', 'N/A')}\n"
            briefing += "\n"

    system_prompt = """
    You are an expert AI recruiting assistant for a student project platform.
    Your job is to write a "Dream Team Report" for a Project Leader.
    
    You will be given a "briefing packet" with a project's details and a list of top candidates for each role.
    
    Your task is to write a concise, professional, and enthusiastic report.
    - For each role, introduce the top candidate.
    - *Synthesize* their skills, reliability, and GitHub data to explain why they are a good match for the project.
    - Be professional and encouraging.
    - Format your response clearly using Markdown (e.g., ###, **).
    - If no candidates were found for a role, state that.
    """
    
    try:
        response_stream = openai_client.chat.completions.create(
            model="gpt-4o", # Use the best model for this
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": briefing}
            ],
            temperature=0.4,
            stream=True # Stream the response for a "live" feel
        )
        return response_stream
        
    except Exception as e:
        st.error(f"Error calling OpenAI for team report: {e}")
        return None


@st.cache_data(ttl=60)
def get_all_profiles():
    try:
        response = supabase.table('profiles').select("*").execute()
        return response.data
    except Exception as e:
        st.error(f"Error fetching profiles: {e}")
        return []

def upsert_profile(profile_data):
    try:
        if profile_data.get("skills"):
            st.write("Generating AI skill embedding...")
            profile_data["skills_embedding"] = get_embedding(profile_data["skills"])
        else:
            profile_data["skills_embedding"] = None
        
        data, count = supabase.table('profiles').upsert(
            profile_data,
            on_conflict='email'
        ).execute()
        st.cache_data.clear()
        return data
    except Exception as e:
        st.error(f"Error saving profile: {e}")
        return None

@st.cache_data(ttl=60)
def get_all_projects_with_roles():
    try:
        response = supabase.table("projects").select("""
            id, created_at, leader_email, title, description, status, project_embedding,
            project_roles ( id, role_name, status )
        """).order('created_at', desc=True).execute()
        return response.data
    except Exception as e:
        st.error(f"Error fetching projects: {e}")
        return []

def create_project(project_data, roles_list):
    try:
        
        project_text = f"Title: {project_data['title']}\nDescription: {project_data['description']}"
        project_data['project_embedding'] = get_embedding(project_text)
        
        if project_data['project_embedding'] is None:
            st.error("Failed to create AI embedding for project.")
            return None
        
        
        project_response = supabase.table("projects").insert(project_data).execute()
        
        if not project_response.data:
            st.error("Failed to create project.")
            return None

        new_project_id = project_response.data[0]['id']
        roles_to_insert = [{"project_id": new_project_id, "role_name": role} for role in roles_list]
        roles_response = supabase.table("project_roles").insert(roles_to_insert).execute()
        st.cache_data.clear()
        return project_response.data
    
    except Exception as e:
        st.error(f"Error creating project: {e}")
        return None

def find_matching_profiles(search_query, role, availability):
    try:
        query_embedding = get_embedding(search_query)
        if query_embedding is None:
            st.error("Could not generate AI embedding for your search.")
            return []
            
        response = supabase.rpc('match_profiles', {
            'query_embedding': query_embedding,
            'match_threshold': 0.5,
            'role_query': role,
            'weekdays_query': 'weekdays' in availability,
            'weekends_query': 'weekends' in availability,
            'evenings_query': 'evenings' in availability
        }).execute()
        
        return response.data
    except Exception as e:
        st.error(f"Error finding matches: {e}")
        return []

def find_matches_for_project(project_embedding, role_name):
    try:
        response = supabase.rpc('match_profiles_for_project', {
            'p_project_embedding': project_embedding,
            'p_role_query': role_name
        }).execute()
        return response.data
    except Exception as e:
        st.error(f"Error running project match: {e}")
        return []

def submit_review(project_id, reviewer_email, reviewee_email, rating):
    try:
        data, count = supabase.table("team_reviews").insert({
            "project_id": project_id,
            "reviewer_email": reviewer_email,
            "reviewee_email": reviewee_email,
            "reliability_rating": rating
        }).execute()
        st.cache_data.clear()
        return data
    except Exception as e:
        st.error(f"Error submitting review: {e}")
        return None

@st.cache_data(ttl=300)
def get_user_rating(user_email):
    try:
        response = supabase.rpc('get_average_rating', {
            'user_email': user_email
        }).execute()
        return response.data
    except Exception as e:
        st.error(f"Error fetching rating: {e}")
        return None

inject_custom_css()
st.title("CO:LAB 🚀")
st.header("The AI-Powered Team Builder")
st.divider()

ROLE_OPTIONS = ["Developer", "Designer", "Project Manager", "Researcher", "Presenter"]

if "recruiter_messages" not in st.session_state:
    recruiter_intro = '<span style="color: #fff; font-weight: bold; font-size: 1.1em;">Hi! I\'m your AI Recruiter. Tell me what kind of teammate you\'re looking for. (e.g., \'I need a Python developer who is free on weekends.\')</span>'
    st.session_state.recruiter_messages = [
        {"role": "assistant", "content": recruiter_intro, "is_html": True}
    ]
if "search_results" not in st.session_state:
    st.session_state.search_results = []


tab_profile, tab_projects, tab_find_team, tab_review = st.tabs(["👤 My Profile", "🚀 Project Pitch Board", "🧠 AI Recruiter", "⭐ Submit Review"])


with tab_profile:
    st.header('Create Your "Stand-Out" Profile')
    st.write("Your profile is your 'resume' for other students. Fill it out to get matched to projects.")
    st.markdown('<div class="glass-container">', unsafe_allow_html=True)
    with st.form(key='profile_form'):
        st.subheader("Basic Information")
        email = st.text_input("My Email (This is your unique ID)", help="Use your student email.")
        name = st.text_input("My Full Name")
        github_username = st.text_input("My GitHub Username (Optional)", help="e.g., 'hiteshverma01'. This will be used to validate your skills.")
        
        st.divider()
        st.subheader("Skills & Role")
        primary_role = st.selectbox("My Primary Role", ROLE_OPTIONS, help="What is your main strength?")
        skills = st.text_area("My Technical Skills", placeholder="e.g., Python, Figma, React, Public Speaking, Market Research...")
        
        st.divider()
        st.subheader("My Availability")
        st.write("When are you usually free to work on projects?")
        avail_col1, avail_col2, avail_col3 = st.columns(3)
        with avail_col1:
            avail_weekdays = st.checkbox("Weekdays", help="Monday-Friday during the day.")
        with avail_col2:
            avail_weekends = st.checkbox("Weekends", help="Saturday or Sunday.")
        with avail_col3:
            avail_evenings = st.checkbox("Evenings", help="After 6 PM on any day.")
        
        st.divider()
        submit_button = st.form_submit_button(label="Create / Update My Profile", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True) 

    if submit_button:
        if not email or not name or not primary_role:
            st.warning("Please fill out at least your Email, Name, and Primary Role.")
        else:
            profile_data = {
                "email": email.strip(),
                "name": name.strip(),
                "github_username": github_username.strip() or None,
                "primary_role": primary_role,
                "skills": skills or None,
                "availability_weekdays": avail_weekdays,
                "availability_weekends": avail_weekends,
                "availability_evenings": avail_evenings
            }
            
            with st.spinner("Saving your profile to the cloud... (This may take a moment to generate AI embedding)"):
                data = upsert_profile(profile_data)
                if data:
                    st.success("Profile saved successfully! 🎉")
                    st.balloons()
                else:
                    st.error("There was an error saving your profile.")


# --- Tab 2: Project Pitch Board (Updated - MILESTONE 7) ---
with tab_projects:
    st.header("Project Pitch Board")
    st.write("Find a project that inspires you, or post your own idea and recruit a team.")
    st.divider()

    st.subheader("Post a New Project Idea")
    
    all_profiles = get_all_profiles()
    if not all_profiles:
        st.warning("You must create a profile first before you can post a project.", icon="👤")
    else:
        email_options = [p['email'] for p in all_profiles]
        
        st.markdown('<div class="glass-container">', unsafe_allow_html=True)
        with st.form(key="project_form", clear_on_submit=True):
            project_title = st.text_input("Project Title")
            project_desc = st.text_area("Project Description", placeholder="Describe your project, your goals, and what you want to build.")
            leader_email = st.selectbox("Project Leader (Your Email)", options=email_options)
            roles_needed = st.multiselect("Roles Needed", options=ROLE_OPTIONS, help="Select all the roles you need for your team.")
            project_submit_button = st.form_submit_button("Post My Project", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if project_submit_button:
            if not project_title or not project_desc or not leader_email or not roles_needed:
                st.warning("Please fill out all project fields, including at least one role.")
            else:
                project_data = {
                    "leader_email": leader_email,
                    "title": project_title,
                    "description": project_desc
                }
                with st.spinner("Posting your project... (This may take a moment to generate AI embedding)"):
                    data = create_project(project_data, roles_needed)
                    if data:
                        st.success("Project posted successfully! 🎉")
                    else:
                        st.error("An error occurred while posting your project.")

    st.divider()

    st.subheader("All Open Projects")
    projects = get_all_projects_with_roles()
    
    if not projects:
        st.info("No projects have been posted yet. Be the first!")
    else:
        # --- NEW: Create a modal for the AI Auto-Builder ---
        auto_build_modal = st.modal("🤖 AI Team Builder")
        
        for p in projects:
            leader_name = next((prof['name'] for prof in all_profiles if prof['email'] == p['leader_email']), p['leader_email'])
            
            st.markdown(f"""
            <div class="project-card">
                <h4>{p['title']}</h4>
                <p><strong>Project Leader:</strong> {leader_name}</p>
                <p><strong>Description:</strong> {p['description']}</p>
                <p><strong>Status:</strong> {p['status']}</p>
                <hr style="border-color: rgba(255, 255, 255, 0.1); margin: 0.5em 0;">
                <p><strong>Roles Needed:</strong></p>
                <div>
                    {''.join(f'<span class="role-tag">{role["role_name"]} ({role["status"]})</span>' for role in p['project_roles'])}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # --- NEW: AI AUTO-BUILDER BUTTON (MILESTONE 7) ---
            if st.button("🤖 Auto-Build My Team (AI)", key=f"build_{p['id']}", use_container_width=True, help="Click to have AI find and recommend a full team for this project."):
                
                with auto_build_modal.container():
                    st.header(f"AI 'Dream Team' Report for:")
                    st.subheader(p['title'])
                    st.divider()
                    
                    with st.spinner(f"Generating AI embeddings and finding matches for {len(p['project_roles'])} roles..."):
                        roles_with_matches = {}
                        
                        for role in p['project_roles']:
                            role_name = role['role_name']
                            
                            # 1. Run the AI vector search
                            matches = find_matches_for_project(p['project_embedding'], role_name)
                            
                            # 2. Get extra data (Reliability & GitHub) for top matches
                            top_matches_data = []
                            for match in matches[:3]: # Get top 3
                                # Get reliability
                                rating = get_user_rating(match['email'])
                                match['reliability_score'] = f"{rating:.1f}/5" if rating else "No Reviews"
                                
                                # Get GitHub analysis
                                if match['github_username']:
                                    match['github_analysis'] = get_github_analysis(match['github_username'])
                                else:
                                    match['github_analysis'] = "No GitHub provided."
                                
                                top_matches_data.append(match)
                            
                            roles_with_matches[role_name] = top_matches_data
                    
                    # 3. Send all data to the LLM for the final report
                    with st.spinner("Contacting Generative AI to write your 'Dream Team' report..."):
                        report_stream = generate_team_report(
                            p['title'],
                            p['description'],
                            roles_with_matches
                        )
                        
                        if report_stream:
                            st.write_stream(report_stream) # Stream the AI's response!
                        else:
                            st.error("The AI report generator failed.")

            st.button("I'm Interested in this Project", key=f"apply_{p['id']}", use_container_width=True)


# --- Tab 3: AI Recruiter (Milestone 5) ---
with tab_find_team:
    st.header("Chat with the AI Recruiter")
    st.write("Just tell the AI what you're looking for in plain English.")

    for message in st.session_state.recruiter_messages:
        with st.chat_message(message["role"]):
            if message.get("is_html"):
                st.markdown(message["content"], unsafe_allow_html=True)
            else:
                st.markdown(message["content"])

    if prompt := st.chat_input("I'm looking for a..."):
        st.session_state.recruiter_messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                intent = extract_search_intent(prompt)
                
                if not intent or not intent.get("role") or not intent.get("skills_query"):
                    st.error("I had trouble understanding that. Can you be more specific about the *role* and *skills* you need?")
                    st.session_state.recruiter_messages.append({"role": "assistant", "content": "I had trouble understanding that. Can you be more specific about the *role* and *skills* you need?"})
                    st.stop()
                
                ai_response = f"Okay, I'm searching for a *{intent['role']}* with skills in *'{intent['skills_query']}'*"
                if intent['availability']:
                    ai_response += f" who is available on *{', '.join(intent['availability'])}*."
                else:
                    ai_response += "."
                
                st.markdown(ai_response)
                st.session_state.recruiter_messages.append({"role": "assistant", "content": ai_response})
            
            with st.spinner("Searching the database..."):
                availability_filters = {
                    "weekdays": "weekdays" in intent['availability'],
                    "weekends": "weekends" in intent['availability'],
                    "evenings": "evenings" in intent['availability']
                }
                matches = find_matching_profiles(intent['skills_query'], intent['role'], availability_filters)
                st.session_state.search_results = matches
        
        st.rerun()

    if st.session_state.search_results:
        st.divider()
        st.subheader(f"Top AI-Powered Matches:")
        
        if not st.session_state.search_results:
            st.info("No profiles matched your specific criteria. Try broadening your search!")
        
        for match in st.session_state.search_results:
            rating_data = get_user_rating(match['email'])
            reliability_score = f"⭐ {rating_data:.1f}/5 Reliability" if rating_data else "⭐ No Reviews Yet"
            
            st.markdown(f"""
            <div class="profile-card">
                <div style="display: flex; justify-content: space-between;">
                    <h4>{match['name']}</h4>
                    <div class="reliability-score">{reliability_score}</div>
                </div>
                <p><strong>Email:</strong> {match['email']}</p>
                <p><strong>Primary Role:</strong> <span class="tag">{match['primary_role']}</span></p>
                <p><strong>Skills:</strong> {match['skills']}</p>
                <p><strong>Availability:</strong>
                    {f'<span class="tag">Weekdays</span>' if match['availability_weekdays'] else ''}
                    {f'<span class="tag">Weekends</span>' if match['availability_weekends'] else ''}
                    {f'<span class="tag">Evenings</span>' if match['availability_evenings'] else ''}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if match['github_username']:
                with st.expander(f"GitHub Skill Validation for {match['github_username']}"):
                    if st.button("Analyze GitHub Repos", key=f"github_{match['email']}", help="Calls the live GitHub API to analyze public repos."):
                        with st.spinner(f"Calling GitHub API for {match['github_username']}..."):
                            analysis_report = get_github_analysis(match['github_username'])
                            st.markdown(f'<div class="github-analysis">{analysis_report}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="profile-card" style="padding: 1em; margin-top: -1em;"><p><i>No GitHub username provided for validation.</i></p></div>', unsafe_allow_html=True)
            
            st.button("Chat with this user", key=f"chat_{match['email']}", use_container_width=True)

# --- Tab 4: Submit Review (Milestone 6) ---
with tab_review:
    st.header("Submit a Teammate Review")
    st.write("This is anonymous. Your review helps build a more reliable community.")
    
    all_profiles = get_all_profiles()
    all_projects = get_all_projects_with_roles()

    if not all_profiles or not all_projects:
        st.info("We need at least one project and one profile in the system to submit reviews.")
    else:
        profile_email_options = [p['email'] for p in all_profiles]
        project_id_options = {p['id']: f"{p['title']} (ID: {p['id']})" for p in all_projects}

        st.markdown('<div class="glass-container">', unsafe_allow_html=True)
        with st.form(key="review_form", clear_on_submit=True):
            st.subheader("Review Details")
            
            reviewer_email = st.selectbox("Your Email (Reviewer)", options=profile_email_options)
            project_id = st.selectbox("Which project was this for?", options=project_id_options.keys(), format_func=lambda x: project_id_options[x])
            reviewee_email = st.selectbox("Your Teammate's Email (Who you are reviewing)", options=profile_email_options)
            
            rating = st.slider("Reliability Rating (1=Unreliable, 5=Excellent)", min_value=1, max_value=5, value=3)
            
            review_submit_button = st.form_submit_button("Submit Anonymous Review", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if review_submit_button:
            if reviewer_email == reviewee_email:
                st.warning("You cannot review yourself.")
            else:
                with st.spinner("Submitting your review..."):
                    data = submit_review(
                        project_id=project_id,
                        reviewer_email=reviewer_email,
                        reviewee_email=reviewee_email,
                        rating=rating
                    )
                    if data:
                        st.success("Thank you! Your review has been submitted. 🎉")
                    else:
                        st.error("An error occurred while submitting your review.")