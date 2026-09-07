import uuid
import time

import streamlit as st

from langchain_core.messages import HumanMessage
from langgraph.types import Command

from graph import app


# ============================================================
# PAGE CONFIG & THEME
# ============================================================

st.set_page_config(
    page_title="✈️ AI Travel Command Center",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com",
        "Report a bug": "https://github.com",
        "About": "AI-Powered Travel Planning System",
    },
)


# ============================================================
# CUSTOM CSS STYLING
# ============================================================

custom_css = """
<style>

:root {
    --primary-blue: #1e3a8a;
    --secondary-blue: #3b82f6;
    --accent-orange: #f97316;
    --accent-gold: #fbbf24;
    --success-green: #10b981;
    --bg-light: #f8fafc;
    --border-color: #e2e8f0;
}

/* Main page */

.main {
    background: linear-gradient(
        135deg,
        #f8fafc 0%,
        #f1f5f9 100%
    );
}

/* Sidebar */

[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #1e3a8a 0%,
        #2c5aa0 100%
    );
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
    color: white;
}

/* Headers */

h1,
h2,
h3 {
    color: #1e3a8a;
    font-weight: 700;
    letter-spacing: -0.5px;
}

h1 {
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
}

h2 {
    font-size: 2rem;
    margin-top: 2rem;
    margin-bottom: 1rem;
}

h3 {
    font-size: 1.3rem;
}

/* Buttons */

.stButton > button {
    border-radius: 10px;
    font-weight: 600;
    font-size: 1rem;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
}

/* Primary buttons */

[data-testid="stBaseButton-primary"] > button {
    background: linear-gradient(
        135deg,
        #f97316 0%,
        #fb923c 100%
    );
    color: white;
    border: none;
    box-shadow: 0 4px 15px rgba(249, 115, 22, 0.2);
}

[data-testid="stBaseButton-primary"] > button:hover {
    background: linear-gradient(
        135deg,
        #ea580c 0%,
        #f97316 100%
    );
}

/* Inputs */

.stTextInput input,
.stTextArea textarea {
    background-color: white;
    border: 2px solid #e2e8f0;
    border-radius: 10px;
    padding: 12px;
    font-size: 1rem;
}

.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Metrics */

[data-testid="metric-container"] {
    background: linear-gradient(
        135deg,
        #ffffff 0%,
        #f8fafc 100%
    );
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

/* Images */

[data-testid="stImage"] img {
    border-radius: 15px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

/* Expander */

[data-testid="stExpander"] {
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    background: white;
}

/* Markdown */

.stMarkdown {
    line-height: 1.6;
    color: #334155;
}

/* Sidebar buttons */

[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(
        135deg,
        #fbbf24 0%,
        #f97316 100%
    );
    color: #1e3a8a;
    font-weight: 700;
    width: 100%;
    border-radius: 10px;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background: linear-gradient(
        135deg,
        #f59e0b 0%,
        #ea580c 100%
    );
}

/* Animation */

@keyframes slideInUp {

    from {
        opacity: 0;
        transform: translateY(20px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }

}

.animated-section {
    animation: slideInUp 0.5s ease-out;
}

/* Status badge */

.status-badge {
    display: inline-block;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.85rem;
}

.status-online {
    background-color: #ecfdf5;
    color: #065f46;
}

.status-processing {
    background-color: #eff6ff;
    color: #0c4a6e;
}

</style>
"""

st.markdown(
    custom_css,
    unsafe_allow_html=True,
)


# ============================================================
# REMOTE IMAGES
# ============================================================

IMAGES = {

    "airplane": (
        "https://images.unsplash.com/"
        "photo-1436491865332-7a61a109cc05"
        "?auto=format&fit=crop&w=2000&q=90"
    ),

    "dubai": (
        "https://images.unsplash.com/"
        "photo-1512453979798-5ea266f8880c"
        "?auto=format&fit=crop&w=1200&q=90"
    ),

    "tokyo": (
        "https://images.unsplash.com/"
        "photo-1540959733332-eab4deabeeaf"
        "?auto=format&fit=crop&w=1200&q=90"
    ),

    "paris": (
        "https://images.unsplash.com/"
        "photo-1502602898657-3e91760cbb34"
        "?auto=format&fit=crop&w=1200&q=90"
    ),

    "london": (
        "https://images.unsplash.com/"
        "photo-1513635269975-59663e0ac1ad"
        "?auto=format&fit=crop&w=1200&q=90"
    ),

    "istanbul": (
        "https://images.unsplash.com/"
        "photo-1524231757912-21f4fe3a7200"
        "?auto=format&fit=crop&w=1200&q=90"
    ),
}


# ============================================================
# SESSION STATE
# ============================================================

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

if "latest_result" not in st.session_state:
    st.session_state.latest_result = None

if "waiting_for_approval" not in st.session_state:
    st.session_state.waiting_for_approval = False

if "agent_progress" not in st.session_state:
    st.session_state.agent_progress = {}


# ============================================================
# SIDEBAR - PROFESSIONAL CONTROL CENTER
# ============================================================

with st.sidebar:

    # --------------------------------------------------------
    # Header
    # --------------------------------------------------------

    st.image(
        IMAGES["airplane"],
        use_container_width=True,
    )

    st.markdown(
        """
        <h1 style="
            color:white;
            font-size:1.8rem;
            margin:0;
        ">
            ✈️ Travel Command
        </h1>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <p style="
            color:#e0e7ff;
            margin:0.5rem 0 0 0;
        ">
            AI-Powered Journey Planner
        </p>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # --------------------------------------------------------
    # Session Management
    # --------------------------------------------------------

    st.markdown(
        """
        <h3 style="color:white;">
            👤 Session
        </h3>
        """,
        unsafe_allow_html=True,
    )

    user_id = st.text_input(
        "User ID",
        value="traveler_001",
        key="user_id_input",
    )

    if st.session_state.thread_id is None:

        st.session_state.thread_id = (
            f"{user_id}_{uuid.uuid4().hex[:8]}"
        )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "🆕 New Mission",
            use_container_width=True,
        ):

            st.session_state.thread_id = (
                f"{user_id}_{uuid.uuid4().hex[:8]}"
            )

            st.session_state.latest_result = None
            st.session_state.waiting_for_approval = False

            st.rerun()

    with col2:

        if st.button(
            "🔄 Reset",
            use_container_width=True,
        ):

            st.session_state.clear()

            st.rerun()

    st.divider()

    # --------------------------------------------------------
    # System Status
    # --------------------------------------------------------

    st.markdown(
        """
        <h3 style="color:white;">
            ⚙️ System Status
        </h3>
        """,
        unsafe_allow_html=True,
    )

    status_items = [
        ("🟢", "AI System Online"),
        ("🧠", "LangGraph Multi-Agent"),
        ("🔌", "MCP Tools Connected"),
        ("💾", "PostgreSQL Ready"),
        ("👤", "Human Approval Loop"),
    ]

    for icon, label in status_items:

        st.markdown(
            f"""
            <div style="
                color:white;
                margin:0.5rem 0;
            ">
                {icon} {label}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    st.markdown(
        f"""
        <p style="
            color:#cbd5e1;
            font-size:0.85rem;
            word-break:break-all;
        ">
            <strong>Thread:</strong><br>
            {st.session_state.thread_id}
        </p>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# HERO SECTION - PREMIUM LANDING
# ============================================================

col_hero_left, col_hero_right = st.columns(
    [1.5, 1],
    gap="large",
)

with col_hero_left:

    st.markdown(
        """
        <h1 style="
            font-size:3.5rem;
            margin-bottom:1rem;
            color:#1e3a8a;
        ">
            Your Journey.<br>
            Planned by
            <span style="color:#f97316;">
               Intelligent Agents
            </span>.
        </h1>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        Experience the future of travel planning.
        Our intelligent multi-agent system coordinates
        flight intelligence, accommodations, weather
        insights, budget optimization, and itinerary
        crafting — with human control at every step.
        """
    )

    # Quick stats

    stat_col1, stat_col2, stat_col3 = st.columns(3)

    with stat_col1:

        st.metric(
            "🚀 AI Agents",
            "6",
        )

    with stat_col2:

        st.metric(
            "⏱️ Processing",
            "Real-time",
        )

    with stat_col3:

        st.metric(
            "✅ Approval",
            "Required",
        )


with col_hero_right:

    st.image(
        IMAGES["airplane"],
        use_container_width=True,
    )


st.divider()


# ============================================================
# DESTINATION SHOWCASE
# ============================================================

st.markdown(
    """
    <h2 style="
        text-align:center;
        margin-bottom:1.5rem;
    ">
        🌍 Explore Popular Destinations
    </h2>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <p style="
        text-align:center;
        color:#64748b;
        margin-bottom:2rem;
    ">
        Select a destination or describe any location
        in your travel request
    </p>
    """,
    unsafe_allow_html=True,
)


destinations = [
    ("🇦🇪", "Dubai", "UAE", "dubai"),
    ("🇯🇵", "Tokyo", "Japan", "tokyo"),
    ("🇫🇷", "Paris", "France", "paris"),
    ("🇬🇧", "London", "UK", "london"),
    ("🇹🇷", "Istanbul", "Türkiye", "istanbul"),
]


dest_cols = st.columns(
    5,
    gap="medium",
)


for col, (
    flag,
    name,
    country,
    img_key,
) in zip(
    dest_cols,
    destinations,
):

    with col:

        with st.container(border=True):

            st.image(
                IMAGES[img_key],
                use_container_width=True,
            )

            st.markdown(
                f"""
                <h3 style="
                    margin:1rem 0 0.5rem 0;
                    text-align:center;
                ">
                    {flag} {name}
                </h3>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                f"""
                <p style="
                    text-align:center;
                    color:#64748b;
                    margin:0;
                ">
                    {country}
                </p>
                """,
                unsafe_allow_html=True,
            )


st.divider()


# ============================================================
# TRAVEL REQUEST
# ============================================================

st.markdown(
    """
    <h2>
        🎯 Plan Your Adventure
    </h2>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    Describe your ideal trip. Include details like:

    - **Destination** — city, country, or region
    - **Duration** — number of days
    - **Budget** — PKR, USD, or your currency
    - **Preferences** — hotel type, flight class, activities
    - **Constraints** — no overnight flights, dietary needs, etc.
    """
)


query = st.text_area(
    "Travel Request",
    placeholder=(
        "Example:\n"
        "I want a 7-day trip to Japan under Rs. 2,50,000. "
        "I prefer budget-friendly hotels, direct flights only, "
        "and lots of cultural experiences."
    ),
    height=160,
    label_visibility="collapsed",
)


config = {
    "configurable": {
        "thread_id": st.session_state.thread_id
    }
}


# ============================================================
# LAUNCH AGENTS
# ============================================================

button_col1, button_col2 = st.columns(
    [3, 1]
)


with button_col1:

    launch_button = st.button(
        "🚀 Launch AI Travel Mission",
        type="primary",
        use_container_width=True,
        key="launch_mission",
    )


with button_col2:

    if st.button(
        "📋 Example",
        use_container_width=True,
    ):

        st.info(
            """
            **Example Request**

            Plan a 5-day trip to Paris, France with
            a budget of Rs. 1,80,000.

            I prefer 4-star hotels, morning departures,
            museums, cafes and scenic walks.

            Avoid activities between 2-4 PM because
            I like afternoon naps.
            """
        )


# ============================================================
# GRAPH EXECUTION
# ============================================================

if launch_button:

    if not query.strip():

        st.warning(
            "✋ Please describe your travel request to get started."
        )

    else:

        # ----------------------------------------------------
        # Progress Visualization
        # ----------------------------------------------------

        progress_placeholder = st.empty()

        with progress_placeholder.container():

            st.markdown(
                "### 🤖 AI Agents Working..."
            )

            progress_bar = st.progress(0)

            agents_pipeline = [
                (
                    "🧠",
                    "Supervisor",
                    "Analyzing your request",
                ),
                (
                    "✈️",
                    "Flight Agent",
                    "Finding flight options",
                ),
                (
                    "🏨",
                    "Hotel Agent",
                    "Searching accommodations",
                ),
                (
                    "🌤️",
                    "Weather Agent",
                    "Gathering weather data",
                ),
                (
                    "💰",
                    "Budget Agent",
                    "Calculating costs",
                ),
                (
                    "🗺️",
                    "Itinerary Agent",
                    "Building your journey",
                ),
            ]

            for idx, (
                icon,
                agent,
                task,
            ) in enumerate(
                agents_pipeline
            ):

                col1, col2 = st.columns(
                    [1, 4]
                )

                with col1:

                    st.markdown(
                        f"## {icon}"
                    )

                with col2:

                    st.markdown(
                        f"**{agent}** — {task}"
                    )

                progress_bar.progress(
                    (idx + 1) / len(
                        agents_pipeline
                    )
                )

                time.sleep(0.2)

        # ----------------------------------------------------
        # ACTUAL LANGGRAPH CALL
        # ----------------------------------------------------

        try:

            result = app.invoke(
                {
                    "messages": [
                        HumanMessage(
                            content=query
                        )
                    ],
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

            st.session_state.waiting_for_approval = (
                "__interrupt__" in result
            )

            progress_placeholder.empty()

            st.success(
                "✅ AI analysis complete! Review below."
            )

            st.rerun()

        except Exception as e:

            progress_placeholder.empty()

            st.error(
                f"⚠️ Error: {str(e)}"
            )


# ============================================================
# RESULTS
# ============================================================

result = st.session_state.get(
    "latest_result"
)


if result:

    st.divider()

    # ========================================================
    # SUPERVISOR ANALYSIS
    # ========================================================

    st.markdown(
        """
        <h2>
            🧠 Mission Control Analysis
        </h2>
        """,
        unsafe_allow_html=True,
    )

    supervisor_reasoning = result.get(
        "supervisor_reasoning",
        "",
    )

    selected_agents = result.get(
        "selected_agents",
        [],
    )


    if supervisor_reasoning:

        with st.container(border=True):

            st.markdown(
                "**AI Decision Making:**"
            )

            st.write(
                supervisor_reasoning
            )


    if selected_agents:

        st.markdown(
            """
            <h3>
                🤖 Activated Agents
            </h3>
            """,
            unsafe_allow_html=True,
        )

        agent_badges = " • ".join(
            [
                f"✓ {agent}"
                for agent in selected_agents
            ]
        )

        st.success(
            agent_badges
        )


    # ========================================================
    # EXECUTION PIPELINE
    # ========================================================

    st.markdown(
        """
        <h2>
            ⚡ Execution Pipeline
        </h2>
        """,
        unsafe_allow_html=True,
    )


    pipeline = [
        ("🧠", "Supervisor"),
        ("✈️", "Flight"),
        ("🏨", "Hotel"),
        ("🌤️", "Weather"),
        ("💰", "Budget"),
        ("🗺️", "Itinerary"),
    ]


    pipeline_cols = st.columns(
        len(pipeline)
    )


    for col, (
        icon,
        name,
    ) in zip(
        pipeline_cols,
        pipeline,
    ):

        with col:

            st.metric(
                label=f"{icon} {name}",
                value="✓ DONE",
            )


    st.divider()


    # ========================================================
    # TRAVEL INTELLIGENCE
    # ========================================================

    st.markdown(
        """
        <h2>
            📡 Travel Intelligence Dashboard
        </h2>
        """,
        unsafe_allow_html=True,
    )


    # --------------------------------------------------------
    # Flights & Hotels
    # --------------------------------------------------------

    flight_col, hotel_col = st.columns(
        2,
        gap="large",
    )


    with flight_col:

        with st.container(border=True):

            st.markdown(
                "### ✈️ Flight Intelligence"
            )

            flight_result = result.get(
                "flight_results",
                "",
            )

            if flight_result:

                st.markdown(
                    flight_result
                )

            else:

                st.info(
                    "Searching for the best flight options..."
                )


    with hotel_col:

        with st.container(border=True):

            st.markdown(
                "### 🏨 Hotel Intelligence"
            )

            hotel_result = result.get(
                "hotel_results",
                "",
            )

            if hotel_result:

                st.markdown(
                    hotel_result
                )

            else:

                st.info(
                    "Researching accommodation options..."
                )


    # --------------------------------------------------------
    # Weather & Budget
    # --------------------------------------------------------

    weather_col, budget_col = st.columns(
        2,
        gap="large",
    )


    with weather_col:

        with st.container(border=True):

            st.markdown(
                "### 🌤️ Weather Forecast"
            )

            weather_result = result.get(
                "weather_results",
                "",
            )

            if weather_result:

                st.markdown(
                    weather_result
                )

            else:

                st.info(
                    "Gathering weather data..."
                )


    with budget_col:

        with st.container(border=True):

            st.markdown(
                "### 💰 Budget Breakdown"
            )

            budget_result = result.get(
                "budget_results",
                "",
            )

            if budget_result:

                st.markdown(
                    budget_result
                )

            else:

                st.info(
                    "Calculating costs..."
                )


    st.divider()


    # ========================================================
    # ITINERARY PREVIEW
    # ========================================================

    st.markdown(
        """
        <h2>
            🗺️ AI Generated Itinerary
        </h2>
        """,
        unsafe_allow_html=True,
    )


    if "__interrupt__" in result:

        interrupt_data = (
            result["__interrupt__"][0].value
        )

        draft = interrupt_data.get(
            "draft_itinerary",
            "",
        )

    else:

        draft = result.get(
            "itinerary",
            "",
        )


    with st.container(border=True):

        if draft:

            st.markdown(
                draft
            )

        else:

            st.info(
                "Constructing your personalized itinerary..."
            )


    # ========================================================
    # HUMAN APPROVAL
    # ========================================================

    if st.session_state.get(
        "waiting_for_approval"
    ):

        st.divider()

        st.markdown(
            """
            <h2>
                👨‍✈️ Captain's Approval Required
            </h2>
            """,
            unsafe_allow_html=True,
        )


        approval_container = st.container(
            border=True
        )


        with approval_container:

            st.info(
                """
                🎯 **Review & Approve Your Travel Plan**

                The AI has prepared a comprehensive travel
                plan based on your requirements.

                As the mission captain, your approval is
                required before we finalize everything.
                """
            )


            approval_response = st.radio(
                "Do you approve this travel plan?",
                [
                    "✅ Yes, let's go!",
                    "✏️ No, I have feedback",
                ],
                horizontal=True,
                label_visibility="collapsed",
            )


            feedback = ""


            if (
                approval_response
                == "✏️ No, I have feedback"
            ):

                feedback = st.text_area(
                    "What would you like to change?",
                    placeholder=(
                        "Examples:\n"
                        "• Reduce hotel costs\n"
                        "• Add more sightseeing\n"
                        "• Avoid overnight flights\n"
                        "• Include adventure activities"
                    ),
                    height=120,
                    label_visibility="collapsed",
                )


            col1, col2, col3 = st.columns(
                [2, 1, 1]
            )


            with col1:

                submit_button = st.button(
                    "✅ Submit Decision",
                    type="primary",
                    use_container_width=True,
                    key="submit_approval",
                )


            with col2:

                if st.button(
                    "← Back",
                    use_container_width=True,
                ):

                    st.session_state.waiting_for_approval = False

                    st.rerun()


            if submit_button:

                if (
                    approval_response
                    == "✏️ No, I have feedback"
                    and not feedback.strip()
                ):

                    st.warning(
                        "Please provide feedback for your revision request."
                    )

                else:

                    with st.status(
                        "🔄 Finalizing your travel plan...",
                        expanded=True,
                    ):

                        st.write(
                            "Processing your feedback..."
                        )

                        final_result = app.invoke(
                            Command(
                                resume={
                                    "approved": (
                                        approval_response
                                        == "✅ Yes, let's go!"
                                    ),
                                    "feedback": feedback,
                                }
                            ),
                            config=config,
                        )


                    st.session_state.latest_result = (
                        final_result
                    )

                    st.session_state.waiting_for_approval = (
                        False
                    )

                    st.rerun()


# ============================================================
# FINAL RESPONSE
# ============================================================

final_result = st.session_state.get(
    "latest_result"
)


if (
    final_result
    and final_result.get("final_response")
):

    st.divider()

    st.markdown(
        """
        <h2>
            ✨ Your Final Travel Plan
        </h2>
        """,
        unsafe_allow_html=True,
    )

    st.success(
        "🎉 Your AI-powered travel mission is complete!"
    )


    with st.container(border=True):

        st.markdown(
            final_result["final_response"]
        )


    # --------------------------------------------------------
    # Download / Share
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)


    with col1:

        st.download_button(
            label="📥 Download Plan",
            data=final_result["final_response"],
            file_name="travel_plan.txt",
            mime="text/plain",
            use_container_width=True,
        )


    with col2:

        if st.button(
            "🔄 Create Another Plan",
            use_container_width=True,
        ):

            st.session_state.clear()

            st.rerun()


    with col3:

        st.markdown(
            """
            <p style="
                text-align:center;
                color:#64748b;
                padding-top:0.5rem;
            ">
                ✅ Ready to book?
            </p>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# FOOTER
# ============================================================

# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    "### ✈️ AI Travel Command Center"
)

st.caption(
    "Powered by LangGraph • Groq • MCP Tools • PostgreSQL"
)

st.caption(
    "🔒 Your travel data is secure • "
    "🌍 Global coverage • "
    "💡 AI-optimized routes"
)