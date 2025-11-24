# Suggested pattern for new OpenAI Python SDK usage
# import depending on how you vendor the openai package:
# from openai import OpenAI
# or import openai; client = openai.OpenAI(...)

def create_openai_client(api_key: str | None = None):
    try:
        from openai import OpenAI  # modern client
    except Exception:
        import openai as openai_pkg
        OpenAI = getattr(openai_pkg, "OpenAI", None)

    if OpenAI:
        return OpenAI(api_key=api_key) if api_key else OpenAI()
    # Fallback for older patterns (avoid setting global api_key at module level)
    import openai as openai_pkg
    client = getattr(openai_pkg, "OpenAI", None)
    if client:
        return client(api_key=api_key) if api_key else client()
    # Last resort: raise explicit error
    raise RuntimeError("No compatible OpenAI client found. Install official SDK or pin an adapter.")
