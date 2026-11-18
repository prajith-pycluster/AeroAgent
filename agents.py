import asyncio
import json
import os
import re
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.types import interrupt

from config import get_llm
from mcp_client import (
    current_weather,
    forecast,
    list_airlines,
    list_airports,
    tavily_search,
)
from state import TravelState


# ============================================================
# LLM & HELPERS
# ============================================================

llm = get_llm()


def _llm_text(system: str, prompt: str) -> str:
    messages = [
        SystemMessage(content=system),
        HumanMessage(content=prompt),
    ]

    # 1. Try primary LLM
    try:
        active_llm = get_llm()
        response = active_llm.invoke(messages)
        return response.content
    except Exception as e:
        err_msg = str(e).lower()
        print(f"[LLM Exception] {e}")

        # 2. Try alternate Groq models if model not found / deprecated
        if "model_not_found" in err_msg or "404" in err_msg or "does not exist" in err_msg:
            fallback_models = ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.8-27b"]
            for fb_model in fallback_models:
                try:
                    print(f"[LLM Fallback] Trying model {fb_model}...")
                    fb_llm = get_llm(model_override=fb_model)
                    response = fb_llm.invoke(messages)
                    return response.content
                except Exception as fb_err:
                    print(f"[LLM Fallback {fb_model} failed]: {fb_err}")
                    continue

        # 3. Try Gemini fallback if key is present
        g_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if g_key and not g_key.startswith("gsk_"):
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                print("[LLM Fallback] Trying Gemini 3.8 Flash...")
                g_llm = ChatGoogleGenerativeAI(
                    model="gemini-3.8-flash",
                    google_api_key=g_key,
                    temperature=0.3,
                )
                response = g_llm.invoke(messages)
                return response.content
            except Exception as g_err:
                print(f"[LLM Gemini failed]: {g_err}")

        # If all fail, re-raise original
        raise


def _compact(text: Any, max_chars: int = 4000) -> str:
    """
    Prevent very large MCP/agent outputs from being
    passed to the next LLM.
    """
    text = str(text or "")

    if len(text) <= max_chars:
        return text

    return text[:max_chars] + "\n...[truncated]..."


def _clean_html(text: str) -> str:
    """
    Strip HTML tags that LLMs sometimes insert into Markdown output.
    Converts <br> / <br/> to a newline so table content doesn't collapse.
    Removes all other HTML tags entirely.
    """
    if not text:
        return text
    # Replace <br>, <br/>, <br /> with newline
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    # Strip any remaining HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()


def _json_from_llm(text: str) -> dict:
    """
    Extract JSON object from LLM response.
    """

    print("\n========== RAW LLM RESPONSE ==========")
    print(text)
    print("======================================\n")

    start = text.index("{")
    end = text.rindex("}") + 1

    json_text = text[start:end]

    print("\n========== EXTRACTED JSON ==========")
    print(json_text)
    print("====================================\n")

    return json.loads(json_text)


# ============================================================
# SUPERVISOR AGENT
# ============================================================

def supervisor_agent(state: TravelState):

    query = state.get("user_query") or (state.get("messages", [None])[-1].content if state.get("messages") else "") or "Travel Request"

    # --------------------------------------------------------
    # INPUT GUARDRAIL
    # --------------------------------------------------------

    guardrail_prompt = f"""
Determine whether the following request is a valid travel
planning request.

A valid request can involve:

- flights
- hotels
- destinations
- weather
- trip planning
- itinerary
- transportation
- budget
- tourism
- vacation planning

Return ONLY valid JSON:

{{
    "allowed": true,
    "reason": ""
}}

If the request is unrelated to travel planning,
set "allowed" to false.

User request:

{query}
"""

    guardrail_raw = _llm_text(
        "You are a strict travel-request validation guardrail. "
        "Return valid JSON only.",
        guardrail_prompt,
    )

    print("\n========== GUARDRAIL RAW RESPONSE ==========")
    print(guardrail_raw)
    print("============================================\n")

    guardrail_result = _json_from_llm(guardrail_raw)

    print("\n========== GUARDRAIL PARSED RESPONSE ==========")
    print(json.dumps(guardrail_result, indent=2))
    print("================================================\n")

    # --------------------------------------------------------
    # GUARDRAIL REJECTION
    # --------------------------------------------------------

    if not guardrail_result.get("allowed", False):

        reason = guardrail_result.get(
            "reason",
            "Request rejected by input guardrail.",
        )

        return {
            "selected_agents": [],
            "trip_constraints": {},
            "supervisor_reasoning": reason,
            "final_response": reason,
            "messages": [
                AIMessage(
                    content=f"Guardrail blocked request: {reason}"
                )
            ],
            "llm_calls": state.get("llm_calls", 0) + 1,
        }

    # --------------------------------------------------------
    # SUPERVISOR
    # --------------------------------------------------------

    prompt = f"""
You are the supervisor of a real-world multi-agent travel
planning system.

Decide which specialist agents are needed for this request.

Available agents:

- flight_agent:
  Use for flights, airports, airlines, routes and airfare guidance.

- hotel_agent:
  Use for hotels, accommodation and areas to stay.

- weather_agent:
  Use for current weather, forecast, climate and packing guidance.

- budget_agent:
  Use for budget, affordability and cost planning.

- itinerary_agent:
  Use to create the final day-by-day travel plan.

For a normal complete trip request, select all relevant
specialists, normally including itinerary_agent.

Return ONLY valid JSON:

{{
    "selected_agents": [
        "flight_agent",
        "hotel_agent",
        "weather_agent",
        "budget_agent",
        "itinerary_agent"
    ],
    "trip_constraints": {{
        "destination": "",
        "origin": "",
        "duration": "",
        "budget": "",
        "travel_style": "",
        "special_preferences": []
    }},
    "reasoning": ""
}}

Important:

- Extract only information actually present in the user request.
- Do not invent missing dates.
- Do not invent a budget.
- Do not invent an origin.
- If something is unknown, leave it empty.
- Keep the constraints concise.

User request:

{query}
"""

    raw = _llm_text(
        "You are the supervisor of a travel planning system. "
        "Return strict JSON only.",
        prompt,
    )

    print("\n========== RAW SUPERVISOR RESPONSE ==========")
    print(raw)
    print("==============================================\n")

    parsed = _json_from_llm(raw)

    print("\n========== PARSED SUPERVISOR JSON ==========")
    print(json.dumps(parsed, indent=2))
    print("=============================================\n")

    selected = parsed["selected_agents"]

    return {
        "selected_agents": selected,
        "trip_constraints": parsed["trip_constraints"],
        "supervisor_reasoning": parsed["reasoning"],
        "messages": [
            AIMessage(
                content="Supervisor created the agent plan."
            )
        ],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


# ============================================================
# FLIGHT AGENT
# ============================================================

def flight_agent(state: TravelState):

    query = state.get("user_query", "")
    constraints = state.get("trip_constraints", {})

    destination = constraints.get("destination", "")
    origin = constraints.get("origin", "")

    print("\n========== FLIGHT AGENT INPUT ==========")
    print("Query:", query)
    print("Constraints:", constraints)
    print("========================================\n")

    # --------------------------------------------------------
    # MCP
    # --------------------------------------------------------

    try:
        airports = asyncio.run(
            list_airports(
                destination,
                limit=10,
            )
        )
    except Exception as e:
        print(f"[Airports Notice]: {e}")
        airports = f"Airport data: {e}"

    try:
        airlines = asyncio.run(
            list_airlines(
                "",
                limit=10,
            )
        )
    except Exception as e:
        print(f"[Airlines Notice]: {e}")
        airlines = f"Airline data: {e}"

    print("\n========== AIRPORT MCP DATA ==========")
    print(airports)
    print("======================================\n")

    print("\n========== AIRLINE MCP DATA ==========")
    print(airlines)
    print("======================================\n")

    # --------------------------------------------------------
    # LLM
    # --------------------------------------------------------

    prompt = f"""
Create practical flight guidance for this trip.

User request:

{_compact(query, 2000)}

Trip constraints:

{_compact(constraints, 2000)}

Origin:

{_compact(origin, 1000)}

Destination:

{_compact(destination, 1000)}

Airport MCP data:

{_compact(airports, 3000)}

Airline MCP data:

{_compact(airlines, 3000)}

Important data policy:

The available AviationStack MCP tools provide airport
and airline information.

They do NOT provide confirmed live booking inventory,
confirmed ticket availability, or guaranteed current fares.

Therefore:

- Do NOT claim a specific flight is available.
- Do NOT claim a ticket is currently bookable.
- Do NOT present an exact fare as a verified live price.
- If mentioning fares, clearly label them as estimates.
- Do not invent flight numbers.
- Do not invent departure times.
- Do not invent seat availability.

Include:

1. Likely departure/arrival airports
2. Relevant airlines
3. Typical/estimated duration
4. Estimated fare range if useful
5. Peak-season considerations
6. Booking advice

Be concise.

Clearly distinguish:

VERIFIED MCP DATA
from
ESTIMATED TRAVEL GUIDANCE.
"""

    result = _llm_text(
        "You are a flight planning specialist. "
        "Be accurate, concise and transparent about uncertainty.",
        prompt,
    )

    print("\n========== FLIGHT AGENT OUTPUT ==========")
    print(result)
    print("=========================================\n")

    return {
        "flight_results": result,
        "messages": [
            AIMessage(
                content="Flight agent completed."
            )
        ],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


# ============================================================
# HOTEL AGENT
# ============================================================

def hotel_agent(state: TravelState):

    query = (
        f"Best hotels and areas to stay for: "
        f"{state.get('user_query', '')}"
    )

    print("\n========== HOTEL AGENT INPUT ==========")
    print(query)
    print("=======================================\n")

    # --------------------------------------------------------
    # TAVILY MCP
    # --------------------------------------------------------

    try:
        result = asyncio.run(
            tavily_search(query)
        )
    except Exception as e:
        print(f"[Hotel Search Notice]: {e}")
        result = f"Hotel search data: {e}"

    print("\n========== HOTEL SEARCH RESULT ==========")
    print(result)
    print("=========================================\n")

    compact_result = _compact(
        result,
        6000,
    )

    # --------------------------------------------------------
    # HOTEL LLM FILTER
    # --------------------------------------------------------

    prompt = f"""
Analyze the following hotel search results for this travel request.

User request:

{_compact(state.get("user_query", ""), 2000)}

Search results:

{compact_result}

Create concise hotel guidance.

Important:

- Search results are external information, not guaranteed live inventory.
- Do not claim that a hotel has a room available now.
- Do not claim an exact current price unless the source explicitly
  provides it and clearly indicates the price context.
- Do not invent hotel prices.
- Do not invent ratings.
- Do not invent hotel amenities.
- If prices are shown, clearly label them as source-reported
  or approximate.
- Prefer useful areas/neighborhoods when exact hotel information
  is uncertain.

Return:

1. Recommended areas
2. Suitable hotel options if supported by the search results
3. Price information only when supported
4. Important booking advice

Be concise.
"""

    filtered_result = _llm_text(
        "You are a hotel research specialist. "
        "Use only information supported by the provided search results.",
        prompt,
    )

    print("\n========== HOTEL AGENT OUTPUT ==========")
    print(filtered_result)
    print("========================================\n")

    return {
        "hotel_results": filtered_result,
        "messages": [
            AIMessage(
                content="Hotel agent completed."
            )
        ],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


# ============================================================
# WEATHER AGENT
# ============================================================

def weather_agent(state: TravelState):

    constraints = state.get("trip_constraints", {})

    city = constraints.get("destination", "")

    print("\n========== WEATHER AGENT INPUT ==========")
    print("City:", city)
    print("=========================================\n")

    # --------------------------------------------------------
    # MCP
    # --------------------------------------------------------

    try:
        weather_data = asyncio.run(
            current_weather(city)
        )
    except Exception as e:
        print(f"[Weather Notice]: {e}")
        weather_data = None

    try:
        forecast_data = asyncio.run(
            forecast(city)
        )
    except Exception as e:
        print(f"[Forecast Notice]: {e}")
        forecast_data = None

    # Detect API errors in the returned data and suppress them
    def _is_api_error(data) -> bool:
        s = str(data or "").lower()
        return any(x in s for x in ["401", "invalid api key", "api key", "cod:", "error", "traceback"])

    live_weather_text = "No live data — please use seasonal knowledge." if (not weather_data or _is_api_error(weather_data)) else str(weather_data)
    live_forecast_text = "No live data — please use seasonal knowledge." if (not forecast_data or _is_api_error(forecast_data)) else str(forecast_data)

    print("\n========== CURRENT WEATHER ==========")
    print(live_weather_text)
    print("=====================================\n")

    print("\n========== WEATHER FORECAST ==========")
    print(live_forecast_text)
    print("======================================\n")

    # --------------------------------------------------------
    # WEATHER LLM SYNTHESIS & FORMATTING
    # --------------------------------------------------------

    system_prompt = (
        "You are an expert meteorological and travel climate specialist. "
        "Provide a clean, beautifully formatted travel weather overview for the destination city. "
        "If live tool data is provided and valid, format it into clear metrics (temperature, conditions, humidity). "
        "If live API data is unavailable or returned an error, provide an accurate, realistic seasonal climate breakdown, "
        "temperature range (°C), and practical packing recommendations for the traveler. "
        "Never output raw JSON or API error codes to the user. Always return clean, readable Markdown with bullet points and a table."
    )

    user_prompt = f"""
Destination: {city}
Trip Details: {state.get('user_query', '')}

Tool Observation:
{_compact(live_weather_text, 1200)}

Forecast Observation:
{_compact(live_forecast_text, 1500)}

Please generate a professional travel weather dossier:
- 🌤️ Climate & Expected Conditions
- 🌡️ Temperature Overview (°C)
- 🎒 Essential Packing & Clothing Tips
- 💡 Weather Tips for Sightseeing
"""

    try:
        weather_summary = _llm_text(system_prompt, user_prompt)
        weather_summary = _clean_html(weather_summary)
    except Exception as e:
        weather_summary = f"**Weather Overview for {city}:**\n- General Climate: Pleasant seasonal conditions.\n- Recommended clothing: Light breathable layers and comfortable walking shoes."

    print("\n========== WEATHER AGENT OUTPUT ==========")
    print(weather_summary)
    print("==========================================\n")

    return {
        "weather_results": weather_summary,
        "messages": [
            AIMessage(
                content="Weather agent completed."
            )
        ],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


# ============================================================
# BUDGET AGENT
# ============================================================

def budget_agent(state: TravelState):

    print("\n========== BUDGET AGENT INPUT ==========")

    print("Trip Constraints:")
    print(
        state.get(
            "trip_constraints",
            {},
        )
    )

    print("\nFlight Results:")
    print(
        state.get(
            "flight_results",
            "",
        )
    )

    print("\nHotel Results:")
    print(
        state.get(
            "hotel_results",
            "",
        )
    )

    print("\nWeather Results:")
    print(
        state.get(
            "weather_results",
            "",
        )
    )

    print("=========================================\n")

    # --------------------------------------------------------
    # COMPACT CONTEXT
    # --------------------------------------------------------

    prompt = f"""
Analyze whether this trip plan is realistic for the user's budget.

User request:

{_compact(
    state.get("user_query", ""),
    2000,
)}

Trip constraints:

{_compact(
    state.get("trip_constraints", {}),
    2000,
)}

Flight results:

{_compact(
    state.get("flight_results", ""),
    3000,
)}

Hotel results:

{_compact(
    state.get("hotel_results", ""),
    3000,
)}

Weather results:

{_compact(
    state.get("weather_results", ""),
    2000,
)}

Important:

- Treat flight prices as estimates unless explicitly verified.
- Treat hotel prices as estimates/source-reported unless explicitly
  verified.
- Do not create fake exact prices.
- Do not claim a booking is available.
- Clearly identify uncertain costs.
- If the user did not provide a budget, say that a precise
  affordability judgment cannot be made.

Return a concise budget assessment with:

1. Estimated cost categories
2. Risk areas
3. Money-saving suggestions
4. Whether the plan seems feasible
5. Important assumptions

Do not repeat the source data.

Focus only on budget analysis.
"""

    result = _llm_text(
        "You are a practical travel budget analyst. "
        "Never present estimates as verified prices.",
        prompt,
    )

    print("\n========== BUDGET AGENT OUTPUT ==========")
    print(result)
    print("=========================================\n")

    return {
        "budget_results": result,
        "messages": [
            AIMessage(
                content="Budget agent completed."
            )
        ],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


# ============================================================
# ITINERARY AGENT
# ============================================================

def itinerary_agent(state: TravelState):

    print("\n========== ITINERARY AGENT INPUT ==========")

    print("Trip Constraints:")
    print(
        state.get(
            "trip_constraints",
            {},
        )
    )

    print("\nFlight Results:")
    print(
        state.get(
            "flight_results",
            "",
        )
    )

    print("\nHotel Results:")
    print(
        state.get(
            "hotel_results",
            "",
        )
    )

    print("\nWeather Results:")
    print(
        state.get(
            "weather_results",
            "",
        )
    )

    print("\nBudget Results:")
    print(
        state.get(
            "budget_results",
            "",
        )
    )

    print("===========================================\n")

    # --------------------------------------------------------
    # COMPACT CONTEXT
    # --------------------------------------------------------

    prompt = f"""
Create a clear draft travel itinerary.

User request:

{_compact(
    state.get("user_query", ""),
    2000,
)}

Trip constraints:

{_compact(
    state.get("trip_constraints", {}),
    2000,
)}

Flight results:

{_compact(
    state.get("flight_results", ""),
    2500,
)}

Hotel results:

{_compact(
    state.get("hotel_results", ""),
    2500,
)}

Weather results:

{_compact(
    state.get("weather_results", ""),
    2000,
)}

Budget results:

{_compact(
    state.get("budget_results", ""),
    2500,
)}

Create a practical itinerary.

Include:

- Correct origin → destination direction
- Correct trip duration
- Day-by-day plan
- Transportation guidance
- Accommodation guidance
- Estimated daily spending
- Important travel notes

IMPORTANT ACCURACY RULES:

1. Follow the user's requested origin and destination exactly.

2. Do not reverse the travel direction.

3. Follow the requested duration exactly.

4. Do not convert 5 days into 5 nights unless the user
   explicitly requested that.

5. Do not invent exact flight numbers.

6. Do not invent exact departure times.

7. Do not claim live flight availability.

8. Do not claim hotel room availability.

9. Do not present estimated flight or hotel prices
   as confirmed prices.

10. Clearly label estimated costs as estimates.

11. Current weather must not be presented as future-date
    weather if the requested travel date is outside the
    available forecast period.

12. If future weather is unavailable, provide only general
    seasonal guidance.

13. Do not invent visa, health, legal or entry requirements.
    If such information is not verified in the provided data,
    say that the traveler should verify official requirements.

14. Do not invent facts simply to make the itinerary look complete.

15. Prefer "approximately", "estimated", "typically",
    or "check current availability" when appropriate.

Make the output structured and concise.

Do not repeat all source data.

This is a DRAFT and will be reviewed by a human.
"""

    result = _llm_text(
        "You are an expert itinerary planner. "
        "Accuracy and consistency are more important than "
        "making unsupported claims.",
        prompt,
    )

    result = _clean_html(result)

    print("\n========== ITINERARY OUTPUT ==========")
    print(result)
    print("======================================\n")

    approval_request = f"""
Please review this draft travel plan.

{result}

Pay particular attention to:

- Destination and origin
- Trip duration
- Budget
- Estimated prices
- Weather assumptions
- Hotel information
- Flight information

Reply with approval or feedback.
"""

    return {
        "itinerary": result,
        "approval_request": approval_request,
        "messages": [
            AIMessage(
                content="Draft itinerary created for human review."
            )
        ],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


# ============================================================
# HUMAN APPROVAL AGENT
# ============================================================

def human_approval_agent(state: TravelState):

    feedback = interrupt(
        {
            "question": "Do you approve this itinerary?",
            "draft_itinerary": state.get(
                "itinerary",
                "",
            ),
            "approval_request": state.get(
                "approval_request",
                "",
            ),
            "expected_response": {
                "approved": True,
                "feedback": "Optional feedback for revision",
            },
        }
    )

    approved = feedback["approved"]
    human_feedback = feedback["feedback"]

    print("\n========== HUMAN APPROVAL ==========")
    print("Approved:", approved)
    print("Feedback:", human_feedback)
    print("====================================\n")

    return {
        "approved": approved,
        "human_feedback": human_feedback,
        "messages": [
            AIMessage(
                content="Human approval step completed."
            )
        ],
    }


# ============================================================
# FINAL RESPONSE AGENT
# ============================================================

def final_response_agent(state: TravelState):

    print("\n========== FINAL AGENT INPUT ==========")

    print(
        "Approved:",
        state.get("approved"),
    )

    print(
        "Feedback:",
        state.get("human_feedback"),
    )

    print("=======================================\n")

    # --------------------------------------------------------
    # APPROVED
    # --------------------------------------------------------

    if state.get("approved", False):

        prompt = f"""
The human approved this draft itinerary.

Produce the final polished travel plan.

Draft itinerary:

{_compact(
    state.get("itinerary", ""),
    6000,
)}

Budget notes:

{_compact(
    state.get("budget_results", ""),
    2500,
)}

Final response rules:

- Preserve the correct origin → destination direction.
- Preserve the requested trip duration.
- Do not introduce new unsupported facts.
- Do not invent flight numbers.
- Do not invent exact flight availability.
- Do not claim hotel rooms are available.
- Do not turn estimated prices into confirmed prices.
- Keep estimated prices clearly labelled as estimates.
- Do not present current weather as a future forecast.
- If weather information is unavailable for the requested
  future date, say so briefly.
- Do not invent visa or legal requirements.
- Do not mention internal agents.
- Do not mention LLM processing.
- Do not mention the approval workflow.

Use clean Markdown.

Do not use HTML tags such as <br>.

Keep the final answer practical and concise.
"""

    # --------------------------------------------------------
    # NOT APPROVED
    # --------------------------------------------------------

    else:

        prompt = f"""
The human did not approve the draft itinerary.

Revise the plan using the human's feedback.

Original user request:

{_compact(
    state.get("user_query", ""),
    2000,
)}

Draft itinerary:

{_compact(
    state.get("itinerary", ""),
    5000,
)}

Human feedback:

{_compact(
    state.get("human_feedback", ""),
    2500,
)}

Budget notes:

{_compact(
    state.get("budget_results", ""),
    2500,
)}

Produce a revised final travel plan.

Accuracy rules:

- Preserve the user's origin and destination.
- Preserve the requested duration.
- Do not invent flight numbers.
- Do not invent live flight availability.
- Do not claim hotel availability.
- Keep estimated prices clearly labelled.
- Do not present current weather as future weather.
- Do not invent visa, legal or health requirements.
- Do not introduce unsupported facts.
- Do not mention internal agents.
- Do not mention LLM processing.
- Do not mention the approval workflow.

Use clean Markdown.

Do not use HTML tags such as <br>.

Keep the final answer practical and concise.
"""

    result = _llm_text(
        "You produce accurate, user-ready travel plans. "
        "Never convert uncertain information into facts.",
        prompt,
    )

    result = _clean_html(result)

    print("\n========== FINAL RESPONSE ==========")
    print(result)
    print("====================================\n")

    return {
        "final_response": result,
        "messages": [
            AIMessage(
                content=result
            )
        ],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }