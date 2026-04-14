import streamlit as st
import google.generativeai as genai

def show_chatbot_page():
    st.markdown(
        """
        <style>
        .chat-header {
            font-family: 'DM Serif Display', serif;
            font-size: 38px;
            color: #1A1A2E;
            margin-bottom: 8px;
        }
        .chat-subheader {
            font-size: 16px;
            color: #5A5A6E;
            margin-bottom: 24px;
        }
        .botbox {
            background:#F8F5FF;border:1px solid #E9E1FF;border-radius:14px;padding:24px;margin-bottom:24px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="chat-header">Chat Support</div>', unsafe_allow_html=True)
    st.markdown('<div class="chat-subheader">Ask any general questions or receive guidance about counseling, mental health, and the process. Powered by Gemini AI.</div>', unsafe_allow_html=True)

    # API Key Configuration
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        st.error("Developer Setup Required: Please add your GEMINI_API_KEY to `.streamlit/secrets.toml` to activate the chatbot.")
        return

    # Initialize Gemini
    genai.configure(api_key=api_key)
    
    # Give the model a personality and context specific to your app
    app_context_prompt = """
    You are a compassionate, professional AI assistant for a Client-Counselor Matching System.
    Your main goal is to help clients understand mental health, guide them through the process of finding a counselor, and answer questions about the matching system platform.
    If they ask about getting a counselor, encourage them to fill out the assessment form on the 'Find Your Match' page.
    Remember to be empathetic, clear, and never provide medical diagnosis. You are a guide, not a therapist.
    """
    model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=app_context_prompt)

    # Initialize Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I am your AI mental health assistant. How can I help you today?"}
        ]

    # Render Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat Input
    if prompt := st.chat_input("Ask a question..."):
        # Append user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Build context for Gemini (Gemini's generate_content expects specific format or plain string)
        # Using chat session pattern:
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            try:
                # We skip the very first system greeting since Gemini history must start with "user"
                valid_history = []
                for m in st.session_state.messages[:-1]:
                    if m["content"] == "Hello! I am your AI mental health assistant. How can I help you today?":
                        continue
                    valid_history.append({"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]})

                chat_session = model.start_chat(history=valid_history)
                
                response = chat_session.send_message(prompt, stream=True)
                full_response = ""
                
                for chunk in response:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                
                # Add to session_state
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                st.error(f"Error connecting to Gemini: {str(e)}")
