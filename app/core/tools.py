import asyncio
import httpx
from bs4 import BeautifulSoup
from langchain_community.tools import DuckDuckGoSearchRun, WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper, ArxivAPIWrapper
from langchain_community.tools.arxiv.tool import ArxivQueryRun

# Initialize wrappers
search = DuckDuckGoSearchRun()
wiki = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
arxiv = ArxivQueryRun(api_wrapper=ArxivAPIWrapper())

async def web_scrapper(url: str) -> str:
    """
    Custom scrapper with error handling and timeout,
    """
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            return "\n".join(chunk for chunk in chunks if chunk)[:2000]

    except httpx.HTTPStatusError as e:
        return f"Error: HTTP {e.response.status_code} while scraping {url}"
    except Exception as e:
        return f"Scraping failed: {str(e)}"

async def execute_tool(tool_name: str, query: str) -> dict:
    """
    Central dispatcher for tools with safety wrappers.
    """
    # 1. THE SECURITY GUARDRAIL
    forbidden_keywords = ["drop table", "delete from", "forget previous", "system prompt"]
    if any(keyword in query.lower() for keyword in forbidden_keywords):
        return {
            "status": "error", 
            "output": "SECURITY_VIOLATION: Malicious query detected."
        }
    try:
        if tool_name == "search":
            content = await asyncio.to_thread(search.run, query)
            return {"output": content, "status": "success"}
        
        elif tool_name == "wikipedia":
            content = await asyncio.to_thread(wiki.run, query)
            return {"output": content, "status": "success"}
        
        elif tool_name == "arxiv":
            content = await asyncio.to_thread(arxiv.run, query)
            return {"output": content, "status": "success"}
        
        elif tool_name == "scrapper":
            return await web_scrapper(query)
        
        else:
            return f"Tool '{tool_name}' not found."
    
    except Exception as e:
        return f"Tool execution error on {tool_name}: {str(e)}"