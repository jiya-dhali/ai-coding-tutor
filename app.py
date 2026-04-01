import streamlit as st
from google import genai
from PIL import Image
import json
import io

# 1. API Setup
API_KEY = "AIzaSyDof0t8chLmQm2DLBH968PmGe3Gk5GGUI8"
client = genai.Client(api_key=API_KEY)

# 2. Page Configuration
st.set_page_config(page_title="YOUR AI CODING TUTOR", layout="wide", page_icon="🤖")

# 3. Session State for Multi-Chat Management
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {"Chat 1": []}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Chat 1"

# --- SIDEBAR: History, Delete, and Sharing ---
with st.sidebar:
    st.title("♊ History")
    
    # New Chat Button
    if st.button("➕ New Chat", use_container_width=True):
        new_id = f"Chat {len(st.session_state.all_chats) + 1}"
        st.session_state.all_chats[new_id] = []
        st.session_state.current_chat = new_id
        st.rerun()

    st.markdown("---")
    
    # List all chat sessions with a Delete option
    for chat_id in list(st.session_state.all_chats.keys()):
        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            if st.button(chat_id, key=f"select_{chat_id}", use_container_width=True):
                st.session_state.current_chat = chat_id
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{chat_id}"):
                if len(st.session_state.all_chats) > 1:
                    del st.session_state.all_chats[chat_id]
                    st.session_state.current_chat = list(st.session_state.all_chats.keys())[0]
                else:
                    st.session_state.all_chats["Chat 1"] = []
                st.rerun()

    st.markdown("---")
    uploaded_file = st.file_uploader("🖼️ Analyze Image", type=["png", "jpg", "jpeg"])
    
    # --- SHARE OPTION ---
    st.markdown("### 📤 Share This Chat")
    current_history = st.session_state.all_chats[st.session_state.current_chat]
    
    if current_history:
        # Create a formatted text version for sharing
        share_text = f"--- {st.session_state.current_chat} History ---\n\n"
        for m in current_history:
            share_text += f"{m['role'].upper()}: {m['content']}\n\n"
        
        # Download button acts as a 'Share' trigger
        st.download_button(
            label="Download to Share",
            data=share_text,
            file_name=f"{st.session_state.current_chat}_transcript.txt",
            mime="text/plain",
            use_container_width=True
        )
    else:
        st.info("Start a chat to enable sharing.")

# --- MAIN INTERFACE ---
st.title("🚀 YOUR AI CODING TUTOR")
language = st.selectbox("I am teaching you:", ["Python", "Java", "C", "C++", "DSA"])

# Display History for the active chat
for msg in st.session_state.all_chats[st.session_state.current_chat]:
    avatar = "🤖" if msg["role"] == "model" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# Chat Interaction
if prompt := st.chat_input("Ask me anything about coding..."):
    st.session_state.all_chats[st.session_state.current_chat].append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Gemini 2.0 Flash is thinking..."):
            try:
                # Context gathering
                parts = [{"text": f"System: You are a {language} tutor. "}]
                for m in st.session_state.all_chats[st.session_state.current_chat]:
                    parts.append({"text": f"{m['role']}: {m['content']}"})
                
                if uploaded_file:
                    parts.append(Image.open(uploaded_file))

                response = client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=parts
                )
                
                answer = response.text
                st.markdown(answer)
                st.session_state.all_chats[st.session_state.current_chat].append({"role": "model", "content": answer})
                
            except Exception as e:
                st.error(f"Error: {e}")
