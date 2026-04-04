# arifOS Universal MCP Profile

## 1. Protocol
- Standard method names and error codes (JSON-RPC 2.0).
- Consistent notification patterns for progress, cancellation, and state changes.
- Long-lived sessions with stateful context.

## 2. Capabilities
- Precise semantics and lifecycle for all MCP capabilities:
  - Tools, Resources, Prompts, Sampling, Roots, Elicitation.
  - Defined state transitions and error conditions for each capability type.

## 3. Schema
- JSON Schema for all interfaces
- Versioned schemas
- Backward compatibility
- Schema validation

## 4. Discovery
- tools/list and resources/list endpoints
- Change notifications
- Capability negotiation
- Dynamic composition

## 5. Non-functional
- Authentication and authorization
- Logging and monitoring
- Progress and cancellation
- Error reporting

## 6. UI Binding (Optional)
- UI resource URIs
- CSP implementation
- UI-tool linking
- Renderer support