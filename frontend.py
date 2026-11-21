import os
import re
import time
import uuid
import streamlit as st

from langchain_core.messages import HumanMessage
from langgraph.types import Command

from graph import app


# ============================================================
# MARKDOWN & TAG SANITIZATION HELPER
# ============================================================

def _clean_md(text: str) -> str:
    """
    Strip HTML tags (especially <br>) that LLMs frequently insert
    into Markdown table cells so they render natively without glitching.
    """
    if not text:
        return text
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()


# ============================================================
# PAGE CONFIGURATION - TEVELO BRANDING & FULL WIDTH
# ============================================================

st.set_page_config(
    page_title="Tevelo • Intelligent Travel, Effortlessly Planned",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        "Get Help": "https://github.com/prajith-pycluster/AeroAgent",
        "Report a bug": "https://github.com/prajith-pycluster/AeroAgent/issues",
        "About": "Tevelo — Autonomous Multi-Agent AI Travel Intelligence Platform",
    },
)


# ============================================================
# TEVELO PREMIUM DESIGN SYSTEM - PURE LIGHT / WHITE THEME
# ============================================================

custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

:root {
    --bg-main: #ffffff;
    --bg-secondary: #f8fafc;
    --bg-tertiary: #f1f5f9;
    --text-primary: #0f172a;
    --text-secondary: #475569;
    --text-muted: #64748b;
    --border-subtle: #e2e8f0;
    --border-strong: #cbd5e1;
    --primary: #2563eb;
    --primary-hover: #1d4ed8;
    --primary-light: #eff6ff;
    --primary-border: #bfdbfe;
    --success: #10b981;
    --success-light: #ecfdf5;
    --success-border: #a7f3d0;
    --accent-indigo: #4f46e5;
}

/* 1. COMPLETELY HIDE STREAMLIT SIDEBAR AND TOGGLE */
[data-testid="stSidebar"],
[data-testid="collapsedControl"],
section[data-testid="stSidebar"] {
    display: none !important;
    visibility: hidden !important;
    width: 0 !important;
}

/* 2. BASE APP CONTAINER & TYPOGRAPHY */
html, body, [data-testid="stAppViewContainer"], .stApp {
    background-color: #ffffff !important;
    color: var(--text-primary) !important;
    font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

[data-testid="stHeader"] {
    background: rgba(255, 255, 255, 0.95) !important;
    backdrop-filter: blur(12px) !important;
    border-bottom: 1px solid var(--border-subtle);
}

.main .block-container {
    max-width: 1200px !important;
    padding-top: 1.5rem !important;
    padding-bottom: 3.5rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}

/* 3. HEADINGS HIERARCHY */
h1, h2, h3, h4, h5 {
    color: var(--text-primary) !important;
    font-weight: 700 !important;
    letter-spacing: -0.025em !important;
}

h1 {
    font-size: 2.4rem !important;
    line-height: 1.2 !important;
}

h2 {
    font-size: 1.6rem !important;
    margin-top: 1.25rem !important;
    margin-bottom: 0.5rem !important;
}

h3 {
    font-size: 1.15rem !important;
}

/* 4. BUTTONS - CLEAN, ROUNDED & PROPORTIONATE */
.stButton > button {
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 0.925rem !important;
    padding: 0.55rem 1.25rem !important;
    border: 1px solid var(--border-subtle) !important;
    background: #ffffff !important;
    color: var(--text-primary) !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04) !important;
}

.stButton > button:hover {
    border-color: var(--border-strong) !important;
    background: var(--bg-secondary) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06) !important;
    color: var(--primary) !important;
}

/* Primary Button Styling */
[data-testid="stBaseButton-primary"] > button,
button[kind="primary"] {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
    color: #ffffff !important;
    border: none !important;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.25) !important;
}

[data-testid="stBaseButton-primary"] > button:hover,
button[kind="primary"]:hover {
    background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%) !important;
    color: #ffffff !important;
    box-shadow: 0 6px 20px rgba(37, 99, 235, 0.35) !important;
    transform: translateY(-2px) !important;
}

/* 5. FORM INPUTS & TEXTAREAS */
.stTextInput input,
.stTextArea textarea {
    background-color: #ffffff !important;
    border: 1.5px solid var(--border-subtle) !important;
    border-radius: 14px !important;
    padding: 14px 16px !important;
    color: var(--text-primary) !important;
    font-size: 0.975rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02) inset !important;
}

.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12) !important;
    outline: none !important;
}

/* 6. METRIC CARDS */
[data-testid="stMetric"] {
    background: #ffffff !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 14px !important;
    padding: 0.9rem 1.15rem !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03) !important;
    transition: all 0.2s ease !important;
}

[data-testid="stMetric"]:hover {
    border-color: var(--border-strong) !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
}

[data-testid="stMetricLabel"] {
    color: var(--text-muted) !important;
    font-size: 0.775rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.04em !important;
}

[data-testid="stMetricValue"],
[data-testid="stMetricValue"] * {
    color: var(--text-primary) !important;
    font-size: clamp(1rem, 1.2vw, 1.25rem) !important;
    font-weight: 800 !important;
    letter-spacing: -0.01em !important;
    white-space: nowrap !important;
}

/* 7. CARDS & BORDERED CONTAINERS */
div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff !important;
    border-radius: 16px !important;
    border: 1px solid var(--border-subtle) !important;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.03) !important;
    padding: 1.25rem !important;
    transition: all 0.2s ease !important;
}

div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: var(--border-strong) !important;
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.04) !important;
}

/* 8. IMAGES */
[data-testid="stImage"] img {
    border-radius: 16px !important;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.05) !important;
}

/* 9. BADGES & CHIPS */
.brand-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px;
    background: #eff6ff;
    color: #1d4ed8;
    border: 1px solid #bfdbfe;
    border-radius: 9999px;
    font-size: 0.825rem;
    font-weight: 600;
    margin-bottom: 0.85rem;
}

.status-dot {
    width: 8px;
    height: 8px;
    background-color: #10b981;
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2);
}

.card-badge {
    display: inline-flex;
    align-items: center;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 0.775rem;
    font-weight: 700;
    letter-spacing: 0.03em;
    text-transform: uppercase;
}

.badge-flight { background: #e0f2fe; color: #0284c7; border: 1px solid #bae6fd; }
.badge-hotel { background: #f3e8ff; color: #7c3aed; border: 1px solid #ddd6fe; }
.badge-weather { background: #fef3c7; color: #d97706; border: 1px solid #fde68a; }
.badge-budget { background: #ecfdf5; color: #059669; border: 1px solid #a7f3d0; }
.badge-agent { background: #eef2ff; color: #4f46e5; border: 1px solid #c7d2fe; }

/* 10. POPOVER (SETTINGS & PREFERENCES) */
[data-testid="stPopover"] > button {
    border-radius: 9999px !important;
    padding: 0.4rem 1rem !important;
    font-size: 0.85rem !important;
    border: 1px solid var(--border-subtle) !important;
    background: #ffffff !important;
}

/* 11. DIVIDERS */
hr {
    border-color: var(--border-subtle) !important;
    margin: 2rem 0 !important;
    opacity: 0.75 !important;
}

/* 12. TAB NAVIGATION */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: #f8fafc;
    padding: 6px;
    border-radius: 12px;
    border: 1px solid var(--border-subtle);
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    padding: 8px 16px !important;
    font-weight: 600 !important;
    color: var(--text-secondary) !important;
}

.stTabs [aria-selected="true"] {
    background-color: #ffffff !important;
    color: var(--primary) !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
}
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)


# ============================================================
# CURATED HIGH-RES IMAGES
# ============================================================

IMAGES = {
    "airplane": (
        "https://images.unsplash.com/"
        "photo-1436491865332-7a61a109cc05"
        "?auto=format&fit=crop&w=1200&q=85"
    ),
    "dubai": (
        "https://images.unsplash.com/"
        "photo-1512453979798-5ea266f8880c"
        "?auto=format&fit=crop&w=800&q=85"
    ),
    "tokyo": (
        "https://images.unsplash.com/"
        "photo-1540959733332-eab4deabeeaf"
        "?auto=format&fit=crop&w=800&q=85"
    ),
    "paris": (
        "https://images.unsplash.com/"
        "photo-1502602898657-3e91760cbb34"
        "?auto=format&fit=crop&w=800&q=85"
    ),
    "london": (
        "https://images.unsplash.com/"
        "photo-1513635269975-59663e0ac1ad"
        "?auto=format&fit=crop&w=800&q=85"
    ),
    "istanbul": (
        "https://images.unsplash.com/"
        "photo-1524231757912-21f4fe3a7200"
        "?auto=format&fit=crop&w=800&q=85"
    ),
}


# ============================================================
# SESSION STATE INITIALIZATION (PRESERVING BACKEND VALUES)
# ============================================================

if "user_id" not in st.session_state:
    st.session_state.user_id = "traveler_001"

if "thread_id" not in st.session_state:
    st.session_state.thread_id = f"{st.session_state.user_id}_{uuid.uuid4().hex[:8]}"

if "latest_result" not in st.session_state:
    st.session_state.latest_result = None

if "waiting_for_approval" not in st.session_state:
    st.session_state.waiting_for_approval = False

if "agent_progress" not in st.session_state:
    st.session_state.agent_progress = {}

if "query_input" not in st.session_state:
    st.session_state.query_input = ""

user_id = st.session_state.user_id


# ============================================================
# TOP NAVIGATION & BRAND IDENTITY BAR
# ============================================================

nav_col1, nav_col2, nav_col3 = st.columns([1.8, 2, 1.2], gap="small")

with nav_col1:
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 12px; padding: 4px 0;">
            <div style="
                background: linear-gradient(135deg, #2563eb, #1d4ed8);
                color: white;
                width: 38px;
                height: 38px;
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.25rem;
                box-shadow: 0 4px 10px rgba(37,99,235,0.22);
            ">✈️</div>
            <div>
                <div style="font-size: 1.35rem; font-weight: 800; color: #0f172a; line-height: 1.1; letter-spacing: -0.02em;">Tevelo</div>
                <div style="font-size: 0.725rem; color: #64748b; font-weight: 600; letter-spacing: 0.02em;">Intelligent Travel, Effortlessly Planned</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with nav_col2:
    st.markdown(
        """
        <div style="display: flex; align-items: center; justify-content: center; gap: 24px; height: 100%; font-size: 0.9rem; font-weight: 600;">
            <span style="color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 2px;">Home</span>
            <span style="color: #64748b; cursor: default;">Explore</span>
            <span style="color: #64748b; cursor: default;">My Trips</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with nav_col3:
    # PRESERVED CONTROLS: Model, Traveler ID, New Trip & Reset in clean popover
    with st.popover("⚙️ Settings & System", use_container_width=True):
        st.markdown("##### 👤 Traveler Profile")
        new_uid = st.text_input(
            "Traveler ID",
            value=st.session_state.user_id,
            key="user_id_pref",
            help="Unique identifier for state persistence",
        )
        if new_uid != st.session_state.user_id:
            st.session_state.user_id = new_uid
            user_id = new_uid

        st.markdown("##### 🧠 AI Reasoning Engine")
        selected_model_option = st.selectbox(
            "Active Model",
            [
                "openai/gpt-oss-120b (Groq Flagship)",
                "openai/gpt-oss-20b (Groq Fast)",
                "qwen/qwen3.8-27b (Groq Qwen)",
                "gemini-3.8-flash (Google Gemini)",
            ],
            index=0,
            help="Select which LLM model powers the multi-agent workflow",
        )
        chosen_model_id = selected_model_option.split(" ")[0]
        os.environ["GROQ_MODEL"] = chosen_model_id
        if "gemini" in chosen_model_id:
            os.environ["GEMINI_MODEL"] = chosen_model_id

        st.divider()

        st.markdown(
            f"""
            <div style="font-size: 0.775rem; color: #64748b; margin-bottom: 8px;">
                <strong>Session Thread:</strong><br>
                <code style="color: #2563eb; background: #eff6ff; padding: 2px 6px; border-radius: 4px;">{st.session_state.thread_id}</code>
            </div>
            """,
            unsafe_allow_html=True,
        )

        p_btn1, p_btn2 = st.columns(2)
        with p_btn1:
            if st.button("🆕 New Trip", use_container_width=True):
                st.session_state.thread_id = f"{user_id}_{uuid.uuid4().hex[:8]}"
                st.session_state.latest_result = None
                st.session_state.waiting_for_approval = False
                st.session_state.query_input = ""
                st.rerun()
        with p_btn2:
            if st.button("🔄 Reset", use_container_width=True):
                st.session_state.clear()
                st.rerun()

st.divider()


# ============================================================
# HERO SECTION - CENTERED, ELEGANT & BALANCED
# ============================================================

hero_left, hero_right = st.columns([1.5, 1.1], gap="large")

with hero_left:
    st.markdown(
        """
        <div class="brand-pill">
            <span class="status-dot"></span> Autonomous Multi-Agent Travel Platform
        </div>
        <h1 style="color: #0f172a; margin-bottom: 0.6rem;">
            Where would you like to travel?
        </h1>
        <h3 style="color: #2563eb; font-weight: 700; margin-top: 0; margin-bottom: 1rem; font-size: 1.35rem;">
            Your Journey. Intelligently Planned.
        </h3>
        <p style="color: #475569; font-size: 1.05rem; line-height: 1.65; margin-bottom: 1.5rem;">
            Discover destinations, explore travel possibilities and let intelligent AI agents coordinate your flights, accommodation, weather and budget.
        </p>
        """,
        unsafe_allow_html=True,
    )

    stat1, stat2, stat3 = st.columns(3)
    with stat1:
        st.metric(label="AI AGENTS", value="6 Specialists")
    with stat2:
        st.metric(label="TOOL LAYER", value="MCP Live")
    with stat3:
        st.metric(label="APPROVAL", value="Human Gate")

with hero_right:
    st.image(
        IMAGES["airplane"],
        use_container_width=True,
        caption="Tevelo • Coordinated Multi-Agent Flight & Stay Synthesis",
    )

st.divider()


# ============================================================
# DESTINATION SHOWCASE & 1-CLICK DISCOVERY
# ============================================================

st.markdown(
    """
    <div style="text-align: center; margin-bottom: 1.5rem;">
        <h2 style="margin: 0; color: #0f172a;">Explore Top Global Destinations</h2>
        <p style="color: #64748b; font-size: 0.95rem; margin-top: 0.25rem;">
            Select any destination below to immediately load a verified multi-day itinerary template:
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

destinations = [
    ("🇦🇪", "Dubai", "United Arab Emirates", "dubai", "Plan a 4-day luxury trip to Dubai. Focus on high-end dining, desert safari, Burj Khalifa, and modern skyline views. Budget Rs. 3,50,000."),
    ("🇯🇵", "Tokyo", "Japan", "tokyo", "Plan a 7-day cultural and tech exploration in Tokyo, Japan. Include Shibuya, Akihabara, traditional temples, and authentic ramen spots. Budget Rs. 2,80,000."),
    ("🇫🇷", "Paris", "France", "paris", "Plan a romantic 5-day trip to Paris, France. Include Louvre, Eiffel Tower, boutique cafes in Le Marais, and relaxed evening river walks. Budget Rs. 2,20,000."),
    ("🇬🇧", "London", "United Kingdom", "london", "Plan a 6-day historic trip to London, UK. Include West End theater, British Museum, scenic parks, and historic pubs. Budget Rs. 2,60,000."),
    ("🇹🇷", "Istanbul", "Türkiye", "istanbul", "Plan a 5-day cultural trip to Istanbul, Türkiye. Include Bosphorus cruise, Grand Bazaar, Hagia Sophia, and traditional culinary tours. Budget Rs. 1,75,000."),
]

dest_cols = st.columns(5, gap="medium")

for col, (flag, name, country, img_key, prompt_text) in zip(dest_cols, destinations):
    with col:
        with st.container(border=True):
            st.image(IMAGES[img_key], use_container_width=True)
            st.markdown(
                f"""
                <div style="text-align: center; padding: 4px 0 8px 0;">
                    <h3 style="margin: 0; font-size: 1.05rem;">{flag} {name}</h3>
                    <span style="font-size: 0.8rem; color: #64748b;">{country}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(f"Explore {name}", key=f"dest_btn_{name}", use_container_width=True):
                st.session_state.query_input = prompt_text
                st.rerun()

st.divider()


# ============================================================
# CUSTOM TRAVEL REQUEST (SECTION 7)
# ============================================================

st.markdown("## 🎯 Custom Travel Request")
st.markdown(
    """
    <p style="color: #475569; margin-bottom: 0.75rem;">
        Specify your destination, duration, currency budget, and preferences. You can also pick quick presets below:
    </p>
    """,
    unsafe_allow_html=True,
)

# Quick Preset Filter Chips
quick_col1, quick_col2, quick_col3, quick_col4 = st.columns(4)

with quick_col1:
    if st.button("⚡ 3-Day Weekend Getaway", use_container_width=True):
        st.session_state.query_input = "Plan a quick 3-day weekend trip to Dubai with balanced budget, morning flight departures, and top sightseeing attractions."
        st.rerun()

with quick_col2:
    if st.button("🏛️ 7-Day Cultural Tour", use_container_width=True):
        st.session_state.query_input = "Plan a 7-day deep cultural and culinary trip to Tokyo with budget-friendly hotels, historic sights, and local transport."
        st.rerun()

with quick_col3:
    if st.button("✨ 5-Day Luxury Escape", use_container_width=True):
        st.session_state.query_input = "Plan a 5-day luxury vacation in Paris, France. 5-star accommodations, fine dining, private tours, and relaxed itinerary."
        st.rerun()

with quick_col4:
    if st.button("🧹 Clear Input", use_container_width=True):
        st.session_state.query_input = ""
        st.rerun()

query = st.text_area(
    "Travel Request",
    value=st.session_state.query_input,
    placeholder=(
        "Example:\n"
        "Plan a 7-day trip to Tokyo, Japan with a budget of Rs. 2,50,000. "
        "I prefer 3 to 4-star hotels near transit stations, direct flights, "
        "and a mix of cultural temples, local food markets, and evening walks."
    ),
    height=140,
    label_visibility="collapsed",
)

config = {
    "configurable": {
        "thread_id": st.session_state.thread_id
    }
}


# ============================================================
# LAUNCH BUTTONS
# ============================================================

btn_col1, btn_col2 = st.columns([3, 1], gap="medium")

with btn_col1:
    launch_button = st.button(
        "🚀 Launch Multi-Agent Workflow",
        type="primary",
        use_container_width=True,
        key="launch_mission",
    )

with btn_col2:
    if st.button("💡 Load Example", use_container_width=True):
        st.session_state.query_input = (
            "Plan a 5-day trip to Paris, France with a budget of Rs. 2,00,000. "
            "I prefer boutique hotels, morning departures, cultural museums, "
            "and scenic river walks."
        )
        st.rerun()


# ============================================================
# AGENT EXECUTION INTERFACE (SECTION 8)
# ============================================================

if launch_button:
    if not query.strip():
        st.warning("✋ Please describe your travel destination and request to get started.")
    else:
        progress_placeholder = st.empty()

        with progress_placeholder.container():
            st.markdown(
                """
                <div style="background: #ffffff; border: 1px solid #bfdbfe; border-radius: 14px; padding: 1.25rem; margin: 1rem 0;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 1.4rem;">🤖</span>
                        <div>
                            <h3 style="margin: 0; color: #1e40af;">Tevelo Multi-Agent Swarm Orchestrating...</h3>
                            <p style="color: #3b82f6; font-size: 0.875rem; margin: 2px 0 0 0;">
                                Coordinating autonomous specialist nodes through LangGraph and Model Context Protocol
                            </p>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            progress_bar = st.progress(0)

            agents_pipeline = [
                ("🧠", "Supervisor Agent", "Decomposing mission & extracting constraints"),
                ("✈️", "Flight Agent", "Analyzing flight corridors & schedules via Aviation MCP"),
                ("🏨", "Hotel Agent", "Filtering accommodations & districts via Tavily Search"),
                ("🌤️", "Weather Agent", "Querying 5-day meteorological guidance"),
                ("💰", "Budget Agent", "Auditing expenses, reserves & feasibility"),
                ("🗺️", "Itinerary Agent", "Synthesizing chronological master draft"),
            ]

            for idx, (icon, agent, task) in enumerate(agents_pipeline):
                p_col1, p_col2 = st.columns([1, 6])
                with p_col1:
                    st.markdown(f"### {icon}")
                with p_col2:
                    st.markdown(f"**{agent}** — *{task}*")
                progress_bar.progress((idx + 1) / len(agents_pipeline))
                time.sleep(0.18)

        try:
            result = app.invoke(
                {
                    "messages": [HumanMessage(content=query)],
                    "user_id": user_id,
                    "user_query": query,
                    "flight_results": "",
                    "hotel_results": "",
                    "weather_results": "",
                    "budget_results": "",
                    "itinerary": "",
                    "final_response": "",
                    "llm_calls": 0,
                },
                config=config,
            )

            st.session_state.latest_result = result
            st.session_state.waiting_for_approval = ("__interrupt__" in result)
            progress_placeholder.empty()
            st.success("✅ Multi-agent execution complete! Results are ready below.")
            st.rerun()

        except Exception as e:
            progress_placeholder.empty()
            st.error(f"⚠️ Workflow Exception: {str(e)}")


# ============================================================
# RESULTS & INTELLIGENCE DASHBOARD
# ============================================================

result = st.session_state.get("latest_result")

if result:
    st.divider()

    # Section 1: Supervisor Decision Making
    st.markdown("## 🧠 Mission Control Analysis")

    supervisor_reasoning = result.get("supervisor_reasoning", "")
    selected_agents = result.get("selected_agents", [])

    if supervisor_reasoning:
        with st.container(border=True):
            st.markdown(
                """
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.5rem;">
                    <span class="card-badge badge-agent">Autonomous Reasoning</span>
                    <strong style="color: #0f172a;">Supervisor Strategy:</strong>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.write(supervisor_reasoning)

    if selected_agents:
        st.markdown("#### 🤖 Activated Agents in Workflow")
        badges_html = " ".join([
            f'<span class="card-badge badge-agent" style="margin-right: 6px;">✓ {agent.replace("_", " ").title()}</span>'
            for agent in selected_agents
        ])
        st.markdown(badges_html, unsafe_allow_html=True)

    # Section 2: Execution Status Row
    st.markdown("## ⚡ Agent Pipeline Status")
    pipeline = [
        ("🧠", "Supervisor"),
        ("✈️", "Flight"),
        ("🏨", "Hotel"),
        ("🌤️", "Weather"),
        ("💰", "Budget"),
        ("🗺️", "Itinerary"),
    ]

    pipeline_cols = st.columns(len(pipeline))
    for col, (icon, name) in zip(pipeline_cols, pipeline):
        with col:
            st.metric(label=f"{icon} {name}", value="✓ DONE")

    st.divider()

    # Section 3: Intelligence Dashboard
    st.markdown("## 📡 Travel Intelligence Dashboard")

    tab_flights, tab_hotels, tab_weather, tab_budget = st.tabs([
        "✈️ Flight Intelligence",
        "🏨 Hotel Recommendations",
        "🌤️ Weather Forecast",
        "💰 Budget Allocation",
    ])

    with tab_flights:
        with st.container(border=True):
            st.markdown(
                """
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem;">
                    <h3 style="margin: 0; color: #0f172a;">✈️ Flight Analysis & Routes</h3>
                    <span class="card-badge badge-flight">Aviation Intelligence</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            flight_res = result.get("flight_results", "")
            if flight_res:
                st.markdown(_clean_md(flight_res))
            else:
                st.info("No specific flight constraints triggered for this route.")

    with tab_hotels:
        with st.container(border=True):
            st.markdown(
                """
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem;">
                    <h3 style="margin: 0; color: #0f172a;">🏨 Accommodations & Stays</h3>
                    <span class="card-badge badge-hotel">Lodging Insights</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            hotel_res = result.get("hotel_results", "")
            if hotel_res:
                st.markdown(_clean_md(hotel_res))
            else:
                st.info("Hotel recommendations will appear here.")

    with tab_weather:
        with st.container(border=True):
            st.markdown(
                """
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem;">
                    <h3 style="margin: 0; color: #0f172a;">🌤️ Meteorological Forecast</h3>
                    <span class="card-badge badge-weather">Live Weather</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            weather_res = result.get("weather_results", "")
            if weather_res:
                st.markdown(_clean_md(weather_res))
            else:
                st.info("Weather data will appear here.")

    with tab_budget:
        with st.container(border=True):
            st.markdown(
                """
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem;">
                    <h3 style="margin: 0; color: #0f172a;">💰 Expense Breakdown & Optimization</h3>
                    <span class="card-badge badge-budget">Financial Audit</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            budget_res = result.get("budget_results", "")
            if budget_res:
                st.markdown(_clean_md(budget_res))
            else:
                st.info("Budget calculations will appear here.")

    st.divider()

    # Section 4: AI Itinerary Blueprint
    st.markdown("## 🗺️ Master Travel Itinerary")

    draft = ""
    if "__interrupt__" in result:
        interrupt_data = result["__interrupt__"][0].value
        draft = interrupt_data.get("draft_itinerary", "")
    else:
        draft = result.get("itinerary", "")

    with st.container(border=True):
        if draft:
            st.markdown(_clean_md(draft))
        else:
            st.info("Itinerary generation in progress...")

    # Section 5: Human in the Loop (Captain's Approval)
    if st.session_state.get("waiting_for_approval"):
        st.divider()
        st.markdown("## 👨‍✈️ Captain's Approval Protocol")

        with st.container(border=True):
            st.markdown(
                """
                <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 12px; padding: 1.15rem; margin-bottom: 1rem;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 1.4rem;">🛡️</span>
                        <div>
                            <strong style="color: #1e40af; font-size: 1rem;">Human-in-the-Loop Decision Required</strong>
                            <p style="margin: 2px 0 0 0; color: #3b82f6; font-size: 0.875rem;">
                                The multi-agent workflow has synthesized this draft plan. Please verify and approve or submit custom adjustments before final execution.
                            </p>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            approval_response = st.radio(
                "Decision Selection:",
                ["✅ Approve & Finalize Mission", "✏️ Request Custom Adjustments"],
                horizontal=True,
                label_visibility="collapsed",
            )

            feedback = ""
            if approval_response == "✏️ Request Custom Adjustments":
                feedback = st.text_area(
                    "Your Revision Instructions:",
                    placeholder="E.g., Please swap the museum on Day 2 for an outdoor park, and keep total hotel costs under 40% of the budget.",
                    height=100,
                )

            act_col1, act_col2 = st.columns([2, 1])
            with act_col1:
                submit_button = st.button("🚀 Confirm Decision", type="primary", use_container_width=True)
            with act_col2:
                if st.button("← Dismiss Approval", use_container_width=True):
                    st.session_state.waiting_for_approval = False
                    st.rerun()

            if submit_button:
                if approval_response == "✏️ Request Custom Adjustments" and not feedback.strip():
                    st.warning("Please enter your revision feedback.")
                else:
                    with st.status("🔄 Finalizing customized itinerary...", expanded=True):
                        st.write("Synthesizing feedback into final itinerary response...")
                        is_approved = (approval_response == "✅ Approve & Finalize Mission")
                        try:
                            # 1. Check if graph has an active interrupted task to resume
                            state_snap = app.get_state(config)
                            can_resume = bool(state_snap.tasks and any(t.interrupts for t in state_snap.tasks))

                            if can_resume:
                                final_result = app.invoke(
                                    Command(
                                        resume={
                                            "approved": is_approved,
                                            "feedback": feedback,
                                        }
                                    ),
                                    config=config,
                                )
                            else:
                                # 2. Resilient fallback: if checkpoint was reset or cleared,
                                # synthesize final response directly from session state without restarting workflow
                                from agents import final_response_agent
                                prev_res = st.session_state.get("latest_result", {}) or {}
                                recovery_state = {
                                    "user_id": user_id,
                                    "user_query": prev_res.get("user_query") or st.session_state.get("query_input", ""),
                                    "itinerary": prev_res.get("itinerary", "") or draft,
                                    "budget_results": prev_res.get("budget_results", ""),
                                    "flight_results": prev_res.get("flight_results", ""),
                                    "hotel_results": prev_res.get("hotel_results", ""),
                                    "weather_results": prev_res.get("weather_results", ""),
                                    "approved": is_approved,
                                    "human_feedback": feedback,
                                    "messages": [],
                                }
                                fr_output = final_response_agent(recovery_state)
                                final_result = {**prev_res, **fr_output}

                            st.session_state.latest_result = final_result
                            st.session_state.waiting_for_approval = False
                            st.rerun()

                        except Exception as e:
                            st.error(f"⚠️ Error finalizing itinerary: {str(e)}")


# ============================================================
# FINAL RESPONSE & DOSSIER EXPORT (SECTION 10)
# ============================================================

final_result = st.session_state.get("latest_result")

if final_result and final_result.get("final_response"):
    st.divider()
    st.markdown("## ✨ Final Approved Travel Plan")
    st.success("🎉 Your travel plan is verified and complete! Safe travels!")

    with st.container(border=True):
        st.markdown(_clean_md(final_result["final_response"]))

    down_col1, down_col2, down_col3 = st.columns(3)
    with down_col1:
        st.download_button(
            label="📥 Download Travel Dossier (.txt)",
            data=_clean_md(final_result["final_response"]),
            file_name="Tevelo_Travel_Dossier.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with down_col2:
        if st.button("🔄 Plan Another Journey", use_container_width=True):
            st.session_state.clear()
            st.rerun()
    with down_col3:
        st.markdown(
            """
            <div style="text-align: center; padding-top: 0.5rem; color: #059669; font-weight: 600; font-size: 0.9rem;">
                ✓ Verified by Tevelo Intelligence
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# MODERN TEVELO FOOTER
# ============================================================

st.divider()

st.markdown(
    """
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; padding: 0.5rem 0; color: #64748b; font-size: 0.85rem;">
        <div>
            <strong style="color: #0f172a;">✈️ Tevelo</strong> — Intelligent Travel, Effortlessly Planned
        </div>
        <div>
            🔒 End-to-End Privacy • 🌍 195+ Countries Covered • ⚡ Multi-Agent MCP Orchestration
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
