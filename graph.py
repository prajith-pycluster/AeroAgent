import psycopg

from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import END, START, StateGraph

from agents import (
    budget_agent,
    final_response_agent,
    flight_agent,
    hotel_agent,
    human_approval_agent,
    itinerary_agent,
    supervisor_agent,
    weather_agent,
)

from config import DATABASE_URL
from state import TravelState


AGENT_ORDER = [
    "flight_agent",
    "hotel_agent",
    "weather_agent",
    "budget_agent",
    "itinerary_agent",
]


ROUTE_MAP = {
    "flight_agent": "flight_agent",
    "hotel_agent": "hotel_agent",
    "weather_agent": "weather_agent",
    "budget_agent": "budget_agent",
    "itinerary_agent": "itinerary_agent",
}


def _selected_agents(state: TravelState) -> list[str]:
    selected = state.get("selected_agents", [])

    return [
        agent
        for agent in AGENT_ORDER
        if agent in selected
    ]


def route_from_supervisor(state: TravelState) -> str:
    selected = _selected_agents(state)

    return selected[0] if selected else "itinerary_agent"


def route_after_agent(current_agent: str):

    def route(state: TravelState) -> str:

        selected = _selected_agents(state)

        current_index = AGENT_ORDER.index(current_agent)

        for next_agent in AGENT_ORDER[current_index + 1:]:
            if next_agent in selected:
                return next_agent

        return "itinerary_agent"

    return route


def build_graph():

    graph = StateGraph(TravelState)

    # =========================
    # NODES
    # =========================

    graph.add_node("supervisor", supervisor_agent)

    graph.add_node("flight_agent", flight_agent)

    graph.add_node("hotel_agent", hotel_agent)

    graph.add_node("weather_agent", weather_agent)

    graph.add_node("budget_agent", budget_agent)

    graph.add_node("itinerary_agent", itinerary_agent)

    graph.add_node("human_approval", human_approval_agent)

    graph.add_node("final_response", final_response_agent)

    # =========================
    # START
    # =========================

    graph.add_edge(
        START,
        "supervisor"
    )

    # =========================
    # SUPERVISOR ROUTING
    # =========================

    graph.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        ROUTE_MAP,
    )

    # =========================
    # AGENT ROUTING
    # =========================

    graph.add_conditional_edges(
        "flight_agent",
        route_after_agent("flight_agent"),
        ROUTE_MAP,
    )

    graph.add_conditional_edges(
        "hotel_agent",
        route_after_agent("hotel_agent"),
        ROUTE_MAP,
    )

    graph.add_conditional_edges(
        "weather_agent",
        route_after_agent("weather_agent"),
        ROUTE_MAP,
    )

    graph.add_conditional_edges(
        "budget_agent",
        route_after_agent("budget_agent"),
        ROUTE_MAP,
    )

    # =========================
    # ITINERARY
    # =========================

    graph.add_edge(
        "itinerary_agent",
        "human_approval"
    )

    # =========================
    # HUMAN APPROVAL
    # =========================

    graph.add_edge(
        "human_approval",
        "final_response"
    )

    # =========================
    # FINAL
    # =========================

    graph.add_edge(
        "final_response",
        END
    )

    # =========================
    # POSTGRES CHECKPOINTER
    # =========================

    if DATABASE_URL:

        conn = psycopg.connect(
            DATABASE_URL,
            autocommit=True
        )

        checkpointer = PostgresSaver(conn)

        checkpointer.setup()

        # IMPORTANT:
        # Checkpointer MUST be passed to compile()

        return graph.compile(
            checkpointer=checkpointer
        )

    # Fallback to persistent disk-backed checkpointer when DATABASE_URL is not set
    import os
    import pickle
    from collections import defaultdict
    from langgraph.checkpoint.memory import MemorySaver

    class DiskMemorySaver(MemorySaver):
        def __init__(self, filepath=".langgraph_checkpoints.pkl"):
            super().__init__()
            self.filepath = filepath
            if os.path.exists(filepath):
                try:
                    with open(filepath, "rb") as f:
                        data = pickle.load(f)
                        self.storage = defaultdict(lambda: defaultdict(dict), data.get("storage", {}))
                        self.writes = defaultdict(dict, data.get("writes", {}))
                        self.blobs = defaultdict(dict, data.get("blobs", {}))
                except Exception as e:
                    print(f"[Checkpointer]: Could not restore {filepath}: {e}")

        def _save_to_disk(self):
            try:
                with open(self.filepath, "wb") as f:
                    pickle.dump({
                        "storage": dict(self.storage),
                        "writes": dict(self.writes),
                        "blobs": dict(self.blobs),
                    }, f)
            except Exception as e:
                print(f"[Checkpointer]: Could not write {self.filepath}: {e}")

        def put(self, config, checkpoint, metadata, new_versions):
            res = super().put(config, checkpoint, metadata, new_versions)
            self._save_to_disk()
            return res

        def put_writes(self, config, writes, task_id, task_path=""):
            super().put_writes(config, writes, task_id, task_path)
            self._save_to_disk()

    return graph.compile(checkpointer=DiskMemorySaver())


# =========================
# COMPILED APP
# =========================

app = build_graph()