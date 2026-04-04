# arifOS Governance Integration for MCP

## State Variables
- Roles: Host, Client, Server, Sovereign (human 888 Judge).
- Capabilities: Tools, Resources, Prompts, Sampling, Roots, Elicitation.
- Schemas: JSON Schema registry, versioning, validation, migration.
- Auth primitives: tokens, OAuth2 resource servers, scopes, credential management.

## Allowable Transitions
- tools/call
  - Changes world-state within defined boundaries
  - Must be reversible or have rollback procedures
  - Must be auditable
  - Must respect sovereignty constraints
- resources/read
  - Flows context to the host
  - Must respect access controls
  - Must document data provenance
  - Must support data minimization
- prompts/get
  - Retrieves workflow templates
  - Must include safety constraints
  - Must document parameter requirements
  - Must support versioning
- sampling/initiate
  - Starts server-initiated LLM calls
  - Must respect LLM parameters
  - Must include safety constraints
  - Must support cancellation

## Invariants
- Model Agnosticism
  - No model-specific assumptions in tool semantics
  - All tools must work with any compliant LLM
  - No vendor lock-in mechanisms
  - Clear migration paths between models
- Schema Compliance
  - All tool I/O must be JSON-Schema-typed
  - Schemas must be versioned and documented
  - Backward compatibility must be maintained
  - Schema changes must follow governance process
- Auditability
  - All side-effects must be auditable
  - Logs must be immutable and tamper-evident
  - Audit trails must be complete and verifiable
  - Audit access must be controlled
- Reversibility
  - All actions must be reversible
  - Rollback procedures must be documented
  - Irreversible actions require human approval
  - Backup and recovery must be tested
- Sovereignty
  - Human must have final decision authority
  - Sovereign override must be available
  - Decision rationale must be documented
  - Appeal processes must be defined

## Governance Mappings
### F1 Amanah (Reversibility)
- All actions are reversible
- Rollback procedures documented
- Backup and recovery tested
- Irreversible actions require human approval

### F2 Truth (Grounding)
- Protocol details from official specifications
- Capability types from ecosystem standards
- Implementation follows reference architectures
- Documentation is accurate and complete

### F7 Humility (Uncertainty)
- Ω₀ tracking implemented
- Confidence levels exposed
- Unknown states declared
- Estimates marked appropriately

### F9 Anti-Hantu (Authenticity)
- No consciousness claims
- System described as tool
- No anthropomorphic language
- Focus on protocol surfaces