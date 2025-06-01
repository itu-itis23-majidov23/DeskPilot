import asyncio
from typing import List, Optional

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.tools.mcp import McpWorkbench, StdioServerParams

# Choose LLM Client
from autogen_ext.models.openai import OpenAIChatCompletionClient
# from autogen_ext.models.gemini import GeminiChatClient

# MCP Server imports
from mcp_servers import (
    TIME_SERVER,
    EMAIL_SERVER,
    WEB_SEARCH_SERVER,
    WIKIPEDIA_SERVER,
    SEQUENTIAL_THINKING_SERVER,
    FILESYSTEM_SERVER,
)

TOOL_CATALOG = {
    "time": TIME_SERVER,
    "email": EMAIL_SERVER,
    "search": WEB_SEARCH_SERVER,
    "wikipedia": WIKIPEDIA_SERVER,
    "plan": SEQUENTIAL_THINKING_SERVER,
    "file": FILESYSTEM_SERVER,
}

class DeskPilot:
    def __init__(self, model: str = "gemini-2.0-flash"):
        self.model_client = OpenAIChatCompletionClient(model=model)
        # self.model_client = GeminiChatClient(model="models/gemini-1.5-pro")

    async def infer_tools(self, question: str) -> List[str]:
        prompt = f"""
        You are a tool router. Given the question: "{question}", 
        return a list of tool categories to use. Only respond with a comma-separated list
        using these exact tool keywords if needed:
        - time
        - email
        - search
        - wikipedia
        - plan
        - file
        If no tool is needed, return: none
        """
        agent = AssistantAgent(name="router_agent", model_client=self.model_client)
        result = await agent.run(task=prompt)
        text = result.messages[-1].content.strip().lower()
        return [] if "none" in text else [t.strip() for t in text.split(",") if t.strip() in TOOL_CATALOG]

    async def run_tool_sequence(self, tools: List[str], task: str) -> str:
        output = ""
        for tool in tools:
            print(f"\n[🔧 Running tool: {tool}]")
            server = TOOL_CATALOG[tool]
            async with McpWorkbench(server) as workbench:
                agent = AssistantAgent(
                    name=f"{tool}_agent",
                    model_client=self.model_client,
                    workbench=workbench,
                    reflect_on_tool_use=True
                )
                result = await agent.run(task=task if not output else output)
                output = result.messages[-1].content if isinstance(result.messages[-1], TextMessage) else output
        return output or "[❌ No response generated.]"

    async def run(self, question: str) -> str:
        tools = await self.infer_tools(question)
        if tools:
            return await self.run_tool_sequence(tools, question)
        else:
            print("\n[💬 No tools needed → using LLM only]")
            agent = AssistantAgent(name="llm_agent", model_client=self.model_client)
            result = await agent.run(task=question)
            return result.messages[-1].content if isinstance(result.messages[-1], TextMessage) else "[❌ No response]"

    async def close(self):
        await self.model_client.close()


async def main():
    pilot = DeskPilot()
    print("🧠 DeskPilot ready. Ask your question (Ctrl+C to exit).\n")

    try:
        while True:
            question = input(">> ").strip()
            if not question:
                continue
            response = await pilot.run(question)
            print(f"\n🟢 Response:\n{response}\n")

    except KeyboardInterrupt:
        print("\n👋 Exiting DeskPilot...")
    finally:
        await pilot.close()


if __name__ == "__main__":
    asyncio.run(main())
