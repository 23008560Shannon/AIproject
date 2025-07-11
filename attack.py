# === Run with: streamlit run attack.py ===

import streamlit as st
from datetime import datetime

# === Page config ===
st.set_page_config(page_title="JobGenie: Career Assistant", layout="centered")

# === Light theme CSS with job-related icons ===
st.markdown("""
    <style>
        [data-testid="stSidebar"] {background-color: #f5faff;}
        .css-1v0mbdj, .css-10trblm, .st-emotion-cache-1v0mbdj {color: #222222 !important;}
        label, .css-1xarl3l {color: #222222 !important; font-weight: bold;}
        .stButton>button {background-color: #e0f7fa !important; color: #222222 !important; border: 1px solid #90caf9 !important;}
        body, .stApp, .main, .block-container {background-color: #f5faff !important;}
        /* Decorative job icons in the background */
        body::before {
            content: '';
            position: fixed;
            top: 10%;
            left: 5%;
            width: 90vw;
            height: 80vh;
            background-image: url('https://img.icons8.com/ios-filled/100/briefcase.png'), url('https://img.icons8.com/ios-filled/100/resume.png'), url('https://img.icons8.com/ios-filled/100/job.png');
            background-repeat: no-repeat, no-repeat, no-repeat;
            background-position: 10% 20%, 80% 60%, 50% 80%;
            background-size: 80px, 80px, 80px;
            opacity: 0.07;
            z-index: 0;
            pointer-events: none;
        }
    </style>
""", unsafe_allow_html=True)

# === Resume fields and state ===
resume_fields = ["name", "education", "skills", "interests", "experience"]
if "resume_data" not in st.session_state:
    st.session_state.resume_data = {field: None for field in resume_fields}
if "awaiting_field" not in st.session_state:
    st.session_state.awaiting_field = "name"
if "resume_ready" not in st.session_state:
    st.session_state.resume_ready = False
if "resume_summary" not in st.session_state:
    st.session_state.resume_summary = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def reset_resume():
    st.session_state.resume_data = {field: None for field in resume_fields}
    st.session_state.awaiting_field = "name"
    st.session_state.resume_ready = False
    st.session_state.resume_summary = ""
    st.session_state.chat_history = []

# === Resume summary generator ===
def generate_resume_summary(data):
    # Professional summary paragraph
    summary = f"""
# Professional Resume\n\n"""
    summary += f"**Name:** {data['name']}\n\n"
    summary += (
        f"**Professional Summary:**\n"
        f"{data['name']} is a motivated and goal-oriented polytechnic student with a background in {data['education']}. "
        f"Skilled in {data['skills']}, and passionate about {data['interests']}. "
        f"Demonstrates strong communication, adaptability, and a commitment to continuous learning. "
        f"Eager to contribute these strengths to future opportunities.\n\n"
    )
    summary += f"**Education:**\n- {data['education']}\n\n"
    # Skills as bullet points
    skills_list = [s.strip() for s in data['skills'].split(',') if s.strip()]
    if skills_list:
        summary += "**Skills:**\n"
        for skill in skills_list:
            summary += f"- {skill}\n"
        summary += "\n"
    else:
        summary += f"**Skills:** {data['skills']}\n\n"
    summary += f"**Interests & Career Goals:**\n- {data['interests']}\n\n"
    # Work experience section
    if data['experience'].lower() != 'none' and len(data['experience']) > 2:
        summary += f"**Work Experience:**\n- {data['experience']}\n\n"
    else:
        summary += "**Work Experience:**\n- Entry-level candidate or no prior work experience.\n\n"
    summary += "---\n"
    # Career suggestions
    summary += "**Personalized Career Suggestions:**\n"
    summary += generate_career_suggestions(skills_list, data['interests'])
    summary += "\n---\n"
    # Interview questions
    summary += "**Interview Practice:**\n"
    summary += generate_interview_questions(data)
    summary += ("\n---\n*This career summary was generated by an AI Assistant. Review and personalize as needed.*\n")
    return summary

# Generate 3 career suggestions based on skills and interests
def generate_career_suggestions(skills, interests):
    # Simple rule-based suggestions for demo; in production, use LLM or database
    suggestions = []
    interests_lower = interests.lower()
    if any("data" in s.lower() or "python" in s.lower() for s in skills) or "data" in interests_lower:
        suggestions.append("1. Data Analyst or Junior Data Scientist: Leverage your analytical and programming skills to interpret data and support business decisions.")
    if any("web" in s.lower() or "html" in s.lower() or "javascript" in s.lower() for s in skills) or "web" in interests_lower:
        suggestions.append("2. Web Developer: Use your web development skills to build and maintain websites or web applications.")
    if any("network" in s.lower() or "security" in s.lower() for s in skills) or "cyber" in interests_lower:
        suggestions.append("3. IT Support or Cybersecurity Associate: Apply your technical knowledge to support IT infrastructure or help protect organizations from cyber threats.")
    if not suggestions:
        suggestions = [
            "1. Project Assistant: Use your teamwork and communication skills to support project management tasks.",
            "2. Customer Service Executive: Apply your interpersonal skills in a client-facing role.",
            "3. Marketing Coordinator: Combine creativity and organization to support marketing campaigns."
        ]
    return '\n'.join(suggestions[:3]) + '\n'

# Generate 2 interview questions and sample answers
def generate_interview_questions(data):
    name = data['name'].split()[0]
    skills = [s.strip() for s in data['skills'].split(',') if s.strip()]
    interests = data['interests']
    education = data['education']
    q1 = f"1. Can you tell us about your background and why you chose {education}?\n"
    a1 = f"   *Sample Answer:* Certainly! My name is {name}, and I chose to pursue {education} because it aligns with my interests in {interests}. Through my studies, I've developed skills such as {', '.join(skills[:2]) if len(skills) >= 2 else ', '.join(skills)}, and I'm eager to apply them in a professional setting.\n"
    q2 = f"2. What is one of your key strengths, and how have you demonstrated it?\n"
    a2 = f"   *Sample Answer:* One of my key strengths is {skills[0] if skills else 'adaptability'}. For example, during my coursework or internship, I was able to use this skill to overcome challenges and achieve positive results.\n"
    return q1 + a1 + '\n' + q2 + a2 + '\n'

# === Chatbot logic ===
def chatbot_response(user_input):
    try:
        field = st.session_state.awaiting_field
        data = st.session_state.resume_data
        response = ""
        if field == "name":
            greetings = ["hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening"]
            name_input = user_input.strip().lower()
            # Require at least two words and not a greeting
            if len(user_input.split()) >= 2 and name_input not in greetings:
                data["name"] = user_input.strip()
                st.session_state.awaiting_field = "education"
                response = "Thank you! What is your highest diploma or education background?"
            else:
                response = "Please enter your full name (first and last name)."
        elif field == "education":
            if len(user_input) > 2:
                data["education"] = user_input.strip()
                st.session_state.awaiting_field = "skills"
                response = "Great! Please list your top 2–3 technical or soft skills (comma-separated)."
            else:
                response = "Could you clarify your education background?"
        elif field == "skills":
            if "," in user_input or len(user_input.split()) >= 2:
                data["skills"] = user_input.strip()
                st.session_state.awaiting_field = "interests"
                response = "Thank you! What are your main interests and career goals?"
            else:
                response = "Please list at least two skills, separated by commas."
        elif field == "interests":
            if len(user_input) > 2:
                data["interests"] = user_input.strip()
                st.session_state.awaiting_field = "experience"
                response = "Do you have any relevant work experience? If yes, please describe. If none, just say 'None'."
            else:
                response = "Could you share your main interests or career goals?"
        elif field == "experience":
            data["experience"] = user_input.strip()
            st.session_state.resume_ready = True
            st.session_state.resume_summary = generate_resume_summary(data)
            response = "Thank you! Here is your professional resume summary below. You can download it as a text file."
            # Instantly show the resume and next prompts
            st.rerun()
        else:
            response = "All information collected. If you want to start over, click 'Clear Chat'."
        return response
    except Exception as e:
        return f"Error: {str(e)}"

# === Main UI ===
st.markdown("<h1 style='color:#222222;'>JobGenie: Career Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#222222;'>Build your professional resume step by step through conversation.</p>", unsafe_allow_html=True)

if st.button("Clear Chat / Start Over"):
    reset_resume()
    st.rerun()

for chat in st.session_state.chat_history:
    align = "right" if chat["role"] == "user" else "left"
    bubble_color = "#e0f7fa" if chat["role"] == "user" else "#f5faff"
    st.markdown(f"""
        <div style="text-align: {align};">
            <div style="display: inline-block; background-color: {bubble_color}; padding: 10px; border-radius: 10px; margin: 5px; max-width: 80%; text-align: left;">
                <p style="margin: 0; color: #222222;">{chat['message']}</p>
                <span style="font-size: 0.8em; color: #222222;">{chat.get('timestamp', '')}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

if st.session_state.resume_ready:
    st.markdown(f"<div style='color:#222222'>{st.session_state.resume_summary}</div>", unsafe_allow_html=True)
    st.download_button(
        label="Download Resume as Text",
        data=st.session_state.resume_summary,
        file_name="resume_summary.txt",
        mime="text/plain"
    )
    # Ask if user wants job recommendations
    if "jobstreet_prompted" not in st.session_state:
        st.session_state.jobstreet_prompted = False
    if not st.session_state.jobstreet_prompted:
        st.markdown("<span style='color:#222222;'>Would you like to see job recommendations from JobStreet Singapore based on your profile?</span>", unsafe_allow_html=True)
        if st.button("Show JobStreet Recommendations"):
            st.session_state.jobstreet_prompted = True
    elif st.session_state.jobstreet_prompted:
        # Build a JobStreet search URL using skills and interests
        data = st.session_state.resume_data
        search_terms = []
        if data.get("skills"):
            search_terms.append(data["skills"].replace(",", " "))
        if data.get("interests"):
            search_terms.append(data["interests"])
        query = "+".join([s.replace(" ", "+") for s in search_terms if s])
        jobstreet_url = f"https://www.jobstreet.com.sg/en/job-search/{query}-jobs/"
        st.markdown("<span style='color:#222222;'>Here are job recommendations from JobStreet Singapore based on your profile:</span>", unsafe_allow_html=True)
        st.markdown(f"[View jobs on JobStreet Singapore]({jobstreet_url})")
else:
    if not st.session_state.chat_history:
        greet = "Hello! I'm your AI career assistant. Let's build your professional resume together. What is your full name?"
        st.session_state.chat_history.append({
            "role": "bot", "message": greet, "timestamp": datetime.now().strftime('%H:%M')
        })
        align = "left"
        bubble_color = "#f5faff"
        st.markdown(f"""
            <div style="text-align: {align};">
                <div style="display: inline-block; background-color: {bubble_color}; padding: 10px; border-radius: 10px; margin: 5px; max-width: 80%; text-align: left;">
                    <p style="margin: 0; color: #222222;">{greet}</p>
                    <span style="font-size: 0.8em; color: #222222;">{datetime.now().strftime('%H:%M')}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    if prompt := st.chat_input("Type your message here..."):
        user_message = prompt.strip()
        if user_message:
            chat_time = datetime.now().strftime('%H:%M')
            st.session_state.chat_history.append({
                "role": "user", "message": user_message, "timestamp": chat_time
            })
            align = "right"
            bubble_color = "#e0f7fa"
            st.markdown(f"""
                <div style="text-align: {align};">
                    <div style="display: inline-block; background-color: {bubble_color}; padding: 10px; border-radius: 10px; margin: 5px; max-width: 80%; text-align: left;">
                        <p style="margin: 0; color: #222222;">{user_message}</p>
                        <span style="font-size: 0.8em; color: #222222;">{chat_time}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            with st.spinner("Generating response..."):
                try:
                    bot_response = chatbot_response(user_message)
                    chat_time = datetime.now().strftime('%H:%M')
                    st.session_state.chat_history.append({
                        "role": "bot", "message": bot_response, "timestamp": chat_time
                    })
                    align = "left"
                    bubble_color = "#f5faff"
                    st.markdown(f"""
                        <div style="text-align: {align};">
                            <div style="display: inline-block; background-color: {bubble_color}; padding: 10px; border-radius: 10px; margin: 5px; max-width: 80%; text-align: left;">
                                <p style="margin: 0; color: #222222;">{bot_response}</p>
                                <span style="font-size: 0.8em; color: #222222;">{chat_time}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.error("An error occurred while processing your request.")
                    st.error(str(e))
