import uuid
import time
import re
import streamlit as st

from langchain_core.messages import HumanMessage
from langgraph.types import Command

from graph import app


def _clean_md(text: str) -> str:
    """Strip HTML tags (especially <br>) that LLMs insert into Markdown."""
    if not text:
        return text
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()


# ============================================================
# PAGE CONFIG & ENFORCE LIGHT THEME
# ============================================================

st.set_page_config(
    page_title="AeroAgent • AI Travel Command Center",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com",
        "Report a bug": "https://github.com",
        "About": "AeroAgent - Multi-Agent AI Travel Planning System",
    },
)


# ============================================================
# PURE WHITE MODE CUSTOM CSS
# ============================================================

custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

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
    --success: #10b981;
    --success-light: #ecfdf5;
    --accent-orange: #f97316;
}

/* Base typography & pure white background */
html, body, [data-testid="stAppViewContainer"], .stApp {
    background-color: #ffffff !important;
    color: var(--text-primary) !important;
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

[data-testid="stHeader"] {
    background: rgba(255, 255, 255, 0.9) !important;
    backdrop-filter: blur(12px) !important;
    border-bottom: 1px solid var(--border-subtle);
}

/* Sidebar in Clean White Mode */
[data-testid="stSidebar"] {
    background-color: #fafbfc !important;
    border-right: 1px solid var(--border-subtle) !important;
}

[data-testid="stSidebar"] * {
    color: var(--text-primary);
}

[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown span {
    color: var(--text-secondary);
}

/* Headers */
h1, h2, h3, h4 {
    color: var(--text-primary) !important;
    font-weight: 700 !important;
    letter-spacing: -0.025em !important;
}

h1 {
    font-size: 2.35rem !important;
    line-height: 1.2 !important;
}

h2 {
    font-size: 1.65rem !important;
    margin-top: 1.5rem !important;
    margin-bottom: 0.75rem !important;
}

h3 {
    font-size: 1.15rem !important;
}

/* Buttons */
.stButton > button {
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
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
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.06) !important;
    color: var(--primary) !important;
}

/* Primary Button */
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

/* Inputs & Textareas */
.stTextInput input,
.stTextArea textarea {
    background-color: #ffffff !important;
    border: 1.5px solid var(--border-subtle) !important;
    border-radius: 12px !important;
    padding: 12px 14px !important;
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

/* Metric Cards */
[data-testid="stMetric"] {
    background: #ffffff !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 14px !important;
    padding: 0.85rem 1rem !important;
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
    font-size: clamp(1rem, 1.25vw, 1.28rem) !important;
    font-weight: 800 !important;
    letter-spacing: -0.01em !important;
    white-space: nowrap !important;
    overflow: visible !important;
    text-overflow: clip !important;
}

/* Containers with Border (Card Style) */
div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff !important;
    border-radius: 16px !important;
    border: 1px solid var(--border-subtle) !important;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.03) !important;
    padding: 1.25rem !important;
    transition: all 0.2s ease !important;
}

div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.05) !important;
}

/* Images */
[data-testid="stImage"] img {
    border-radius: 12px !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06) !important;
}

/* Dividers */
hr {
    border-color: var(--border-subtle) !important;
    margin: 1.75rem 0 !important;
    opacity: 0.8 !important;
}

/* Pill Tags & Chips */
.hero-tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 12px;
    background: #eff6ff;
    color: #1d4ed8;
    border: 1px solid #bfdbfe;
    border-radius: 9999px;
    font-size: 0.825rem;
    font-weight: 600;
    margin-bottom: 0.75rem;
}

.system-status-chip {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 12px;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    margin-bottom: 6px;
    font-size: 0.85rem;
    font-weight: 500;
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
    font-size: 0.785rem;
    font-weight: 700;
    letter-spacing: 0.03em;
    text-transform: uppercase;
}

.badge-flight { background: #e0f2fe; color: #0284c7; border: 1px solid #bae6fd; }
.badge-hotel { background: #f3e8ff; color: #7c3aed; border: 1px solid #ddd6fe; }
.badge-weather { background: #fef3c7; color: #d97706; border: 1px solid #fde68a; }
.badge-budget { background: #ecfdf5; color: #059669; border: 1px solid #a7f3d0; }
.badge-agent { background: #eef2ff; color: #4f46e5; border: 1px solid #c7d2fe; }

/* Radio buttons & Checkboxes */
.stRadio > div {
    gap: 12px;
}

/* Alerts & Notices */
.stAlert {
    border-radius: 12px !important;
    border: 1px solid var(--border-subtle) !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02) !important;
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
# SESSION STATE INITIALIZATION
# ============================================================

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

if "latest_result" not in st.session_state:
    st.session_state.latest_result = None

if "waiting_for_approval" not in st.session_state:
    st.session_state.waiting_for_approval = False

if "agent_progress" not in st.session_state:
    st.session_state.agent_progress = {}

if "query_input" not in st.session_state:
    st.session_state.query_input = ""


# ============================================================
# SIDEBAR - PURE WHITE COMMAND CENTER
# ============================================================

with st.sidebar:
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 0.25rem;">
            <div style="
                background: linear-gradient(135deg, #2563eb, #1d4ed8);
                color: white;
                width: 36px;
                height: 36px;
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.2rem;
                box-shadow: 0 4px 10px rgba(37,99,235,0.25);
            ">✈️</div>
            <div>
                <h2 style="font-size: 1.25rem; margin: 0; font-weight: 800; color: #0f172a;">AeroAgent</h2>
                <span style="font-size: 0.75rem; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">AI Mission Control</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption("Autonomous multi-agent system coordinating flights, accommodations, weather & budgets.")

    st.divider()

    # Session Management
    st.markdown("#### 👤 Traveler Identity")

    user_id = st.text_input(
        "Traveler ID",
        value="traveler_001",
        key="user_id_input",
        help="Unique identifier for persistent state storage",
    )

    if st.session_state.thread_id is None:
        st.session_state.thread_id = f"{user_id}_{uuid.uuid4().hex[:8]}"

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🆕 New Trip", use_container_width=True):
            st.session_state.thread_id = f"{user_id}_{uuid.uuid4().hex[:8]}"
            st.session_state.latest_result = None
            st.session_state.waiting_for_approval = False
            st.session_state.query_input = ""
            st.rerun()

    with col_btn2:
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    st.divider()

    # Model Engine Selection
    st.markdown("#### 🧠 AI Reasoning Engine")
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
    import os
    os.environ["GROQ_MODEL"] = chosen_model_id
    if "gemini" in chosen_model_id:
        os.environ["GEMINI_MODEL"] = chosen_model_id

    st.divider()

    # System Diagnostics (White Mode Card)
    st.markdown("#### ⚙️ System Diagnostics")

    system_metrics = [
        ("Multi-Agent Graph", "Active", "🟢"),
        ("LLM Inference", "Gemini / Groq", "⚡"),
        ("MCP Tool Layer", "Connected", "🔌"),
        ("Checkpoint Engine", "Memory / PG", "💾"),
        ("Human Approval Loop", "Armed", "🛡️"),
    ]

    for label, status, icon in system_metrics:
        st.markdown(
            f"""
            <div class="system-status-chip">
                <span style="color: #334155;">{icon} {label}</span>
                <span style="color: #059669; font-weight: 600; font-size: 0.785rem; background: #ecfdf5; padding: 2px 8px; border-radius: 9999px; border: 1px solid #a7f3d0;">{status}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    st.markdown(
        f"""
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 10px 12px; font-size: 0.8rem; color: #64748b;">
            <strong style="color: #0f172a;">Active Thread:</strong><br>
            <code style="color: #2563eb; background: #eff6ff; padding: 2px 6px; border-radius: 4px; font-size: 0.75rem;">{st.session_state.thread_id}</code>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# HERO SECTION - MODERN CLEAN LANDING
# ============================================================

hero_left, hero_right = st.columns([1.6, 1], gap="large")

with hero_left:
    st.markdown(
        """
        <div class="hero-tag">
            <span class="status-dot"></span> Production Multi-Agent Architecture
        </div>
        <h1 style="color: #0f172a; margin-bottom: 0.75rem;">
            Where would you like to travel? <br>
            <span style="background: linear-gradient(135deg, #2563eb, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                Planned by Autonomous Agents.
            </span>
        </h1>
        <p style="color: #475569; font-size: 1.05rem; line-height: 1.6; margin-bottom: 1.25rem;">
            Instead of a single AI prompt, AeroAgent coordinates specialized agents for flights, hotels, live weather forecasts, and currency-optimized budgets — verified by your captain's approval.
        </p>
        """,
        unsafe_allow_html=True,
    )

    stat1, stat2, stat3 = st.columns(3)
    with stat1:
        st.metric(label="AI Agents", value="6 Nodes")
    with stat2:
        st.metric(label="Tools", value="MCP Live")
    with stat3:
        st.metric(label="Approval", value="Required")

with hero_right:
    st.image(
        IMAGES["airplane"],
        use_container_width=True,
        caption="Real-time multi-agent intelligence at your service",
    )

st.divider()


# ============================================================
# DESTINATION SHOWCASE & 1-CLICK SELECTORS
# ============================================================

st.markdown(
    """
    <div style="text-align: center; margin-bottom: 1.5rem;">
        <h2 style="margin: 0; color: #0f172a;">Explore Top Global Destinations</h2>
        <p style="color: #64748b; font-size: 0.95rem; margin-top: 0.25rem;">Click any destination to pre-fill your journey plan instantly</p>
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
            if st.button(f"Select {name}", key=f"dest_btn_{name}", use_container_width=True):
                st.session_state.query_input = prompt_text
                st.rerun()

st.divider()


# ============================================================
# TRIP CUSTOMIZER & SMART INPUT SECTION
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
# WORKFLOW EXECUTION
# ============================================================

if launch_button:
    if not query.strip():
        st.warning("✋ Please describe your travel destination and request to get started.")
    else:
        progress_placeholder = st.empty()

        with progress_placeholder.container():
            st.markdown(
                """
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 1.25rem; margin: 1rem 0;">
                    <h3 style="margin: 0 0 0.5rem 0; color: #0f172a;">🤖 AI Multi-Agent Swarm Orchestrating...</h3>
                    <p style="color: #64748b; font-size: 0.9rem; margin: 0 0 1rem 0;">Decomposing your itinerary across autonomous specialist agents</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            progress_bar = st.progress(0)

            agents_pipeline = [
                ("🧠", "Supervisor Agent", "Decomposing mission & assigning tools"),
                ("✈️", "Flight Agent", "Searching routes & flight schedules"),
                ("🏨", "Hotel Agent", "Analyzing accommodations & ratings"),
                ("🌤️", "Weather Agent", "Querying 5-day meteorology forecast"),
                ("💰", "Budget Agent", "Optimizing expense breakdown & currency"),
                ("🗺️", "Itinerary Agent", "Synthesizing day-by-day travel blueprint"),
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
                <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 12px; padding: 1rem; margin-bottom: 1rem;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 1.3rem;">🛡️</span>
                        <div>
                            <strong style="color: #1e40af;">Human-in-the-Loop Verification Required</strong>
                            <p style="margin: 0; color: #3b82f6; font-size: 0.875rem;">
                                The multi-agent workflow has crafted this draft plan. Please approve or submit requested modifications before final execution.
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
# FINAL RESPONSE & DOWNLOAD
# ============================================================

final_result = st.session_state.get("latest_result")

if final_result and final_result.get("final_response"):
    st.divider()
    st.markdown("## ✨ Final Approved Travel Plan")
    st.success("🎉 Your mission is verified and complete! Safe travels!")

    with st.container(border=True):
        st.markdown(_clean_md(final_result["final_response"]))

    down_col1, down_col2, down_col3 = st.columns(3)
    with down_col1:
        st.download_button(
            label="📥 Download Travel Dossier (.txt)",
            data=_clean_md(final_result["final_response"]),
            file_name="AeroAgent_Travel_Plan.txt",
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
                ✓ Ready for Departure
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# MODERN FOOTER
# ============================================================

st.divider()

st.markdown(
    """
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; padding: 0.5rem 0; color: #64748b; font-size: 0.85rem;">
        <div>
            <strong style="color: #0f172a;">✈️ AeroAgent Command Center</strong> — Built with LangGraph • LangChain • Gemini / Groq • Streamlit • MCP
        </div>
        <div>
            🔒 End-to-End Privacy • 🌍 195+ Countries Covered • ⚡ Autonomous Tool Calling
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
