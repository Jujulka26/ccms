import base64
import os
import streamlit as st
import streamlit.components.v1 as components

from frontend.utils.api import get_counselors
from frontend.utils.avatar import avatar_html
from frontend.views.matching import show_profile_dialog, show_request_success_dialog


_SPEC_COLORS = {
    "Anxiety":    ("#F3F0FF", "#6D28D9"),
    "Depression": ("#FFF7ED", "#C2410C"),
    "Stress":     ("#F0FDF4", "#15803D"),
    "Trauma":     ("#FFF1F2", "#BE123C"),
}

_MODALITY_ICONS = {
    "CBT": "🧠", "Mindfulness": "🌿", "Humanistic": "🤝", "REBT": "💡",
}


def inject_styles():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

        .dir-hero {
            position: relative; overflow: hidden;
            background-color: #FAFAFF;
            background-image: radial-gradient(at 0% 0%, #E9DFFF 0px, transparent 60%), radial-gradient(at 100% 100%, #F0E6FF 0px, transparent 60%);
            border-radius: 20px; padding: 48px 52px; margin-bottom: 32px;
            border: 1px solid rgba(124,58,237,0.15);
            box-shadow: 0 16px 32px -8px rgba(124,58,237,0.12), inset 0 1px 0 rgba(255,255,255,0.9);
        }
        .dir-hero-content { display: flex; align-items: center; position: relative; z-index: 2; }
        .dir-hero-text { flex: 1; min-width: 0; max-width: 60%; }
        .dir-hero-image-wrap { position: absolute; top: -48px; bottom: -48px; right: 0; width: 38%; pointer-events: none; z-index: 1; }
        .dir-hero-img { width: 100%; height: 100%; object-fit: contain; object-position: right center; opacity: 0.9; mix-blend-mode: multiply; -webkit-mask-image: linear-gradient(to right, transparent 0%, rgba(0,0,0,0.5) 30%, black 60%); mask-image: linear-gradient(to right, transparent 0%, rgba(0,0,0,0.5) 30%, black 60%); }
        .dir-eyebrow {
            display: inline-block; font-size: 11px; font-weight: 700; letter-spacing: 0.12em;
            text-transform: uppercase; color: #8B5CF6; background: rgba(167,139,250,0.12);
            border: 1px solid rgba(167,139,250,0.25); border-radius: 20px; padding: 4px 14px; margin-bottom: 16px;
        }
        .dir-title { font-family: 'DM Serif Display', serif; font-size: 42px; color: #1A1A2E; margin: 0 0 12px; line-height: 1.15; letter-spacing: -0.5px; }
        .dir-subtitle { font-size: 16px; color: #4A4A5C; margin: 0; line-height: 1.65; max-width: 520px; }

        .filter-bar {
            background: #FFFFFF; border-radius: 16px;
            padding: 20px 24px; border: 1px solid rgba(0,0,0,0.06);
            margin-bottom: 28px;
        }
        .filter-label {
            font-size: 11px; font-weight: 700; letter-spacing: 0.08em;
            text-transform: uppercase; color: #8B5CF6; margin-bottom: 10px;
        }

        .c-card {
            background: #FFFFFF; border-radius: 20px;
            padding: 24px 24px 0; border: 1px solid rgba(0,0,0,0.06);
            display: flex; flex-direction: column;
            overflow: hidden;
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
        }
        .c-card:hover {
            border-color: rgba(139,92,246,0.3);
            box-shadow: 0 4px 20px rgba(139,92,246,0.1);
        }
        .card-view-btn-dir {
            display: block; width: calc(100% + 48px); margin: 18px -24px 0;
            padding: 14px 24px; background: transparent; border: none;
            border-top: 1px solid rgba(0,0,0,0.07);
            color: #7C3AED; font-size: 12px; font-weight: 700;
            letter-spacing: 0.08em; text-transform: uppercase;
            cursor: pointer; text-align: center;
            font-family: 'DM Sans', sans-serif;
            transition: background 0.15s, color 0.15s;
        }
        .card-view-btn-dir:hover { background: rgba(124,58,237,0.07); color: #5B21B6; }
        [data-testid="stElementContainer"]:has(.c-card) { margin-bottom: 24px !important; }
        .c-avatar-wrap {
            display: flex; align-items: center; gap: 14px; margin-bottom: 16px;
        }
        .c-name {
            font-family: 'DM Serif Display', serif;
            font-size: 17px; color: #1A1A2E; margin: 0 0 2px;
        }
        .c-title { font-size: 12px; color: #8B5CF6; font-weight: 600; margin: 0; }
        .c-spec-badge {
            display: inline-block; font-size: 11px; font-weight: 700;
            letter-spacing: 0.05em; text-transform: uppercase;
            border-radius: 20px; padding: 3px 12px; margin-bottom: 14px;
            align-self: flex-start;
        }
        .c-info { display: flex; flex-direction: column; gap: 7px; margin-bottom: 18px; flex: 1; }
        .c-info-row {
            display: flex; align-items: center; gap: 8px;
            font-size: 13px; color: #5A5A6E;
        }
        .c-info-icon { font-size: 14px; flex-shrink: 0; }

        .result-count {
            font-size: 13px; color: #8B5CF6; font-weight: 600;
            margin-bottom: 20px; letter-spacing: 0.02em;
        }
        [class*="st-key-dir_vp_"] { display: none !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_counselors_page():
    inject_styles()

    if "_success_name" in st.session_state:
        _sname = st.session_state["_success_name"]
        del st.session_state["_success_name"]
        show_request_success_dialog(_sname)

    if "hero_img_1_b64" not in st.session_state:
        try:
            with open(os.path.join("frontend", "assets", "ourcounselor.png"), "rb") as f:
                st.session_state["hero_img_1_b64"] = base64.b64encode(f.read()).decode()
        except FileNotFoundError:
            st.session_state["hero_img_1_b64"] = None
    b64 = st.session_state["hero_img_1_b64"]
    img_tag = f'<img src="data:image/png;base64,{b64}" class="dir-hero-img" alt="" />' if b64 else ""

    st.markdown(
        f"""
        <div class="dir-hero">
            <div class="dir-hero-content">
                <div class="dir-hero-text">
                    <div class="dir-eyebrow">Our Team</div>
                    <div class="dir-title">Meet Our Counselors</div>
                    <p class="dir-subtitle">Get to know our counselors before you match.</p>
                </div>
                <div class="dir-hero-image-wrap">{img_tag}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    counselors = get_counselors()
    if not counselors:
        st.info("No counselors available at the moment.")
        return

    # ── Collect filter options ────────────────────────────────────────────────
    all_specs = sorted({c.get("specialization", "") for c in counselors if c.get("specialization")})
    all_langs = sorted({
        lang.strip()
        for c in counselors
        for lang in str(c.get("counselor_language", "")).split(",")
        if lang.strip()
    })
    all_modalities = sorted({
        mod.strip()
        for c in counselors
        for mod in str(c.get("counselor_modality", "")).split(",")
        if mod.strip()
    })

    # ── Filter bar ────────────────────────────────────────────────────────────
    st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
    st.markdown('<div class="filter-label">Filter Counselors</div>', unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3, gap="medium")
    with f1:
        sel_spec = st.selectbox("Specialization", ["All"] + all_specs, key="dir_spec")
    with f2:
        sel_lang = st.selectbox("Language", ["All"] + all_langs, key="dir_lang")
    with f3:
        sel_mod = st.selectbox("Modality", ["All"] + all_modalities, key="dir_mod")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Apply filters ─────────────────────────────────────────────────────────
    filtered = counselors
    if sel_spec != "All":
        filtered = [c for c in filtered if c.get("specialization") == sel_spec]
    if sel_lang != "All":
        filtered = [c for c in filtered if sel_lang in str(c.get("counselor_language", ""))]
    if sel_mod != "All":
        filtered = [c for c in filtered if sel_mod in str(c.get("counselor_modality", ""))]

    total = len(filtered)
    st.markdown(
        f'<div class="result-count">Showing {total} counselor{"s" if total != 1 else ""}</div>',
        unsafe_allow_html=True,
    )

    if not filtered:
        st.info("No counselors match the selected filters.")
        return

    # ── Pagination ───────────────────────────────────────────────────────────
    PAGE_SIZE = 9
    total_pages = max(1, -(-len(filtered) // PAGE_SIZE))  # ceiling division

    if "dir_page" not in st.session_state or st.session_state.get("dir_last_total") != len(filtered):
        st.session_state["dir_page"] = 0
    st.session_state["dir_last_total"] = len(filtered)

    page = st.session_state["dir_page"]
    page_items = filtered[page * PAGE_SIZE : (page + 1) * PAGE_SIZE]

    # ── Grid ─────────────────────────────────────────────────────────────────
    cols = st.columns(3, gap="large")
    for i, c in enumerate(page_items):
        name     = c.get("name", "Counselor")
        spec     = c.get("specialization", "")
        exp      = c.get("experience_years", "—")
        lang     = c.get("counselor_language", "—")
        modality = c.get("counselor_modality", "—")

        spec_bg, spec_color = _SPEC_COLORS.get(spec, ("#F3F4F6", "#374151"))
        mod_icon = _MODALITY_ICONS.get(modality.split(",")[0].strip(), "💬")
        av = avatar_html(name, c.get("image"), size=56, radius=12)

        with cols[i % 3]:
            st.markdown(
                f"""
                <div class="c-card">
                    <div class="c-avatar-wrap">
                        {av}
                        <div>
                            <div class="c-name">{name}</div>
                            <div class="c-title">Licensed Counselor</div>
                        </div>
                    </div>
                    <span class="c-spec-badge"
                          style="background:{spec_bg}; color:{spec_color};">{spec}</span>
                    <div class="c-info">
                        <div class="c-info-row"><span class="c-info-icon">🏅</span>{exp} yrs experience</div>
                        <div class="c-info-row"><span class="c-info-icon">{mod_icon}</span>{modality}</div>
                        <div class="c-info-row"><span class="c-info-icon">💬</span>{lang}</div>
                    </div>
                    <button class="card-view-btn-dir">VIEW FULL PROFILE →</button>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("View Full Profile", key=f"dir_vp_{c.get('counselor_id')}_{i}",
                         use_container_width=True):
                show_profile_dialog(c)

    # ── Pagination controls ───────────────────────────────────────────────────
    if total_pages > 1:
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        st.markdown(
            """
            <style>
            .st-key-dir_prev button, .st-key-dir_next button {
                background: #FFFFFF !important;
                border: 1.5px solid rgba(109,40,217,0.25) !important;
                color: #6D28D9 !important;
                border-radius: 50px !important;
                font-family: 'DM Sans', sans-serif !important;
                font-size: 13px !important;
                font-weight: 600 !important;
                letter-spacing: 0.04em !important;
                padding: 10px 24px !important;
                transition: all 0.2s ease !important;
                box-shadow: 0 1px 4px rgba(109,40,217,0.08) !important;
            }
            .st-key-dir_prev button:hover:not(:disabled), .st-key-dir_next button:hover:not(:disabled) {
                background: rgba(109,40,217,0.06) !important;
                border-color: #6D28D9 !important;
                box-shadow: 0 2px 10px rgba(109,40,217,0.15) !important;
            }
            .st-key-dir_prev button:disabled, .st-key-dir_next button:disabled {
                opacity: 0.35 !important;
                cursor: not-allowed !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        pcol1, pcol2, pcol3 = st.columns([1, 2, 1])
        with pcol1:
            if st.button("← Previous", key="dir_prev", disabled=(page == 0), use_container_width=True):
                st.session_state["dir_page"] -= 1
                st.rerun()
        with pcol2:
            dots = "".join(
                f'<span style="width:8px;height:8px;border-radius:50%;display:inline-block;margin:0 4px;background:{"#8B5CF6" if i == page else "#D8D0F5"};"></span>'
                for i in range(total_pages)
            )
            st.markdown(
                f'<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;padding-top:8px;">'
                f'<div style="display:flex;align-items:center;gap:4px;">{dots}</div>'
                f'<span style="font-size:12px;color:#8B8B9A;">{page+1} / {total_pages}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with pcol3:
            if st.button("Next →", key="dir_next", disabled=(page >= total_pages - 1), use_container_width=True):
                st.session_state["dir_page"] += 1
                st.rerun()

    components.html(
        """
        <script>
        (function() {
            function run() {
                var doc = window.parent.document;
                doc.querySelectorAll('.card-view-btn-dir').forEach(function(btn) {
                    if (btn._ready) return;
                    var container = btn.closest('[data-testid="stElementContainer"]');
                    if (!container) return;
                    var sibling = container.nextElementSibling;
                    while (sibling) {
                        var stBtn = sibling.querySelector('[data-testid="stButton"] button');
                        if (stBtn) {
                            btn._ready = true;
                            (function(b, nb) {
                                b.addEventListener('click', function() { nb.click(); });
                            })(btn, stBtn);
                            break;
                        }
                        sibling = sibling.nextElementSibling;
                    }
                });
            }
            [0, 150, 400, 800].forEach(function(t) { setTimeout(run, t); });
            new MutationObserver(run).observe(
                window.parent.document.body,
                { subtree: true, childList: true }
            );
        })();
        </script>
        """,
        height=0, width=0,
    )
