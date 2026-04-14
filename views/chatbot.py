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

    st.markdown(
        '''
        <div class="chat-header" style="display: flex; align-items: center; gap: 12px;">
            <svg width="34" height="34" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <linearGradient id="ai-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#4285F4"/>
                        <stop offset="50%" stop-color="#9B72CB"/>
                        <stop offset="100%" stop-color="#D96570"/>
                    </linearGradient>
                </defs>
                <path d="M12 2L14.4 9.6L22 12L14.4 14.4L12 22L9.6 14.4L2 12L9.6 9.6L12 2Z" fill="url(#ai-gradient)"/>
            </svg>
            Chat Support
        </div>
        ''', 
        unsafe_allow_html=True
    )
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
    You are a compassionate, warm, and supportive AI mental health guide for our Client-Counselor Matching System.
    You have two main roles:
    1. Be an empathetic listener: Offer emotional support, active listening, and gentle coping strategies for everyday mental health struggles, similar to a supportive therapeutic AI. Create a safe, non-judgmental space for clients to vent.
    2. Be a platform guide: Help users navigate the system. If they ask about getting a counselor or need long-term support, actively guide them to fill out the assessment form on the 'Find Your Match' page to connect with a professional human counselor.
    Always be conversational, empathetic, and clear. Remind users you are an AI guide, not a medical doctor.
    """
    model = genai.GenerativeModel("gemini-2.5-flash", system_instruction=app_context_prompt)

    # Initialize Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I am your AI mental health assistant. How can I help you today?"}
        ]

    # Render Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Scrolling Suggestion Pills (Only show on first message to help the user)
    if len(st.session_state.messages) == 1:
        st.markdown(
            """
            <style>
            .suggestions-wrapper {
                position: fixed;
                bottom: 130px; /* Increased to hover cleanly above Streamlit's white chat container */
                left: 50%;
                transform: translateX(-50%);
                width: 100%;
                max-width: 730px; /* Streamlit standard chat width */
                overflow: hidden;
                z-index: 999999;
                pointer-events: none; /* Let users click through to chat history */
                -webkit-mask-image: linear-gradient(to right, transparent, black 10%, black 90%, transparent);
                mask-image: linear-gradient(to right, transparent, black 10%, black 90%, transparent);
            }
            .suggestions-track {
                display: flex;
                gap: 14px;
                width: max-content;
                animation: scroll-left 30s linear infinite;
            }
            .suggestion-pill {
                background: #FFFFFF;
                border: 1px solid #E9E1FF;
                border-radius: 20px;
                padding: 10px 18px;
                font-size: 14px;
                color: #5A5A6E;
                white-space: nowrap;
                box-shadow: 0 4px 12px rgba(124,58,237,0.06);
            }
            @keyframes scroll-left {
                0% { transform: translateX(0); }
                100% { transform: translateX(-50%); }
            }
            /* Media query for smaller displays */
            @media (max-width: 768px) {
                .suggestions-wrapper { bottom: 110px; }
            }
            </style>
            
            <div class="suggestions-wrapper">
                <div class="suggestions-track">
                    <!-- First Set -->
                    <div class="suggestion-pill">I feel overwhelmed with work... 😔</div>
                    <div class="suggestion-pill">How do I choose the right counselor? 🔍</div>
                    <div class="suggestion-pill">Can we talk about relationship issues? 💔</div>
                    <div class="suggestion-pill">What happens during an assessment? 📝</div>
                    <div class="suggestion-pill">I want to develop a positive mindset ✨</div>
                    <div class="suggestion-pill">How does the matching process work? 🤝</div>
                    <!-- Second Set (Duplicate for seamless CSS loop) -->
                    <div class="suggestion-pill">I feel overwhelmed with work... 😔</div>
                    <div class="suggestion-pill">How do I choose the right counselor? 🔍</div>
                    <div class="suggestion-pill">Can we talk about relationship issues? 💔</div>
                    <div class="suggestion-pill">What happens during an assessment? 📝</div>
                    <div class="suggestion-pill">I want to develop a positive mindset ✨</div>
                    <div class="suggestion-pill">How does the matching process work? 🤝</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

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
