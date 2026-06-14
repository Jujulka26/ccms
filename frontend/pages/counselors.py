import streamlit as st
import streamlit.components.v1 as components

from frontend.utils.api import get_counselors
from frontend.utils.avatar import avatar_html
from frontend.pages.matching import show_profile_dialog, show_request_success_dialog, MAX_CASELOAD


_SPEC_COLORS = {
    "Anxiety":    ("#F5F3FF", "#9D63E8"),
    "Depression": ("#FFF7ED", "#C2410C"),
    "Stress":     ("#F0FDF4", "#15803D"),
    "Trauma":     ("#FFF1F2", "#BE123C"),
}

_MODALITY_ICONS = {
    "Cognitive": "🧠", "Behavioral": "🌿", "Humanistic": "🤝", "Psychodynamic": "💡",
}


def inject_styles():
    st.markdown(
        """
        <style>

        .filter-bar {
            background: #FFFFFF; border-radius: 16px;
            padding: 20px 24px; border: 1px solid rgba(0,0,0,0.06);
            margin-bottom: 28px;
        }
        .filter-label {
            font-size: 11px; font-weight: 700; letter-spacing: 0.08em;
            text-transform: uppercase; color: #9D63E8; margin-bottom: 10px;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }

        .c-card {
            background: #FFFFFF; border-radius: 20px;
            padding: 24px 24px 0; border: 1px solid rgba(0,0,0,0.06);
            display: flex; flex-direction: column;
            overflow: hidden;
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
        }
        .c-card:hover {
            border-color: rgba(157,99,232,0.3);
            box-shadow: 0 4px 20px rgba(157,99,232,0.1);
        }
        .card-view-btn-dir {
            display: block; width: calc(100% + 48px); margin: 18px -24px 0;
            padding: 14px 24px; background: transparent; border: none;
            border-top: 1px solid rgba(0,0,0,0.07);
            color: #9D63E8; font-size: 12px; font-weight: 700;
            letter-spacing: 0.08em; text-transform: uppercase;
            cursor: pointer; text-align: center;
            font-family: 'Plus Jakarta Sans', sans-serif;
            transition: background 0.15s, color 0.15s;
        }
        .card-view-btn-dir:hover { background: rgba(157,99,232,0.06); color: #9D63E8; }
        [data-testid="stElementContainer"]:has(.c-card) { margin-bottom: 24px !important; }
        .c-avatar-wrap {
            display: flex; align-items: center; gap: 14px; margin-bottom: 16px;
        }
        .c-name {
            font-family: 'Fraunces', serif;
            font-size: 17px; color: #1C1917; margin: 0 0 2px; font-weight: 600;
        }
        .c-title { font-size: 12px; color: #9D63E8; font-weight: 600; margin: 0; font-family: 'Plus Jakarta Sans', sans-serif; }
        .c-spec-badge {
            display: inline-block; font-size: 11px; font-weight: 700;
            letter-spacing: 0.05em; text-transform: uppercase;
            border-radius: 20px; padding: 3px 12px; margin-bottom: 14px;
            align-self: flex-start; font-family: 'Plus Jakarta Sans', sans-serif;
        }
        .c-info { display: flex; flex-direction: column; gap: 7px; margin-bottom: 18px; flex: 1; }
        .c-info-row {
            display: flex; align-items: center; gap: 8px;
            font-size: 13px; color: #6B6560; font-family: 'Plus Jakarta Sans', sans-serif;
        }
        .c-info-icon { font-size: 14px; flex-shrink: 0; }

        .result-count {
            font-size: 13px; color: #9D63E8; font-weight: 600;
            margin-bottom: 20px; letter-spacing: 0.02em;
            font-family: 'Plus Jakarta Sans', sans-serif;
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

    st.markdown(
        """
        <div style="padding:24px 0 20px; border-bottom:1px solid rgba(0,0,0,0.07); margin-bottom:24px;">
            <div style="font-family:'Fraunces',serif; font-size:clamp(22px,3vw,36px); color:#1C1917; margin:0 0 8px; letter-spacing:-0.4px; line-height:1.12; font-weight:600; display:flex; align-items:center; gap:16px;">
                <svg width="35" height="35" viewBox="0 0 24 24" fill="none" stroke="#9D63E8" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0;">
                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                    <circle cx="9" cy="7" r="4"/>
                    <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                    <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                </svg>
                Meet Our Counselors
            </div>
            <p style="font-size:14px; color:#6B6560; margin:0; line-height:1.6; font-family:'Plus Jakarta Sans',sans-serif;">Get to know our counselors and find one that's right for you.</p>
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

    components.html(
        """
        <script>
        (function() {
            var doc = window.parent.document;
            function styleSelects() {
                doc.querySelectorAll('[data-baseweb="select"] > div').forEach(function(el) {
                    el.style.setProperty('background-color', '#FFFFFF', 'important');
                    el.style.setProperty('border', '1.5px solid rgba(157,99,232,0.4)', 'important');
                    el.style.setProperty('border-radius', '10px', 'important');
                });
            }
            styleSelects();
            [100, 300, 600].forEach(function(t) { setTimeout(styleSelects, t); });
            new MutationObserver(styleSelects).observe(doc.body, { subtree: true, childList: true });
        })();
        </script>
        """,
        height=0, width=0,
    )

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
        avail    = c.get("availability") or "—"

        spec_bg, spec_color = _SPEC_COLORS.get(spec, ("#F3F4F6", "#374151"))
        mod_icon = _MODALITY_ICONS.get(modality.split(",")[0].strip(), "💬")
        av = avatar_html(name, c.get("image"), size=56, radius=12)
        is_full = int(c.get("caseload") or 0) >= MAX_CASELOAD
        full_badge = (
            '<span class="c-spec-badge" style="background:#FEF2F2; color:#B91C1C; margin-left:6px;">🚫 Fully booked</span>'
            if is_full else ""
        )

        with cols[i % 3]:
            st.markdown(
                f"""
                <div class="c-card">
                    <div class="c-avatar-wrap">
                        {av}
                        <div>
                            <div class="c-name">{name}</div>
                            <div class="c-title">Registered Counsellor (LKM)</div>
                        </div>
                    </div>
                    <span class="c-spec-badge"
                          style="background:{spec_bg}; color:{spec_color};">{spec}</span>{full_badge}
                    <div class="c-info">
                        <div class="c-info-row"><span class="c-info-icon">🏅</span>{exp} yrs experience</div>
                        <div class="c-info-row"><span class="c-info-icon">{mod_icon}</span>{modality}</div>
                        <div class="c-info-row"><span class="c-info-icon">💬</span>{lang}</div>
                        <div class="c-info-row"><span class="c-info-icon">🕒</span>{avail}</div>
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
                border: 1.5px solid rgba(157,99,232,0.25) !important;
                color: #9D63E8 !important;
                border-radius: 50px !important;
                font-family: 'Plus Jakarta Sans', sans-serif !important;
                font-size: 13px !important;
                font-weight: 600 !important;
                letter-spacing: 0.04em !important;
                padding: 10px 24px !important;
                transition: all 0.2s ease !important;
                box-shadow: 0 1px 4px rgba(157,99,232,0.08) !important;
            }
            .st-key-dir_prev button:hover:not(:disabled), .st-key-dir_next button:hover:not(:disabled) {
                background: rgba(157,99,232,0.06) !important;
                border-color: #9D63E8 !important;
                box-shadow: 0 2px 10px rgba(157,99,232,0.15) !important;
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
                f'<span style="width:8px;height:8px;border-radius:50%;display:inline-block;margin:0 4px;background:{"#9D63E8" if i == page else "#E8D5FD"};"></span>'
                for i in range(total_pages)
            )

            st.markdown(
                f'<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;padding-top:8px;font-family:\'Plus Jakarta Sans\',sans-serif;">'
                f'<div style="display:flex;align-items:center;gap:4px;">{dots}</div>'
                f'<span style="font-size:12px;color:#9C9790;">{page+1} / {total_pages}</span>'
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
