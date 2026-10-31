from datetime import datetime
from google import genai
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Page Configuration & Branding
st.set_page_config(page_title="Gift Empowers | AI LinkedIn Coach")
st.title("Gift Empowers LinkedIn Reputation Coach")
st.markdown(
    "Your private AI strategist for building a non-generic digital footprint"
    " for emerging professionals."
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

# System Instructions & Framework (Strict Quiet Authority + Value Ladder Upsells)
system_prompt = """
You are an uncompromising Growth & Positioning Strategist for emerging professionals 
(students and recent graduates up to 3 years post-graduation) under Gift Empowers. 

CORE RULES:
1. Guide them strictly using the Quiet Authority framework: prioritize substance, proprietary perspective, 
   distinct market identity, and long-term reputation over vanity metrics or high-volume posting.
2. NEVER use the word 'aspiring' or generic AI buzzwords (e.g., 'synergy', 'game-changer', 'rockstar', 'hustle').
3. Always challenge weak, generic thinking first by asking probing, strategic questions before providing frameworks.
4. When a user needs deep, bespoke review, profile teardowns, or advanced human-crafted execution beyond what AI can solve, 
   seamlessly and professionally guide them toward Gift Empowers' higher-level offerings (such as live profile audit sessions, 
   masterclasses, or upcoming cohort masterclasses) as the natural next step.
"""

# --- CONNECT TO GOOGLE SHEETS DATABASE ---
conn = st.connection("gsheets", type=GSheetsConnection)


# 1. Verify user email from the 'emails' tab
def verify_user_email(email_to_check):
  try:
    df = conn.read(worksheet="emails", ttl=0)
    df["email"] = df["email"].str.strip().str.lower()
    clean_email = email_to_check.strip().lower()
    return clean_email in df["email"].values
  except Exception as e:
    st.error(f"Database connection error (Emails): {e}")
    return False


# 2. Load past chats for this specific user from the 'chats' tab
def load_user_chats(user_email):
  try:
    df = conn.read(worksheet="chats", ttl=0)
    if df.empty or "email" not in df.columns:
      return []
    df["email"] = df["email"].str.strip().str.lower()
    user_df = df[df["email"] == user_email.strip().lower()]

    history = []
    for _, row in user_df.iterrows():
      if pd_notnull_safe(row["role"]) and pd_notnull_safe(row["content"]):
        history.append({"role": str(row["role"]), "content": str(row["content"])})
    return history
  except Exception:
    return []


def pd_notnull_safe(val):
  return val is not None and str(val) != "nan"


# 3. Save a new message to the 'chats' tab
def save_chat_to_sheet(user_email, role, content):
  try:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df_existing = conn.read(worksheet="chats", ttl=0)
    new_row = pd.DataFrame(
        [
            {
                "email": user_email,
                "timestamp": timestamp,
                "role": role,
                "content": content,
            }
        ]
    )
    updated_df = (
        pd.concat([df_existing, new_row], ignore_index=True)
        if not df_existing.empty
        else new_row
    )
    conn.update(worksheet="chats", data=updated_df)
  except Exception as e:
    print(f"Error saving chat: {e}")


# --- ACCESS VERIFICATION GATE (VIP Vault Framing) ---
if "user_email" not in st.session_state:
  st.session_state.user_email = None

if not st.session_state.user_email:
  st.subheader("🔐 Emerging Professional Access Verification")
  st.markdown(
      "Please enter the **email address you used to enroll** to access"
      " your AI Coach."
  )

  with st.form("auth_form"):
    entered_email = st.text_input("Your Email Address")
    submit_button = st.form_submit_button("Unlock AI Coach")

    if submit_button:
      if entered_email and "@" in entered_email:
        with st.spinner("Verifying your payment records..."):
          if verify_user_email(entered_email):
            cleaned_email = entered_email.strip().lower()
            st.session_state.user_email = cleaned_email

            # Load past chats or initialize with Quiet Authority welcome
            past_chats = load_user_chats(cleaned_email)
            if not past_chats:
              initial_greeting = (
                  "Welcome. You are inside the Gift Empowers LinkedIn Reputation"
                  " Coach. We don't chase vanity metrics or use generic"
                  " buzzwords here. What is your current career focus, and what"
                  " specific positioning challenge are we solving today?"
              )
              past_chats = [{"role": "assistant", "content": initial_greeting}]
              save_chat_to_sheet(cleaned_email, "assistant", initial_greeting)

            st.session_state.messages = past_chats
            st.success(
                "Access Granted. Initializing your secure session with your"
                " 24/7 Private Positioning Strategist..."
            )
            st.rerun()
          else:
            st.error(
                "❌ **Email not found.** Please ensure you use the exact email"
                " address you used during purchase."
            )
      else:
        st.error("Please enter a valid email address.")
  st.stop()

# Sidebar display for active user with a logout option
st.sidebar.markdown(f"👤 **Logged in as:** `{st.session_state.user_email}`")
if st.sidebar.button("Switch Account / Logout"):
  st.session_state.user_email = None
  st.session_state.messages = []
  st.rerun()

# --- CHAT INTERFACE ---
if "messages" not in st.session_state:
  st.session_state.messages = load_user_chats(st.session_state.user_email)

# Display past messages
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])

# User Chat Input Box
if prompt := st.chat_input(
    "Ask your positioning question..."
):
  st.session_state.messages.append({"role": "user", "content": prompt})
  save_chat_to_sheet(st.session_state.user_email, "user", prompt)

  with st.chat_message("user"):
    st.markdown(prompt)

  # Generate streaming response from Gemini backend
  with st.chat_message("assistant"):
    message_placeholder = st.empty()
    full_response = ""
    try:
      response_stream = client.models.generate_content_stream(
          model="gemini-3.8-flash",
          contents=prompt,
          config={"system_instruction": system_prompt},
      )

      for chunk in response_stream:
        if chunk.text:
          full_response += chunk.text
          message_placeholder.markdown(full_response + "▌")

      message_placeholder.markdown(full_response)
      st.session_state.messages.append(
          {"role": "assistant", "content": full_response}
      )
      save_chat_to_sheet(st.session_state.user_email, "assistant", full_response)

    except Exception as e:
      st.error(f"An error occurred: {e}")
