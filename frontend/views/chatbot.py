import streamlit as st
import streamlit.components.v1 as components
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
    import os
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        st.error("Developer Setup Required: Please set the GEMINI_API_KEY environment variable to activate the chatbot.")
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
    model = genai.GenerativeModel("gemini-2.5-flash-lite", system_instruction=app_context_prompt)

    # Initialize Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I am your AI mental health assistant. How can I help you today?"}
        ]

    # Render Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Scrolling Suggestion Pills — injected into the parent document so they
    # sit directly above the chat input box and span its exact width.
    # They are single-use: clicking any pill fills + submits the input then
    # removes the strip. Streamlit also stops rendering this block once
    # messages > 1, so they never reappear.
    if len(st.session_state.messages) == 1:
        components.html(
            """
            <script>
            (function() {
                var doc = window.parent.document;
                var win = window.parent;

                // Clean up any leftover strip AND prior watcher from a previous render
                ['sugg-wrap', 'sugg-style', 'sugg-watcher'].forEach(function(id) {
                    var el = doc.getElementById(id);
                    if (el) el.remove();
                });
                if (win.__suggWatcher) {
                    win.clearInterval(win.__suggWatcher);
                    win.__suggWatcher = null;
                }

                var pills = [
                    'I feel overwhelmed with work... 😔',
                    'How do I choose the right counselor? 🔍',
                    'Can we talk about relationship issues? 💔',
                    'What happens during an assessment? 📝',
                    'I want to develop a positive mindset ✨',
                    'How does the matching process work? 🤝'
                ];

                function findChatBox() {
                    return doc.querySelector('[data-testid="stChatInputContainer"]')
                        || doc.querySelector('[data-testid="stChatInput"]')
                        || doc.querySelector('[data-testid="stBottomBlockContainer"]')
                        || doc.querySelector('div[class*="stChatInput"]');
                }

                function build() {
                    // Match the chat input box width; fall back to a safe fixed position
                    var chatBox = findChatBox();
                    var rect = chatBox ? chatBox.getBoundingClientRect() : null;
                    var leftPx   = rect ? rect.left  : 390;
                    var widthPx  = rect && rect.width > 100 ? rect.width : 850;
                    var bottomPx = 140;

                    var style = doc.createElement('style');
                    style.id = 'sugg-style';
                    style.textContent =
                        '#sugg-wrap{' +
                            'position:fixed;' +
                            'bottom:' + bottomPx + 'px;' +
                            'left:' + leftPx + 'px;' +
                            'width:' + widthPx + 'px;' +
                            'overflow:hidden;' +
                            'z-index:999999;' +
                            'pointer-events:none;' +
                            '-webkit-mask-image:linear-gradient(to right,transparent 0%,black 7%,black 93%,transparent 100%);' +
                            'mask-image:linear-gradient(to right,transparent 0%,black 7%,black 93%,transparent 100%);' +
                        '}' +
                        '#sugg-track{' +
                            'display:flex;gap:12px;' +
                            'width:max-content;' +
                            'animation:sugg-scroll 30s linear infinite;' +
                            'padding:8px 0;' +
                        '}' +
                        '.sugg-pill{' +
                            'background:#FFFFFF;' +
                            'border:1px solid #E9E1FF;' +
                            'border-radius:20px;' +
                            'padding:9px 18px;' +
                            'font-size:13px;' +
                            'font-family:DM Sans,sans-serif;' +
                            'color:#5A5A6E;' +
                            'white-space:nowrap;' +
                            'box-shadow:0 2px 8px rgba(124,58,237,0.08);' +
                            'cursor:pointer;' +
                            'pointer-events:auto;' +
                            'transition:background 0.18s,border-color 0.18s,color 0.18s;' +
                            'user-select:none;' +
                        '}' +
                        '.sugg-pill:hover{' +
                            'background:#F3F0FF;' +
                            'border-color:#8B5CF6;' +
                            'color:#6D28D9;' +
                        '}' +
                        '@keyframes sugg-scroll{' +
                            '0%{transform:translateX(0);}' +
                            '100%{transform:translateX(-50%);}' +
                        '}';
                    doc.head.appendChild(style);

                    var wrap = doc.createElement('div');
                    wrap.id = 'sugg-wrap';
                    var track = doc.createElement('div');
                    track.id = 'sugg-track';

                    // Duplicate pills for a seamless infinite scroll loop
                    pills.concat(pills).forEach(function(text) {
                        var pill = doc.createElement('div');
                        pill.className = 'sugg-pill';
                        pill.textContent = text;
                        pill.addEventListener('click', function() {
                            // Discard the strip immediately
                            wrap.remove();
                            style.remove();

                            // Fill the chat input using React's native value setter
                            var ta = doc.querySelector('textarea[data-testid="stChatInputTextArea"]');
                            if (!ta) return;
                            var setter = Object.getOwnPropertyDescriptor(
                                window.parent.HTMLTextAreaElement.prototype, 'value'
                            ).set;
                            setter.call(ta, text);
                            ta.dispatchEvent(new Event('input', { bubbles: true }));

                            // Click send after React processes the new value
                            setTimeout(function() {
                                var btn = doc.querySelector('button[data-testid="stChatInputSubmitButton"]');
                                if (btn) btn.click();
                            }, 80);
                        });
                        track.appendChild(pill);
                    });

                    wrap.appendChild(track);
                    doc.body.appendChild(wrap);

                    // Discard pills for any reason (pill click, manual send, navigation)
                    function dismiss() {
                        wrap.remove();
                        style.remove();
                        if (win.__suggWatcher) {
                            win.clearInterval(win.__suggWatcher);
                            win.__suggWatcher = null;
                        }
                    }

                    // Dismiss when user sends manually via send button
                    var sendBtn = doc.querySelector('button[data-testid="stChatInputSubmitButton"]');
                    if (sendBtn) sendBtn.addEventListener('click', dismiss);

                    // Dismiss when user presses Enter in the textarea
                    var ta = doc.querySelector('textarea[data-testid="stChatInputTextArea"]');
                    if (ta) {
                        ta.addEventListener('keydown', function(e) {
                            if (e.key === 'Enter' && !e.shiftKey) dismiss();
                        });
                    }

                    // Dismiss when user navigates away (e.g. logout) — chat input leaves the DOM.
                    // Inject the watcher as a <script> tag into parent document so it runs in
                    // parent's own scope; closures defined in this iframe die when Streamlit
                    // tears the iframe down on logout, leaving pills orphaned.
                    var oldWatcher = doc.getElementById('sugg-watcher');
                    if (oldWatcher) oldWatcher.remove();
                    var watcher = doc.createElement('script');
                    watcher.id = 'sugg-watcher';
                    watcher.textContent =
                        '(function(){' +
                            'if(window.__suggWatcher){clearInterval(window.__suggWatcher);}' +
                            'window.__suggWatcher=setInterval(function(){' +
                                'var cb=document.querySelector(\\'[data-testid="stChatInputContainer"]\\')' +
                                    '||document.querySelector(\\'[data-testid="stChatInput"]\\')' +
                                    '||document.querySelector(\\'[data-testid="stBottomBlockContainer"]\\')' +
                                    '||document.querySelector(\\'div[class*="stChatInput"]\\');' +
                                'if(!cb){' +
                                    'var w=document.getElementById("sugg-wrap");' +
                                    'var s=document.getElementById("sugg-style");' +
                                    'if(w)w.remove();if(s)s.remove();' +
                                    'clearInterval(window.__suggWatcher);' +
                                    'window.__suggWatcher=null;' +
                                    'var self=document.getElementById("sugg-watcher");' +
                                    'if(self)self.remove();' +
                                '}' +
                            '},100);' +
                        '})();';
                    doc.head.appendChild(watcher);
                }

                // Retry up to 10 times (3s total) until chat input is in DOM
                var tries = 0;
                function attempt() {
                    if (findChatBox()) {
                        build();
                    } else if (tries++ < 10) {
                        setTimeout(attempt, 300);
                    }
                }
                attempt();
            })();
            </script>
            """,
            height=1,
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
