import re


def patch_file(filepath):
    with open(filepath, "r") as f:
        content = f.read()

    # The canonical signature string we want to inject
    # The requirement: "Every diagnostic tool should tolerate: {}, payload, _envelope, client_capabilities"
    sig = "payload: Any = None,\n    _envelope: dict[str, Any] | None = None,\n    client_capabilities: dict[str, Any] | None = None,"

    # Patch arif_ping()
    content = re.sub(r"def arif_ping\(\)\s*->", f"def arif_ping(\n    {sig}\n) ->", content)
    content = re.sub(
        r"def _arif_ping\(\n.*?_envelope: dict\[str, Any\] \| None = None,\n\)\s*->",
        lambda m: m.group(0).replace("_envelope: dict[str, Any] | None = None,", f"{sig}"),
        content,
        flags=re.DOTALL,
    )

    # Patch arif_schema_echo
    content = re.sub(
        r"def arif_schema_echo\(params: dict = \{\}\)\s*->",
        f"def arif_schema_echo(\n    {sig}\n) ->",
        content,
    )
    # Fix the usage of params inside the first arif_schema_echo
    content = content.replace(
        "received_keys = sorted(params.keys())",
        "params = payload if isinstance(payload, dict) else {}\n    received_keys = sorted(params.keys())",
    )

    # Patch arif_transport_echo
    content = re.sub(
        r'def arif_transport_echo\(\n    protocol_version: str = "unknown",\n    client_name: str = "unknown",\n    client_version: str = "unknown",\n    transport: str = "streamable_http",\n\)\s*->',
        f'def arif_transport_echo(\n    protocol_version: str = "unknown",\n    client_name: str = "unknown",\n    client_version: str = "unknown",\n    transport: str = "streamable_http",\n    {sig}\n) ->',
        content,
    )

    # Now for the redefined ones in server.py and tools.py
    # They usually take only _envelope or (payload, _envelope).
    # We want to replace their argument list to include all.

    # regex to find def arif_XXX( ... ) -> dict:

    # 1. _arif_schema_echo
    content = re.sub(
        r"def _arif_schema_echo\(\n    payload: Any = None,\n    _envelope: dict\[str, Any\] \| None = None,\n\)\s*->",
        f"def _arif_schema_echo(\n    {sig}\n) ->",
        content,
    )

    # 2. _arif_version_echo
    content = re.sub(
        r"def _arif_version_echo\(\n    _envelope: dict\[str, Any\] \| None = None,\n\)\s*->",
        f"def _arif_version_echo(\n    {sig}\n) ->",
        content,
    )

    # 3. _arif_transport_echo
    content = re.sub(
        r"def _arif_transport_echo\(\n    _envelope: dict\[str, Any\] \| None = None,\n\)\s*->",
        f"def _arif_transport_echo(\n    {sig}\n) ->",
        content,
    )

    # 4. _arif_initialize_probe
    content = re.sub(
        r"def _arif_initialize_probe\(\n    protocol_version: str \| None = None,\n    client_capabilities: dict\[str, Any\] \| None = None,\n    _envelope: dict\[str, Any\] \| None = None,\n\)\s*->",
        f"def _arif_initialize_probe(\n    protocol_version: str | None = None,\n    {sig}\n) ->",
        content,
    )

    # 5. redefined arif_schema_echo in server.py
    content = re.sub(
        r"def arif_schema_echo\(  # noqa: F811\n    payload: Any = None,\n    _envelope: dict\[str, Any\] \| None = None,\n\)\s*->",
        f"def arif_schema_echo(  # noqa: F811\n    {sig}\n) ->",
        content,
    )

    # 6. redefined arif_version_echo in server.py
    content = re.sub(
        r"def arif_version_echo\(  # noqa: F811\n    _envelope: dict\[str, Any\] \| None = None,\n\)\s*->",
        f"def arif_version_echo(  # noqa: F811\n    {sig}\n) ->",
        content,
    )

    # 7. redefined arif_transport_echo in server.py
    content = re.sub(
        r"def arif_transport_echo\(  # noqa: F811\n    _envelope: dict\[str, Any\] \| None = None,\n\)\s*->",
        f"def arif_transport_echo(  # noqa: F811\n    {sig}\n) ->",
        content,
    )

    # 8. redefined arif_initialize_probe in server.py
    content = re.sub(
        r"def arif_initialize_probe\(  # noqa: F811\n    protocol_version: str \| None = None,\n    client_capabilities: dict\[str, Any\] \| None = None,\n    _envelope: dict\[str, Any\] \| None = None,\n\)\s*->",
        f"def arif_initialize_probe(  # noqa: F811\n    protocol_version: str | None = None,\n    {sig}\n) ->",
        content,
    )

    # Call replacements in _arif_schema_echo(payload=payload, _envelope=_envelope)
    # -> _arif_schema_echo(payload=payload, _envelope=_envelope, client_capabilities=client_capabilities)
    content = content.replace(
        "_arif_schema_echo(payload=payload, _envelope=_envelope)",
        "_arif_schema_echo(payload=payload, _envelope=_envelope, client_capabilities=client_capabilities)",
    )

    # _arif_version_echo(_envelope=_envelope)
    content = content.replace(
        "_arif_version_echo(_envelope=_envelope)",
        "_arif_version_echo(payload=payload, _envelope=_envelope, client_capabilities=client_capabilities)",
    )

    # _arif_transport_echo(_envelope=_envelope)
    content = content.replace(
        "_arif_transport_echo(_envelope=_envelope)",
        "_arif_transport_echo(payload=payload, _envelope=_envelope, client_capabilities=client_capabilities)",
    )

    # _arif_initialize_probe(protocol_version=protocol_version, client_capabilities=client_capabilities, _envelope=_envelope)
    content = content.replace(
        "_arif_initialize_probe(\n            protocol_version=protocol_version,\n            client_capabilities=client_capabilities,\n            _envelope=_envelope,\n        )",
        "_arif_initialize_probe(\n            protocol_version=protocol_version,\n            client_capabilities=client_capabilities,\n            _envelope=_envelope,\n            payload=payload,\n        )",
    )

    with open(filepath, "w") as f:
        f.write(content)


patch_file("/root/arifOS/arifosmcp/server.py")
patch_file("/root/arifOS/arifosmcp/runtime/tools.py")
