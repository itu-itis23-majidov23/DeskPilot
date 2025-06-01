from autogen_ext.tools.mcp import StdioServerParams
import os


workspace_path = os.path.abspath(".")
allowed_path = os.path.expanduser("~/.")

TIME_SERVER = StdioServerParams(
    command="docker",
    args=[
        "run",
        "-i",
        "--rm",
        "mcp/time"
    ]
)

EMAIL_SERVER = StdioServerParams(
    command="uvx",
    args=[
        "@gongrzhe/server-gmail-autoauth-mcp"
    ]
)

WEB_SEARCH_SERVER = StdioServerParams(
    command="uvx",
    args=["openai-websearch-mcp"],
    env={
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    }
)

WIKIPEDIA_SERVER = StdioServerParams(
    command="wikipedia-mcp",
    args=[
        
    ],
)

SEQUENTIAL_THINKING_SERVER = StdioServerParams(
    command='docker',
    args=[
        "run",
        "--rm",
        "-i",
        "mcp/sequentialthinking",
    ]
)

FILESYSTEM_SERVER = StdioServerParams(
    command='docker',
    args=[
        "run",
        "-i",
        "--rm",
        "--mount", f"type=bind,src={workspace_path},dst=/projects/workspace",
        "--mount", f"type=bind,src={allowed_path},dst=/mnt/host",
        "mcp/filesystem",
        "/mnt/host"
    ]
)
