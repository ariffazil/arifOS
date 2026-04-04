# FastMCP Python SDK Technical Deep Dive

## Executive Summary

FastMCP is a high-level Python framework that simplifies building Model Context Protocol (MCP) servers and clients. Originally created by Prefect and now actively maintained as a standalone project, FastMCP provides decorator-based APIs, automatic schema generation, type safety, and production-ready features including authentication, authorization, and observability.

**Key Statistics:**
- 23.5k+ GitHub stars
- 1M+ daily downloads
- Powers 70% of MCP servers across all languages
- FastMCP 1.0 was incorporated into the official MCP Python SDK in 2024

---

## 1. FastMCP Class Architecture

### 1.1 Constructor Parameters

The `FastMCP` class serves as the central object representing your MCP application:

```python
from fastmcp import FastMCP

mcp = FastMCP(
    name="MyAssistantServer",           # Required: Server identifier
    instructions="Server description",   # Optional: Human-readable instructions
    version="1.0.0",                    # Optional: Server version
    website_url="https://example.com",  # Optional: Documentation URL
    icons={                             # Optional: UI icons for clients
        "emoji": "🚀",
        "color": "#FF5733"
    },
    # Advanced configuration
    mask_error_details=True,            # Security: Hide internal error details
    warn_on_duplicate_tools=True,       # Development: Warn on duplicate registrations
)
```

### 1.2 Server Lifecycle Management

```python
from fastmcp import FastMCP

mcp = FastMCP("Lifecycle Demo")

# Registration phase - add tools, resources, prompts
@mcp.tool
def example_tool():
    return "Hello"

# Server execution - run with different transports
if __name__ == "__main__":
    # STDIO transport (default, for local tools)
    mcp.run()
    
    # Or explicitly specify transport
    mcp.run(transport="stdio")
    
    # HTTP transport (for remote deployments)
    mcp.run(transport="http", host="127.0.0.1", port=8000)
    
    # SSE transport (legacy, backward compatibility)
    mcp.run(transport="sse", host="127.0.0.1", port=8000)
```

### 1.3 Configuration Options

```python
from fastmcp import FastMCP
from fastmcp.server.auth import require_scopes
from fastmcp.server.middleware import AuthMiddleware

# Server with authentication and middleware
mcp = FastMCP(
    name="SecureServer",
    
    # Error handling
    mask_error_details=True,
    
    # Global authorization via middleware
    middleware=[
        AuthMiddleware(auth=require_scopes("mcp:access")),
    ],
    
    # Development settings
    debug=True,
)

# Access settings programmatically
mcp.settings.mount_path = "/api/v1"  # For ASGI mounting
```

---

## 2. Server Primitives Implementation

### 2.1 Tools

Tools are executable functions that LLMs can invoke to perform actions.

#### Basic Tool Registration

```python
from fastmcp import FastMCP

mcp = FastMCP("Calculator")

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two integer numbers together."""
    return a + b

# Async tools are fully supported
@mcp.tool
async def fetch_data(url: str) -> dict:
    """Fetch data from a URL asynchronously."""
    import httpx
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()
```

#### Advanced Tool Configuration

```python
from fastmcp import FastMCP
from fastmcp.server.auth import require_scopes

mcp = FastMCP("AdvancedTools")

@mcp.tool(
    name="find_products",           # Custom tool name
    description="Search product catalog",  # Override docstring
    tags={"catalog", "search"},      # Organization tags
    meta={"version": "1.2", "author": "team"},  # Custom metadata
    annotations={                   # MCP annotations (v2.2.7+)
        "title": "Find Products",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
    auth=require_scopes("read:products"),  # Authorization
)
def search_products(query: str, category: str | None = None) -> list[dict]:
    """Internal description (overridden by description param)."""
    return [{"id": 1, "name": "Product"}]
```

#### Type Annotations and Pydantic Integration

```python
from fastmcp import FastMCP
from pydantic import BaseModel, Field
from typing import Literal

mcp = FastMCP("TypedTools")

# Pydantic models for complex inputs
class Address(BaseModel):
    street: str
    city: str
    zip_code: str
    country: str = "USA"

class User(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r"^[^@]+@[^@]+$")
    age: int = Field(..., ge=0, le=150)
    role: Literal["admin", "user", "guest"] = "user"
    address: Address | None = None

@mcp.tool
def create_user(user: User) -> dict:
    """Create a new user with validated input."""
    return {
        "id": 123,
        "name": user.name,
        "email": user.email,
        "role": user.role,
    }

# Return type annotations
from fastmcp.types import Image, TextContent

@mcp.tool
def get_user_avatar(user_id: int) -> Image:
    """Return an image for the user."""
    # Return Image object with binary data
    return Image(data=avatar_bytes, format="png")
```

#### Return Value Handling

```python
from fastmcp import FastMCP
from fastmcp.types import TextContent, Image, EmbeddedResource

mcp = FastMCP("ReturnTypes")

# String return - automatically wrapped as TextContent
@mcp.tool
def simple_return() -> str:
    return "Hello, World!"

# Dict/List return - automatically JSON serialized
@mcp.tool
def structured_return() -> dict:
    return {"status": "success", "data": [1, 2, 3]}

# Multiple content types
@mcp.tool
def mixed_return() -> list[TextContent | Image]:
    return [
        TextContent(text="Here's your image:"),
        Image(data=image_bytes, format="png"),
    ]

# Explicit TextContent
@mcp.tool
def explicit_text() -> TextContent:
    return TextContent(text="Explicit content type")
```

#### Error Handling in Tools

```python
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

mcp = FastMCP("ErrorHandling")

@mcp.tool
def divide(a: float, b: float) -> float:
    """Divide a by b with proper error handling."""
    if b == 0:
        # ToolError messages are always sent to clients
        raise ToolError("Division by zero is not allowed.")
    
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Both arguments must be numbers.")
    
    return a / b

# With masked error details (security)
mcp_secure = FastMCP("SecureServer", mask_error_details=True)

@mcp_secure.tool
def sensitive_operation() -> str:
    """Internal errors are masked, ToolError messages are shown."""
    try:
        result = risky_database_call()
        return result
    except DatabaseError as e:
        # Internal error details hidden from client
        raise  # Generic error message sent
    except ValueError as e:
        # Explicit error shown to client
        raise ToolError(f"Invalid input: {str(e)}")
```

### 2.2 Resources

Resources expose read-only data sources via URI-based addressing.

#### Static Resources

```python
from fastmcp import FastMCP

mcp = FastMCP("Resources")

# Simple static resource
@mcp.resource("config://version")
def get_version() -> str:
    """Get the server version."""
    return "2.0.1"

# With full metadata
@mcp.resource(
    uri="docs://guide",
    name="userGuide",
    title="User Guide",
    description="Complete user documentation",
    mime_type="text/markdown",
    meta={"version": "1.0", "category": "documentation"},
    annotations={
        "readOnlyHint": True,
        "idempotentHint": True,
    },
)
def get_user_guide() -> str:
    return "# User Guide\n\nWelcome to..."
```

#### Dynamic Resource Templates

```python
from fastmcp import FastMCP

mcp = FastMCP("ResourceTemplates")

# Template with path parameter
@mcp.resource("users://{user_id}/profile")
def get_user_profile(user_id: int) -> dict:
    """Get profile for a specific user."""
    return {
        "user_id": user_id,
        "name": f"User {user_id}",
        "status": "active"
    }

# Multiple parameters
@mcp.resource("organizations://{org_id}/projects/{project_id}")
def get_project(org_id: str, project_id: str) -> dict:
    """Get project details within an organization."""
    return {
        "organization": org_id,
        "project": project_id,
        "tasks": []
    }

# Wildcard parameters (RFC 6570)
@mcp.resource("files://{path*}")
def get_file(path: str) -> str:
    """Get file content by path."""
    # path captures multiple segments: "docs/readme.md"
    with open(path, 'r') as f:
        return f.read()

# Query parameters (RFC 6570)
@mcp.resource("search://query{?q,category,limit}")
def search(q: str, category: str | None = None, limit: int = 10) -> list:
    """Search with query parameters."""
    results = perform_search(q, category, limit)
    return results
```

#### MIME Type Handling

```python
from fastmcp import FastMCP
from fastmcp.types import Image, Blob

mcp = FastMCP("MimeTypes")

# Text resources (default)
@mcp.resource("text://example", mime_type="text/plain")
def get_text() -> str:
    return "Plain text content"

# JSON resources
@mcp.resource("data://config", mime_type="application/json")
def get_config() -> dict:
    return {"setting": "value"}

# Binary resources
@mcp.resource("images://logo", mime_type="image/png")
def get_logo() -> Image:
    return Image(data=png_bytes, format="png")

# Generic binary
@mcp.resource("files://document", mime_type="application/pdf")
def get_pdf() -> Blob:
    return Blob(data=pdf_bytes, mime_type="application/pdf")
```

### 2.3 Prompts

Prompts define reusable message templates to guide LLM interactions.

#### Basic Prompts

```python
from fastmcp import FastMCP

mcp = FastMCP("Prompts")

# Simple string prompt
@mcp.prompt
def summarize_request(text: str) -> str:
    """Generate a prompt asking for a summary."""
    return f"Please summarize the following text:\n\n{text}"

# Multi-line prompt with formatting
@mcp.prompt
def code_review(code: str, language: str = "python") -> str:
    """Generate a code review prompt."""
    return f"""Please review the following {language} code:

```{language}
{code}
```

Consider:
1. Code correctness and edge cases
2. Performance implications
3. Security vulnerabilities
4. Best practices for {language}
"""
```

#### Advanced Prompt Patterns

```python
from fastmcp import FastMCP
from fastmcp.types import Message, TextContent

mcp = FastMCP("AdvancedPrompts")

# Multi-message prompts (conversation context)
@mcp.prompt
def guided_conversation(topic: str) -> list[Message]:
    """Create a multi-turn conversation prompt."""
    return [
        Message(
            role="system",
            content=TextContent(text=f"You are an expert in {topic}.")
        ),
        Message(
            role="user",
            content=TextContent(text=f"Explain {topic} to a beginner.")
        ),
        Message(
            role="assistant",
            content=TextContent(text="I'd be happy to explain! Let me start with...")
        ),
        Message(
            role="user",
            content=TextContent(text="Can you give me a concrete example?")
        ),
    ]

# Parameterized with context injection
from fastmcp.server.context import Context
from fastmcp.dependencies import CurrentContext

@mcp.prompt
async def contextual_prompt(
    query: str,
    ctx: Context = CurrentContext()
) -> str:
    """Generate prompt with server context."""
    # Access server information
    server_info = f"Server: {ctx.server_name}"
    
    return f"""{server_info}

User query: {query}

Please provide a helpful response."""
```

---

## 3. Transport Mechanisms

### 3.1 STDIO Transport (Default)

Best for local development and command-line tools.

```python
from fastmcp import FastMCP

mcp = FastMCP("LocalServer")

@mcp.tool
def local_tool() -> str:
    return "Running locally"

if __name__ == "__main__":
    # STDIO is the default transport
    mcp.run()
    # Equivalent to:
    # mcp.run(transport="stdio")
```

**Characteristics:**
- Client spawns server as subprocess
- Communication via stdin/stdout
- Messages delimited by newlines
- No network overhead
- Single client per server process

### 3.2 Streamable HTTP Transport (Recommended)

Best for production, cloud hosting, and multiple clients.

```python
from fastmcp import FastMCP

mcp = FastMCP("HTTPServer")

@mcp.tool
def remote_tool() -> str:
    return "Accessible via HTTP"

if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8000,
        path="/mcp",  # Default endpoint
    )
```

**Advanced HTTP Configuration:**

```python
from fastmcp import FastMCP
from fastmcp.server.auth import require_scopes

mcp = FastMCP("SecureHTTPServer")

# Mount to existing ASGI application
from starlette.applications import Starlette
from starlette.routing import Mount

app = Starlette(routes=[
    Mount("/mcp", app=mcp.sse_app()),
])

# Multiple servers with different paths
github_mcp = FastMCP("GitHub API")
github_mcp.settings.mount_path = "/github"

browser_mcp = FastMCP("Browser")
browser_mcp.settings.mount_path = "/browser"

combined_app = Starlette(routes=[
    Mount("/github", app=github_mcp.sse_app()),
    Mount("/browser", app=browser_mcp.sse_app()),
])
```

### 3.3 SSE Transport (Legacy)

For backward compatibility with older clients.

```python
from fastmcp import FastMCP

mcp = FastMCP("LegacyServer")

if __name__ == "__main__":
    mcp.run(
        transport="sse",
        host="127.0.0.1",
        port=8000,
    )
```

**Note:** SSE transport is superseded by Streamable HTTP. Use HTTP for new projects.

### 3.4 Transport Selection Criteria

| Criteria | STDIO | HTTP/SSE |
|----------|-------|----------|
| **Use Case** | Local tools, CLI scripts | Remote servers, web deployment |
| **Clients** | Single client | Multiple concurrent clients |
| **Network** | None (local process) | Requires network configuration |
| **Authentication** | Environment variables | OAuth, API keys, tokens |
| **Scalability** | Process-per-client | Server handles multiple clients |
| **Deployment** | Local only | Cloud, containers, serverless |

---

## 4. Dependency Injection

FastMCP uses Docket's dependency injection system for managing runtime dependencies.

### 4.1 CurrentContext - Accessing Request Context

```python
from fastmcp import FastMCP
from fastmcp.dependencies import CurrentContext
from fastmcp.server.context import Context

mcp = FastMCP("ContextDemo")

# Explicit dependency injection (recommended v2.14+)
@mcp.tool
async def process_file(file_uri: str, ctx: Context = CurrentContext()) -> str:
    """Process a file with logging and resource access."""
    # Log to client
    await ctx.info(f"Processing {file_uri}...")
    await ctx.debug("Debug information")
    
    # Read another resource
    data = await ctx.read_resource(file_uri)
    
    # Report progress
    await ctx.report_progress(50, 100)
    
    return "Processed"

# Works with resources and prompts too
@mcp.resource("data://user")
async def get_user_data(ctx: Context = CurrentContext()) -> dict:
    await ctx.debug("Fetching user data")
    return {"user_id": "example"}

@mcp.prompt
async def data_analysis_request(dataset: str, ctx: Context = CurrentContext()) -> str:
    await ctx.info(f"Analyzing dataset: {dataset}")
    return f"Please analyze: {dataset}"
```

### 4.2 Legacy Type-Hint Injection

```python
from fastmcp import FastMCP, Context

mcp = FastMCP("LegacyContext")

# Context injected via type hint (backward compatible)
@mcp.tool
async def legacy_tool(query: str, ctx: Context) -> str:
    """Context is automatically injected based on type hint."""
    await ctx.info(f"Processing: {query}")
    return f"Results for: {query}"

# Optional context
@mcp.tool
async def optional_context(query: str, ctx: Context | None = None) -> str:
    if ctx:
        await ctx.info("Context available")
    return "Done"
```

### 4.3 get_context() Function

For nested function calls where passing context is inconvenient:

```python
from fastmcp import FastMCP
from fastmcp.server.dependencies import get_context

mcp = FastMCP("NestedContext")

async def process_data(data: list[float]) -> dict:
    """Utility function that needs context internally."""
    # Get active context from anywhere in request flow
    ctx = get_context()
    await ctx.info(f"Processing {len(data)} data points")
    return {"processed": len(data)}

@mcp.tool
async def analyze_dataset(dataset_name: str) -> dict:
    data = load_data(dataset_name)
    return await process_data(data)
```

### 4.4 CurrentFastMCP - Server Access

```python
from fastmcp import FastMCP
from fastmcp.dependencies import CurrentFastMCP

mcp = FastMCP("ServerAccess")

@mcp.tool
async def server_info(server: FastMCP = CurrentFastMCP()) -> dict:
    """Access the FastMCP server instance."""
    return {
        "name": server.name,
        "version": getattr(server, 'version', 'unknown'),
        "tools": len(server._tools),
        "resources": len(server._resources),
    }

# Using get_server() function
from fastmcp.server.dependencies import get_server

def get_server_name() -> str:
    return get_server().name
```

### 4.5 Custom Dependencies with Depends()

```python
from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from contextlib import asynccontextmanager

mcp = FastMCP("CustomDeps")

# Simple function dependency
def get_config() -> dict:
    return {"api_url": "https://api.example.com", "timeout": 30}

# Async function dependency
async def get_user_id() -> int:
    # Could fetch from database, external service, etc.
    return 42

@mcp.tool
async def fetch_data(
    query: str,
    config: dict = Depends(get_config),
    user_id: int = Depends(get_user_id),
) -> str:
    """Dependencies automatically injected."""
    return f"User {user_id} fetching '{query}' from {config['api_url']}"

# Async context manager for resource management
@asynccontextmanager
async def get_database():
    """Database connection with automatic cleanup."""
    db = await connect_to_database()
    try:
        yield db
    finally:
        await db.close()

@mcp.tool
async def query_users(sql: str, db = Depends(get_database)) -> list:
    """Database connection automatically managed."""
    return await db.execute(sql)

# Nested dependencies with caching
def get_base_url() -> str:
    return "https://api.example.com"

def get_api_client(base_url: str = Depends(get_base_url)) -> dict:
    return {"base_url": base_url, "version": "v1"}

@mcp.tool
async def call_api(endpoint: str, client: dict = Depends(get_api_client)) -> str:
    return f"Calling {client['base_url']}/{client['version']}/{endpoint}"
```

### 4.6 Dependency Caching

Dependencies are cached per-request:

```python
from fastmcp import FastMCP
from fastmcp.dependencies import Depends

mcp = FastMCP("CachingDemo")

def get_db_connection():
    print("Connecting to database...")  # Printed once per request
    return {"connection": "active"}

def get_user_repo(db=Depends(get_db_connection)):
    return {"db": db, "type": "user"}

def get_order_repo(db=Depends(get_db_connection)):
    return {"db": db, "type": "order"}

@mcp.tool
async def process_order(
    order_id: str,
    users=Depends(get_user_repo),
    orders=Depends(get_order_repo),
) -> str:
    # Both repos share the same db connection (cached)
    return f"Processed order {order_id}"
```

---

## 5. Client Integration

### 5.1 ClientSession Usage

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def use_client():
    # Configure server parameters
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"],
        env={"WORKSPACE": "/safe/workspace"}
    )
    
    # Connect via stdio
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()
            
            # Use the session...
            tools = await session.list_tools()
            print(f"Available tools: {[t.name for t in tools.tools]}")
```

### 5.2 FastMCP Client

```python
from fastmcp import Client

async def use_fastmcp_client():
    # Connect to HTTP server
    async with Client("http://localhost:8000/mcp") as client:
        # List available resources
        resources = await client.list_resources()
        
        # Call a tool
        result = await client.call_tool("my_tool", {"param": "value"})
        
        # Read a resource
        data = await client.read_resource("resource://data")
        
        # Get a prompt
        prompt = await client.get_prompt("my_prompt", {"arg": "value"})
```

### 5.3 Server Introspection

```python
from fastmcp import Client

async def introspect_server():
    async with Client("http://localhost:8000/mcp") as client:
        # List all tools
        tools_response = await client.list_tools()
        for tool in tools_response.tools:
            print(f"Tool: {tool.name}")
            print(f"  Description: {tool.description}")
            print(f"  Schema: {tool.inputSchema}")
        
        # List all resources
        resources_response = await client.list_resources()
        for resource in resources_response.resources:
            print(f"Resource: {resource.uri}")
            print(f"  Name: {resource.name}")
            print(f"  MIME type: {resource.mimeType}")
        
        # List all prompts
        prompts_response = await client.list_prompts()
        for prompt in prompts_response.prompts:
            print(f"Prompt: {prompt.name}")
            print(f"  Description: {prompt.description}")
```

### 5.4 Tool Invocation

```python
from fastmcp import Client

async def call_tools():
    async with Client("http://localhost:8000/mcp") as client:
        # Simple tool call
        result = await client.call_tool("add", {"a": 5, "b": 3})
        print(f"Result: {result.data}")  # 8
        
        # Tool with complex arguments
        result = await client.call_tool(
            "create_user",
            {
                "user": {
                    "name": "Alice",
                    "email": "alice@example.com",
                    "age": 30
                }
            }
        )
        
        # Handle tool errors
        try:
            result = await client.call_tool("divide", {"a": 10, "b": 0})
        except Exception as e:
            print(f"Tool error: {e}")
```

### 5.5 Resource Access

```python
from fastmcp import Client

async def access_resources():
    async with Client("http://localhost:8000/mcp") as client:
        # Read static resource
        version = await client.read_resource("config://version")
        print(f"Version: {version.content}")
        
        # Read template resource
        profile = await client.read_resource("users://123/profile")
        print(f"Profile: {profile.content}")
        
        # Subscribe to resource updates
        await client.subscribe_resource("data://live-feed")
```

### 5.6 Connection Initialization Patterns

```python
import asyncio
from contextlib import AsyncExitStack
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

class MCPClient:
    def __init__(self):
        self.session = None
        self.exit_stack = AsyncExitStack()
    
    async def connect_to_server(self, server_url: str):
        """Connect to an MCP server."""
        transport = StreamableHttpTransport(server_url)
        
        self.session = await self.exit_stack.enter_async_context(
            Client(transport=transport)
        )
        
        # List available capabilities
        tools = await self.session.list_tools()
        print(f"Connected with tools: {[t.name for t in tools.tools]}")
    
    async def cleanup(self):
        """Clean up resources."""
        await self.exit_stack.aclose()

# Usage
async def main():
    client = MCPClient()
    try:
        await client.connect_to_server("http://localhost:8000/mcp")
        # Use client...
    finally:
        await client.cleanup()
```

---

## 6. Advanced Features

### 6.1 Background Tasks

FastMCP integrates with Docket for background task execution (requires `fastmcp[tasks]`):

```python
from fastmcp import FastMCP
from fastmcp.dependencies import CurrentDocket

mcp = FastMCP("BackgroundTasks")

# Install: pip install fastmcp[tasks]

@mcp.tool
async def long_running_task(
    data: str,
    docket=CurrentDocket()
) -> str:
    """Submit a task for background processing."""
    # Schedule background task
    task = await docket.submit(
        process_large_dataset,
        args=(data,),
        queue="heavy-processing"
    )
    
    return f"Task {task.id} submitted for processing"

async def process_large_dataset(data: str) -> None:
    """Background task function."""
    # Long-running processing
    await asyncio.sleep(60)
    await save_results(data)
```

### 6.2 Telemetry and Observability

FastMCP 3.0 includes native OpenTelemetry instrumentation:

```python
from fastmcp import FastMCP
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Configure OpenTelemetry
trace.set_tracer_provider(TracerProvider())
otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4317")
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

mcp = FastMCP("ObservableServer")

@mcp.tool
def instrumented_tool(query: str) -> dict:
    """Tool calls are automatically traced."""
    tracer = trace.get_tracer(__name__)
    
    with tracer.start_as_current_span("database_query") as span:
        span.set_attribute("query", query)
        result = execute_query(query)
        span.set_attribute("results", len(result))
    
    return result

# Every tool call, resource read, and prompt render is traced
# with standardized MCP attributes
```

### 6.3 Authentication and Authorization

#### Server Authentication

```python
from fastmcp import FastMCP
from fastmcp.server.auth import require_scopes, restrict_tag
from fastmcp.server.middleware import AuthMiddleware

mcp = FastMCP("SecureServer")

# Global authentication via middleware
mcp = FastMCP(
    "SecureServer",
    middleware=[
        AuthMiddleware(auth=require_scopes("mcp:access")),
    ],
)

# Component-level authorization
@mcp.tool(auth=require_scopes("admin"))
def admin_operation() -> str:
    """Requires 'admin' scope."""
    return "Admin action completed"

@mcp.tool(auth=require_scopes("read", "write"))
def read_write_operation() -> str:
    """Requires both 'read' AND 'write' scopes."""
    return "Read/write action completed"

# Tag-based authorization
mcp = FastMCP(
    "TaggedServer",
    middleware=[
        AuthMiddleware(auth=restrict_tag("admin", scopes=["admin"])),
        AuthMiddleware(auth=restrict_tag("write", scopes=["write"])),
    ]
)

@mcp.tool(tags={"admin"})
def delete_all_data() -> str:
    """Tagged 'admin', requires 'admin' scope."""
    return "Deleted"

@mcp.tool(tags={"write"})
def update_record(id: str, data: str) -> str:
    """Tagged 'write', requires 'write' scope."""
    return f"Updated {id}"

@mcp.tool
def read_record(id: str) -> str:
    """No tag, accessible to all authenticated users."""
    return f"Record {id}"
```

#### Accessing Authentication Tokens

```python
from fastmcp import FastMCP
from fastmcp.server.dependencies import get_access_token

mcp = FastMCP("TokenAccess")

@mcp.tool
def personalized_greeting() -> str:
    """Greet user based on their token claims."""
    token = get_access_token()
    
    if token is None:
        return "Hello, guest!"
    
    name = token.claims.get("name", "user")
    return f"Hello, {name}!"

@mcp.tool
def user_dashboard() -> dict:
    """Return user-specific data based on token."""
    token = get_access_token()
    
    if token is None:
        return {"error": "Not authenticated"}
    
    return {
        "client_id": token.client_id,
        "scopes": token.scopes,
        "claims": token.claims,
    }
```

#### Client Authentication

```python
from fastmcp import Client
from fastmcp.client.auth import OAuth

# OAuth authentication
oauth = OAuth(scopes=["user", "read"])

async with Client(
    "https://your-server.fastmcp.app/mcp",
    auth=oauth
) as client:
    await client.ping()

# Pre-registered client
oauth = OAuth(
    client_id="my-client-id",
    client_secret="my-client-secret",
    scopes=["read", "write"]
)

# Custom token storage
from fastmcp.client.auth import FileTokenStorage

oauth = OAuth(
    scopes=["user"],
    token_storage=FileTokenStorage("~/.mcp/tokens.json")
)
```

### 6.4 Error Handling Patterns

```python
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.server.middleware import ErrorHandlingMiddleware, RetryMiddleware

mcp = FastMCP(
    "ResilientServer",
    middleware=[
        ErrorHandlingMiddleware(),
        RetryMiddleware(max_retries=3, backoff_factor=2.0),
    ]
)

# Structured error handling
class ValidationError(ToolError):
    """Custom validation error."""
    pass

class NotFoundError(ToolError):
    """Resource not found error."""
    pass

@mcp.tool
def get_user(user_id: str) -> dict:
    """Get user with proper error handling."""
    if not user_id:
        raise ValidationError("user_id is required")
    
    user = database.find_user(user_id)
    if not user:
        raise NotFoundError(f"User {user_id} not found")
    
    return user

# Exception chaining with context
@mcp.tool
async def external_api_call(endpoint: str) -> dict:
    """Call external API with error context."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://api.example.com/{endpoint}")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise NotFoundError(f"Endpoint {endpoint} not found") from e
        elif e.response.status_code == 429:
            raise ToolError("Rate limit exceeded. Please retry later.") from e
        else:
            raise ToolError(f"API error: {e.response.status_code}") from e
    except httpx.TimeoutException as e:
        raise ToolError("Request timed out. Please try again.") from e
```

### 6.5 Testing

#### In-Memory Testing

```python
import pytest
from fastmcp import FastMCP, Client

# Create test server
@pytest.fixture
def weather_server():
    server = FastMCP("WeatherServer")
    
    @server.tool
    def get_temperature(city: str) -> dict:
        temps = {"NYC": 72, "LA": 85, "Chicago": 68}
        return {"city": city, "temp": temps.get(city, 70)}
    
    return server

# Test with in-memory client
async def test_temperature_tool(weather_server):
    async with Client(weather_server) as client:
        result = await client.call_tool("get_temperature", {"city": "LA"})
        assert result.data == {"city": "LA", "temp": 85}
```

#### Mocking External Dependencies

```python
from unittest.mock import AsyncMock, patch

async def test_with_mocks():
    server = FastMCP("DataServer")
    mock_db = AsyncMock()
    mock_db.fetch_users.return_value = [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"}
    ]
    
    @server.tool
    async def list_users() -> list:
        return await mock_db.fetch_users()
    
    async with Client(server) as client:
        result = await client.call_tool("list_users", {})
        assert len(result.data) == 2
        mock_db.fetch_users.assert_called_once()
```

#### Network Transport Testing

```python
import pytest
from fastmcp import FastMCP, Client
from fastmcp.client.transports import StreamableHttpTransport
from fastmcp.utilities.tests import run_server_async

def create_test_server():
    server = FastMCP("TestServer")
    
    @server.tool
    def greet(name: str) -> str:
        return f"Hello, {name}!"
    
    return server

@pytest.fixture
async def http_server():
    server = create_test_server()
    async with run_server_async(server) as url:
        yield url

async def test_http_transport(http_server: str):
    async with Client(
        transport=StreamableHttpTransport(http_server)
    ) as client:
        result = await client.call_tool("greet", {"name": "World"})
        assert result.data == "Hello, World!"
```

### 6.6 Server Composition

```python
from fastmcp import FastMCP

# Create modular servers
calculator_mcp = FastMCP("Calculator")
@calculator_mcp.tool
def add(a: float, b: float) -> float:
    return a + b

weather_mcp = FastMCP("Weather")
@weather_mcp.tool
def get_forecast(city: str) -> dict:
    return {"city": city, "forecast": "Sunny"}

# Compose into parent server
main_mcp = FastMCP("MainServer")
main_mcp.mount("/calc", calculator_mcp)
main_mcp.mount("/weather", weather_mcp)

# Or import (static copy)
main_mcp.import_server(calculator_mcp)
main_mcp.import_server(weather_mcp)
```

### 6.7 Versioning

```python
from fastmcp import FastMCP

mcp = FastMCP("VersionedServer")

# Multiple versions of same tool
@mcp.tool(version="1.0")
def process_data_v1(data: str) -> str:
    """Legacy processing."""
    return data.upper()

@mcp.tool(version="2.0")
def process_data_v2(data: str, options: dict | None = None) -> dict:
    """Enhanced processing with options."""
    return {
        "original": data,
        "processed": data.upper(),
        "options": options or {}
    }

# FastMCP exposes highest version by default
# Use VersionFilter to expose specific versions
```

---

## 7. Context API Reference

The `Context` object provides access to MCP session capabilities:

```python
from fastmcp.server.context import Context

class Context:
    # Logging
    async def debug(self, message: str) -> None
    async def info(self, message: str) -> None
    async def warning(self, message: str) -> None
    async def error(self, message: str) -> None
    
    # Progress reporting
    async def report_progress(self, current: int, total: int) -> None
    
    # Resource access
    async def read_resource(self, uri: str) -> Resource
    
    # LLM sampling
    async def sample(
        self,
        message: str,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> SamplingResult
    
    # HTTP requests
    async def http_request(
        self,
        method: str,
        url: str,
        headers: dict | None = None,
        body: str | None = None,
    ) -> HttpResponse
```

---

## 8. Best Practices Summary

### Security
- Use `mask_error_details=True` in production
- Implement proper authentication and authorization
- Validate all inputs with Pydantic models
- Use `ToolError` for client-facing error messages

### Performance
- Use async functions for I/O-bound operations
- Leverage dependency injection for connection pooling
- Use background tasks for long-running operations
- Implement caching for expensive computations

### Maintainability
- Write comprehensive tests using in-memory clients
- Use type hints throughout
- Document with docstrings
- Organize tools/resources into logical modules

### Deployment
- Use HTTP transport for remote deployments
- Configure proper reverse proxy settings (nginx)
- Enable OpenTelemetry for observability
- Use environment variables for configuration

---

## References

- **Documentation:** https://gofastmcp.com
- **GitHub:** https://github.com/jlowin/fastmcp
- **MCP Specification:** https://modelcontextprotocol.io
- **PyPI:** `pip install fastmcp`
- **With tasks:** `pip install fastmcp[tasks]`

---

*Document generated for constitutional AI governance system analysis.*
