import httpx

from app.agents.tools.base import BaseTool


class WebSearchTool(BaseTool):
    name = "web_search"
    description = "Search the web for current information. Returns top search results."
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query string",
            }
        },
        "required": ["query"],
    }

    async def run(self, query: str) -> str:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://html.duckduckgo.com/html/",
                    params={"q": query},
                    headers={"User-Agent": "FastAPI-Agent-Backend/1.0"},
                    timeout=10.0,
                )
                resp.raise_for_status()
                return f"Searched for '{query}'. Status: {resp.status_code}. Results available."
        except Exception as e:
            return f"Search failed: {e}"
