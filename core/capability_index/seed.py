"""Seed data: the 97 tools currently exposed across the federation.

This is the ground-truth snapshot at 2026-06-05.
When tools are added/removed, re-run the seed script.
"""

from __future__ import annotations

from capability_index.models import CapabilityRecord

SEED_CAPABILITIES: list[CapabilityRecord] = [
    # ── arifOS (Constitutional Kernel) ──
    CapabilityRecord(tool_name="arif_session_init", server="arifOS", description="Start or resume a governed constitutional session. Must be called first.", tags=["governance", "session", "constitutional"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="arif_sense_observe", server="arifOS", description="Search the web, ingest URLs, check system vitals, or map a repository.", tags=["web", "search", "observation", "evidence"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="arif_evidence_fetch", server="arifOS", description="Fetch and preserve external evidence with source citations.", tags=["evidence", "citation", "fact-check"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="arif_mind_reason", server="arifOS", description="Multi-step reasoning, planning, and reflection with confidence labeling.", tags=["reasoning", "planning", "reflection", "analysis"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="arif_heart_critique", server="arifOS", description="Assess ethical risks and human impact before acting.", tags=["ethics", "critique", "human-impact", "safety"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="arif_kernel_route", server="arifOS", description="Route intent to the correct tool or federation organ.", tags=["routing", "orchestration", "dispatch"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="arif_reply_compose", server="arifOS", description="Compose the final response for the user.", tags=["composition", "reply", "formatting"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="arif_memory_recall", server="arifOS", description="Search past sessions, assets, sealed events, or repositories.", tags=["memory", "search", "history", "recall"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="arif_gateway_connect", server="arifOS", description="Bridge to other federation agents (GEOX, WEALTH, WELL, A-FORGE, AAA, APEX, cn-organ).", tags=["bridge", "gateway", "multi-agent"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="arif_judge_deliberate", server="arifOS", description="Render final constitutional verdict on a proposed action.", tags=["judge", "verdict", "constitutional", "deliberation"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="arif_vault_seal", server="arifOS", description="Seal a verdict or outcome to the immutable audit ledger.", tags=["vault", "seal", "audit", "immutable"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="arif_forge_execute", server="arifOS", description="Execute approved builds, deployments, or system changes.", tags=["forge", "deploy", "build", "execution"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="arif_ops_measure", server="arifOS", description="Check system health, thermodynamic state, and resource metrics.", tags=["health", "metrics", "monitoring", "ops"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="arif_appeal_raise", server="arifOS", description="Raise an appeal against a sealed or decided verdict.", tags=["appeal", "governance", "challenge"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="arif_appeal_status", server="arifOS", description="Check the status of a previously raised appeal.", tags=["appeal", "status", "governance"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="arif_appeal_list", server="arifOS", description="List all appeals with optional status filter.", tags=["appeal", "list", "governance"], epistemic_tag="CLAIM"),

    # ── WEALTH (Capital Intelligence) ──
    CapabilityRecord(tool_name="wealth_personal_finance", server="WEALTH", description="Unified surface for cashflow, runway, and net worth.", tags=["finance", "cashflow", "runway", "net-worth", "personal"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="wealth_epf_project", server="WEALTH", description="Project EPF accumulation to target age.", tags=["epf", "malaysia", "retirement", "projection"], epistemic_tag="ESTIMATE"),
    CapabilityRecord(tool_name="wealth_zakat_calculate", server="WEALTH", description="Malaysian 2.5%% zakat above nisab.", tags=["zakat", "malaysia", "islamic-finance"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="wealth_market_data", server="WEALTH", description="Unified surface for FX, commodities, and macro indicators.", tags=["market", "fx", "commodity", "macro"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="wealth_health_check", server="WEALTH", description="Universal health check for federation stability.", tags=["health", "federation", "stability"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="wealth_survival_engine", server="WEALTH", description="Unified survival intelligence: cashflow, runway, burn, liquidity.", tags=["survival", "liquidity", "burn", "runway"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="wealth_entropy_audit", server="WEALTH", description="Calculate structural and narrative entropy coefficients for an SOE/NOC.", tags=["entropy", "audit", "soe", "noc", "governance"], epistemic_tag="ESTIMATE"),
    CapabilityRecord(tool_name="wealth_governance_verdict", server="WEALTH", description="Final Allocation Verdict — sovereign governance recommendation.", tags=["governance", "verdict", "allocation", "sovereign"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="wealth_preference_rank", server="WEALTH", description="Personal Utility Ranking — preference ordering under constraints.", tags=["preference", "ranking", "utility", "decision"], epistemic_tag="PLAUSIBLE"),
    CapabilityRecord(tool_name="wealth_agent_path", server="WEALTH", description="Sovereign Intent Router — classifies tasks into L1/L2 physics-economic paths.", tags=["routing", "intent", "physics", "economics"], epistemic_tag="PLAUSIBLE"),
    CapabilityRecord(tool_name="wealth_ledger_query", server="WEALTH", description="Ledger Read — query the immutable governance ledger.", tags=["ledger", "query", "audit"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="wealth_ledger_write", server="WEALTH", description="Ledger Append — irreversible state transition to VAULT999.", tags=["ledger", "write", "vault", "irreversible"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="wealth_conservation_capital", server="WEALTH", description="Conservation — capital stock reality (assets, liabilities, reserves).", tags=["capital", "assets", "liabilities", "reserves"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="wealth_flow_liquidity", server="WEALTH", description="Flow — liquidity movement (cashflow, burn, runway, survival).", tags=["liquidity", "cashflow", "burn", "runway"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="wealth_gradient_price", server="WEALTH", description="Gradient — price pressure, spread, mispricing detection.", tags=["price", "spread", "mispricing", "trading"], epistemic_tag="ESTIMATE"),
    CapabilityRecord(tool_name="wealth_entropy_risk", server="WEALTH", description="Entropy — uncertainty, dispersion, tail risk, disorder.", tags=["risk", "entropy", "uncertainty", "tail-risk"], epistemic_tag="ESTIMATE"),
    CapabilityRecord(tool_name="wealth_energy_productivity", server="WEALTH", description="Energy — output per input, productivity, capital efficiency.", tags=["productivity", "efficiency", "energy"], epistemic_tag="ESTIMATE"),
    CapabilityRecord(tool_name="wealth_time_discount", server="WEALTH", description="Time — NPV, IRR, payback, compounding, decay.", tags=["npv", "irr", "payback", "time-value"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="wealth_inertia_leverage", server="WEALTH", description="Inertia — resistance to change, leverage stress, fragility.", tags=["leverage", "dscr", "fragility", "stress"], epistemic_tag="ESTIMATE"),
    CapabilityRecord(tool_name="wealth_field_macro", server="WEALTH", description="Field — macro environment (rates, FX, energy, carbon, regime).", tags=["macro", "rates", "fx", "energy", "carbon"], epistemic_tag="ESTIMATE"),
    CapabilityRecord(tool_name="wealth_signal_information", server="WEALTH", description="Signal — information value, evidence quality, schema validity.", tags=["signal", "information", "evidence", "e-and-p"], epistemic_tag="ESTIMATE"),
    CapabilityRecord(tool_name="wealth_game_coordination", server="WEALTH", description="Game — multi-agent incentives, bargaining, coordination.", tags=["game-theory", "incentives", "bargaining", "coordination"], epistemic_tag="PLAUSIBLE"),
    CapabilityRecord(tool_name="wealth_boundary_governance", server="WEALTH", description="Boundary — constitutional floors, maruah, stewardship, constraint.", tags=["boundary", "governance", "maruah", "stewardship"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="wealth_system_registry_status", server="WEALTH", description="Registry truth diagnostic — intended, registered, and alias surfaces.", tags=["registry", "diagnostic", "truth"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="wealth_omni_wisdom", server="WEALTH", description="Unified capital intelligence — synthesis + deal + hysteresis in one tool.", tags=["synthesis", "wisdom", "capital", "deal"], epistemic_tag="PLAUSIBLE"),
    CapabilityRecord(tool_name="wealth_inequality_kernel", server="WEALTH", description="Inequality Kernel — unified diagnosis across all 5 inequality dimensions.", tags=["inequality", "kernel", "diagnosis", "social"], epistemic_tag="ESTIMATE"),

    # ── WELL (Human Readiness) ──
    CapabilityRecord(tool_name="mcp_health_check", server="WELL", description="DEPRECATED: use well_assess_reliability instead.", tags=["health", "deprecated"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="well_classify_substrate", server="WELL", description="Substrate classification and boundary sensing.", tags=["substrate", "classification", "boundary"], epistemic_tag="PLAUSIBLE"),
    CapabilityRecord(tool_name="well_trace_lineage", server="WELL", description="Memory, trend, ledger, and vault chain tracing.", tags=["lineage", "memory", "trace", "vault"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="well_detect_boundary", server="WELL", description="Boundary detection across membrane, body, machine, and federation.", tags=["boundary", "detection", "membrane"], epistemic_tag="PLAUSIBLE"),
    CapabilityRecord(tool_name="well_measure_gradient", server="WELL", description="Measure chemical, energy, pressure, attention, and compute gradients.", tags=["gradient", "energy", "pressure", "attention"], epistemic_tag="ESTIMATE"),
    CapabilityRecord(tool_name="well_assess_metabolism", server="WELL", description="Assess biological metabolism and system throughput across substrates.", tags=["metabolism", "throughput", "biology"], epistemic_tag="ESTIMATE"),
    CapabilityRecord(tool_name="well_assess_homeostasis", server="WELL", description="Assess regulation, stability, energy, stress, and empathic balance under change.", tags=["homeostasis", "stability", "empathy", "regulation", "energy", "stress"], epistemic_tag="ESTIMATE"),
    CapabilityRecord(tool_name="well_check_repair", server="WELL", description="Check repair, recovery, resilience, and forge cycle integrity.", tags=["repair", "recovery", "resilience", "forge"], epistemic_tag="PLAUSIBLE"),
    CapabilityRecord(tool_name="well_validate_vitality", server="WELL", description="Validate vitality, readiness, and NIAT.", tags=["vitality", "readiness", "niat"], epistemic_tag="ESTIMATE"),
    CapabilityRecord(tool_name="well_assess_livelihood", server="WELL", description="Assess human wellness, role, dignity, support, and meaning.", tags=["livelihood", "wellness", "dignity", "meaning"], epistemic_tag="ESTIMATE"),
    CapabilityRecord(tool_name="well_assess_reliability", server="WELL", description="Assess machine, tool, institution, and operational reliability.", tags=["reliability", "machine", "institution"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="well_compute_metabolic_flux", server="WELL", description="Compute metabolic_flux — unified thermodynamic entropy rate.", tags=["metabolic-flux", "entropy", "thermodynamics"], epistemic_tag="ESTIMATE"),
    CapabilityRecord(tool_name="well_assess_sovereign_entropy", server="WELL", description="Measure the sovereign's resistance to behavioral modeling.", tags=["sovereignty", "entropy", "behavioral-modeling"], epistemic_tag="PLAUSIBLE"),
    CapabilityRecord(tool_name="well_guard_dignity", server="WELL", description="Guard soul, personhood, meaning, and symbolic boundaries.", tags=["dignity", "soul", "personhood", "boundaries"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="well_system_registry_status", server="WELL", description="WELL registry truth probe — somatic surface vs autonomic internals.", tags=["registry", "truth", "somatic"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="well_registry_status", server="WELL", description="WELL registry truth diagnostic — blueprint canonical format.", tags=["registry", "diagnostic", "blueprint"], epistemic_tag="CLAIM"),

    # ── minimax ──
    CapabilityRecord(tool_name="web_search", server="minimax", description="Search the web and return ranked results with feedback-driven scoring.", tags=["web", "search", "ranking"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="understand_image", server="minimax", description="Analyze and interpret image content from local files or URLs.", tags=["vision", "image", "analysis"], epistemic_tag="PLAUSIBLE"),

    # ── github ──
    CapabilityRecord(tool_name="create_or_update_file", server="github", description="Create or update a single file in a GitHub repository.", tags=["github", "file", "write"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="search_repositories", server="github", description="Search for GitHub repositories.", tags=["github", "search", "repository"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="create_repository", server="github", description="Create a new GitHub repository in your account.", tags=["github", "repository", "create"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="get_file_contents", server="github", description="Get the contents of a file or directory from a GitHub repository.", tags=["github", "file", "read"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="push_files", server="github", description="Push multiple files to a GitHub repository in a single commit.", tags=["github", "file", "push", "commit"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="create_issue", server="github", description="Create a new issue in a GitHub repository.", tags=["github", "issue", "create"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="create_pull_request", server="github", description="Create a new pull request in a GitHub repository.", tags=["github", "pull-request", "create"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="fork_repository", server="github", description="Fork a GitHub repository to your account or specified organization.", tags=["github", "fork", "repository"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="create_branch", server="github", description="Create a new branch in a GitHub repository.", tags=["github", "branch", "create"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="list_commits", server="github", description="Get list of commits of a branch in a GitHub repository.", tags=["github", "commit", "list"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="list_issues", server="github", description="List issues in a GitHub repository with filtering options.", tags=["github", "issue", "list"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="update_issue", server="github", description="Update an existing issue in a GitHub repository.", tags=["github", "issue", "update"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="add_issue_comment", server="github", description="Add a comment to an existing issue.", tags=["github", "issue", "comment"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="search_code", server="github", description="Search for code across GitHub repositories.", tags=["github", "code", "search"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="search_issues", server="github", description="Search for issues and pull requests across GitHub repositories.", tags=["github", "issue", "search"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="search_users", server="github", description="Search for users on GitHub.", tags=["github", "user", "search"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="get_issue", server="github", description="Get details of a specific issue in a GitHub repository.", tags=["github", "issue", "detail"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="get_pull_request", server="github", description="Get details of a specific pull request.", tags=["github", "pull-request", "detail"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="list_pull_requests", server="github", description="List and filter repository pull requests.", tags=["github", "pull-request", "list"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="create_pull_request_review", server="github", description="Create a review on a pull request.", tags=["github", "pull-request", "review"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="merge_pull_request", server="github", description="Merge a pull request.", tags=["github", "pull-request", "merge"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="get_pull_request_files", server="github", description="Get the list of files changed in a pull request.", tags=["github", "pull-request", "files"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="get_pull_request_status", server="github", description="Get the combined status of all status checks for a pull request.", tags=["github", "pull-request", "status"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="update_pull_request_branch", server="github", description="Update a pull request branch with the latest changes from the base branch.", tags=["github", "pull-request", "update"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="get_pull_request_comments", server="github", description="Get the review comments on a pull request.", tags=["github", "pull-request", "comments"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="get_pull_request_reviews", server="github", description="Get the reviews on a pull request.", tags=["github", "pull-request", "reviews"], epistemic_tag="CLAIM"),

    # ── brave-search ──
    CapabilityRecord(tool_name="brave_web_search", server="brave-search", description="Search the open web using the Brave Search API. Find news, updates, protocol specifications, documentation, and general information on the internet.", tags=["web", "search", "brave", "protocol", "updates", "mcp"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="brave_local_search", server="brave-search", description="Searches for local businesses and places using Brave's Local Search API.", tags=["local", "search", "business", "brave"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="brave_video_search", server="brave-search", description="Searches for videos using Brave's Video Search API.", tags=["video", "search", "brave"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="brave_image_search", server="brave-search", description="Performs an image search using the Brave Search API.", tags=["image", "search", "brave"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="brave_news_search", server="brave-search", description="Searches for news articles using Brave's News Search API.", tags=["news", "search", "brave"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="brave_summarizer", server="brave-search", description="Retrieves AI-generated summaries of web search results.", tags=["summary", "search", "brave", "ai"], epistemic_tag="PLAUSIBLE"),

    # ── meyhem ──
    CapabilityRecord(tool_name="search", server="meyhem", description="Search the web and return ranked results with feedback-driven scoring.", tags=["web", "search", "meyhem"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="select", server="meyhem", description="Select a search result to get its full content.", tags=["web", "select", "content"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="outcome", server="meyhem", description="Report whether a search result helped complete your task.", tags=["feedback", "search", "meyhem"], epistemic_tag="CLAIM"),
    CapabilityRecord(tool_name="find_server", server="meyhem", description="Find MCP servers for a given task.", tags=["discovery", "server"], epistemic_tag="PLAUSIBLE"),
    CapabilityRecord(tool_name="find_capability", server="meyhem", description="Find the best tool for your task across MCP servers and OpenClaw skills.", tags=["discovery", "capability"], epistemic_tag="PLAUSIBLE"),
]
