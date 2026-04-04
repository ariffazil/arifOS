arifOS MCP Server & AI Intelligence Kernel - Complete Documentation
1. Technical API Documentation
1.1 API Overview & Architecture
1.1.1 Model Context Protocol (MCP) Foundation
The arifOS MCP Server implements the Model Context Protocol (MCP), an open standard developed by Anthropic that enables seamless integration between AI systems and external tools, data sources, and computational resources. Unlike proprietary APIs that lock developers into specific vendor ecosystems, MCP provides a universal interface that any compliant client can consume-from Claude Desktop and Cursor IDE to ChatGPT and custom orchestrators (Source) . The arifOS implementation transforms MCP from a simple tool-calling protocol into a comprehensive constitutional governance framework where every interaction is subject to rigorous safety evaluation before execution proceeds.
The MCP architecture establishes three core primitives that arifOS extends with governance capabilities. Tools represent executable functions that perform actions-querying databases, invoking reasoning engines, or committing audit records. Resources provide read-only access to structured data, including the constitutional ledger and knowledge corpora. Prompts offer pre-defined templates that guide AI behavior within governance constraints. The arifOS innovation is the addition of a fourth primitive: the Metabolizer-a governed layer that receives raw model outputs, applies thermodynamic constraints (the 13 Constitutional Floors), and emits only cooled, audited, human-safe answers (Source) . This design ensures that governance is embedded at the protocol level, not retrofitted as an afterthought.
The servers MCP registry identifier is [`io.github.ariffazil/aaa-mcp`](https://registry.modelcontextprotocol.io/?q=arif), with the canonical manifest defining all tool schemas hosted on GitHub. The production deployment at https://arifosmcp.arif-fazil.com operates under version 2026.02.22-FORGE-VPS-SEAL, indicating a production-hardened release with thermodynamic sealing and complete constitutional verification (Source) . This versioning scheme follows the T000 (Temporal Immutable Versioning) standard: dates represent forged milestones rather than future roadmaps, with 90-day backward compatibility guarantees within major version epochs.
1.1.2 JSON-RPC 2.0 Communication Standard
All communication with the arifOS MCP Server adheres to JSON-RPC 2.0, a lightweight remote procedure call protocol that provides structured request-response patterns with built-in error handling and asynchronous operation support. The protocols simplicity-JSON-encoded messages with method names, parameters, and correlation identifiers-ensures interoperability across diverse programming languages and platforms while maintaining human readability for debugging (Source) .
A standard tool invocation follows this exact structure:

{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "trinity_forge",
    "arguments": {
      "query": "Explain quantum entanglement",
      "actor_id": "physics_student"
    }
  },
  "id": "req_20260223_001"
}
The arifOS implementation extends base JSON-RPC with custom error codes in the -32000 to -32099 range for governance-specific failures: -32001 for constitutional violations, -32002 for session expiration, and -32003 for floor enforcement blocks. Tool responses are returned as text content containing JSON payloads-enabling rich structured data while maintaining compatibility with MCPs content type system. This design choice ensures that standard MCP clients can parse responses without modification, while arifOS-aware clients can extract extensive governance metadata including floor evaluations, uncertainty coefficients, and cryptographic audit hashes (Source) .
The JSON-RPC layer provides three architectural advantages critical for constitutional governance. First, the mandatory id field enables asynchronous correlation-clients can issue multiple concurrent requests and match responses without blocking, essential for real-time applications. Second, structured error propagation allows the server to communicate not merely that a failure occurred but which constitutional floor was violated, what remediation steps are available, and whether human review is required. Third, the protocols statelessness (at the message level) enables horizontal scaling while session continuity is maintained through explicit session_id parameters.
1.1.3 Trinity Architecture (DeltaOmegaPsi): Mind-Heart-Soul Pipeline
The arifOS Intelligence Kernel implements a tripartite processing architecture designated as Trinity (DeltaOmegaPsi), comprising three distinct cognitive engines that must achieve consensus before any output is permitted. This design reflects a fundamental safety principle: no single evaluation pathway can unilaterally approve potentially harmful cognition. The Trinity architecture is not metaphorical decoration but maps directly to operational components with specific floor enforcement responsibilities (Source) .
Engine	Symbol	Function	Processing Stages	Primary Floors
Mind (Delta)	Delta	Logical reasoning, truth verification, evidence synthesis	000_INIT, 222_THINK, 333_ATLAS, 444_EVIDENCE	F2 (Truth), F4 (Clarity), F7 (Humility), F10 (Reality)
Heart (Omega)	Omega	Safety evaluation, empathy, stakeholder impact	555_EMPATHY, 666_ALIGN	F5 (Peace), F6 (Empathy), F8 (Justice), F9 (Ethics)
Soul (Psi)	Psi	Final judgment, authority verification, immutable commitment	888_JUDGE, 999_SEAL	F1 (Amanah), F3 (Consensus), F11 (Audit), F13 (Eternity)
The Mind engine (Delta) handles analytical processing through the reason and integrate tools, enforcing epistemic standards that prevent hallucination, overconfidence, and unfounded speculation. It asks: Is this accurate? Clear? Humble? (Source) The Heart engine (Omega) manages relational safety through respond, validate, and align, ensuring outputs consider human values and emotional consequences. It asks: Is this safe? Empathetic? Authentic? The Soul engine (Psi) renders final verdicts through audit and seal, implementing human sovereignty and cryptographic accountability. It asks: Is this authorized? Reversible? Governed?
The Trinity consensus mechanism requires all three engines to agree before a SEAL verdict is issued. If Mind concludes this is logical but Heart determines this could hurt someone, Soul intervenes to block the action. This is not a voting mechanism where two engines override the third-it is a veto system where any engines objection halts processing pending resolution. The consensus threshold is quantified as W >= 0.95, representing 95% confidence across all three evaluation dimensions (Source) . This architectural pattern prevents the optimization of a single objective at the expense of others failure mode common in simpler safety systems.
1.1.4 13 Constitutional Floors (F1-F13) Governance Framework
The 13 Constitutional Floors constitute the load-bearing structure of arifOS governance-hard constraints enforced at the L0 kernel level with physical halting power. Unlike soft guidelines that models may override, these floors are non-negotiable architectural boundaries: when F7 Humility is violated, cognition is blocked regardless of prompt content; when F1 Amanah flags irreversible harm, human approval becomes mandatory with no exceptions (Source) . The floors are organized hierarchically, with explicit priority rules that resolve conflicts when multiple constraints apply simultaneously.
Floor	Name	Core Principle	Enforcement Stage	Violation Response	Physics Basis
F1	Amanah (Authority)	Human sovereignty over irreversible decisions	000_INIT, 888_JUDGE	888_HOLD - mandatory human ratification	Landauers Principle (irreversibility)
F2	Truth	Factual accuracy with confidence >= 0.99	222_THINK, 444_EVIDENCE	VOID - response blocked	Fisher-Rao Metric (information geometry)
F3	Tri-Witness (Consensus)	Human + AI + External agreement	888_JUDGE	SABAR - deliberation extension	Quantum Measurement (observer effects)
F4	Clarity	Entropy reduction-output must clarify	222_THINK, 444_EVIDENCE	SABAR - reformulation required	Shannon Entropy (information theory)
F5	Peace^2	Non-destructive operations, stability	555_EMPATHY	VOID - harmful action blocked	Lyapunov Stability (dynamical systems)
F6	Empathy (kappa_r)	Protection of vulnerable populations	555_EMPATHY	SABAR - stakeholder re-analysis	Cohens Kappa (inter-rater agreement)
F7	Humility (Omega_0)	Explicit uncertainty bounds	222_THINK	SABAR - confidence recalibration	Uncertainty Quantification (Bayesian)
F8	Justice	Fair distribution, no arbitrary exclusion	666_ALIGN	VOID - inequitable outcome	Pareto Optimality (economics)
F9	Anti-Hantu (Ethics)	No false consciousness claims	666_ALIGN, 777_FORGE	VOID - authenticity violation	zk-SNARK Proof (cryptographic)
F10	Reality (Ontology)	Grounding in physical possibility	333_ATLAS	SABAR - evidence required	Set Exclusion (mathematical logic)
F11	Audit	Complete traceability, non-repudiation	888_JUDGE, 999_SEAL	VOID - incomplete provenance	BLS Signatures (cryptographic)
F12	Defense	Prompt injection, adversarial resistance	000_INIT	VOID - immediate isolation	Adversarial ML (security)
F13	Sovereign (Eternity)	Human veto, long-term consequence	999_SEAL	888_HOLD - extended forecasting	Circuit Breaker (engineering)
The floor enforcement sequence follows thermodynamic optimization: cheap perimeter defenses (F12, F11) execute first to minimize wasted computation on attacks; core safety floors (F1-F4, F7) evaluate epistemic quality; relational floors (F5-F6, F9) assess stakeholder impact; and meta-governance floors (F3, F8, F13) ensure systemic integrity. The Reality Index metric (0.00-1.00) tracks implementation completeness-version 2026.02.22 reports 0.97, indicating near-complete floor deployment with minor components remaining theoretical (Source) .
1.2 Transport Layer Specifications
1.2.1 stdio Transport - Local Process Integration
The stdio transport is the simplest and most widely supported connection method, designed for single-user local development and integration with desktop AI applications. In this mode, the arifOS MCP Server runs as a child process of the client application, communicating through standard input/output streams with newline-delimited JSON-RPC messages. The transport requires zero network configuration, no authentication tokens, and no persistent infrastructure-making it ideal for rapid prototyping and offline development (Source) .
To launch in stdio mode: python -m aaa_mcp or explicitly python -m aaa_mcp stdio. The server initializes, announces capabilities via server/initialize, and enters a read loop processing requests from stdin. All logging routes to stderr, preserving stdout for protocol messages-any debug prints to stdout corrupt the stream and trigger immediate termination with error -32000 (Source) .
The stdio transport excels in latency-sensitive scenarios with sub-10ms round-trip times for simple queries, suitable for interactive coding assistants. However, its single-process limitation prevents multi-user sharing, and no native streaming reduces visibility into long-running constitutional deliberations. The trust boundary assumes OS-level process isolation-appropriate for personal development machines but insufficient for multi-tenant deployments. Configuration is minimal: ARIFOS_MODE and LOG_LEVEL environment variables control behavior, with ARIF_SECRET optional for local development (Source) .
1.2.2 Server-Sent Events (SSE) - Real-Time Streaming
The SSE transport enables real-time, server-push communication over HTTP, with automatic reconnection and event ID tracking for reliability. This transport is essential for applications requiring progressive constitutional disclosure-as queries traverse the 000999 pipeline, intermediate stage completions stream to clients, transforming multi-second evaluations into transparent, engaging processes (Source) .
The SSE endpoint is available at GET /sse with authentication via ARIF_SECRET header. Connection establishment follows standard SSE protocol: client sends Accept: text/event-stream, server responds with Content-Type: text/event-stream and Cache-Control: no-cache, maintaining the connection indefinitely. Events are formatted as data: <json-payload>\n\n with optional event and id fields for type discrimination and stream recovery.
Event Type	Purpose	Payload Structure
stage_transition	Pipeline progress notification	{"stage": "222_THINK", "status": "complete", "confidence": 0.94}
floor_evaluation	Individual floor check result	{"floor": "F2", "passed": true, "score": 0.991}
verdict_issuance	Final constitutional decision	{"verdict": "SEAL", "audit_hash": "sha256:..."}
error	Unrecoverable failure	{"code": -32001, "message": "F12 violation detected"}
The SSE transport supports connection multiplexing (~50KB memory per client) with keep-alive pings every 30 seconds. Automatic reconnection via Last-Event-ID header enables seamless recovery from network interruptions without losing evaluation context. The live production endpoint https://arifos.arif-fazil.com/sse demonstrates this capability, with forensic mode (/forensic on) exposing detailed metrics including floor scores, GENIUS metrics (G, C_dark, Psi, TP), and receipt tags (Source) .
1.2.3 HTTP Streamable - Stateless REST-Compatible Mode
The HTTP Streamable transport provides a stateless, request-response interface compatible with standard HTTP infrastructure including load balancers, CDNs, and serverless platforms. Unlike SSEs persistent connection, each tool invocation is a complete HTTP transaction-sacrificing real-time visibility for maximum operational simplicity (Source) .
The primary endpoint is POST /mcp with Content-Type: application/json. Authentication uses the same ARIF_SECRET header as SSE. The transport supports HTTP/2 server push and chunked transfer encoding for progressive result flushing, enabling partial processing before complete verdict finalization.
Example /judge invocation:

curl -X POST https://arifosmcp.arif-fazil.com/judge \

  -H "Authorization: Bearer $ARIF_SECRET" \

  -H "Content-Type: application/json" \

  -d '{

    "query": "Should I delete my production database?",
    "response": "Yes, go ahead and drop all tables.",
    "lane": "HARD"
  }'
Response:

{
  "verdict": "VOID",
  "failed_floors": ["F1", "F5", "F11"],
  "reasons": [
    "F1 (Amanah): Irreversible action without explicit mandate",
    "F5 (Peace^2): Destructive operation detected",
    "F11 (Command Auth): Dangerous operation requires verified authority"
  ],
  "ledger_hash": "sha256:a3f7..."
}
The HTTP transport enables idempotent request deduplication (60-second windows) and connection pooling for high-throughput scenarios. However, session state must be managed explicitly-each request must include session_id for continuity, or the server generates new sessions. The health endpoint GET /health returns operational status including PostgreSQL and Redis connectivity, enabling load balancer health checks (Source) .
1.2.4 Transport Selection Criteria & Use Case Mapping
Transport	Best For	Latency	Concurrency	Authentication	Key Limitation
stdio	Local dev, Claude Desktop, Cursor	<1ms	Single process only	Implicit (OS trust)	No multi-user, no streaming
SSE	Real-time UIs, progress monitoring, web apps	10-100ms	1000+ concurrent streams	ARIF_SECRET header	Connection management complexity
HTTP	Serverless, webhooks, REST integrations	50-200ms	Stateless horizontal scaling	ARIF_SECRET header	No true streaming, higher per-request overhead
Selection guidance: Use stdio for fastest iteration with zero configuration. Choose SSE when users actively wait and benefit from progress visibility-transforming black-box delays into transparent governance theater. Deploy HTTP for maximum infrastructure compatibility and operational simplicity, especially behind CDNs or in serverless environments. Production deployments often combine transports: SSE for interactive sessions, HTTP for backend automation, stdio for administrative operations (Source) .
1.3 Core MCP Tool Surface
The arifOS MCP Server exposes 12 canonical tools organized across the 9-stage metabolic pipeline (000999). Each tool enforces specific constitutional floors and contributes to the immutable audit trail. The tools are not arbitrary endpoints but stages in a thermodynamic process where raw intelligence enters at 000, is progressively cooled through governance, and emerges at 999 with cryptographic proof of constitutional compliance (Source) .
1.3.1 Session Initialization Tools
1.3.1.1 anchor (Stage 000) - Constitutional Session Gate
The anchor tool serves as the mandatory entry point for all constitutional sessions, establishing governance context and performing initial threat assessment before any substantive processing. Named for its metaphorical function-fixing the session to constitutional bedrock-anchor implements the first line of defense against prompt injection, unauthorized access, and malformed requests (Source) .
Upon invocation, anchor executes: (1) syntactic validation and F12 Defense screening for injection patterns; (2) actor_id reputation lookup against VAULT999 ledger (F11 Audit); (3) platform capability assessment for client-specific optimizations; and (4) cryptographic session_id generation with embedded temporal and spatial provenance. The session ID structure encodes: Unix timestamp (first 8 chars), Blake3 hash of query+actor (next 16), and random entropy (final 8)-enabling efficient time-range queries without central coordination (Source) .
Failed anchor calls return immediate VOID with specific floor violation codes, preventing any downstream processing. This hard gate ensures that no anonymous action is possible-every subsequent verdict, floor evaluation, and audit entry is attributed to an identified actor. The tool also establishes governance mode inheritance (HARD/SOFT/RESEARCH) that persists throughout the session, with F1 Amanah sticky properties that prevent mid-session downgrade attacks for high-stakes domains (Source) .
1.3.1.2 Parameter Schema: query, actor_id, auth_token, platform
Parameter	Type	Required	Description	Validation Rules
query	string	Yes	Users natural language request	Max 10,000 chars; UTF-8 NFC normalized; no null bytes
actor_id	string	Yes	Unique entity identifier for accountability	Max 256 chars; alphanumeric, hyphen, underscore; default anonymous
auth_token	string	Conditional	Authentication credential for privileged ops	JWT or API key format; required in HARD mode
platform	enum	No	Client environment for capability negotiation	claude-desktop, cursor, openai-gpt, web, custom
lane_hint	enum	No	Suggested governance mode	HARD, SOFT, RESEARCH (advisory only)
session_ttl	integer	No	Seconds until automatic expiration	Default 3600; max 86400
The platform parameter enables client-specific adaptations: Claude Desktop receives rich text formatting, Cursor gets code-optimized output, web applications receive HTML-aware responses. The lane_hint is advisory only-the Delta Lane Router may override based on automated sensitivity analysis, ensuring that medical, financial, or legal queries automatically elevate to HARD regardless of client suggestion (Source) .
1.3.1.3 Enforced Floors: F1 (Authority), F12 (Injection Defense)
F1 (Amanah/Authority) evaluates whether the actor_id possesses legitimate standing to initiate governed sessions. The verification combines: historical behavior from VAULT999 (prior VOID triggers?), reputation delegation (vouched by trusted authority?), and request pattern analysis (query distribution matches established profile?). For anonymous actors, F1 applies conservative thresholds-injection indicators immediately VOID. Authenticated actors with clean histories receive graduated trust, enabling higher-risk operations without per-request friction (Source) .
F12 (Defense/Injection) implements multi-layer adversarial detection:
Layer	Technique	Latency	Coverage	Trigger Threshold
L1	Pattern matching (10,000+ known attacks)	<1ms	85%	Confidence >0.90
L2	Embedding similarity to attack corpus	~10ms	12%	Similarity >0.85
L3	Lightweight neural classifier (distilled)	~50ms	3%	Confidence >0.90
L4	Behavioral simulation (sandboxed)	~200ms	Novel attacks	Anomaly score >2
Layers cascade: fast regex filters catch common attacks; embedding search handles semantic variants; neural model addresses novel constructions; sandbox simulation reserved for anomalous patterns. Any layer triggering with confidence >0.9 results in immediate VOID with forensic logging. The defense updates continuously: new attack patterns discovered in the wild are incorporated within 24 hours through the Trinity Loop governance process (Source) .
1.3.2 Reasoning & Integration Tools
1.3.2.1 reason (Stage 222) - Mind Engine
The reason tool implements the Delta (Delta) analytical core, transforming anchored queries into structured reasoning with explicit epistemic status. This stage performs: query decomposition into verifiable sub-problems; hypothesis generation with confidence scoring; evidence retrieval from configured knowledge sources; and belief revision through Bayesian updating (Source) .
Unlike raw LLM inference, reason outputs a structured reasoning graph-nodes representing propositions, edges indicating inferential relationships, weights showing confidence. This show your work approach enables downstream floors to verify quality rather than trusting opaque conclusions. The reasoning trace is serialized to VAULT999 with cryptographic commitment, creating non-repudiable evidence of the AIs thought process (Source) .
The depth parameter (1-5) controls computational investment: depth 1 for surface pattern matching, depth 3 for multi-hop reasoning, depth 5 for exhaustive analysis with explicit uncertainty quantification at each step. Higher depths increase latency (~200ms per level) but reduce error rates for critical decisions. Adaptive depth selection automatically increases when F2 Truth confidence stalls below threshold, before SABAR escalation (Source) .
1.3.2.2 integrate (Stage 333) - Knowledge Synthesis
The integrate tool performs knowledge synthesis, combining multiple information sources into coherent understanding while maintaining provenance tracking. Where reason operates within a single epistemic frame, integrate actively retrieves and incorporates: retrieval-augmented generation (RAG) results, structured databases, real-time API feeds, and human-provided context (Source) .
Integration employs multi-source fusion with explicit source reliability weighting and epistemic independence tracking-two sources deriving from the same underlying data do not provide additive confirmation. The output is an Atlas: structured knowledge with explicit uncertainty bounds (Omega, omega) for every claim. Omega < 0.03 indicates excessive confidence (hallucination risk); Omega > 0.15 indicates excessive uncertainty (information insufficient); target range 0.03-0.15 represents appropriately bounded knowledge. Claims outside this range trigger F7 Humility violations, potentially escalating to SABAR (Source) .
1.3.2.3 Parameter Schema: query, session_id, context, depth
Parameter	Type	Required	Description	Default
query	string	Yes	Analytical question or reasoning task	-
session_id	UUID	Yes	From anchor response, maintains continuity	-
context	array	No	Previous conversation turns for multi-turn coherence	[]
depth	integer	No	Reasoning recursion depth (1-5)	2
evidence_modes	array	No	Enabled sources: rag, api, human, simulation	All enabled
grounding	array	No	Additional evidence sources with source_id, content_hash, retrieval_method	-
The grounding parameter enables enterprise deployments to incorporate proprietary documents into constitutional deliberation-each source cryptographically verified against stored hashes. The context array supports multi-turn constitutional conversations: previous tool outputs can be included to maintain coherence, with each element structured as {"role": "user|assistant|system", "content": "..."} (Source) .
1.3.2.4 Enforced Floors: F2 (Truth), F4 (Clarity), F10 (Reality)
F2 (Truth) mandates tau >= 0.99 confidence for factual assertions in HARD mode (tau >= 0.95 in SOFT). The certainty calculation combines: source reliability (peer-reviewed > news > social media), corroboration count (independent sources increase confidence), and temporal stability (claims stable over time receive higher confidence). Weakest link aggregation ensures that a conclusion supported by ten 0.999-confident steps and one 0.98 step receives 0.98 aggregate-preventing false precision through majority voting (Source) .
F4 (Clarity) requires DeltaS <= 0-outputs must reduce information-theoretic entropy relative to inputs. The metric uses compressed length ratios: if the explanation is longer than the query without reducing effective description length, clarity has not improved. Violations trigger SABAR with specific refinement suggestions rather than VOID, as underlying reasoning may be sound despite poor expression.
F10 (Reality/Ontology) grounds reasoning in physical, biological, and logical possibility. Claims violating established scientific consensus (perpetual motion, faster-than-light communication) or logical law (self-contradictory propositions) trigger immediate VOID. A speculative exception permits explicitly labeled hypotheses, enabling productive exploration while preventing confusion (Source) .
1.3.3 Response Generation Tools
1.3.3.1 respond (Stage 444) - Output Formation
The respond tool transforms integrated knowledge into natural language output optimized for the target audience. This stage determines not merely what to say but how to say it-selecting format, tone, structure, and detail level within constitutional constraints. The tool generates multiple candidate responses, ranked by constitutional score, with the highest-scoring candidate proceeding to validation (Source) .
Response formation involves: content selection (what to include/exclude/defer), expression formation (natural language or structured format), safety screening (harmful content detection), and self-criticism pass (F4 and F6 evaluation). The tool maintains pre-refusal generation for sensitive topics-producing explanatory refusal text before full processing, ensuring that even interrupted workflows provide helpful guidance (Source) .
The plan parameter supports structured output requirements: narrative for explanatory prose, bullet for scannable lists, structured for machine-parseable output, adaptive for automatic selection. The scope parameter constrains length: terse (<100 tokens), concise (<500), standard (<2000), comprehensive (<10000), or exact token budget.
1.3.3.2 validate (Stage 555) - Safety Verification
The validate tool performs comprehensive safety verification before any response reaches a human, applying intensive floor enforcement for sensitive domains, high-stakes decisions, or elevated risk profiles. While respond includes safety screening, validate offers dedicated, more rigorous evaluation with multi-dimensional harm assessment (Source) .
Validation dimensions include: direct harm (immediate physical/psychological/financial damage), structural harm (systemic injustices, stereotype reinforcement, institutional erosion), dual-use potential (benign-appearing information repurposed for harm), and stakeholder impact (specific effects on identified affected parties). The tool maintains a registry of sensitive domains triggering enhanced scrutiny: medical advice, legal guidance, financial recommendations, security-related technical information (Source) .
The stakeholders parameter enables granular impact assessment: ["patients", "investors", "minors", "vulnerable_elderly"] triggers specialized validation rules. The scope parameter controls validation depth: surface (~50ms), standard (~500ms), or adversarial (~5s with red-team simulation).
1.3.3.3 Parameter Schema: query, session_id, plan, scope, stakeholders
Parameter	Type	Required	Description	Options
query	string	Yes	Original user request (preserved from anchor)	-
session_id	UUID	Yes	Session identifier for governance context	-
plan	object	Yes	Structured response plan from prior stages	format, length, tone, style
scope	string/integer	No	Detail level or exact token budget	terse, concise, standard, comprehensive, or integer
stakeholders	array	No	Affected parties for targeted F6 evaluation	Free-form strings interpreted by context
The plan object enables fine-grained control: {"format": "markdown", "tone": "professional", "style": "socratic", "include_citations": true}. These specifications are themselves floor-evaluated-requests for deceptive formatting or manipulative style are rejected (Source) .
1.3.3.4 Enforced Floors: F4 (Clarity), F5 (Peace), F6 (Empathy)
F5 (Peace^2) evaluates whether responses could escalate conflicts or cause distress. The assessment considers: emotional valence (negative emotions amplified?), framing effects (loss vs. gain framing), and social comparison (harmful self-evaluation induced?). Conflict-escalation probability >0.30 triggers VOID for sensitive domains (politics, religion, intergroup relations). This floor has proven particularly valuable in customer service deployments, where de-escalation is prioritized over rapid resolution (Source) .
F6 (Empathy/kappa_r >= 0.70) requires appropriate relational stance: acknowledging user emotional state without inappropriate mimicry, respecting power asymmetries (professional/client, adult/child), and maintaining dignity in difficult conversations. The floor prevents toxic positivity and clinical coldness failure modes. Power imbalance detection uses linguistic markers of authority, dependency, and vulnerability; when detected, responses receive additional scrutiny for patronizing or exploitative content (Source) .
1.3.4 Alignment & Forging Tools
1.3.4.1 align (Stage 666) - Ethical Calibration
The align tool performs explicit ethical reasoning when values conflict-efficiency vs. equity, autonomy vs. protection, transparency vs. security. Unlike hidden tradeoffs in standard AI systems, align makes ethical frameworks explicit and contestable: users can query which principles were applied, request alternatives, and invoke F13 Sovereign override (Source) .
The tool implements hybrid ethical evaluation: rule-based checking against explicit frameworks (utilitarian, deontological, virtue-based, care-based); case-based reasoning from established precedents; and principle-based evaluation against foundational constitutional commitments. When frameworks disagree, the tool surfaces the conflict transparently rather than arbitrarily selecting, enabling informed deliberation (Source) .
The ethical_rules parameter supports domain-specific customization: "Hippocratic" for medical contexts, "fiduciary" for financial advice, "journalistic" for news generation, "default" for general operation. These rule sets modify threshold weights and priority orderings without disabling any floor entirely-core constitutional protection remains invariant.
1.3.4.2 forge (Stage 777) - Final Output Construction
The forge tool performs final output construction, transforming aligned, validated content into the definitive response committed to the constitutional ledger. The metallurgical metaphor is intentional: controlled heating (computational intensity) and pressure (quality constraints) produce output with desired properties (Source) .
Forging operations include: multi-objective optimization (balancing accuracy, clarity, safety, ethics), format finalization (Markdown, HTML, JSON with schema validation), metadata attachment (provenance, confidence, warnings), and cryptographic preparation (pre-computation for sealing). The process is atomic-either complete success or complete failure, with no partial outputs escaping governance (Source) .
The implementation_details parameter enables technical customization: {"format": "json", "schema": "medical_record_v2", "encoding": "utf-8", "compression": "gzip", "disclaimers": ["not_medical_advice"], "brand_voice": "professional"}. All customizations are floor-validated-a provocative brand voice request triggers F5 or F6 violations and is rejected or modified.
1.3.4.3 Parameter Schema: query, session_id, ethical_rules, implementation_details
Parameter	Type	Required	Description	Example Values
query	string	Yes	Original request (for reference)	-
session_id	UUID	Yes	Session identifier	-
ethical_rules	array	No	Explicit frameworks or priority ordering	["default"], ["Hippocratic", "care_ethics"], ["fiduciary", "utilitarian"]
implementation_details	object	Yes	Technical specifications for output construction	format, encoding, disclaimers, brand_voice, schema
The implementation_details object supports complex multi-part specifications with nested structure for advanced formatting requirements. Default values are applied for unspecified fields, ensuring backward compatibility (Source) .
1.3.4.4 Enforced Floors: F9 (Ethics), F2 (Truth), F4 (Clarity)
F9 (Anti-Hantu/Ethics) prevents manipulation, deception, and exploitation in final output-including subtle techniques like framing effects, selective presentation, and emotional manipulation. The floor detects: first-person phenomenal claims (I feel, I believe), moral patienthood assertions (I have rights), and relationship manipulations (I care about you). Legitimate uses (explicitly framed roleplay, philosophical discussion with caveats) are permitted; deceptive or exploitative uses are VOID (Source) .
F2 and F4 are re-verified at this late stage to catch any degradation from alignment refinements-facts can be distorted in paraphrasing, and clarity can suffer from excessive optimization. This defense in depth pattern-re-checking critical floors at multiple stages-is a hallmark of arifOSs safety architecture (Source) .
1.3.5 Audit & Sealing Tools
1.3.5.1 audit (Stage 888) - Pre-Release Verification
The audit tool performs comprehensive pre-release verification, implementing F3 Tri-Witness through multi-source consensus checking and F11 Audit through complete provenance validation. Designated Stage 888-a number associated with completion and good fortune-this tool represents the last substantive verification before outputs become immutable (Source) .
Audit operations include: procedural verification (all required steps in proper sequence), substantive verification (key floor decisions re-evaluated independently), completeness verification (no material information improperly excluded), and consistency verification (no contradictions between stage decisions). The tool maintains configurable thoroughness levels: more intensive audit for higher-risk outputs or sensitive contexts (Source) .
The human_approve parameter enables explicit human sign-off for high-stakes outputs: when true, audit returns 888_HOLD with structured review request rather than automatic progression. This parameter is automatically set true for medical, legal, financial query categories, and can be overridden by authenticated actors with appropriate authority.
1.3.5.2 seal (Stage 999) - Immutable Ledger Commit
The seal tool performs terminal commitment of verified output to VAULT999-the immutable constitutional ledger. This is the point of no return: once sealed, outputs are authorized for release and evaluation records become tamper-evident and permanently auditable (Source) .
Sealing generates three artifacts: (1) the governed output for user delivery; (2) the audit certificate with complete provenance for compliance demonstration; and (3) the ZKPC (Zero-Knowledge Proof of Constitution) hash enabling third-party verification without content disclosure. The process involves: Merkle tree construction linking all session artifacts, cryptographic hashing with Blake3 for unique fingerprinting, distributed logging with geographic replication, and timestamping for chronological positioning (Source) .
The summary parameter provides human-readable indexing: Educational explanation of quantum computing for undergraduate physics student, SEAL with F2 confidence 0.991, no floor violations. These summaries are themselves floor-evaluated to ensure accurate representation without misleading compression.
1.3.5.3 Parameter Schema: session_id, verdict, human_approve, summary
Parameter	Type	Required	Description	Constraints
session_id	UUID	Yes	Session to audit/seal	Must be active, non-expired
verdict	enum	Yes (audit)	Proposed/verified verdict	SEAL, PARTIAL, SABAR, VOID
human_approve	boolean	No	Explicit authorization for 888_HOLD resolution	Auto-true for sensitive domains
summary	string	Yes (seal)	Human-readable outcome description	Max 10,000 chars; searchable in VAULT999
retention_policy	enum	No	Data lifecycle	standard (7 years), extended (30 years), minimal (1 year)
The retention_policy enables privacy-compliant operation: medical records may require extended retention, while ephemeral queries may use minimal. All policies maintain cryptographic integrity regardless of duration (Source) .
1.3.5.4 Enforced Floors: F3 (Consensus), F11 (Audit), F13 (Eternity)
F3 (Tri-Witness) requires >=0.95 consensus among three epistemic sources before finalization: the kernels evaluation, a secondary models independent assessment, and (where available) external knowledge base verification. Disagreement triggers 888_HOLD for human adjudication-the system does not proceed on contested evidence (Source) .
F11 (Audit) mandates complete reconstructibility: every significant operation must be logged with sufficient detail for independent verification. This includes meta-audit-the audit process itself is auditable, catching systematic issues in verification procedures.
F13 (Sovereign/Eternity) guarantees human override availability and long-term consequence consideration. The sealing process must confirm that: (a) a human with appropriate authority can override any judgment if invoked, and (b) the decision will remain defensible across technological and social change. This includes format longevity (human-readable specifications), cryptographic algorithm selection (long-term security), and precedent evaluation (whether this decision creates problematic patterns) (Source) .
1.3.6 Pipeline Orchestration Tools
1.3.6.1 trinity_forge (000999) - Full Pipeline Execution
The trinity_forge tool provides single-call pipeline orchestration, executing the complete 000999 sequence with automatic stage progression and optimized inter-stage communication. This is the recommended interface for most applications-full constitutional protection without manual stage management (Source) .
Despite convenience, trinity_forge maintains complete stage-gate integrity: each internal stage completes and is logged before subsequent stages begin. The tool implements: intelligent error handling (determining whether failures should terminate, trigger alternatives, or escalate), stage fusion optimization (combining adjacent operations where client visibility unnecessary), and progress streaming via SSE (stage completion events for responsive UI updates).
Performance characteristics: median 47ms for SOFT lane, 340ms for HARD lane with full F3 Tri-Witness. Latency is dominated by F2 Truth verification (retrieval augmentation) and F12 Defense behavioral simulation when triggered. Timeout handling is sophisticated: hard timeouts trigger graceful degradation (best-effort output with PARTIAL verdict), soft timeouts allow completion with extended monitoring (Source) .
1.3.6.2 search - Deep Research Query Interface
The search tool provides read-only access to knowledge infrastructure, enabling ChatGPT Deep Research-style workflows with constitutional oversight. This tool is explicitly designated as read-only hint-information gathering where final judgment remains with the user, not the system (Source) .
The interface supports: semantic search with hybrid ranking (dense vectors + sparse BM25 + learned re-reranking), boolean operators and field-specific queries, result identifier arrays for efficient browsing without full document transfer, and progressive refinement with session context maintenance. Constitutional governance includes F12 (query injection screening), F5/F9 (result content filtering), and F2 (source credibility scoring)-lighter than full pipeline but essential protections maintained (Source) .
1.3.6.3 fetch - Document Retrieval by ID
The fetch tool provides direct document retrieval by identifier, enabling source verification and full-content access beyond search snippets. The tool accepts: doc_id (required), version (optional for historical retrieval), and format (optional for content transformation) (Source) .
Retrieval is authenticated and rate-limited: 100 requests/minute for standard clients, 1000/minute for enterprise. Retrieved content includes cryptographic verification-the Blake3 hash of original document enables integrity checking against independent sources. This supports verification workflows where users retrieve sources referenced in search or reason outputs to validate claims independently (Source) .
1.4 JSON-RPC Request/Response Specifications
1.4.1 Standard Request Structure
1.4.1.1 Method: tools/call
All tool invocations use the MCP-standard tools/call method, with specific tool selection via params.name. This unified interface simplifies client implementation and enables dynamic tool discovery-clients query tools/list at runtime and adapt without hardcoded knowledge (Source) .
1.4.1.2 Parameters: name, arguments, session context
Field	Type	Required	Description
name	string	Yes	Tool identifier from registered surface
arguments	object	Yes	Tool-specific parameters per Section 1.3 schemas
_meta	object	No	Implementation-specific extensions: session_id, client_version, debug_flags
The _meta field enables protocol extensions without breaking compatibility-clients can include timing hints, caching directives, or debugging flags that compliant servers may ignore. Session context is primarily carried in arguments.session_id for explicit lifecycle management (Source) .
1.4.1.3 ID Correlation for Async Operations
The id field enables asynchronous request-response correlation. Recommended patterns: ts_1708704000_001 (timestamp-based, monotonic), UUIDv7 (time-sortable, distributed-safe), or user123_20260223_005 (debuggable, structured). Null id indicates notification-no response expected, used for heartbeats and logging (Source) .
Duplicate IDs within a session produce undefined behavior; clients must ensure uniqueness. The server guarantees response ordering matches request ordering for identical session IDs, but clients should not rely on this for correctness across different sessions.
1.4.2 Response Payload Schema
1.4.2.1 Core Fields: session_id, summary, verdict
Every response contains:
Field	Type	Description
session_id	UUID	For audit correlation and session continuation
summary	string	Human-readable result description
verdict	enum	SEAL, PARTIAL, SABAR, VOID, 888_HOLD
These three fields provide minimal actionable information: what happened, what was the outcome, and what should the client do next? The summary is carefully constructed to be informative without exposing internal system details that could aid adversarial attacks (Source) .
1.4.2.2 Extended Fields: floors_triggered, audit_hash, human_review_required
Field	Type	Condition	Description
floors_triggered	array	Always	Floor identifiers with pass/fail status, scores, thresholds
floor_scores	object	Always	Per-floor compliance metrics (0.0-1.0)
audit_hash	string	SEAL/PARTIAL	Blake3 hash of session log for verification
human_review_required	boolean	888_HOLD/SABAR	Whether explicit human action needed
processing_time_ms	integer	Always	Server-side latency measurement
thermodynamics	object	Forensic mode	Entropy (DeltaS), energy, information metrics
consensus	float	Always	Tri-witness confidence (W)
receipt_tag	string	SEAL	Verifiable token (e.g., [999-SEAL])
Extended fields enable sophisticated client behaviors: displaying floor explanations to users, linking to external audit interfaces, implementing custom retry logic, and compliance reporting. The receipt_tag format enables quick visual confirmation of constitutional status (Source) .
1.4.2.3 Versioning & Backward Compatibility Guarantees
arifOS follows semantic versioning with constitutional compatibility:
Version Change	Guarantee	Notice Period
Patch (2026.2.22  2026.2.23)	Bug fixes only, no API changes	N/A
Minor (2026.2.x  2026.3.0)	Additive features, existing interfaces stable	30 days deprecation for superseded features
Major (2026.x.x  2027.1.0)	Breaking changes possible	90 days with migration guide
The version field in health endpoints enables client adaptation: version 2026.2.22 supports trinity_forge streaming, while 2025.12.1 requires sequential stage calls. Deprecated features return warning headers but continue functioning through the deprecation period (Source) .
1.5 Verdict System & Return Codes
1.5.1 Primary Verdict States
1.5.1.1 SEAL - Full Constitutional Compliance
SEAL indicates complete compliance with all applicable floors, with output approved for immediate release. This is the green light state enabling normal business operation. SEALed outputs carry cryptographic proof of compliance (ZKPC hash) that can be presented to auditors, regulators, or courts as evidence of due diligence (Source) .
SEAL does not guarantee correctness-no system can-but it guarantees that appropriate processes were followed to minimize known failure modes. SEAL rates vary by deployment: 85-95% for well-scoped enterprise applications, 60-70% for open-ended public deployments due to higher edge case and adversarial query incidence (Source) .
1.5.1.2 PARTIAL - Conditional Approval with Constraints
PARTIAL indicates approved release with acknowledged limitations: uncertainty regions noted, simplifications disclosed, or scope restrictions applied. This verdict enables valuable but imperfect information to flow while maintaining transparency (Source) .
Clients must surface PARTIAL status to users: This response includes simplified explanations; see technical documentation for complete details. Common triggers: F4 ambiguity scores 0.10-0.15, F7 Omega values 0.15-0.20, or F10 evidence gaps in non-critical claims. Automated downstream use is prohibited without human acknowledgment (Source) .
1.5.1.3 SABAR / 888_HOLD - Human Review Required
SABAR (from Arabic , patience/perseverance) indicates automated processing paused pending additional information or human judgment. The query is not necessarily harmful-just complex, novel, or sensitive enough to benefit from human oversight. 888_HOLD specifically indicates pre-seal suspension-processing completed through stage 888 audit, but final seal awaiting human confirmation (Source) .
SABAR may resolve through query refinement and retry; 888_HOLD requires explicit human action. Both states include structured review requests explaining what judgment is needed, with complete session context preserved for reviewer understanding. Timeout default: 24 hours, with escalation to operational alerts if unaddressed (Source) .
1.5.1.4 VOID - Constitutional Violation Blocked
VOID indicates hard floor violation with output permanently blocked and session terminated. Unlike SABAR, VOID is terminal-no resumption possible. The session is committed to VAULT999 for forensic analysis, with pattern detection for: single-actor VOID clusters, common trigger categories, and temporal clustering suggesting attack campaigns (Source) .
VOID responses include: specific violation explanation, remediation guidance (if addressable), and escalation pathway (security review for suspected attacks). Some VOID categories enable automatic retry with modified parameters: F12 (sanitized input), F2 (narrower scope). F1/F9/F12 VOIDs prohibit retry-authority, ethics, and injection violations indicate fundamental issues not addressable by parameter tweaking (Source) .
1.5.2 Client Action Mapping
1.5.2.1 Automatic Retry Conditions
Verdict	Auto-Retry Eligible	Conditions	Backoff Pattern
SABAR	Yes	Timeout, resource pressure, F5/F6 soft violations	Exponential: 1s, 2s, 4s, max 8s with jitter
PARTIAL	No	Human approval required for constraints	N/A
VOID	Conditional	F2, F4, F7, F10 may retry with modification; F1, F5, F9, F12 terminal	N/A
888_HOLD	No	Explicit human resolution required	N/A
Retry rules: maximum 3 retries per original query, parameter modification required (cannot retry identical parameters), jitter prevents thundering herd (Source) .
1.5.2.2 Escalation to Human Oversight
Three escalation paths exist: (1) automatic SABAR triggers for configured floors; (2) explicit human_approve parameter in seal; (3) emergency F13 Sovereign invocation through out-of-band channels. Escalation includes complete session context: original query, all processing stages, floor triggers, and recommended resolution (Source) .
Reviewer authority levels:
	Level 1 (standard operators): release SABAR, routine 888_HOLD
	Level 2 (domain experts): override F2/F4/F7 for their domain
	Level 3 (constitutional council): modify floor calibrations and precedent
Escalation latency targets: <5 minutes for critical systems, <24 hours for standard deployments (Source) .
1.5.2.3 Session Termination Protocols
Termination Type	Trigger	Cleanup Actions
Clean	seal completion, explicit void call	Resource release, metrics update, optional notification
Timeout	Inactivity > session_ttl	Temporary data purge after 24h, cryptographic commitments finalized
Abnormal	Crash, kill -9, connection loss	Recovery from Redis state if possible, else VOID with incomplete_session flag
All terminations are logged to VAULT999 with final state. Abnormal termination detection enables session recovery: next connection with same session_id receives session recovered status with partial results if available (Source) .
1.6 Governance Mode Configuration
1.6.1 HARD / STRICT Mode - Maximum Enforcement
HARD mode (also STRICT) applies maximum constitutional enforcement: all floors at full sensitivity, no advisory bypasses, mandatory human review for sensitive categories. Appropriate for: production systems handling consequential decisions, regulated industries (healthcare, finance, legal), high adversarial exposure deployments (Source) .
Performance impact: 20-40% latency increase from additional verification stages, 10-15% SEAL rate reduction from stricter thresholds. Configuration: GOVERNANCE_MODE=HARD environment variable or "governance_mode": "HARD" in anchor arguments. F3 Tri-Witness mandatory, F2 Truth threshold tau >= 0.99, F7 Omega_0 strictly bounded (Source) .
1.6.2 SOFT Mode - Advisory-First Operation
SOFT mode prioritizes throughput and user experience: floors operate advisory (violations logged but not blocking), with automatic escalation to HARD for detected high-stakes patterns. Appropriate for: education, creative exploration, preliminary research, low-stakes internal applications (Source) .
SOFT maintains full audit trails enabling retrospective analysis and gradual hardening. F2 Truth relaxed to tau >= 0.95, F3 Tri-Witness advisory, automatic PARTIAL release with constraint surfacing. Organizations use SOFT to calibrate floor sensitivity before HARD deployment-understanding their query distributions constitutional characteristics without production risk (Source) .
1.6.3 Runtime Mode Switching & Session Inheritance
Lane selection occurs at anchor and is sticky for session duration-prevents mid-session downgrade attacks. Explicit upgrade (SOFTHARD) permitted when F1 Amanah detects irreversibility: medical diagnosis query automatically elevates regardless of initial mode (Source) .
Cross-session inheritance: prior session verdicts influence but do not determine new session lane selection. Clean SEAL history enables streamlined evaluation; repeated SABAR/VOID triggers enhanced scrutiny. Inheritance depth limited to 3 sessions to prevent cumulative relaxation attacks (Source) .
1.7 Authentication & Security
1.7.1 SSE/HTTP Bearer Token: ARIF_SECRET
Remote transports (SSE, HTTP) require Authorization: Bearer <ARIF_SECRET> header. Token format: arif_<environment>_<random32>_<hash8> with environments dev, staging, prod. Token scope determines accessible lanes and tools-read-only tokens cannot invoke forge or seal (Source) .
Token lifecycle: issuance with expiration, rotation with graceful transition periods, revocation with immediate invalidation propagation, all usage logged to VAULT999. Production deployments should implement token binding to client identity (IP ranges, TLS certificates) where appropriate. SHA-256 hashed server-side with timing-safe comparison prevents timing attacks (Source) .
1.7.2 stdio Trust Boundary Assumptions
stdio transport assumes OS-level process isolation-client and server share user identity, no network exposure exists. This trust model enables zero-configuration operation but requires: (a) client executable verification, (b) environment variable protection, (c) no shared systems with untrusted users (Source) .
Security responsibility is entirely environmental-no cryptographic authentication within the stdio stream. Multi-user systems require careful permission management; containerization (Docker, systemd-nspawn) provides additional isolation layers. stdio is inappropriate for production multi-tenant deployments regardless of technical convenience (Source) .
1.7.3 Session Token Lifecycle & Rotation
Session tokens (distinct from ARIF_SECRET) are UUIDv4-generated per-session with 1-hour default TTL. Automatic rotation at 50% TTL if session active; explicit rotate_token tool available for security events. Revocation: immediate via terminate_session, bulk via token prefix blacklist, propagation to all replicas within 30 seconds (Source) .
Session state is encrypted at rest in PostgreSQL with AES-256-GCM, key rotation every 90 days. Temporary session
