from google import genai
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Gift Empowers | AI LinkedIn Coach", page_icon="🚀"
)
st.title("🚀 Gift Empowers 60-Day LinkedIn Authority Coach")
st.markdown(
    "Your private AI strategist for building a non-generic digital footprint."
)

# Initialize Gemini Client securely using Streamlit Secrets
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# System Instructions & Framework baked safely into the backend
system_prompt = """
You are an uncompromising Growth & Positioning Strategist for Nigerian students 
under Gift Empowers / Project 1000. Guide them using the Quiet Authority framework. 
Never use 'aspiring' or generic AI buzzwords. Ask probing questions first.
"""

# Chat History Setup
if "messages" not in st.session_state:
  st.session_state.messages = []

# Display past messages
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])

# User Chat Input Box
if prompt := st.chat_input(
    "Ask your positioning question or paste a YouTube link..."
):
  st.session_state.messages.append({"role": "user", "content": prompt})
  with st.chat_message("user"):
    st.markdown(prompt)

  # Generate response from Gemini backend
  with st.chat_message("assistant"):
    with st.spinner("Analyzing your positioning..."):
      response = client.models.generate_content(
          model="gemini-3.8-flash",
          contents=prompt,
          config={"system_instruction": system_prompt},
      )
      st.markdown(response.text)
      st.session_state.messages.append(
          {"role": "assistant", "content": response.text}
      )
