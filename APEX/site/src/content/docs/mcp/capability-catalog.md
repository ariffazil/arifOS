# arifOS MCP Capability Catalog

This catalog lists all MCP capabilities exposed by the arifOS server. All tools are model-agnostic and JSON-Schema-typed.

## Tools

### 000_init
| Property | Value |
| --- | --- |
| Name | 000_init |
| Description | Initialize a new governance session |
| Schema | [000_init.schema.json](schemas/000_init.schema.json) |
| Auth Scope | session:init |
| Safety Constraints | None |
| Version | 1.0 |
| Specification | [MCP 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25) |

### 222_reason
| Property | Value |
| --- | --- |
| Name | 222_reason |
| Description | Cognitive processing and truth assessment |
| Schema | [222_reason.schema.json](schemas/222_reason.schema.json) |
| Auth Scope | cognition:reason |
| Safety Constraints | None |
| Version | 1.0 |
| Specification | [MCP 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25) |

### 555_validate
| Property | Value |
| --- | --- |
| Name | 555_validate |
| Description | Empathy assessment and stakeholder impact analysis |
| Schema | [555_validate.schema.json](schemas/555_validate.schema.json) |
| Auth Scope | empathy:validate |
| Safety Constraints | None |
| Version | 1.0 |
| Specification | [MCP 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25) |

### 888_audit
| Property | Value |
| --- | --- |
| Name | 888_audit |
| Description | Final judgment system that issues governance verdicts |
| Schema | [888_audit.schema.json](schemas/888_audit.schema.json) |
| Auth Scope | governance:audit |
| Safety Constraints | None |
| Version | 1.0 |
| Specification | [MCP 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25) |

### 999_seal
| Property | Value |
| --- | --- |
| Name | 999_seal |
| Description | Seal a session with cryptographic integrity |
| Schema | [999_seal.schema.json](schemas/999_seal.schema.json) |
| Auth Scope | vault:seal |
| Safety Constraints | None |
| Version | 1.0 |
| Specification | [MCP 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25) |

## Resources

### VAULT999
| Property | Value |
| --- | --- |
| URI | vault://arifos/sealed_events |
| MIME Type | application/json |
| Access | Read/Write |
| Version | 1.0 |
| Description | Immutable ledger of sealed decisions |
| Specification | [MCP 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25) |

## Prompts

### trinity_analysis
| Property | Value |
| --- | --- |
| Name | trinity_analysis |
| Description | Comprehensive analysis using ΔΩΨ framework |
| Parameters | query, context |
| Safety Constraints | None |
| Version | 1.0 |
| Specification | [MCP 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25) |

## Governance

### Invariants
- All tools are model-agnostic
- All I/O uses JSON Schema
- All side-effects are auditable
- All actions are reversible
- Human sovereignty is preserved

### Versioning
- Semantic versioning (MAJOR.MINOR.PATCH)
- MAJOR for breaking changes
- MINOR for backward-compatible additions
- PATCH for backward-compatible fixes

### Change Process
1. Propose change in GitHub issue
2. Discuss with stakeholders
3. Implement with tests
4. Document changes
5. Update version
6. Notify users

### References
- [MCP 2025-11-25 Specification](https://modelcontextprotocol.io/specification/2025-11-25)
- [MCP Architecture Overview](https://modelcontextprotocol.io/docs/learn/architecture)
- [MCP Tools Specification](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)
- [MCP June 2025 Updates](https://auth0.com/blog/mcp-specs-update-all-about-auth)
- [MCP Apps Extension](https://modelcontextprotocol.io/docs/extensions/apps)