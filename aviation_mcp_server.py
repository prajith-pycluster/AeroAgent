from mcp.server.fastmcp import FastMCP
import requests
import os
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("AviationStack Server")

AVIATION_STACK_API_KEY = os.getenv("AVIATION_STACK_API_KEY")


@mcp.tool()
def list_airports(search: str = "", limit: int = 10, offset: int = 0):
    response = requests.get(
        "https://api.aviationstack.com/v1/airports",
        params={
            "access_key": AVIATION_STACK_API_KEY,
            "search": search,
            "limit": limit,
            "offset": offset,
        },
        timeout=30,
    )

    data = response.json()

    if response.status_code != 200:
        return data

    return data


@mcp.tool()
def list_airlines(search: str = "", limit: int = 10, offset: int = 0):
    response = requests.get(
        "https://api.aviationstack.com/v1/airlines",
        params={
            "access_key": AVIATION_STACK_API_KEY,
            "search": search,
            "limit": limit,
            "offset": offset,
        },
        timeout=30,
    )

    data = response.json()

    if response.status_code != 200:
        return data

    return data


if __name__ == "__main__":
    mcp.run()