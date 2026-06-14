import os
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai

# Mira's profile picture, shown next to every assistant message.
MIRA_AVATAR = str(Path(__file__).parent.parent / "assets" / "brand" / "mira.png")

def show_chatbot_page():
    st.markdown(
        """
        <style>
        .botbox {
            background:#F5F3FF;border:1px solid #F0E8FF;border-radius:14px;padding:24px;margin-bottom:24px;
        }
        /* User messages: align right, hide the avatar, show as a bubble */
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
            flex-direction: row-reverse;
            background: transparent;
            gap: 0 !important;
            padding-right: 0 !important;
        }
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageAvatarUser"] {
            display: none;
        }
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {
            flex-grow: 0;
            max-width: 80%;
            margin-left: auto !important;
            margin-right: 0 !important;
            background: rgba(157,99,232,0.12);
            border: 1px solid rgba(157,99,232,0.22);
            border-radius: 14px;
            padding: 10px 16px;
            text-align: left;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '''
        <div style="padding:24px 0 20px; border-bottom:1px solid rgba(0,0,0,0.07); margin-bottom:24px;">
            <div style="font-family:'Fraunces',serif; font-size:clamp(22px,3vw,36px); color:#1C1917; margin:0 0 8px; letter-spacing:-0.4px; line-height:1.12; font-weight:600; display:flex; align-items:center; gap:16px;">
                <svg width="35" height="35" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="flex-shrink:0;">
                    <defs>
                        <linearGradient id="mira-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stop-color="#9D63E8"/>
                            <stop offset="50%" stop-color="#9D63E8"/>
                            <stop offset="100%" stop-color="#9D63E8"/>
                        </linearGradient>
                    </defs>
                    <path d="M12 2L14.4 9.6L22 12L14.4 14.4L12 22L9.6 14.4L2 12L9.6 9.6L12 2Z" fill="url(#mira-grad)"/>
                </svg>
                Chat with Mira
            </div>
            <p style="font-size:14px; color:#6B6560; margin:0; line-height:1.6; font-family:'Plus Jakarta Sans',sans-serif;">Ask any questions about counseling, mental health, and our platform. Powered by Gemini AI.</p>
        </div>
        ''',
        unsafe_allow_html=True
    )

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        st.error("Developer Setup Required: Please set the GEMINI_API_KEY environment variable to activate the chatbot.")
        return

    genai.configure(api_key=api_key)
    app_context_prompt = """
You are Mira, a warm and knowledgeable assistant for the Client-Counselor Matching System — a platform that uses machine learning to help clients find the right mental health counselor.

PRIMARY ROLE — Platform Guide:
Your main job is to help users navigate the platform. You know everything about how it works:
- The matching questionnaire has 3 steps:
  Step 1 (About You): age, gender, ethnicity.
  Step 2 (Your Needs): primary concern (Anxiety, Depression, Stress, or Trauma) and previous counseling experience.
  Step 3 (Preferences): preferred modality (Cognitive, Behavioral, Humanistic, Psychodynamic), preferred language, preferred counselor gender.
- After submitting, an ML model ranks counselors by compatibility score (0-100%). The top 2 matches are shown.
- Each card shows score, experience, specialization, modality, and language. "View Full Profile" opens a detailed profile.
- An AI-generated paragraph explains why each counselor fits the client.
- "Technical Details - SHAP" shows which factors influenced the match score.
- To connect, clients click "Get to know [name]", enter their name and email, and a coordinator arranges the session.
- Pages available: Find Your Match, Chat Support (here), FAQ, About Us, Privacy Policy, Contact Us.
- Modality guide:
  Cognitive: Restructures negative thoughts and beliefs (e.g. CBT, REBT).
  Behavioral: Changes behaviour through exposure and activation techniques.
  Humanistic: Person-centred, warm, non-judgmental.
  Psychodynamic: Explores how past experiences shape present patterns.

SECONDARY ROLE — Supportive Listener:
When users want to talk about how they feel, listen without judgment, validate their emotions, and respond with warmth. You are not a replacement for a real counselor — if concerns are serious, always guide them to use Find Your Match to connect with a professional.

TONE: Warm, clear, and conversational. Never clinical or robotic.
LIMITS: You are an AI. Never diagnose or prescribe. Redirect serious concerns to a professional counselor through the platform.
"""
    model = genai.GenerativeModel("gemini-2.5-flash-lite", system_instruction=app_context_prompt)

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi, I'm Mira 👋 How can I help you today?"}
        ]

    for msg in st.session_state.messages:
        avatar = MIRA_AVATAR if msg["role"] == "assistant" else None
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    # Read the chat input up front (it stays bottom-pinned regardless of where
    # it's called) so the suggestion pills know if a message is being submitted
    # on this run.
    prompt = st.chat_input("Ask a question...")

    # Scrolling Suggestion Pills — injected into the parent document so they
    # sit directly above the chat input box and span its exact width.
    # They are single-use first-message helpers: only shown when the chat is
    # still just Mira's greeting AND the user isn't submitting a message this
    # run. The `not prompt` guard prevents them re-injecting on the submit run
    # (when the new message hasn't been appended to history yet).
    if len(st.session_state.messages) == 1 and not prompt:
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
                    'How does the counselor matching work? 🤝',
                    'What questions are in the assessment? 📝',
                    'How do I contact a matched counselor? 📩',
                    'What counseling modality should I choose? 🧠',
                    'Feeling really overwhelmed today 😔',
                    'I just need someone to talk to 💬'
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
                            'border:1px solid #F0E8FF;' +
                            'border-radius:20px;' +
                            'padding:9px 18px;' +
                            'font-size:13px;' +
                            'font-family:Plus Jakarta Sans,sans-serif;' +
                            'color:#6B6560;' +
                            'white-space:nowrap;' +
                            'box-shadow:0 2px 8px rgba(157,99,232,0.08);' +
                            'cursor:pointer;' +
                            'pointer-events:auto;' +
                            'transition:background 0.18s,border-color 0.18s,color 0.18s;' +
                            'user-select:none;' +
                        '}' +
                        '.sugg-pill:hover{' +
                            'background:#F5F3FF;' +
                            'border-color:#9D63E8;' +
                            'color:#9D63E8;' +
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
    else:
        # Reliable removal path: when the user is submitting (prompt set) or the
        # chat has moved past Mira's greeting, strip any leftover pills from the
        # parent document. The in-strip dismiss handlers can miss this because
        # the component iframe gets torn down on rerun before they fire.
        components.html(
            """
            <script>
            (function() {
                var doc = window.parent.document;
                ['sugg-wrap', 'sugg-style', 'sugg-watcher'].forEach(function(id) {
                    var el = doc.getElementById(id);
                    if (el) el.remove();
                });
                if (window.parent.__suggWatcher) {
                    window.parent.clearInterval(window.parent.__suggWatcher);
                    window.parent.__suggWatcher = null;
                }
            })();
            </script>
            """,
            height=0,
        )

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar=MIRA_AVATAR):
            message_placeholder = st.empty()

            try:
                # Skip any initial assistant greeting — Gemini history must start with "user"
                _SKIP = {
                    "Hello! I am your AI mental health assistant. How can I help you today?",
                    "Hi, I'm Mira 👋 How can I help you today?",
                }
                valid_history = []
                for m in st.session_state.messages[:-1]:
                    if m["content"] in _SKIP:
                        continue
                    valid_history.append({"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]})

                chat_session = model.start_chat(history=valid_history)

                response = chat_session.send_message(prompt, stream=True)
                full_response = ""

                for chunk in response:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")

                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})

            except Exception as e:
                st.error(f"Error connecting to Gemini: {str(e)}")
