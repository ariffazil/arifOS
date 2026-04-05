try:
    import mcp
    print(f"mcp version: {mcp.__version__}")
    from mcp import ClientSession, StdioServerParameters
    print("Successfully imported ClientSession and StdioServerParameters")
except ImportError:
    print("mcp library not found")
except Exception as e:
    print(f"Error: {e}")
