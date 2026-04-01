import streamlit as st
from openai import OpenAI
from PIL import Image

# =========================
# 1. API SETUP (OpenRouter)
# =========================
API_KEY = "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"

client = OpenAI(
    api_key=API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

# =========================
# 2. PAGE CONFIG
# =========================
st.set_page_config(page_title="YOUR AI CODING TUTOR", layout="wide", page_icon="🤖")

# =========================
# 3. SESSION STATE
# =========================
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {"Chat 1": []}

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Chat 1"

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.title("♊ History")

    # New Chat
    if st.button("➕ New Chat", use_container_width=True):
        new_id = f"Chat {len(st.session_state.all_chats) + 1}"
        st.session_state.all_chats[new_id] = []
        st.session_state.current_chat = new_id
        st.rerun()

    st.markdown("---")

    # Chat List + Delete
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

    # Share Chat
    st.markdown("### 📤 Share This Chat")
    current_history = st.session_state.all_chats[st.session_state.current_chat]

    if current_history:
        share_text = f"--- {st.session_state.current_chat} History ---\n\n"
        for m in current_history:
            share_text += f"{m['role'].upper()}: {m['content']}\n\n"

        st.download_button(
            label="Download to Share",
            data=share_text,
            file_name=f"{st.session_state.current_chat}_transcript.txt",
            mime="text/plain",
            use_container_width=True
        )
    else:
        st.info("Start a chat to enable sharing.")

# =========================
# MAIN UI
# =========================
st.title("🚀 YOUR AI CODING TUTOR")

language = st.selectbox("I am teaching you:", ["Python", "Java", "C", "C++", "DSA"])

# Display chat history
for msg in st.session_state.all_chats[st.session_state.current_chat]:
    avatar = "🤖" if msg["role"] == "model" else "👤"
    role = "assistant" if msg["role"] == "model" else "user"

    with st.chat_message(role, avatar=avatar):
        st.markdown(msg["content"])

# =========================
# CHAT INPUT
# =========================
if prompt := st.chat_input("Ask me anything about coding..."):

    # Save user message
    st.session_state.all_chats[st.session_state.current_chat].append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("AI is thinking..."):
            try:
                messages = []

                # System prompt
                messages.append({
                    "role": "system",
                    "content": f"You are a helpful {language} coding tutor."
                })

                # Chat history
                for m in st.session_state.all_chats[st.session_state.current_chat]:
                    role = "assistant" if m["role"] == "model" else "user"
                    messages.append({
                        "role": role,
                        "content": m["content"]
                    })

                # API call
                response = client.chat.completions.create(
                    model="openai/gpt-4o-mini",  # fast & cheap
                    messages=messages
                )

                answer = response.choices[0].message.content

                st.markdown(answer)

                # Save response
                st.session_state.all_chats[st.session_state.current_chat].append(
                    {"role": "model", "content": answer}
                )

            except Exception as e:
                st.error(f"Error: {e}")
    
    

