from datetime import datetime
from google import genai
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Gift Empowers | AI LinkedIn Coach", page_icon="🚀"
)
st.title("Gift Empowers Project 1000 LinkedIn Reputation Coach")
st.markdown(
    "Your private AI strategist for building a non-generic digital footprint."
)

# Securely load API key
if "GEMINI_API_KEY" not in st.secrets:
  st.error(
      "⚠️ **API Key Missing!** Please add your `GEMINI_API_KEY` in your"
      " Streamlit Cloud App Settings under 'Secrets'."
  )
  st.stop()

# Initialize Gemini Client
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# System Instructions & Framework baked safely into the backend
system_prompt = """
You are an uncompromising Growth & Positioning Strategist for Nigerian students 
under Gift Empowers / Project 1000. Guide them using the Quiet Authority framework. 
Never use 'aspiring' or generic AI buzzwords. Ask probing questions first.
"""

# --- 1. STUDENT EMAIL VERIFICATION GATE ---
if "user_email" not in st.session_state:
  st.session_state.user_email = None

if not st.session_state.user_email:
  st.subheader("🔐 Student Access Verification")
  st.markdown(
      "Please enter the **email address you used to purchase/enroll** in the"
      " 60-Day LinkedIn Accelerator to unlock your AI Coach."
  )

  with st.form("auth_form"):
    entered_email = st.text_input("Your Email Address")
    submit_button = st.form_submit_button("Unlock AI Coach")

    if submit_button:
      if entered_email and "@" in entered_email:
        st.session_state.user_email = entered_email.strip().lower()
        st.success("Access granted! Loading your coach...")
        st.rerun()
      else:
        st.error("Please enter a valid email address.")
  st.stop()

# Sidebar display for active user with a logout option
st.sidebar.markdown(f"👤 **Logged in as:** `{st.session_state.user_email}`")
if st.sidebar.button("Switch Account / Logout"):
  st.session_state.user_email = None
  st.rerun()

# --- 2. CHAT INTERFACE & BACKEND LOGGING ---
if "messages" not in st.session_state:
  st.session_state.messages = []

# Display past messages
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])

# User Chat Input Box
if prompt := st.chat_input(
    "Ask your positioning question or paste a link..."
):
  st.session_state.messages.append({"role": "user", "content": prompt})
  with st.chat_message("user"):
    st.markdown(prompt)

  # BACKEND LOGGING: Automatically prints student email & prompt to your Streamlit Cloud Logs
  timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  print(
      f"🔍 [STUDENT USAGE LOG] Time: {timestamp} | User:"
      f" {st.session_state.user_email} | Prompt: {prompt}"
  )

  # Generate response from Gemini backend
  with st.chat_message("assistant"):
    with st.spinner("Analyzing your positioning..."):
      try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config={"system_instruction": system_prompt},
        )
        st.markdown(response.text)
        st.session_state.messages.append(
            {"role": "assistant", "content": response.text}
        )
      except Exception as e:
        st.error(f"An error occurred: {e}")
