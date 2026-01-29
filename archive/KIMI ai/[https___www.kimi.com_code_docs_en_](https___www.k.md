<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# [https://www.kimi.com/code/docs/en/](https://www.kimi.com/code/docs/en/)

im arif. tell me everything about kimi code

Kimi Code (sometimes called **Kimi for Coding** or Kimi Code membership) is a coding-focused perk inside the Kimi Membership Plan that turns Kimi K2 into a high-speed, API-exposed pair programmer for your local tools (Kimi CLI, Claude Code, Roo Code, etc.). It is explicitly positioned for individual/personal dev workflows, not enterprise backends, and rides on Moonshot’s K2 agentic stack.[^1_1][^1_2][^1_3]

## Core concept

- **What it is**
    - A membership benefit that unlocks higher-performance, coding-optimised usage of Kimi (K2) for personal software development tasks.[^1_2][^1_1]
    - Packaged as “one subscription, code everywhere”: same membership gives you Kimi Code in Kimi CLI, Claude Code, Roo Code and other supported coding agents.[^1_1][^1_2]
- **What it is not**
    - Not a separate enterprise API; for company-scale use, Moonshot AI Open Platform is the channel (usage-based billing, model choice, etc.).[^1_3][^1_2]
    - Not licensed for enterprise scenarios; docs explicitly limit it to personal development usage.[^1_2]


## Main capabilities for devs

- **Agentic coding behaviour**
    - Built around Kimi K2, which is an MoE model tuned for agentic tasks: multi-step reasoning, tool use, and environment interaction.[^1_4][^1_5]
    - In coding context this translates to: reading/editing files, executing commands, orchestrating multi-step dev flows via Kimi CLI (build, test, refactor, etc.).[^1_6][^1_7]
- **Typical development tasks**
    - Writing and modifying code: implement new features, refactor modules, fix bugs from natural-language instructions.[^1_7][^1_6]
    - Understanding projects: answer questions about unfamiliar repos, architecture, and implementation details after scanning files.[^1_6][^1_7]
    - Automating workflows: run builds/tests, batch-edit files, execute scripts or shell commands through Kimi CLI’s “shell-like” interface.[^1_7][^1_6]
- **Performance characteristics**
    - High-frequency, “turbo” interactions: membership unlocks faster responses and more generous quotas vs base chat usage.[^1_1][^1_2]
    - Large-context coding: Kimi K2 supports 100k–128k-class context windows via Moonshot platform, making it viable for big repos and long docs.[^1_8][^1_3][^1_7]


## How you actually use it (dev workflow)

- **1. Subscribe \& get the key**
    - In Kimi web UI: Avatar → Settings / Manage / Subscription, then click “Kimi for Coding” / Kimi Code to open a popup.[^1_9][^1_2][^1_1]
    - From that popup or membership details page, copy or reset the dedicated Kimi Code API key and see quota info.[^1_9][^1_2]
- **2. Wire it into tools**
    - Kimi CLI:
        - Install CLI, then in your project directory run `kimi`, use `/setup` to configure API platform + model, and paste the Kimi Code API key.[^1_6]
        - Once configured, CLI acts as a shell-like agent: you talk in natural language or flip into shell mode and let it execute commands.[^1_6]
    - Other agents (Claude Code, Roo Code, etc.):
        - Each tool exposes a “Kimi” or “custom provider” backend where you paste the same Kimi Code key; from there they call Moonshot’s K2 endpoints under your membership.[^1_2][^1_1]
- **3. Runtime behaviour**
    - Real-time request logs and quota in the Kimi Code console: balance, refresh countdown, and call history for observability.[^1_1][^1_2]
    - Dynamically managed limits: request caps and output speeds adjust with system load; specs can evolve as they tune capacity.[^1_2][^1_1]


## Pricing / quotas context

- **Membership framing**
    - Kimi Code is bundled as a perk inside paid Kimi membership tiers rather than pay-per-call à la carte.[^1_1][^1_2]
    - For heavy API usage, Moonshot platform exposes standard token pricing (e.g. around 0.15 USD / 1M input tokens, 2.50 USD / 1M output tokens for Kimi K2), which is substantially cheaper than GPT‑4-scale models.[^1_8][^1_3]
- **Practical limits**
    - Public discussion suggests per-day/per-week call caps for coding usage (ballpark thousands of calls per week on some plans), but exact numbers can change and are not hard-coded in the official short docs.[^1_10][^1_1]
    - Official docs emphasise that performance, quotas and interoperability “may be adjusted or updated periodically,” so it behaves like an evolving capacity pool rather than fixed SLAs.[^1_9][^1_2][^1_1]


## Governance \& constraints (arifOS lens)

- **Licensing \& acceptable use**
    - Explicit constraint: personal development only; enterprise workloads should go through Moonshot AI’s Open Platform with proper commercial terms.[^1_3][^1_2]
    - Usage must stay within “Kimi CLI and other coding agents we permit or list on the official Kimi site,” meaning no arbitrary redistribution as a backend for third-party SaaS without alignment with their policy.[^1_2]
- **Model / infra separation**
    - Kimi Code = membership gating + quotas + convenience tooling layer.
    - Moonshot AI Open Platform = raw K2 API (long context, tool calling) for system builders and enterprises.[^1_5][^1_3]


### Governance audit (uncertainty band)

- **High confidence (Ω ≈ 0.03–0.05)**:
    - Nature of Kimi Code as a membership perk for personal coding, supported tools (Kimi CLI, Claude Code, Roo Code), personal vs enterprise split, and existence of dedicated API key + console.[^1_9][^1_6][^1_1][^1_2]
- **Medium uncertainty (Estimate Only)**:
    - Exact numeric quotas (daily/weekly call caps), per-tier prices inside Kimi Membership, and any region-specific terms; forum chatter suggests ranges but official docs leave them fluid.[^1_10][^1_8]

If you want, next step can be: design an arifOS-compliant coding stack diagram (Kimi Code + Moonshot API + your local tools + vaults) or compare Kimi Code vs OpenAI/Anthropic for your specific basin-analysis and arifOS workflows.
<span style="display:none">[^1_11][^1_12][^1_13][^1_14][^1_15]</span>

<div align="center">⁂</div>

[^1_1]: https://www.kimi.com/code/en

[^1_2]: https://www.kimi.com/code/docs/en/benefits.html

[^1_3]: https://platform.moonshot.ai

[^1_4]: https://www.datacamp.com/tutorial/kimi-k2

[^1_5]: https://www.kimi.com/preview/1980c532-5631-8c55-885f-517d380005e7

[^1_6]: https://www.kimi.com/code/docs/en/kimi-cli/guides/getting-started.html

[^1_7]: https://www.secondtalent.com/resources/kimi-k2-ai-for-coding/

[^1_8]: https://kimi-ai.chat/pricing/

[^1_9]: https://www.kimi.com/code/docs/en/

[^1_10]: https://www.reddit.com/r/kimi/comments/1ouk5gh/kimi_coding_usage_is_tiny_apparently/

[^1_11]: https://www.kimi.com/en

[^1_12]: https://www.kimi.com/code/docs/

[^1_13]: https://kimi-ai.chat

[^1_14]: https://hackmd.io/msiciwuST9mn3sgSPSyENw

[^1_15]: https://en.wikipedia.org/wiki/Kimi_(chatbot)


---

# Getting Started

What is Kimi CLI
Kimi CLI is an AI agent that runs in the terminal, helping you complete software development tasks and terminal operations. It can read and edit code, execute shell commands, search and fetch web pages, and autonomously plan and adjust actions during execution.
Kimi CLI is suited for:
Writing and modifying code: Implementing new features, fixing bugs, refactoring code
Understanding projects: Exploring unfamiliar codebases, answering architecture and implementation questions
Automating tasks: Batch processing files, running builds and tests, executing scripts
Kimi CLI provides a shell-like interactive experience in the terminal. You can describe your needs in natural language or switch to shell mode at any time to execute commands directly. Beyond terminal usage, Kimi CLI also supports integration with [IDEs](https://www.kimi.com/code/docs/en/kimi-cli/guides/ides.html) and other local agent clients via the [Agent Client Protocol](https://agentclientprotocol.com/).
Note
Kimi CLI is currently in technical preview. Features and APIs may change. If you encounter issues or have suggestions, please provide feedback on [GitHub Issues](https://github.com/MoonshotAI/kimi-cli/issues).
Installation
Run the installation script to complete the installation. The script will first install [uv](https://docs.astral.sh/uv/) (a Python package manager), then install Kimi CLI via uv:

# Linux / macOS

curl -LsSf [https://cdn.kimi.com/binaries/kimi-cli/install.sh](https://cdn.kimi.com/binaries/kimi-cli/install.sh) | bash

# Windows (PowerShell)

Invoke-RestMethod [https://cdn.kimi.com/binaries/kimi-cli/install.ps1](https://cdn.kimi.com/binaries/kimi-cli/install.ps1) | Invoke-Expression
Verify the installation:
kimi --version
TIP
Due to macOS security checks, the first run of the kimi command may take longer. You can add your terminal application in "System Settings → Privacy \& Security → Developer Tools" to speed up subsequent launches.
If you already have uv installed, you can also run:
uv tool install --python 3.14 kimi-cli
Upgrade and uninstall
Upgrade to the latest version:
uv tool upgrade kimi-cli --no-cache
Uninstall Kimi CLI:
uv tool uninstall kimi-cli
First run
Run the kimi command in the project directory where you want to work to start Kimi CLI:
cd your-project
kimi
On first launch, you need to configure the API platform and model. Enter the /setup command to start the configuration wizard:
Select an API platform (e.g., Kimi Code, Moonshot AI Open Platform)
Enter your API key
Select the model to use
After configuration, Kimi CLI will automatically save the settings and reload. See [Providers](https://moonshotai.github.io/kimi-cli/en/configuration/providers.html) for details.
Now you can chat with Kimi CLI directly using natural language. Try describing a task you want to complete, for example:
Show me the directory structure of this project
TIP
If the project doesn't have an AGENTS.md file, you can run the /init command to have Kimi CLI analyze the project and generate this file, helping the AI better understand the project structure and conventions.
Enter /help to view all available [slash commands](https://moonshotai.github.io/kimi-cli/en/reference/slash-commands.html) and usage tips.
Pager
[Previous pageBenefit Description](https://www.kimi.com/code/docs/en/benefits.html)
[Next pa](https://www.kimi.com/code/docs/en/kimi-cli/guides/use-cases.html)

Kimi CLI is a terminal-native **AI agent** that can read/edit your codebase, execute shell commands, browse the web, and self-plan multi-step actions to automate dev work and ops.  It is in technical preview, tightly coupled to Kimi For Coding / Moonshot K2, and meant to live inside your project folder as a “smart shell” plus agent.[^2_1][^2_2][^2_3][^2_4]

## What Kimi CLI actually is

- Runs as an interactive agent in your terminal, with a shell-like UI that can:
    - Write/modify code, fix bugs, refactor, and propose changes.[^2_5][^2_2]
    - Understand projects by reading files and answering architecture / implementation questions.[^2_2]
    - Automate tasks: batch file operations, builds, tests, script execution and other shell workflows.[^2_5][^2_2]
- Uses Kimi K2 (via Kimi Code or Moonshot Open Platform) as the backend LLM, giving long context and agentic planning.[^2_6][^2_7][^2_2]
- Status: “Technical preview”; APIs, features, and behaviour can change, and they explicitly invite GitHub Issues feedback.[^2_3][^2_2]


## Install / upgrade / uninstall

- **Standard install (Linux/macOS)**:
    - `curl -LsSf https://cdn.kimi.com/binaries/kimi-cli/install.sh | bash` installs uv, then Kimi CLI. [^2_2]
- **Windows (PowerShell)**:
    - `Invoke-RestMethod https://cdn.kimi.com/binaries/kimi-cli/install.ps1 | Invoke-Expression`. [^2_2]
- **If uv already exists**:
    - `uv tool install --python 3.14 kimi-cli`.[^2_2]
- **Verify / upgrade / remove**:
    - `kimi --version` to check install; `uv tool upgrade kimi-cli --no-cache` to upgrade; `uv tool uninstall kimi-cli` to remove.[^2_8][^2_2]
- macOS quirk: first run may be slow due to security checks; adding your terminal to “Privacy \& Security → Developer Tools” speeds subsequent runs.[^2_2]


## First run \& configuration

- Start inside the repo you want it to reason about:
    - `cd your-project && kimi`.[^2_1][^2_2]
- On first launch, run `/setup` to open the config wizard:
    - Choose API platform: Kimi Code (membership) or Moonshot AI Open Platform.[^2_9][^2_2]
    - Paste API key.
    - Select model (e.g. a Kimi K2 variant).[^2_9][^2_2]
- Settings are saved and auto-reloaded; provider details live in Kimi CLI config (see Providers docs).[^2_3][^2_2]
- After setup, you can:
    - Chat: “Show me the directory structure of this project.”[^2_2]
    - Run `/help` to see all slash commands and usage tips.[^2_5][^2_2]


## Modes, commands \& AGENTS.md

- **Interactive / agent mode**:
    - You speak natural language; it plans, reads files, executes commands, edits code, then reports back.[^2_5][^2_2]
- **Shell mode**:
    - You can toggle into a shell-like mode to run commands (`ls`, `make`, `pytest`, etc.) directly through Kimi CLI.[^2_5][^2_2]
    - Some shell built-ins like persistent `cd` are limited; best practice is starting Kimi in the correct project directory.[^2_1][^2_5]
- **AGENTS.md integration**:
    - If no `AGENTS.md` exists, `/init` analyzes the repo and generates one, encoding project overview, build/test commands, style rules, etc., to guide agents.[^2_10][^2_11][^2_2]
- Slash commands (non-exhaustive):
    - `/setup` for configuration, `/init` for AGENTS.md, `/help` to list commands; more are documented in the reference.[^2_10][^2_1][^2_2]


## Integration: IDEs, ACP, MCP

- **IDEs / editors**:
    - Kimi CLI can act as an agent backend for IDEs via Agent Client Protocol (ACP); for example, Zed config uses `"command": "kimi", "args": ["--acp"]`.[^2_2][^2_5]
    - Other local agent clients can talk to it over ACP so they share the same agent session/context.[^2_5][^2_2]
- **Model Context Protocol (MCP)**:
    - Supports MCP to connect external tools (search, filesystem, APIs) into the agent runtime.[^2_4][^2_5]
    - You can pass an MCP config file like `kimi --mcp-config-file ~/.config/kimi/mcp.json` to load tool servers (linters, search, custom services).[^2_1][^2_5]


## arifOS lens: where Kimi CLI fits

- Thermodynamic role in your stack:
    - Kimi CLI = local agent shell sitting closest to “heat” (raw commands, filesystem), with K2 as the reasoning core and ACP/MCP as conduction paths to other tools.[^2_6][^2_2][^2_5]
- Constraints / uncertainty band:
    - High confidence (Ω ≈ 0.03–0.05) on install steps, basic commands, modes, AGENTS.md `/init`, and ACP/MCP support, as these are documented consistently across official docs and GitHub.[^2_11][^2_3][^2_2][^2_5]
    - Estimate Only for long-term API shapes, command set details, and UX polish, since “technical preview” implies active change and third-party guides note gaps in official docs.[^2_9][^2_2][^2_5]

If you want, next step can be: design a concrete Kimi CLI + MCP layout for arifOS (e.g. which MCP servers for geology data, vault access, and governance logs) and map it against your existing Claude Code / Cursor pipelines.
<span style="display:none">[^2_12][^2_13][^2_14][^2_15]</span>

<div align="center">⁂</div>

[^2_1]: https://skywork.ai/blog/agent/kimi-cli-guide-2025-setup-commands-automation/

[^2_2]: https://www.kimi.com/code/docs/en/kimi-cli/guides/getting-started.html

[^2_3]: https://github.com/MoonshotAI/kimi-cli

[^2_4]: https://www.reddit.com/r/kimi/comments/1okrfe7/introducing_kimi_cli_technical_preview_kimi_for/

[^2_5]: https://apidog.com/blog/how-to-use-kimi-cli/

[^2_6]: https://moonshotai.github.io/Kimi-K2/

[^2_7]: https://platform.moonshot.ai/docs/guide/use-kimi-k2-to-setup-agent

[^2_8]: https://skywork.ai/blog/agent/install-kimi-cli-5-steps-macos-windows-linux-2025/

[^2_9]: https://www.youtube.com/watch?v=ZC7YsJVt700

[^2_10]: https://www.youtube.com/watch?v=D55LDNIZQ_o

[^2_11]: https://agents.md

[^2_12]: https://www.facebook.com/groups/techtitansgroup/posts/1504101904250456/

[^2_13]: https://www.reddit.com/r/opencodeCLI/comments/1q1sqfi/what_models_do_you_use_for_the_init_command/

[^2_14]: https://www.kimi.com/coding/docs/kimi-cli.html

[^2_15]: https://x.com/Kimi_Moonshot/status/1984207733177090274


---

# Interaction and Input

Kimi CLI provides rich interaction features to help you collaborate efficiently with AI.
Agent and shell mode
Kimi CLI has two input modes:
Agent mode: The default mode, where input is sent to the AI for processing
Shell mode: Execute shell commands directly without leaving Kimi CLI
Press Ctrl-X to switch between the two modes. The current mode is displayed in the bottom status bar.
In shell mode, you can execute commands just like in a regular terminal:
\$ ls -la
\$ git status
\$ npm run build
Note
In shell mode, each command executes independently. Commands that change the environment like cd or export won't affect subsequent commands.
Thinking mode
Thinking mode allows the AI to think more deeply before responding, suitable for handling complex problems.
In agent mode, press Tab to toggle thinking mode on or off. The status bar at the bottom will show a notification after switching. You can also enable it at startup with the --thinking flag:
kimi --thinking
TIP
Thinking mode requires support from the current model.
Multi-line input
Sometimes you need to enter multiple lines, such as pasting a code snippet or error log. Press Ctrl-J or Alt-Enter to insert a newline instead of sending the message immediately.
After finishing your input, press Enter to send the complete message.
Clipboard and image paste
Press Ctrl-V to paste text or images from the clipboard.
If the clipboard contains an image, Kimi CLI will automatically add the image as an attachment to the message. After sending the message, the AI can see and analyze the image.
TIP
Image input requires the model to support the image_in capability. Video input requires the video_in capability.
Slash commands
Slash commands are special instructions starting with /, used to execute Kimi CLI's built-in features, such as /help, /setup, /sessions, etc. After typing /, a list of available commands will automatically appear. For the complete list of slash commands, see the [slash commands reference](https://moonshotai.github.io/kimi-cli/en/reference/slash-commands.html).
@ path completion
When you type @ in a message, Kimi CLI will auto-complete file and directory paths in the working directory. This allows you to conveniently reference files in your project:
Check if there are any issues with @src/components/Button.tsx
After typing @, start entering the filename and matching completions will appear. Press Tab or Enter to select a completion.
Approvals
When the AI needs to perform operations that may have an impact (such as modifying files or running commands), Kimi CLI will request your confirmation.
The confirmation prompt will show operation details, and you can choose:
Allow: Execute this operation
Allow for this session: Automatically approve similar operations in the current session
Reject: Do not execute this operation
If you trust the AI's operations, or you're running Kimi CLI in a safe isolated environment, you can enable "YOLO mode" to automatically approve all requests:

# Enable at startup

kimi --yolo

# Or toggle during runtime

/yolo
When YOLO mode is enabled, a yellow YOLO badge appears in the status bar at the bottom. Enter /yolo again to disable it.
Note
YOLO mode skips all confirmations. Make sure you understand the potential risks. It's recommended to only use this in controlled environments.
Pager
[Previous pageCommon Use Cases](https://www.kimi.com/code/docs/en/kimi-cli/guides/use-cases.html)
[Next page](https://www.kimi.com/code/docs/en/kimi-cli/guides/sessions.html)

Kimi CLI’s interaction layer is essentially a controlled “agent shell” with hotkeys for mode switching, deeper thinking, safe approvals, and quick file/addressing ergonomics.  Used well, it lets you treat K2 like a junior dev sitting inside your terminal while you keep thermodynamic control over side effects.[^3_1][^3_2]

## Modes: agent, shell, thinking

- **Agent vs shell**
    - Two main input modes:
        - Agent mode (default): everything you type goes to the AI for reasoning and tool use.[^3_1]
        - Shell mode: direct shell command execution inside Kimi CLI without leaving the UI.[^3_1]
    - Toggle with **Ctrl‑X**; current mode is shown in the bottom status bar.[^3_3][^3_1]
    - Shell mode runs each command in isolation; env‑changing commands like `cd` or `export` do not persist across commands, so project root is defined by where you start `kimi`.[^3_4][^3_1]
- **Thinking mode**
    - “Thinking mode” lets the model take more steps / deeper reasoning before replying, aimed at complex problems.[^3_5][^3_1]
    - Toggle in agent mode with **Tab**, or start with `kimi --thinking`; status bar shows when it’s on.[^3_1]
    - Requires a model that supports this capability (certain K2 variants / backends only).[^3_6][^3_1]


## Input ergonomics: multiline, clipboard, images

- **Multi‑line entry**
    - Use **Ctrl‑J** or **Alt‑Enter** to insert a newline without sending; press Enter when done to send the whole block (good for long traces or code).[^3_1]
- **Clipboard and images**
    - **Ctrl‑V** pastes from clipboard; if the clipboard is an image, it’s attached to the message automatically.[^3_1]
    - Image analysis only works if the current model supports `image_in`; similarly, video attachments need `video_in`.[^3_6][^3_1]


## Slash commands \& path completion

- **Slash commands**
    - Commands beginning with `/` control Kimi CLI itself (e.g. `/help`, `/setup`, `/sessions`).[^3_1]
    - After typing `/`, a menu of available slash commands appears; the full catalogue is in the slash commands reference.[^3_7][^3_1]
- **@ path completion**
    - Typing `@` triggers auto‑completion for files/dirs in the working directory.[^3_1]
    - Example: `Check if there are any issues with @src/components/Button.tsx`; start typing after `@`, then accept the completion with Tab or Enter.[^3_1]


## Approvals \& YOLO mode

- **Normal approval flow**
    - When the agent wants to do impactful things (file edits, command execution, tool calls), Kimi CLI shows a confirmation panel describing the operation.[^3_2][^3_1]
    - Choices:
        - Allow (this operation only).
        - Allow for this session (auto‑approve similar operations until session ends).
        - Reject.[^3_1]
- **YOLO mode (auto‑approval)**
    - Enables full auto‑approval of all operations: file writes, shell commands, and also MCP tool calls.[^3_2][^3_1]
    - Start with `kimi --yolo` or toggle at runtime with `/yolo`; a yellow YOLO badge appears in the status bar while it’s active.[^3_2][^3_1]
    - Disabling: run `/yolo` again. Pending prompts after disabling still need manual approval.[^3_2][^3_1]
    - Docs explicitly warn this should only be used in controlled / isolated environments where you fully trust both the agent and any MCP servers in the loop.[^3_2][^3_1]


## arifOS governance view

- Under arifOS, **default mode** = Agent mode + manual approvals, with Thinking off unless the task is genuinely complex.[^3_5][^3_1]
- YOLO is a deliberate “high‑entropy” override, acceptable only in sandboxed containers or disposable branches where destructive commands are bounded; MCP guidance reinforces this by stressing server trust and manual checks for high‑risk actions.[^3_2]
- Uncertainty band: Ω ≈ 0.03–0.05 for key bindings, modes, approvals, YOLO semantics (straight from current docs); Estimate Only for how “thinking mode” is implemented under the hood and exact planning depth per backend model.[^3_5][^3_6][^3_1]

If you like, the next step can be a concrete keybinding + mode policy for your workflow (e.g. when to flip on Thinking vs YOLO for arifOS repo work vs geology/basin analysis repos).
<span style="display:none">[^3_10][^3_11][^3_12][^3_13][^3_14][^3_15][^3_16][^3_8][^3_9]</span>

<div align="center">⁂</div>

[^3_1]: https://www.kimi.com/code/docs/en/kimi-cli/guides/interaction.html

[^3_2]: https://moonshotai.github.io/kimi-cli/en/customization/mcp.html

[^3_3]: https://www.reddit.com/r/vibecoding/comments/1pov0uw/introducing_kimi_cli_an_opensource_coding_agent/

[^3_4]: https://skywork.ai/blog/agent/kimi-cli-guide-2025-setup-commands-automation/

[^3_5]: https://llmmultiagents.com/en/blogs/kimi-cli-technical-deep-dive

[^3_6]: https://www.together.ai/models/kimi-k2-0905

[^3_7]: https://kiro.dev/docs/cli/reference/slash-commands/

[^3_8]: https://github.com/MoonshotAI/kimi-cli/blob/main/AGENTS.md

[^3_9]: https://www.youtube.com/watch?v=yG3KFTwnGJ8

[^3_10]: https://www.kimi.com/code/docs/kimi-cli/guides/interaction.html

[^3_11]: https://blog.kilo.ai/p/this-week-in-kilo-code-cli-upgrades

[^3_12]: https://huggingface.co/moonshotai/Kimi-K2-Instruct/discussions/41

[^3_13]: https://hackmd.io/msiciwuST9mn3sgSPSyENw?both

[^3_14]: https://docs.cline.bot/features/yolo-mode

[^3_15]: https://www.facebook.com/groups/techtitansgroup/posts/1504101904250456/

[^3_16]: https://apidog.com/blog/claude-code-gemini-yolo-mode/


---

# essions and Context

Kimi CLI automatically saves your conversation history, allowing you to continue previous work at any time.
Session resuming
Each time you start Kimi CLI, a new session is created. If you want to continue a previous conversation, there are several ways:
Continue the most recent session
Use the --continue flag to continue the most recent session in the current working directory:
kimi --continue
Switch to a specific session
Use the --session flag to switch to a session with a specific ID:
kimi --session abc123
Switch sessions during runtime
Enter /sessions (or /resume) to view all sessions in the current working directory, and use arrow keys to select the session you want to switch to:
/sessions
The list shows each session's title and last update time, helping you find the conversation you want to continue.
Startup replay
When you continue an existing session, Kimi CLI will replay the previous conversation history so you can quickly understand the context. During replay, previous messages and AI responses will be displayed.
Clear and compact
As the conversation progresses, the context grows longer. Kimi CLI will automatically compress the context when needed to ensure the conversation can continue.
You can also manually manage the context using slash commands:
Clear context
Enter /clear to clear all context in the current session and start a fresh conversation:
/clear
After clearing, the AI will forget all previous conversation content. You usually don't need to use this command; for new tasks, starting a new session is a better choice.
Compact context
Enter /compact to have the AI summarize the current conversation and replace the original context with the summary:
/compact
Compacting preserves key information while reducing token consumption. This is useful when the conversation is long but you still want to retain some context.
TIP
The bottom status bar displays the current context usage (context: xx%), helping you understand when you need to clear or compact.

Kimi CLI treats each working directory as a “room” with its own saved sessions and compressed context, so you can leave and re‑enter long conversations without losing the project thread.  It also exposes explicit controls (`/clear`, `/compact`, context %) so you can manage how much of that history actually flows into K2.[^4_1][^4_2][^4_3][^4_4]

## Sessions: create, resume, switch

- **Automatic sessioning**
    - Every time you run `kimi` in a directory, Kimi CLI creates a new session tied to that working directory.[^4_2][^4_3]
- **Resume latest session**
    - `kimi --continue` resumes the most recent session for the current directory.[^4_5][^4_2]
- **Jump to a specific session**
    - `kimi --session <id>` starts Kimi CLI directly on a session by its ID (e.g. `kimi --session abc123`).[^4_6][^4_2]
- **Switch during runtime**
    - Use `/sessions` (or `/resume`) to list all sessions for that directory, then use arrow keys to select one to switch into.[^4_3][^4_2][^4_5]
    - The list shows each session’s title and last update time so you can identify the right thread.[^4_2][^4_6]


## Startup replay and context growth

- **Startup replay**
    - When you continue an existing session (via `--continue`, `--session`, or `/sessions`), Kimi CLI replays prior user + AI messages so you can quickly re‑orient.[^4_5][^4_2]
- **Automatic compaction**
    - As conversations get long, Kimi CLI automatically compresses context when needed, keeping sessions usable within the model’s context window.[^4_7][^4_8][^4_9]
    - Internally, this works like summarising older turns and pruning detail, which is why replay may show earlier content but not all of it is sent verbatim to the model.[^4_8][^4_9]


## Manual context control: clear \& compact

- **/clear**
    - `/clear` wipes all context for the current session; the AI then “forgets” previous conversation content for that session.[^4_3][^4_2]
    - Docs note you usually do not need this; for new tasks it’s generally better to start a new session instead.[^4_2]
- **/compact**
    - `/compact` asks the AI to summarise the ongoing conversation and replace detailed history with a compact summary, preserving key info while reducing token load.[^4_8][^4_2]
    - This is useful for very long threads where you still need continuity (requirements, constraints) but want cheaper, snappier turns.[^4_8][^4_5]
- **Context usage indicator**
    - The status bar includes a `context: xx%` indicator showing how full the context window is for the current session.[^4_10][^4_2]
    - This helps you decide when to call `/compact` or start a fresh session to avoid slowdowns or truncation.[^4_5][^4_2]


## arifOS angle: session thermodynamics

- For arifOS, each session = a local “basin” of state; using separate sessions per repo/task keeps entropy local and makes `/compact` behave like stratigraphic summarisation rather than random erosion.[^4_8][^4_2]
- High confidence (Ω ≈ 0.03–0.05) on the flags (`--continue`, `--session`), commands (`/sessions`, `/clear`, `/compact`), replay behaviour, and context %.[^4_1][^4_3][^4_2][^4_5]
- Estimate Only on implementation details of automatic compression (exact summarisation strategy, thresholds), since those live in internal agent logic and may change with K2 / CLI updates.[^4_9][^4_8]
<span style="display:none">[^4_11][^4_12][^4_13][^4_14][^4_15][^4_16]</span>

<div align="center">⁂</div>

[^4_1]: https://github.com/MoonshotAI/kimi-cli

[^4_2]: https://skywork.ai/blog/agent/kimi-cli-guide-2025-setup-commands-automation/

[^4_3]: https://www.linkedin.com/posts/jeremy-grove-mediadatafusion_kimicli-moonshotai-aicodingtools-activity-7388606018726805504-6fxI

[^4_4]: https://www.kimi.com/code/docs/en/kimi-cli/guides/interaction.html

[^4_5]: https://skywork.ai/blog/agent/top-20-kimi-cli-prompt-templates-2025-guide/

[^4_6]: https://github.com/MoonshotAI/kimi-cli/issues/83

[^4_7]: https://apidog.com/blog/how-to-use-kimi-cli/

[^4_8]: https://llmmultiagents.com/en/blogs/kimi-cli-technical-deep-dive

[^4_9]: https://docs.together.ai/docs/kimi-k2-quickstart

[^4_10]: https://www.kimi.com/coding/docs/kimi-cli.html

[^4_11]: https://platform.moonshot.ai/docs/guide/use-kimi-k2-to-setup-agent

[^4_12]: https://kiro.dev/docs/cli/chat/context/

[^4_13]: https://www.reddit.com/r/LocalLLaMA/comments/1m0lyjn/kimi_has_impressive_coding_performance_even_deep/

[^4_14]: https://www.youtube.com/watch?v=yG3KFTwnGJ8

[^4_15]: https://www.linkedin.com/posts/sebastianraschka_the-newly-released-1-trillion-parameter-kimi-activity-7349829221013180416-sIOh

[^4_16]: https://www.reddit.com/r/LocalLLaMA/comments/1lz2i5h/kimi_k2_on_cli/


---

# Using in IDEs

Kimi CLI supports integration with IDEs through the [Agent Client Protocol (ACP)](https://agentclientprotocol.com/), allowing you to use AI-assisted programming directly within your editor.
Prerequisites
Before configuring your IDE, make sure you have installed Kimi CLI and completed the /setup configuration.
Using in Zed
[Zed](https://zed.dev/) is a modern IDE that supports ACP.
Add the following to Zed's configuration file ~/.config/zed/settings.json:
{
"agent_servers": {
"Kimi CLI": {
"type": "custom",
"command": "kimi",
"args": ["acp"],
"env": {}
}
}
}
Configuration notes:
type: Fixed value "custom"
command: Path to the Kimi CLI command. If kimi is not in PATH, use the full path
args: Startup arguments. acp enables ACP mode
env: Environment variables, usually left empty
After saving the configuration, you can create Kimi CLI sessions in Zed's Agent panel.
Using in JetBrains IDEs
JetBrains IDEs (IntelliJ IDEA, PyCharm, WebStorm, etc.) support ACP through the AI Chat plugin.
If you don't have a JetBrains AI subscription, you can enable llm.enable.mock.response in the Registry to use the AI Chat feature. Press Shift twice to search for "Registry" to open it.
In the AI Chat panel menu, click "Configure ACP agents" and add the following configuration:
{
"agent_servers": {
"Kimi CLI": {
"command": "~/.local/bin/kimi",
"args": ["acp"],
"env": {}
}
}
}
command needs to be the full path. You can run which kimi in the terminal to get it. After saving, you can select Kimi CLI in the AI Chat Agent selector.

Kimi CLI can sit *inside* your IDE via ACP, so Zed/JetBrains become just the UI while Kimi runs as the agent server over stdio.  This removes lock‑in: you keep your editor, swap agents freely.[^5_1][^5_2][^5_3][^5_4][^5_5]

## ACP basics (what’s happening)

- **ACP (Agent Client Protocol)**
    - Open JSON‑RPC‑over‑stdio protocol between editors (“clients”) and AI agents like Kimi CLI (“servers”).[^5_6][^5_5]
    - Editor sends code, cursor context, instructions; agent replies with messages, edits, and actions, all without editor‑specific plugins per agent.[^5_7][^5_5]


## Prerequisites for IDE use

- Install and configure Kimi CLI (`/setup` with your Kimi Code or Moonshot API key and chosen model).[^5_2][^5_4]
- Ensure `kimi` is on your PATH or know its full path (e.g. `~/.local/bin/kimi` on Linux). `which kimi` gives you the path.[^5_4][^5_2]


## Zed configuration

- Edit `~/.config/zed/settings.json` and add an `agent_servers` block:[^5_2][^5_4][^5_7]

```json
{
  "agent_servers": {
    "Kimi CLI": {
      "type": "custom",
      "command": "kimi",
      "args": ["acp"],
      "env": {}
    }
  }
}
```

- Key fields:
    - `type`: must be `"custom"` for external agents.[^5_7]
    - `command`: `kimi` if in PATH; otherwise full path, e.g. `/home/arif/.local/bin/kimi`.[^5_8][^5_2]
    - `args`: `["acp"]` (or `["--acp"]` depending on version – both are documented), which tells Kimi CLI to start in ACP server mode.[^5_4][^5_2]
    - `env`: optional environment variables (API keys, region, etc.), usually left empty if already configured.[^5_2][^5_7]
- After saving, open Zed → Agent panel → create a new thread with “Kimi CLI” as the agent.[^5_4][^5_7]


## JetBrains IDEs configuration

- JetBrains IDEs (IntelliJ, PyCharm, WebStorm, etc.) expose ACP via the AI Chat tool window.[^5_3][^5_9][^5_6]
- If you don’t have JetBrains AI subscription, enable mock responses to unlock AI Chat UI:
    - Press Shift twice → search “Registry” → open Registry and enable `llm.enable.mock.response`.[^5_9][^5_4]
- In AI Chat:
    - Open AI Chat → menu (⋯) → “Configure ACP agents”.[^5_6][^5_9]
    - This creates/opens `~/.jetbrains/acp.json`, where you add Kimi:[^5_6][^5_4]

```json
{
  "agent_servers": {
    "Kimi CLI": {
      "command": "/full/path/to/kimi",
      "args": ["acp"],
      "env": {}
    }
  }
}
```

- Notes:
    - `command` must be a full path (e.g. `/Users/arif/.local/bin/kimi`), not just `kimi`.[^5_4][^5_6]
    - `args`: `["acp"]` to start ACP mode. Some JetBrains examples also include flags like `use_idea_mcp`/`use_custom_mcp`, but Kimi’s minimal config matches the snippet above.[^5_6][^5_4]
    - After saving, select “Kimi CLI” in the AI Chat agent selector and chat/code directly from the IDE.[^5_9][^5_4]


## arifOS framing

- **Thermodynamics**
    - CLI is the hot core (filesystem + shell); ACP turns Zed/JetBrains into low‑friction “views” over that core, so you can swap agents (Kimi, Claude Code, OpenCode) without editor rewiring.[^5_5][^5_7][^5_2]
- **Uncertainty band**
    - Ω ≈ 0.03–0.05 for: need `/setup` first, ACP support, Zed/JetBrains JSON shapes, `acp` arg, and path requirements.[^5_2][^5_4][^5_6]
    - Estimate Only: exact flag spelling across Kimi CLI versions (`acp` vs `--acp`), plus any future JetBrains UI tweaks, as these may shift with updates.[^5_10][^5_3][^5_2]

If you want, next step can be drafting a single `acp.json` / `settings.json` pattern that you can reuse across Zed + JetBrains + future ACP clients for arifOS.
<span style="display:none">[^5_11][^5_12][^5_13][^5_14][^5_15][^5_16]</span>

<div align="center">⁂</div>

[^5_1]: https://agentclientprotocol.com

[^5_2]: https://github.com/MoonshotAI/kimi-cli

[^5_3]: https://blog.jetbrains.com/ai/2025/12/bring-your-own-ai-agent-to-jetbrains-ides/

[^5_4]: https://www.kimi.com/code/docs/en/kimi-cli/guides/ides.html

[^5_5]: https://zed.dev/acp

[^5_6]: https://www.jetbrains.com/help/ai-assistant/acp.html

[^5_7]: https://zed.dev/docs/ai/external-agents

[^5_8]: https://github.com/zed-industries/zed/blob/main/docs/src/configuring-zed.md

[^5_9]: https://www.jetbrains.com/help/ai-assistant/ai-chat.html

[^5_10]: https://x.com/Kimi_Moonshot/status/1996953835080966390

[^5_11]: https://www.reddit.com/r/vibecoding/comments/1pov0uw/introducing_kimi_cli_an_opensource_coding_agent/

[^5_12]: https://apidog.com/blog/how-to-use-kimi-cli/

[^5_13]: https://opencode.ai/docs/acp/

[^5_14]: https://www.youtube.com/watch?v=AqGmnmkN2Mc

[^5_15]: https://skywork.ai/blog/agent/install-kimi-cli-5-steps-macos-windows-linux-2025/

[^5_16]: https://www.youtube.com/watch?v=wXJl4IhIYVg


---

# Integrations with Tools

Besides using in the terminal and IDEs, Kimi CLI can also be integrated with other tools.
Zsh plugin
[zsh-kimi-cli](https://github.com/MoonshotAI/zsh-kimi-cli) is a Zsh plugin that lets you quickly switch to Kimi CLI in Zsh.
Installation
If you use Oh My Zsh, you can install it like this:
git clone [https://github.com/MoonshotAI/zsh-kimi-cli.git](https://github.com/MoonshotAI/zsh-kimi-cli.git) \
\${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/kimi-cli
Then add the plugin in ~/.zshrc:
plugins=(... kimi-cli)
Reload the Zsh configuration:
source ~/.zshrc
Usage
After installation, press Ctrl-X in Zsh to quickly switch to Kimi CLI without manually typing the kimi command.
TIP
If you use other Zsh plugin managers (like zinit, zplug, etc.), please refer to the [zsh-kimi-cli repository](https://github.com/MoonshotAI/zsh-kimi-cli) README for installation instructions.

Kimi CLI has a dedicated **Zsh plugin** so you can jump into the agent from your shell with a single keypress instead of typing `kimi` manually.  It is optional but useful if you live in Zsh and want “agent on tap” without breaking your flow.[^6_1][^6_2][^6_3][^6_4]

## What the Zsh plugin does

- Adds a keybinding (Ctrl‑X in current docs) in Zsh to launch/switch into Kimi CLI.[^6_3][^6_5][^6_1]
- Makes Kimi CLI feel native in your shell: quick toggle, shared history/completions, and no need to type the command each time.[^6_2][^6_4]


## Oh My Zsh installation

- Clone the plugin into your custom plugins directory:

```sh
git clone https://github.com/MoonshotAI/zsh-kimi-cli.git \
  ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/kimi-cli
```

- Enable it in `~/.zshrc`:

```sh
plugins=(... kimi-cli)
```

- Reload Zsh config to activate:

```sh
source ~/.zshrc
```

- After reload, press **Ctrl‑X** in Zsh to jump straight into Kimi CLI mode.[^6_5][^6_1][^6_3]


## Other Zsh plugin managers

- For Antigen, Zinit, Znap, zplug and others, the exact snippet differs; the README for `zsh-kimi-cli` provides ready‑made lines like:
    - Antigen: `antigen bundle MoonshotAI/zsh-kimi-cli` then `antigen apply`.[^6_6][^6_1]
    - Zinit: `zinit light MoonshotAI/zsh-kimi-cli`.[^6_6]
    - Znap: `znap source MoonshotAI/zsh-kimi-cli`.[^6_6]
- Recommendation from the maintainers: if you’re not on Oh My Zsh, follow the instructions in the GitHub README for your plugin manager.[^6_1][^6_3][^6_6]


## arifOS usage hint

- For your stack, this plugin basically turns Zsh into a **front controller**:
    - Normal Zsh for low‑entropy commands.
    - Hit Ctrl‑X to escalate to Kimi CLI for high‑context, agentic work inside the same terminal.[^6_7][^6_8][^6_1]

Uncertainty band: Ω ≈ 0.03–0.05 for install commands, `plugins=(... kimi-cli)`, and Ctrl‑X behaviour (confirmed across official docs + repo history); Estimate Only for future changes to the default shortcut if the plugin evolves.[^6_9][^6_3][^6_1]
<span style="display:none">[^6_10][^6_11][^6_12][^6_13][^6_14][^6_15]</span>

<div align="center">⁂</div>

[^6_1]: https://github.com/MoonshotAI/kimi-cli

[^6_2]: https://ufukozen.com/blog/kimi-cli-next-generation-ai-assistant

[^6_3]: https://www.kimi.com/coding/docs/kimi-cli.html

[^6_4]: https://apidog.com/blog/how-to-use-kimi-cli/

[^6_5]: https://www.reddit.com/r/vibecoding/comments/1pov0uw/introducing_kimi_cli_an_opensource_coding_agent/

[^6_6]: https://github.com/MoonshotAI/zsh-kimi-cli

[^6_7]: https://skywork.ai/blog/agent/kimi-cli-guide-2025-setup-commands-automation/

[^6_8]: https://www.facebook.com/groups/techtitansgroup/posts/1504101904250456/

[^6_9]: https://github.com/MoonshotAI/zsh-kimi-cli/activity

[^6_10]: https://skywork.ai/blog/agent/install-kimi-cli-5-steps-macos-windows-linux-2025/

[^6_11]: https://www.kimi.com/code/docs/kimi-cli.html

[^6_12]: https://www.youtube.com/watch?v=kvluN1lcJ6Q

[^6_13]: https://www.kevnu.com/en/posts/the-ultimate-comparison-of-claude-code-alternatives-a-complete-analysis-of-the-10-strongest-cli-ai-programming-tools

[^6_14]: https://www.youtube.com/watch?v=D55LDNIZQ_o

[^6_15]: https://www.kimi.com/code/docs/en/kimi-cli/guides/interaction.html


---

# Model Context Protocol

[Model Context Protocol (MCP)](https://modelcontextprotocol.io/) is an open protocol that allows AI models to safely interact with external tools and data sources. Kimi CLI supports connecting to MCP servers to extend AI capabilities.
What is MCP
MCP servers provide "tools" for AI to use. For example, a database MCP server can provide query tools that allow AI to execute SQL queries; a browser MCP server can let AI control browsers for automation tasks.
Kimi CLI has built-in tools (file read/write, shell commands, web fetching, etc.). Through MCP, you can add more tools, such as:
Accessing specific APIs or databases
Controlling browsers or other applications
Integrating with third-party services (GitHub, Linear, Notion, etc.)
MCP server management
Use the [kimi mcp](https://moonshotai.github.io/kimi-cli/en/reference/kimi-mcp.html) command to manage MCP servers.
Add a server
Add an HTTP server:

# Basic usage

kimi mcp add --transport http context7 [https://mcp.context7.com/mcp](https://mcp.context7.com/mcp)

# With headers

kimi mcp add --transport http context7 [https://mcp.context7.com/mcp](https://mcp.context7.com/mcp) \
--header "CONTEXT7_API_KEY: your-key"

# Using OAuth authentication

kimi mcp add --transport http --auth oauth linear [https://mcp.linear.app/mcp](https://mcp.linear.app/mcp)
Add a stdio server (local process):
kimi mcp add --transport stdio chrome-devtools -- npx chrome-devtools-mcp@latest
List servers
kimi mcp list
While Kimi CLI is running, you can also enter /mcp to view connected servers and loaded tools.
Remove a server
kimi mcp remove context7
OAuth authorization
For servers using OAuth, you need to complete authorization first:
kimi mcp auth linear
This will open a browser to complete the OAuth flow. After successful authorization, Kimi CLI will save the token for future use.
Test a server
kimi mcp test context7
MCP configuration file
MCP server configuration is stored in ~/.kimi/mcp.json, in a format compatible with other MCP clients:
{
"mcpServers": {
"context7": {
"url": "https://mcp.context7.com/mcp",
"headers": {
"CONTEXT7_API_KEY": "your-key"
}
},
"chrome-devtools": {
"command": "npx",
"args": ["chrome-devtools-mcp@latest"],
"env": {
"SOME_VAR": "value"
}
}
}
}
Temporary configuration loading
Use the --mcp-config-file flag to load a configuration file from another location:
kimi --mcp-config-file /path/to/mcp.json
Use the --mcp-config flag to pass JSON configuration directly:
kimi --mcp-config '{"mcpServers": {"test": {"url": "https://..."}}}'
Security
MCP tools may access and operate external systems. Be aware of security risks.
Approval mechanism
Kimi CLI requests user confirmation for sensitive operations (such as file modifications and command execution). MCP tools follow the same approval mechanism, with all MCP tool calls prompting for confirmation.
Prompt injection risks
Content returned by MCP tools may contain malicious instructions attempting to trick the AI into performing dangerous operations. Kimi CLI marks tool return content to help the AI distinguish between tool output and user instructions, but you should still:
Only use MCP servers from trusted sources
Check whether AI-proposed operations are reasonable
Keep manual approval for high-risk operations
Note
In YOLO mode, MCP tool operations will also be automatically approved. It's recommended to only use YOLO mode when you fully trust the MCP servers.

MCP is the “tool bus” for Kimi CLI: it lets K2 call external tools/servers (HTTP or local stdio) in a standard way, with the same approval safety you use for file edits and shell commands.[^7_1][^7_2]

## MCP basics

- **What MCP is**
    - An open protocol where MCP *servers* expose tools (APIs, DBs, browsers, apps) and MCP *clients* (Kimi CLI, Claude, etc.) let models call those tools.[^7_2][^7_1]
    - Examples: DB servers exposing SQL tools, browser servers for automation, or connectors to GitHub/Notion/Linear.[^7_1][^7_2]
- **Kimi CLI + MCP**
    - Kimi CLI already has built‑ins (file read/write, shell, web fetch). MCP lets you add more like API clients, org databases, browser drivers, and SaaS integrations.[^7_2]


## Managing MCP servers with `kimi mcp`

- **Add HTTP servers**

```sh
# Basic
kimi mcp add --transport http context7 https://mcp.context7.com/mcp

# With headers (e.g. API key)
kimi mcp add --transport http context7 https://mcp.context7.com/mcp \
  --header "CONTEXT7_API_KEY: your-key"

# With OAuth
kimi mcp add --transport http --auth oauth linear https://mcp.linear.app/mcp
```

- **Add stdio (local) servers**

```sh
kimi mcp add --transport stdio chrome-devtools -- npx chrome-devtools-mcp@latest
```

- **List / inspect while running**

```sh
kimi mcp list
```

- Inside Kimi: `/mcp` shows connected servers and loaded tools.[^7_2]
- **Remove / auth / test**

```sh
kimi mcp remove context7
kimi mcp auth linear      # opens browser OAuth flow, stores token
kimi mcp test context7    # sanity-check connectivity and tools
```


## MCP config: files and flags

- **Persistent config**
    - Stored at `~/.kimi/mcp.json`, compatible with other MCP clients.[^7_2]
    - Example:

```json
{
  "mcpServers": {
    "context7": {
      "url": "https://mcp.context7.com/mcp",
      "headers": {
        "CONTEXT7_API_KEY": "your-key"
      }
    },
    "chrome-devtools": {
      "command": "npx",
      "args": ["chrome-devtools-mcp@latest"],
      "env": {
        "SOME_VAR": "value"
      }
    }
  }
}
```

- **Temporary / alternate config**

```sh
# Load from another file
kimi --mcp-config-file /path/to/mcp.json

# Inline JSON config
kimi --mcp-config '{"mcpServers": {"test": {"url": "https://..."}}}'
```


## Security, approvals, YOLO

- **Approval model**
    - MCP tools inherit Kimi CLI’s approval system: any operation that can modify files, run commands, or affect external systems prompts for confirmation.[^7_3][^7_2]
    - You choose: Allow once, Allow for this session, or Reject; this applies equally to file tools, shell, and MCP tools.[^7_2]
- **Prompt‑injection risk**
    - MCP tool outputs can contain adversarial instructions; Kimi CLI marks tool output separately so the AI can distinguish it from user messages, but human judgment is still required.[^7_2]
    - Guidance:
        - Only connect to MCP servers from **trusted sources**.
        - Manually check high‑impact operations for sanity before approving.[^7_2]
- **YOLO mode implications**
    - In YOLO mode, MCP tool operations are auto‑approved as well; this removes the human checkpoint.[^7_3][^7_2]
    - Docs recommend YOLO only in controlled/sandboxed environments where you fully trust all configured MCP servers.[^7_2]


## arifOS lens: how to use MCP

- Treat built‑in tools (fs/shell/web) as “local geology,” and MCP servers as external data reservoirs and actuators (APIs, SaaS, infra).[^7_1][^7_2]
- For arifOS, a reasonable policy:
    - MCP on, approvals on by default, Thinking mode on for complex multi‑tool plans;
    - YOLO reserved for disposable environments with whitelisted MCP servers only.[^7_3][^7_1][^7_2]

Uncertainty band: Ω ≈ 0.03–0.05 for commands/flags (`kimi mcp add/list/remove/auth/test`, config layout, inheritance of approvals, YOLO semantics); Estimate Only for internals of how K2 reasons with tool output and the exact prompt‑injection defenses, which can evolve with CLI/model updates.[^7_1][^7_3][^7_2]

<div align="center">⁂</div>

[^7_1]: https://modelcontextprotocol.io

[^7_2]: https://moonshotai.github.io/kimi-cli/en/customization/mcp.html

[^7_3]: https://www.kimi.com/code/docs/en/kimi-cli/guides/interaction.html


---

# Agent Skills

[Agent Skills](https://agentskills.io/) is an open format for adding specialized knowledge and workflows to AI agents. Kimi CLI supports loading Agent Skills to extend AI capabilities.
What are Agent Skills
A skill is a directory containing a SKILL.md file. When Kimi CLI starts, it discovers all skills and injects their names, paths, and descriptions into the system prompt. The AI will decide on its own whether to read the specific SKILL.md file to get detailed guidance based on the current task's needs.
For example, you can create a "code style" skill to tell the AI your project's naming conventions, comment styles, etc.; or create a "security audit" skill to have the AI focus on specific security issues when reviewing code.
Skill discovery
Kimi CLI discovers skills from the following directories:
Built-in skills (shipped with the package)
~/.kimi/skills (user directory)
~/.claude/skills (compatible with Claude's skills)
If a skill with the same name exists in multiple directories, later ones override earlier ones. You can also specify other directories with the --skills-dir flag:
kimi --skills-dir /path/to/my-skills
Built-in skills
Kimi CLI includes the following built-in skills:
kimi-cli-help: Kimi CLI help. Answers questions about Kimi CLI installation, configuration, slash commands, keyboard shortcuts, MCP integration, providers, environment variables, and more.
skill-creator: Guide for creating skills. When you need to create a new skill (or update an existing skill) to extend Kimi's capabilities, you can use this skill to get detailed creation guidance and best practices.
Creating a skill
Creating a skill only requires two steps:
Create a subdirectory in the skills directory
Create a SKILL.md file in the subdirectory
Directory structure
A skill directory needs at least a SKILL.md file, and can also include auxiliary directories to organize more complex content:
~/.kimi/skills/
└── my-skill/
├── SKILL.md          \# Required: main file
├── scripts/          \# Optional: script files
├── references/       \# Optional: reference documents
└── assets/           \# Optional: other resources
SKILL.md format
SKILL.md uses YAML frontmatter to define metadata, followed by prompt content in Markdown format:
---
name: code-style
description: My project's code style guidelines
---

## Code Style

In this project, please follow these conventions:

- Use 4-space indentation
- Variable names use camelCase
- Function names use snake_case
- Every function needs a docstring
- Lines should not exceed 100 characters
Frontmatter fields
FieldDescriptionRequired
name
Skill name, 1-64 characters, only lowercase letters, numbers, and hyphens allowed; defaults to directory name if omitted
No
description
Skill description, 1-1024 characters, explaining the skill's purpose and use cases; shows "No description provided." if omitted
No
license
License name or file reference
No
compatibility
Environment requirements, up to 500 characters
No
metadata
Additional key-value attributes
No
Best practices
Keep SKILL.md under 500 lines, move detailed content to scripts/, references/, or assets/ directories
Use relative paths in SKILL.md to reference other files
Provide clear step-by-step instructions, input/output examples, and edge case explanations
Example skills
PowerPoint creation
---
name: pptx
description: Create and edit PowerPoint presentations
---

## PPT Creation Workflow

When creating presentations, follow these steps:

1. Analyze content structure, plan slide outline
2. Choose appropriate color scheme and fonts
3. Use python-pptx library to generate .pptx files

## Design Principles

- Each slide focuses on one topic
- Keep text concise, use bullet points instead of long paragraphs
- Maintain clear visual hierarchy with distinct titles, body, and notes
- Use consistent colors, avoid more than 3 main colors
Python project standards
---
name: python-project
description: Python project development standards, including code style, testing, and dependency management
---

## Python Development Standards

- Use Python 3.14+
- Use ruff for code formatting and linting
- Use pyright for type checking
- Use pytest for testing
- Use uv for dependency management

Code style:

- Line length limit 100 characters
- Use type annotations
- Public functions need docstrings
Git commit conventions
---
name: git-commits
description: Git commit message conventions using Conventional Commits format
---

## Git Commit Conventions

Use Conventional Commits format:

type(scope): description

Allowed types: feat, fix, docs, style, refactor, test, chore

Examples:

- feat(auth): add OAuth login support
- fix(api): fix user query returning null
- docs(readme): update installation instructions
Using slash commands to load a skill
The /skill:<name> slash command lets you save commonly used prompt templates as skills and quickly invoke them when needed. When you enter the command, Kimi CLI reads the corresponding SKILL.md file content and sends it to the Agent as a prompt.
For example:
/skill:code-style: Load code style guidelines
/skill:pptx: Load PPT creation workflow
/skill:git-commits fix user login issue: Load Git commit conventions with an additional task description
You can append additional text after the slash command, which will be added to the skill prompt as the user's specific request.
TIP
For regular conversations, the Agent will automatically decide whether to read skill content based on context, so you don't need to invoke it manually.
Skills allow you to codify your team's best practices and project standards, ensuring the AI always follows consistent standards.

Agent Skills is a **skills layer** for Kimi CLI: small, versioned SKILL.md bundles that tell the agent how to behave (style, workflows, standards) without hard‑coding it into every prompt.  They’re discovered automatically from a few directories and can also be loaded explicitly with `/skill:<name>`.[^8_1][^8_2]

## What Agent Skills are

- A skill = directory with a `SKILL.md` file (plus optional `scripts/`, `references/`, `assets/`).[^8_2]
- On startup, Kimi CLI scans skill directories and injects each skill’s name/path/description into the system prompt so the AI knows which skills exist and can decide when to open them.[^8_2]
- Typical use:
    - “code-style” skill: naming conventions, comments, line lengths.
    - “security-audit” skill: threat checklist, patterns to look for in reviews.[^8_1][^8_2]


## Skill discovery \& locations

- Discovery order:
    - Built‑in skills (bundled with Kimi CLI).
    - `~/.kimi/skills` (user skills).
    - `~/.claude/skills` (reuses Claude’s skills ecosystem).[^8_2]
- If the same skill name appears multiple places, later locations override earlier ones (user wins over built‑in).[^8_2]
- Extra directories:

```sh
kimi --skills-dir /path/to/my-skills
```

adds another root for discovery.[^8_2]

## Built‑in skills

- `kimi-cli-help`
    - Embedded skill that answers questions about installation, configuration, slash commands, MCP, providers, env vars, etc.[^8_2]
- `skill-creator`
    - Guides you through designing new skills or updating existing ones: structure, examples, edge cases, and best practices.[^8_2]


## Creating a skill

- **Directory layout (minimum)**

```text
~/.kimi/skills/
└── my-skill/
    ├── SKILL.md          # required
    ├── scripts/          # optional
    ├── references/       # optional
    └── assets/           # optional
```

- **SKILL.md format (YAML frontmatter + Markdown)**

```markdown
---
name: code-style
description: My project's code style guidelines
---

## Code Style

In this project, please follow these conventions:

- Use 4-space indentation
- Variable names use camelCase
- Function names use snake_case
- Every function needs a docstring
- Lines should not exceed 100 characters
```

- Frontmatter fields:
    - `name`: 1–64 chars, lowercase letters/numbers/hyphens; default is directory name if omitted.[^8_2]
    - `description`: 1–1024 chars, shown to the model as the skill’s purpose; defaults to “No description provided.” if missing.[^8_2]
    - Optional: `license`, `compatibility`, `metadata` for license text, environment requirements, arbitrary attributes.[^8_2]
- Best practices:
    - Keep `SKILL.md` under 500 lines; move detail into `scripts/`, `references/`, `assets/` and refer via relative paths.[^8_2]
    - Provide clear step‑by‑step instructions, I/O examples, edge‑case handling.[^8_2]


## Example skills

- **PowerPoint creation (`pptx`)**
    - Workflow: analyze content → outline slides → choose colours/fonts → use `python-pptx` to generate `.pptx`.[^8_2]
    - Principles: one topic per slide, concise bullets, consistent colours (≤3 main colours), clear visual hierarchy.[^8_2]
- **Python project standards (`python-project`)**
    - Requirements: Python 3.14+, `ruff` for format/lint, `pyright` for types, `pytest` for tests, `uv` for deps.[^8_2]
    - Style: 100‑char lines, type annotations, docstrings for public functions.[^8_2]
- **Git commit conventions (`git-commits`)**
    - Uses Conventional Commits (`type(scope): description`) with `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`.[^8_2]
    - Example messages included for the AI to imitate.[^8_2]


## Loading skills with slash commands

- Kimi will *automatically* decide when to read skills based on context, so you often don’t need manual loading.[^8_2]
- For explicit control, use `/skill:<name>`:

```text
/skill:code-style                     # load code style guidelines
/skill:pptx                           # load PPT workflow
/skill:git-commits fix user login    # load git-commits + your extra request
```

- Any text after the skill name is appended as the task‑specific user request, so the model sees “skill instructions + your current task” as one combined prompt.[^8_2]


## arifOS lens: why this matters

- Skills = portable, version‑controlled “adat” packets: they encode domain procedures, standards, and governance once, reusable across Kimi CLI and other skills‑compatible agents.[^8_1][^8_2]
- For your stack, that means:
    - arifOS‑style “Basin analysis”, “Petroleum economics”, “Governance / Maruah constraints” can each be a separate skill, switched on per repo or task via `/skill:<name>`.[^8_1][^8_2]
    - Thermodynamically, prompts become thin; **skills** carry the heavy structured knowledge, keeping entropy low and behaviour consistent across agents and sessions.[^8_1][^8_2]

<div align="center">⁂</div>

[^8_1]: https://agentskills.io

[^8_2]: https://moonshotai.github.io/kimi-cli/en/customization/mcp.html


---

# Agents and Subagents

An agent defines the AI's behavior, including system prompts, available tools, and subagents. You can use built-in agents or create custom agents.
Built-in agents
Kimi CLI provides two built-in agents. You can select one at startup with the --agent flag:
kimi --agent okabe
default
The default agent, suitable for general use. Enabled tools:
Task, SetTodoList, Shell, ReadFile, Glob, Grep, WriteFile, StrReplaceFile, SearchWeb, FetchURL
okabe
An experimental agent for testing new prompts and tools. Adds SendDMail on top of default.
Custom agent files
Agents are defined in YAML format. Load a custom agent with the --agent-file flag:
kimi --agent-file /path/to/my-agent.yaml
Basic structure
version: 1
agent:
name: my-agent
system_prompt_path: ./system.md
tools:
- "kimi_cli.tools.shell:Shell"
- "kimi_cli.tools.file:ReadFile"
- "kimi_cli.tools.file:WriteFile"
Inheritance and overrides
Use extend to inherit another agent's configuration and only override what you need to change:
version: 1
agent:
extend: default  \# Inherit from default agent
system_prompt_path: ./my-prompt.md  \# Override system prompt
exclude_tools:  \# Exclude certain tools
- "kimi_cli.tools.web:SearchWeb"
- "kimi_cli.tools.web:FetchURL"
extend: default inherits from the built-in default agent. You can also specify a relative path to inherit from another agent file.
Configuration fields
FieldDescriptionRequired
extend
Agent to inherit from, can be default or a relative path
No
name
Agent name
Yes (optional when inheriting)
system_prompt_path
System prompt file path, relative to agent file
Yes (optional when inheriting)
system_prompt_args
Custom arguments passed to system prompt, merged when inheriting
No
tools
Tool list, format is module:ClassName
Yes (optional when inheriting)
exclude_tools
Tools to exclude
No
subagents
Subagent definitions
No
System prompt built-in parameters
The system prompt file is a Markdown template that can use \${VAR} syntax to reference variables. Built-in variables include:
VariableDescription
\${KIMI_NOW}
Current time (ISO format)
\${KIMI_WORK_DIR}
Working directory path
\${KIMI_WORK_DIR_LS}
Working directory file list
\${KIMI_AGENTS_MD}
AGENTS.md file content (if exists)
${KIMI_SKILLS}
Loaded skills list
You can also define custom parameters via system_prompt_args:
agent:
  system_prompt_args:
    MY_VAR: "custom value"
Then use${MY_VAR} in the prompt.
System prompt example

# My Agent

You are a helpful assistant. Current time: \${KIMI_NOW}.

Working directory: \${KIMI_WORK_DIR}

\${MY_VAR}
Defining subagents in agent files
Subagents can handle specific types of tasks. After defining subagents in an agent file, the main agent can launch them via the Task tool:
version: 1
agent:
extend: default
subagents:
coder:
path: ./coder-sub.yaml
description: "Handle coding tasks"
reviewer:
path: ./reviewer-sub.yaml
description: "Code review expert"
Subagent files are also standard agent format, typically inheriting from the main agent and excluding certain tools:

# coder-sub.yaml

version: 1
agent:
extend: ./agent.yaml  \# Inherit from main agent
system_prompt_args:
ROLE_ADDITIONAL: |
You are now running as a subagent...
exclude_tools:
- "kimi_cli.tools.multiagent:Task"  \# Exclude Task tool to avoid nesting
How subagents run
Subagents launched via the Task tool run in an isolated context and return results to the main agent when complete. Advantages of this approach:
Isolated context, avoiding pollution of main agent's conversation history
Multiple independent tasks can be processed in parallel
Subagents can have targeted system prompts
Dynamic subagent creation
CreateSubagent is an advanced tool that allows AI to dynamically define new subagent types at runtime (not enabled by default). To use it, add to your agent file:
agent:
tools:
- "kimi_cli.tools.multiagent:CreateSubagent"
Built-in tools list
The following are all built-in tools in Kimi CLI.
Task
Path: kimi_cli.tools.multiagent:Task
Description: Dispatch a subagent to execute a task. Subagents cannot access the main agent's context; all necessary information must be provided in the prompt.
ParameterTypeDescription
description
string
Short task description (3-5 words)
subagent_name
string
Subagent name
prompt
string
Detailed task description
SetTodoList
Path: kimi_cli.tools.todo:SetTodoList
Description: Manage todo list, track task progress
ParameterTypeDescription
todos
array
Todo list items
todos[].title
string
Todo item title
todos[].status
string
Status: pending, in_progress, done
Shell
Path: kimi_cli.tools.shell:Shell
Description: Execute shell commands. Requires user approval. Uses the appropriate shell for the OS (bash/zsh on Unix, PowerShell on Windows).
ParameterTypeDescription
command
string
Command to execute
timeout
int
Timeout in seconds, default 60, max 300
ReadFile
Path: kimi_cli.tools.file:ReadFile
Description: Read file content. Supports text, image, and video files. For text files, max 1000 lines per read, max 2000 characters per line; for image/video files, max 80MB. Files outside working directory require absolute paths.
ParameterTypeDescription
path
string
File path
line_offset
int
Starting line number, default 1 (text files only)
n_lines
int
Number of lines to read, default/max 1000 (text files only)
Glob
Path: kimi_cli.tools.file:Glob
Description: Match files and directories by pattern. Returns max 1000 matches, patterns starting with ** not allowed.
ParameterTypeDescription
pattern
string
Glob pattern (e.g., *.py, src/**/*.ts)
directory
string
Search directory, defaults to working directory
include_dirs
bool
Include directories, default true
Grep
Path: kimi_cli.tools.file:Grep
Description: Search file content with regular expressions, based on ripgrep
ParameterTypeDescription
pattern
string
Regular expression pattern
path
string
Search path, defaults to current directory
glob
string
File filter (e.g., *.js)
type
string
File type (e.g., py, js, go)
output_mode
string
Output mode: files_with_matches (default), content, count_matches
-B
int
Show N lines before match
-A
int
Show N lines after match
-C
int
Show N lines before and after match
-n
bool
Show line numbers
-i
bool
Case insensitive
multiline
bool
Enable multiline matching
head_limit
int
Limit output lines
WriteFile
Path: kimi_cli.tools.file:WriteFile
Description: Write files. Can only write to files within working directory, must use absolute paths, requires user approval.
ParameterTypeDescription
path
string
Absolute path
content
string
File content
mode
string
overwrite (default) or append
StrReplaceFile
Path: kimi_cli.tools.file:StrReplaceFile
Description: Edit files using string replacement. Can only edit files within working directory, must use absolute paths, requires user approval.
ParameterTypeDescription
path
string
Absolute path
edit
object/array
Single edit or list of edits
edit.old
string
Original string to replace
edit.new
string
Replacement string
edit.replace_all
bool
Replace all matches, default false
SearchWeb
Path: kimi_cli.tools.web:SearchWeb
Description: Search the web. Requires search service configuration (auto-configured on Kimi Code platform).
ParameterTypeDescription
query
string
Search keywords
limit
int
Number of results, default 5, max 20
include_content
bool
Include page content, default false
FetchURL
Path: kimi_cli.tools.web:FetchURL
Description: Fetch webpage content, returns extracted main text. Uses fetch service if configured, otherwise uses local HTTP request.
ParameterTypeDescription
url
string
URL to fetch
Think
Path: kimi_cli.tools.think:Think
Description: Let the agent record thinking process, suitable for complex reasoning scenarios
ParameterTypeDescription
thought
string
Thinking content
SendDMail
Path: kimi_cli.tools.dmail:SendDMail
Description: Send delayed message (D-Mail), for checkpoint rollback scenarios
ParameterTypeDescription
message
string
Message to send
checkpoint_id
int
Checkpoint ID to send back to (>= 0)
CreateSubagent
Path: kimi_cli.tools.multiagent:CreateSubagent
Description: Dynamically create subagents
ParameterTypeDescription
name
string
Unique name for the subagent, used to reference in Task tool
system_prompt
string
System prompt defining agent's role, capabilities, and boundaries
Tool security boundaries
Working directory restrictions
File writing and editing can only be done within the working directory
Files outside working directory can be read, but require absolute paths
Approval mechanism
The following operations require user approval:
OperationApproval required
Shell command execution
Each execution
File write/edit
Each operation
MCP tool calls
Each call

Agents in Kimi CLI are YAML-defined **personalities** that specify system prompts, tools, and optional subagents; you can use the built-ins (`default`, `okabe`) or define your own with inheritance and tool selection.  Subagents let one agent delegate tasks to specialized children with isolated context, orchestrated via the `Task` and `CreateSubagent` tools.[^9_1][^9_2][^9_3][^9_4]

## Built-in agents

- **`default` agent**
    - General-purpose agent enabled by default; tools: `Task`, `SetTodoList`, `Shell`, `ReadFile`, `Glob`, `Grep`, `WriteFile`, `StrReplaceFile`, `SearchWeb`, `FetchURL`, `Think`.[^9_3][^9_4]
- **`okabe` agent**
    - Experimental variant for new prompts/tools; same as `default` plus `SendDMail` for time-travel checkpoints.[^9_4][^9_1]
    - Select at startup: `kimi --agent okabe`.[^9_4]


## Custom agent files (YAML)

- **Load a custom agent**

```sh
kimi --agent-file /path/to/my-agent.yaml
```

- **Minimal structure**

```yaml
version: 1
agent:
  name: my-agent
  system_prompt_path: ./system.md
  tools:
    - "kimi_cli.tools.shell:Shell"
    - "kimi_cli.tools.file:ReadFile"
    - "kimi_cli.tools.file:WriteFile"
```

- **Inheritance and overrides**

```yaml
version: 1
agent:
  extend: default              # inherit from built-in default
  system_prompt_path: ./my-prompt.md
  exclude_tools:
    - "kimi_cli.tools.web:SearchWeb"
    - "kimi_cli.tools.web:FetchURL"
```

- Key fields:
    - `extend`: `default` or relative path to another agent YAML.[^9_2]
    - `name`: agent name (optional if inheriting).[^9_2]
    - `system_prompt_path`: Markdown system prompt template, relative to the YAML.[^9_2]
    - `system_prompt_args`: extra template variables merged on inherit.[^9_2]
    - `tools`: explicit tool list (`module:ClassName`).[^9_2]
    - `exclude_tools`: tools to remove from inherited set.[^9_2]
    - `subagents`: subagent definitions (see below).[^9_2]


## System prompt templating

- System prompt file is a Markdown template using `${VAR}` placeholders.[^9_2]
- Built-in variables:
    - `${KIMI_NOW}`: current time (ISO).
    - `${KIMI_WORK_DIR}`: working directory.
    - `${KIMI_WORK_DIR_LS}`: directory listing.
    - `${KIMI_AGENTS_MD}`: contents of `AGENTS.md` if present.
    - `${KIMI_SKILLS}`: list of loaded skills.[^9_4][^9_2]
- Custom args via YAML:

```yaml
agent:
  system_prompt_args:
    MY_VAR: "custom value"
```

Use `${MY_VAR}` inside `system.md`.[^9_2]

## Subagents and delegation

- **Defining subagents in main agent**

```yaml
version: 1
agent:
  extend: default
  subagents:
    coder:
      path: ./coder-sub.yaml
      description: "Handle coding tasks"
    reviewer:
      path: ./reviewer-sub.yaml
      description: "Code review expert"
```

- **Subagent file pattern**

```yaml
# coder-sub.yaml
version: 1
agent:
  extend: ./agent.yaml
  system_prompt_args:
    ROLE_ADDITIONAL: |
      You are now running as a subagent...
  exclude_tools:
    - "kimi_cli.tools.multiagent:Task"  # avoid nested delegation
```

- Properties:
    - Subagents inherit prompts/tools from the main agent, but usually **exclude** `Task`, `SendDMail`, and `SetTodoList` to prevent infinite chains and over-orchestration.[^9_3][^9_2]
    - `ROLE_ADDITIONAL` is a common custom arg used to add subagent-specific role text to the system prompt.[^9_2]
- **How subagents run**
    - Launched via `Task` tool; each subagent has its own context/history and cannot access the main agent’s context directly.[^9_1][^9_3]
    - Main agent must pass all required info in the `Task.prompt` field; results are returned when the subagent finishes.[^9_1]
    - Multiple tasks can run in parallel; this is orchestrated by the internal “LaborMarket” subagent manager.[^9_3][^9_1]
- **Dynamic subagent creation**

```yaml
agent:
  tools:
    - "kimi_cli.tools.multiagent:CreateSubagent"
```

allows the model to define new subagent types at runtime by specifying `name` and `system_prompt`.[^9_3][^9_1]

## Built-in tools (capabilities surface)

From the docs, these tools are available for agents to include/exclude:[^9_4][^9_3]


| Tool | Path | Purpose |
| :-- | :-- | :-- |
| Task | `kimi_cli.tools.multiagent:Task` | Dispatch a subagent with `description`, `subagent_name`, `prompt`. |
| SetTodoList | `kimi_cli.tools.todo:SetTodoList` | Manage todo list (`todos[].title`, `todos[].status`). |
| Shell | `kimi_cli.tools.shell:Shell` | Run shell commands with `command`, `timeout` (60 default, 300 max); approval required. |
| ReadFile | `kimi_cli.tools.file:ReadFile` | Read text/image/video; text limited to 1000 lines × 2000 chars; outside work dir needs absolute path. |
| Glob | `kimi_cli.tools.file:Glob` | Glob patterns (no leading `**`); max 1000 matches; can include dirs. |
| Grep | `kimi_cli.tools.file:Grep` | Regex search (ripgrep); filters via `glob`, `type`; supports `-B`, `-A`, `-C`, `-n`, `-i`, `multiline`, `head_limit`, `output_mode`. |
| WriteFile | `kimi_cli.tools.file:WriteFile` | Write files within working dir, absolute paths only, `mode` = `overwrite`/`append`; approval required. |
| StrReplaceFile | `kimi_cli.tools.file:StrReplaceFile` | String-based edits in files in working dir, absolute paths; supports single or list of `edit` objects with `old`, `new`, `replace_all`; approval required. |
| SearchWeb | `kimi_cli.tools.web:SearchWeb` | Web search with `query`, `limit` (default 5, max 20), `include_content`. |
| FetchURL | `kimi_cli.tools.web:FetchURL` | Fetch a URL’s main text content. |
| Think | `kimi_cli.tools.think:Think` | Record explicit “thinking content” for complex reasoning. |
| SendDMail | `kimi_cli.tools.dmail:SendDMail` | Send delayed message to `checkpoint_id` with `message` for time-travel rollback. |
| CreateSubagent | `kimi_cli.tools.multiagent:CreateSubagent` | Define new subagents dynamically by `name` and `system_prompt`. |

[^9_1][^9_3][^9_4]

## Tool security boundaries

- **Working directory rules**
    - File writes/edits only inside the working directory; must use absolute paths for `WriteFile` and `StrReplaceFile`.[^9_3][^9_4]
    - Files outside the working directory can be read, but only with absolute paths.[^9_4]
- **Approval requirements**
    - Each shell command execution requires explicit user approval.[^9_3]
    - Each file write/edit operation requires approval.
    - MCP tool calls also require approval (unless YOLO mode is enabled, in which case all are auto-approved).[^9_5][^9_3]


## arifOS governance view

- Agents = configurable **governance shells**; tools/subagents = actuators and specialised thermodynamic layers.[^9_1][^9_3]
- Reasonable pattern for you:
    - Main agent extending `default` with strict tool set and arifOS system prompt;
    - Subagents for coding, reviews, basin analysis, economics, each with tailored `ROLE_ADDITIONAL` and narrowed tools;
    - No `CreateSubagent` in production agents unless explicitly needed, to bound agent topology.[^9_1][^9_3][^9_2]

Uncertainty band: Ω ≈ 0.03–0.05 for YAML fields, built-in tools, and subagent patterns as described; Estimate Only for internal orchestration details (exact LaborMarket implementation, checkpoint semantics), which may evolve with Kimi CLI releases.[^9_3][^9_1][^9_2]
<span style="display:none">[^9_10][^9_11][^9_12][^9_13][^9_14][^9_15][^9_16][^9_6][^9_7][^9_8][^9_9]</span>

<div align="center">⁂</div>

[^9_1]: https://llmmultiagents.com/en/blogs/kimi-cli-technical-deep-dive

[^9_2]: https://deepwiki.com/MoonshotAI/kimi-cli/5-agent-configuration

[^9_3]: https://deepwiki.com/MoonshotAI/kimi-cli

[^9_4]: https://github.com/MoonshotAI/kimi-cli/blob/main/AGENTS.md

[^9_5]: https://moonshotai.github.io/kimi-cli/en/customization/mcp.html

[^9_6]: https://github.com/MoonshotAI/kimi-cli

[^9_7]: https://www.kimi.com/code/en

[^9_8]: https://www.reddit.com/r/vibecoding/comments/1pov0uw/introducing_kimi_cli_an_opensource_coding_agent/

[^9_9]: https://platform.moonshot.ai/docs/guide/kimi-k2-quickstart

[^9_10]: https://kiro.dev/docs/cli/chat/subagents/

[^9_11]: https://apidog.com/blog/how-to-use-kimi-cli/

[^9_12]: https://kiro.dev/docs/cli/reference/built-in-tools/

[^9_13]: https://platform.moonshot.ai/docs/guide/use-kimi-k2-to-setup-agent

[^9_14]: https://hackmd.io/msiciwuST9mn3sgSPSyENw

[^9_15]: https://www.facebook.com/groups/techtitansgroup/posts/1504101904250456/

[^9_16]: https://moonshotai.github.io/Kimi-K2/


---

# Print Mode

Print mode lets Kimi CLI run non-interactively, suitable for scripting and automation scenarios.
Basic usage
Use the --print flag to enable print mode:

# Pass instructions via -c

kimi --print -c "List all Python files in the current directory"

# Pass instructions via stdin

echo "Explain what this code does" | kimi --print
Print mode characteristics:
Non-interactive: Exits automatically after executing instructions
Auto-approval: Implicitly enables --yolo mode, all operations are auto-approved
Text output: AI responses are output to stdout
Final message only
Use the --final-message-only option to only output the final assistant message, skipping intermediate tool call processes:
kimi --print -c "Give me a Git commit message based on the current changes" --final-message-only
--quiet is a shortcut for --print --output-format text --final-message-only, suitable for scenarios where only the final result is needed:
kimi --quiet -c "Give me a Git commit message based on the current changes"
JSON format
Print mode supports JSON format for input and output, convenient for programmatic processing. Both input and output use the [Message](https://moonshotai.github.io/kimi-cli/en/customization/print-mode.html#message-format) format.
JSON output
Use --output-format=stream-json to output in JSONL (one JSON per line) format:
kimi --print -c "Hello" --output-format=stream-json
Example output:
{"role":"assistant","content":"Hello! How can I help you?"}
If the AI called tools, assistant messages and tool messages are output sequentially:
{"role":"assistant","content":"Let me check the current directory.","tool_calls":[{"type":"function","id":"tc_1","function":{"name":"Shell","arguments":"{\"command\":\"ls\"}"}}]}
{"role":"tool","tool_call_id":"tc_1","content":"file1.py\nfile2.py"}
{"role":"assistant","content":"There are two Python files in the current directory."}
JSON input
Use --input-format=stream-json to receive JSONL format input:
echo '{"role":"user","content":"Hello"}' | kimi --print --input-format=stream-json --output-format=stream-json
In this mode, Kimi CLI continuously reads from stdin, processing and outputting responses for each user message received until stdin is closed.
Message format
Both input and output use a unified message format.
User message
{"role": "user", "content": "Your question or instruction"}
Array-form content is also supported:
{"role": "user", "content": [{"type": "text", "text": "Your question"}]}
Assistant message
{"role": "assistant", "content": "Response content"}
Assistant message with tool calls:
{
"role": "assistant",
"content": "Let me execute this command.",
"tool_calls": [
{
"type": "function",
"id": "tc_1",
"function": {
"name": "Shell",
"arguments": "{\"command\":\"ls\"}"
}
}
]
}
Tool message
{"role": "tool", "tool_call_id": "tc_1", "content": "Tool execution result"}
Use cases
CI/CD integration
Auto-generate code or perform checks in CI workflows:
kimi --print -c "Check if there are any obvious security issues in the src/ directory, output a JSON format report"
Batch processing
Combine with shell loops for batch file processing:
for file in src/*.py; do
kimi --print -c "Add type annotations to \$file"
done
Integration with other tools
Use as a backend for other tools, communicating via JSON format:
my-tool | kimi --print --input-format=stream-json --output-format=stream-json | proces

Print mode turns Kimi CLI into a **non-interactive** command that reads input once, runs the agent, auto-approves actions, prints output, then exits—ideal for scripts, CI, and tool backends.[^10_1][^10_2]

## Core behavior

- Enabled with `--print`; accepts instructions via `-c` or stdin:

```sh
kimi --print -c "List all Python files in the current directory"
echo "Explain what this code does" | kimi --print
```

- Characteristics:
    - Non-interactive: exits after finishing the task.
    - Auto-approval: implicitly enables `--yolo` (all shell/file/MCP ops auto-approved).[^10_2][^10_1]
    - Outputs agent responses to stdout (so you can pipe/redirect).


## Final-message-only and quiet

- **`--final-message-only`**: show only the last assistant message, hide intermediate tool chatter:

```sh
kimi --print -c "Give me a Git commit message based on the current changes" --final-message-only
```

- **`--quiet`**: shorthand for `--print --output-format text --final-message-only`:

```sh
kimi --quiet -c "Give me a Git commit message based on the current changes"
```


Useful when you only care about the final string (e.g., commit hook).

## JSON I/O (Message format)

- **stream-json output**

```sh
kimi --print -c "Hello" --output-format=stream-json
```

Example output (JSONL):

```json
{"role":"assistant","content":"Hello! How can I help you?"}
{"role":"assistant","content":"Let me check the current directory.","tool_calls":[{"type":"function","id":"tc_1","function":{"name":"Shell","arguments":"{\"command\":\"ls\"}"}}]}
{"role":"tool","tool_call_id":"tc_1","content":"file1.py\nfile2.py"}
{"role":"assistant","content":"There are two Python files in the current directory."}
```

- **stream-json input**

```sh
echo '{"role":"user","content":"Hello"}' \
  | kimi --print --input-format=stream-json --output-format=stream-json
```

In this mode Kimi CLI reads JSONL messages from stdin until EOF and outputs responses as JSONL.
- **Message types**:
    - User: `{"role":"user","content":"Your question"}` or array `content` with typed chunks.
    - Assistant: `{"role":"assistant","content":"Response"}` (plus optional `tool_calls`).
    - Tool: `{"role":"tool","tool_call_id":"tc_1","content":"Result"}`.


## Typical use cases

- **CI/CD checks**

```sh
kimi --print -c \
  "Check if there are any obvious security issues in the src/ directory, output a JSON format report"
```

Integrate as a job that emits a machine-readable report.
- **Batch processing**

```sh
for file in src/*.py; do
  kimi --print -c "Add type annotations to $file"
done
```

- **Backend for other tools**

```sh
my-tool \
  | kimi --print --input-format=stream-json --output-format=stream-json \
  | proces
```

(Use your own post-processor instead of `proces` placeholder.)


## arifOS governance note

- Print mode = max convenience, max risk: YOLO is always on, so no approval gates for shell, file writes, or MCP; only use in **controlled sandboxes** or tightly constrained prompts.[^10_1][^10_2]
- For production arifOS flows, pair print mode with:
    - Restricted agent config (limited tools).
    - Narrow working dirs.
    - JSON outputs that your own scripts validate before acting.
<span style="display:none">[^10_10][^10_11][^10_12][^10_13][^10_14][^10_15][^10_3][^10_4][^10_5][^10_6][^10_7][^10_8][^10_9]</span>

<div align="center">⁂</div>

[^10_1]: https://llmmultiagents.com/en/blogs/kimi-cli-technical-deep-dive

[^10_2]: https://joshuaberkowitz.us/blog/github-repos-8/kimi-cli-your-next-command-line-ai-agent-from-moonshot-ai-1593

[^10_3]: https://github.com/MoonshotAI/kimi-cli/blob/main/AGENTS.md

[^10_4]: https://platform.moonshot.ai/docs/guide/use-official-tools

[^10_5]: https://developers.openai.com/codex/noninteractive/

[^10_6]: https://platform.moonshot.ai/docs/guide/use-json-mode-feature-of-kimi-api

[^10_7]: https://apidog.com/blog/how-to-use-kimi-cli/

[^10_8]: https://www.kimi.com/code/docs/en/kimi-cli/guides/interaction.html

[^10_9]: https://platform.moonshot.ai/docs/guide/utilize-the-streaming-output-feature-of-kimi-api

[^10_10]: https://github.com/MoonshotAI/kimi-cli/issues/122

[^10_11]: https://github.com/MoonshotAI/kimi-cli

[^10_12]: https://community.openai.com/t/json-format-causes-infinite-n-n-n-n-in-response/519333

[^10_13]: https://platform.moonshot.ai/docs/guide/use-kimi-k2-to-setup-agent

[^10_14]: https://hackmd.io/msiciwuST9mn3sgSPSyENw

[^10_15]: https://forum.beginner.center/t/topic/2325?tl=en


---

# Config Files

Kimi CLI uses configuration files to manage API providers, models, services, and runtime parameters, supporting both TOML and JSON formats.
Config file location
The default configuration file is located at ~/.kimi/config.toml. On first run, if the configuration file doesn't exist, Kimi CLI will automatically create a default configuration file.
You can specify a different configuration file (TOML or JSON format) with the --config-file flag:
kimi --config-file /path/to/config.toml
When calling Kimi CLI programmatically, you can also pass the complete configuration content directly via the --config flag:
kimi --config '{"default_model": "kimi-for-coding", "providers": {...}, "models": {...}}'
Config items
The configuration file contains the following top-level configuration items:
ItemTypeDescription
default_model
string
Default model name, must be a model defined in models
providers
table
API provider configuration
models
table
Model configuration
loop_control
table
Agent loop control parameters
services
table
External service configuration (search, fetch)
mcp
table
MCP client configuration
Complete configuration example
default_model = "kimi-for-coding"

[providers.kimi-for-coding]
type = "kimi"
base_url = "https://api.kimi.com/coding/v1"
api_key = "sk-xxx"

[models.kimi-for-coding]
provider = "kimi-for-coding"
model = "kimi-for-coding"
max_context_size = 262144

[loop_control]
max_steps_per_turn = 100
max_retries_per_step = 3
max_ralph_iterations = 0

[services.moonshot_search]
base_url = "https://api.kimi.com/coding/v1/search"
api_key = "sk-xxx"

[services.moonshot_fetch]
base_url = "https://api.kimi.com/coding/v1/fetch"
api_key = "sk-xxx"

[mcp.client]
tool_call_timeout_ms = 60000
providers
providers defines API provider connection information. Each provider uses a unique name as key.
FieldTypeRequiredDescription
type
string
Yes
Provider type, see [Providers](https://moonshotai.github.io/kimi-cli/en/configuration/providers.html) for details
base_url
string
Yes
API base URL
api_key
string
Yes
API key
env
table
No
Environment variables to set before creating provider instance
custom_headers
table
No
Custom HTTP headers to attach to requests
Example:
[providers.moonshot-cn]
type = "kimi"
base_url = "https://api.moonshot.cn/v1"
api_key = "sk-xxx"
custom_headers = { "X-Custom-Header" = "value" }
models
models defines available models. Each model uses a unique name as key.
FieldTypeRequiredDescription
provider
string
Yes
Provider name to use, must be defined in providers
model
string
Yes
Model identifier (model name used in API)
max_context_size
integer
Yes
Maximum context length (in tokens)
capabilities
array
No
Model capability list, see [Providers](https://moonshotai.github.io/kimi-cli/en/configuration/providers.html#model-capabilities) for details
Example:
[models.kimi-k2-thinking-turbo]
provider = "moonshot-cn"
model = "kimi-k2-thinking-turbo"
max_context_size = 262144
capabilities = ["thinking", "image_in"]
loop_control
loop_control controls agent execution loop behavior.
FieldTypeDefaultDescription
max_steps_per_turn
integer
100
Maximum steps per turn (alias: max_steps_per_run)
max_retries_per_step
integer
3
Maximum retries per step
max_ralph_iterations
integer
0
Extra iterations after each user message; 0 disables; -1 is unlimited
services
services configures external services used by Kimi CLI.
moonshot_search
Configures web search service. When enabled, the SearchWeb tool becomes available.
FieldTypeRequiredDescription
base_url
string
Yes
Search service API URL
api_key
string
Yes
API key
custom_headers
table
No
Custom HTTP headers to attach to requests
moonshot_fetch
Configures web fetch service. When enabled, the FetchURL tool prioritizes using this service to fetch webpage content.
FieldTypeRequiredDescription
base_url
string
Yes
Fetch service API URL
api_key
string
Yes
API key
custom_headers
table
No
Custom HTTP headers to attach to requests
TIP
When configuring the Kimi Code platform using the /setup command, search and fetch services are automatically configured.
mcp
mcp configures MCP client behavior.
FieldTypeDefaultDescription
client.tool_call_timeout_ms
integer
60000
MCP tool call timeout (milliseconds)
JSON configuration migration
If ~/.kimi/config.toml doesn't exist but ~/.kimi/config.json exists, Kimi CLI will automatically migrate the JSON configuration to TOML format and backup the original file as config.json.bak.
Configuration files specified via --config-file are parsed based on file extension. Configuration content passed via --config is first attempted as JSON, then falls back to TOML if that fails.
Pager

Kimi CLI config is the **control plane** for providers, models, tools, and loop behavior, stored by default at `~/.kimi/config.toml` and overridable per run.  It supports TOML or JSON, plus inline `--config` for fully programmatic setups.[^11_1]

## Where config lives and how to load it

- Default file: `~/.kimi/config.toml`. If missing on first run, Kimi CLI auto-creates a default config.[^11_1]
- Override file (TOML or JSON):

```sh
kimi --config-file /path/to/config.toml
```

- Inline config content (useful for CI, scripts):

```sh
kimi --config '{
  "default_model": "kimi-for-coding",
  "providers": {...},
  "models": {...}
}'
```

JSON is tried first; if parsing fails, it falls back to TOML.[^11_1]
- Migration: if `~/.kimi/config.toml` doesn’t exist but `~/.kimi/config.json` does, Kimi CLI migrates JSON → TOML and keeps `config.json.bak`.[^11_1]


## Top-level items

Supported top-level keys:[^11_1]

- `default_model` (string): name of the default model; must match a key in `models`.
- `providers` (table): API provider definitions (base URLs, keys, headers).
- `models` (table): logical model names mapping to providers, model IDs, capabilities.
- `loop_control` (table): agent loop behavior (step limits, retries, Ralph iterations).
- `services` (table): external services (search, fetch) used by tools.
- `mcp` (table): MCP client behavior (timeouts).

Example skeleton:

```toml
default_model = "kimi-for-coding"

[providers.kimi-for-coding]
type = "kimi"
base_url = "https://api.kimi.com/coding/v1"
api_key = "sk-xxx"

[models.kimi-for-coding]
provider = "kimi-for-coding"
model = "kimi-for-coding"
max_context_size = 262144

[loop_control]
max_steps_per_turn = 100
max_retries_per_step = 3
max_ralph_iterations = 0

[services.moonshot_search]
base_url = "https://api.kimi.com/coding/v1/search"
api_key  = "sk-xxx"

[services.moonshot_fetch]
base_url = "https://api.kimi.com/coding/v1/fetch"
api_key  = "sk-xxx"

[mcp.client]
tool_call_timeout_ms = 60000
```


## Providers and models

### Providers

Each provider entry describes how to talk to one API.[^11_1]

- Required fields:
    - `type`: provider type (e.g. `"kimi"`); behavior explained in Providers docs.
    - `base_url`: API base URL.
    - `api_key`: key/token.
- Optional:
    - `env`: env vars to set before creating the provider instance.
    - `custom_headers`: extra HTTP headers.

Example:

```toml
[providers.moonshot-cn]
type = "kimi"
base_url = "https://api.moonshot.cn/v1"
api_key = "sk-xxx"
custom_headers = { "X-Custom-Header" = "value" }
```


### Models

Each model entry is a logical model name used by Kimi CLI.[^11_1]

- Required:
    - `provider`: provider name from `providers`.
    - `model`: model identifier for the provider API.
    - `max_context_size`: max context (tokens).
- Optional:
    - `capabilities`: list like `["thinking", "image_in"]`, used to gate features like Thinking mode or image input.

Example:

```toml
[models.kimi-k2-thinking-turbo]
provider = "moonshot-cn"
model = "kimi-k2-thinking-turbo"
max_context_size = 262144
capabilities = ["thinking", "image_in"]
```


## Loop control and services

### loop_control

Controls how “aggressive” the agent is per turn.[^11_1]

- `max_steps_per_turn` (alias `max_steps_per_run`, default 100): hard cap on internal tool/reasoning steps per user turn.
- `max_retries_per_step` (default 3): retries when a step/tool fails.
- `max_ralph_iterations` (default 0): extra planner iterations after each user message; `0` disables, `-1` = unlimited.


### services

Controls external services powering `SearchWeb` and `FetchURL`.[^11_1]

- `services.moonshot_search`
    - Enables `SearchWeb` tool when set.
    - Required: `base_url`, `api_key`.
    - Optional: `custom_headers`.
- `services.moonshot_fetch`
    - When set, `FetchURL` prefers this fetch service instead of raw HTTP.
    - Same fields as search.

Config is auto-populated when you run `/setup` against the Kimi Code platform.[^11_1]

## MCP client

- `mcp.client.tool_call_timeout_ms`: default 60000; sets how long to wait for each MCP tool call.[^11_2][^11_1]


## arifOS view (how to actually use this)

- Treat `providers` + `models` as your **thermodynamic boundary**:
    - One provider for Kimi Code membership, another for Moonshot enterprise K2.
    - Separate model keys for “thinking-turbo” vs cheaper batch models, with explicit `capabilities`.[^11_3][^11_1]
- Use `loop_control` to bound agent wander: lower `max_steps_per_turn` for CI and print mode; higher for interactive deep refactors.[^11_4][^11_5]
- For security, keep `services.moonshot_search/fetch` limited to trusted endpoints and pair with MCP timeouts in `mcp.client` when adding external servers.[^11_2][^11_1]

Uncertainty band: Ω ≈ 0.03–0.05 for key names, defaults, and example structure; Estimate Only for future provider types or additional config keys that may appear in newer Kimi CLI releases.[^11_6][^11_2][^11_1]

<div align="center">⁂</div>

[^11_1]: https://github.com/MoonshotAI/kimi-cli

[^11_2]: https://moonshotai.github.io/kimi-cli/en/customization/mcp.html

[^11_3]: https://platform.moonshot.ai/docs/guide/use-kimi-k2-to-setup-agent

[^11_4]: https://llmmultiagents.com/en/blogs/kimi-cli-technical-deep-dive

[^11_5]: https://joshuaberkowitz.us/blog/github-repos-8/kimi-cli-your-next-command-line-ai-agent-from-moonshot-ai-1593

[^11_6]: https://github.com/MoonshotAI/kimi-cli/blob/main/AGENTS.md


---

# Providers and Models

Kimi CLI supports multiple LLM platforms, which can be configured via configuration files or the /setup command.
Platform selection
The easiest way to configure is to run the /setup command in shell mode and follow the wizard to select platform and model:
Select an API platform
Enter your API key
Select a model from the available list
After configuration, Kimi CLI will automatically save settings to ~/.kimi/config.toml and reload.
/setup currently supports the following platforms:
PlatformDescription
Kimi Code
Kimi Code platform, supports search and fetch services
Moonshot AI Open Platform (moonshot.cn)
China region API endpoint
Moonshot AI Open Platform (moonshot.ai)
Global region API endpoint
For other platforms, please manually edit the configuration file.
Provider types
The type field in providers configuration specifies the API provider type. Different types use different API protocols and client implementations.
TypeDescription
kimi
Kimi API
openai_legacy
OpenAI Chat Completions API
openai_responses
OpenAI Responses API
anthropic
Anthropic Claude API
gemini
Google Gemini API
vertexai
Google Vertex AI
kimi
For connecting to Kimi API, including Kimi Code and Moonshot AI Open Platform.
[providers.kimi-for-coding]
type = "kimi"
base_url = "https://api.kimi.com/coding/v1"
api_key = "sk-xxx"
openai_legacy
For platforms compatible with OpenAI Chat Completions API, including the official OpenAI API and various compatible services.
[providers.openai]
type = "openai_legacy"
base_url = "https://api.openai.com/v1"
api_key = "sk-xxx"
openai_responses
For OpenAI Responses API (newer API format).
[providers.openai-responses]
type = "openai_responses"
base_url = "https://api.openai.com/v1"
api_key = "sk-xxx"
anthropic
For connecting to Anthropic Claude API.
[providers.anthropic]
type = "anthropic"
base_url = "https://api.anthropic.com"
api_key = "sk-ant-xxx"
gemini
For connecting to Google Gemini API.
[providers.gemini]
type = "gemini"
base_url = "https://generativelanguage.googleapis.com"
api_key = "xxx"
vertexai
For connecting to Google Vertex AI. Requires setting necessary environment variables via the env field.
[providers.vertexai]
type = "vertexai"
base_url = "https://xxx-aiplatform.googleapis.com"
api_key = ""
env = { GOOGLE_CLOUD_PROJECT = "your-project-id" }
Model capabilities
The capabilities field in model configuration declares the capabilities supported by the model. This affects feature availability in Kimi CLI.
CapabilityDescription
thinking
Supports thinking mode (deep reasoning)
image_in
Supports image input
video_in
Supports video input
[models.gemini-3-pro-preview]
provider = "gemini"
model = "gemini-3-pro-preview"
max_context_size = 262144
capabilities = ["thinking", "image_in"]
thinking
When thinking mode is enabled, the model performs deeper reasoning before answering, suitable for complex problems. In shell mode, you can toggle thinking mode with the Tab key, or control it at startup with --thinking / --no-thinking flags.
image_in
When image input capability is enabled, you can paste images in conversations (Ctrl-V).
video_in
When video input capability is enabled, you can send video content in conversations.
Search and fetch services
The SearchWeb and FetchURL tools depend on external services, currently only provided by the Kimi Code platform.
When selecting the Kimi Code platform using /setup, search and fetch services are automatically configured.
ServiceCorresponding toolBehavior when not configured
moonshot_search
SearchWeb
Tool unavailable
moonshot_fetch
FetchURL
Falls back to local fetching
When using other platforms, the FetchURL tool is still available but will fall back to local fetching.

Providers and models let Kimi CLI talk to **multiple LLM backends** (Kimi, OpenAI, Claude, Gemini, Vertex) while exposing a unified tool/agent surface.  Capabilities flags (`thinking`, `image_in`, `video_in`) then gate features like Thinking mode and multimodal input.[^12_1][^12_2][^12_3]

## Platform setup and `/setup` wizard

- In shell mode, `/setup` runs a wizard:
    - Choose API platform → enter API key → choose model.[^12_1]
    - Result is saved to `~/.kimi/config.toml` and applied immediately.[^12_1]
- Supported platforms in the wizard:
    - **Kimi Code** (coding plan, search + fetch services).
    - **Moonshot AI Open Platform (moonshot.cn)** – China endpoint.
    - **Moonshot AI Open Platform (moonshot.ai)** – global endpoint.[^12_4][^12_1]
- Other providers (OpenAI, Anthropic, Gemini, Vertex) must be added manually in the config file.[^12_2][^12_1]


## Provider types (`providers.*`)

Each provider entry has a `type` that selects the client implementation.[^12_1]

- **`kimi`** – Kimi API (Kimi Code + Moonshot Open Platform).

```toml
[providers.kimi-for-coding]
type     = "kimi"
base_url = "https://api.kimi.com/coding/v1"
api_key  = "sk-xxx"
```

- **`openai_legacy`** – OpenAI Chat Completions–compatible APIs.

```toml
[providers.openai]
type     = "openai_legacy"
base_url = "https://api.openai.com/v1"
api_key  = "sk-xxx"
```

- **`openai_responses`** – OpenAI Responses API.

```toml
[providers.openai-responses]
type     = "openai_responses"
base_url = "https://api.openai.com/v1"
api_key  = "sk-xxx"
```

- **`anthropic`** – Anthropic Claude API.

```toml
[providers.anthropic]
type     = "anthropic"
base_url = "https://api.anthropic.com"
api_key  = "sk-ant-xxx"
```

- **`gemini`** – Google Gemini API.

```toml
[providers.gemini]
type     = "gemini"
base_url = "https://generativelanguage.googleapis.com"
api_key  = "xxx"
```

- **`vertexai`** – Google Vertex AI; uses `env` for project config.

```toml
[providers.vertexai]
type     = "vertexai"
base_url = "https://xxx-aiplatform.googleapis.com"
api_key  = ""
env = { GOOGLE_CLOUD_PROJECT = "your-project-id" }
```


[^12_1]

## Models and capabilities (`models.*`)

Each model entry binds a logical name to a provider + underlying model ID + capabilities.[^12_1]

- Required fields:
    - `provider`: name from `providers`.
    - `model`: API model identifier.
    - `max_context_size`: max tokens for context.
- Optional:
    - `capabilities`: feature list controlling Kimi CLI’s options.

Example with capabilities:

```toml
[models.gemini-3-pro-preview]
provider         = "gemini"
model            = "gemini-3-pro-preview"
max_context_size = 262144
capabilities     = ["thinking", "image_in"]
```


### Capability flags

- **`thinking`**
    - Enables Thinking mode (deeper reasoning).[^12_3][^12_5]
    - Toggled in agent mode with Tab, or at startup with `--thinking` / `--no-thinking`.[^12_5]
- **`image_in`**
    - Allows image input; paste images with Ctrl‑V and the model can see attachments.[^12_3][^12_5]
- **`video_in`**
    - Enables video input support; model can process video content.[^12_3]

If a model lacks these capabilities, related features are disabled in Kimi CLI for that model.[^12_3][^12_1]

## Search and fetch services (SearchWeb / FetchURL)

Search/fetch tools are decoupled from providers and wired via `services`.[^12_1]

- **`moonshot_search`** → `SearchWeb` tool:
    - When configured, `SearchWeb` becomes available.
    - If not configured, `SearchWeb` is unavailable.[^12_1]
- **`moonshot_fetch`** → `FetchURL` tool:
    - When configured, `FetchURL` uses the Moonshot fetch service.
    - When not, `FetchURL` falls back to local HTTP fetching.[^12_3][^12_1]

Selecting the Kimi Code platform via `/setup` auto-configures both `moonshot_search` and `moonshot_fetch`.[^12_1]

## arifOS integration angle

- Use multiple providers in one config:
    - `kimi-for-coding` for interactive coding.
    - `moonshot-cn` / `moonshot-global` for long-context K2.
    - `openai-responses`, `anthropic`, `gemini`, `vertexai` as alternate engines for cross-checking or specialised tasks.[^12_4][^12_1]
- Encode model roles via `capabilities` + agent files:
    - “Deep basin reasoning” models with `thinking` only.
    - “Geoimage analysis” models with `image_in`.[^12_6][^12_3][^12_1]
- Keep Kimi Code `/setup` for convenience, then hand-edit `providers`/`models` to align with arifOS governance (quotas, data locality, allowed tools).[^12_7][^12_1]

<div align="center">⁂</div>

[^12_1]: https://github.com/MoonshotAI/kimi-cli

[^12_2]: https://deepwiki.com/MoonshotAI/kimi-cli/5-agent-configuration

[^12_3]: https://moonshotai.github.io/kimi-cli/en/customization/mcp.html

[^12_4]: https://platform.moonshot.ai/docs/guide/use-kimi-k2-to-setup-agent

[^12_5]: https://www.kimi.com/code/docs/en/kimi-cli/guides/interaction.html

[^12_6]: https://moonshotai.github.io/Kimi-K2/

[^12_7]: https://llmmultiagents.com/en/blogs/kimi-cli-technical-deep-dive


---

# Config Overrides

Kimi CLI configuration can be set through multiple methods, with different sources overriding each other by priority.
Priority
Configuration priority from highest to lowest:
Environment variables - Highest priority, for temporary overrides or CI/CD environments
CLI flags - Flags specified at startup
Configuration file - ~/.kimi/config.toml or file specified via --config-file
CLI flags
Configuration file related
FlagDescription
--config <TOML/JSON>
Pass configuration content directly, overrides default config file
--config-file <PATH>
Specify configuration file path, replaces default ~/.kimi/config.toml
--config and --config-file cannot be used together.
Model related
FlagDescription
--model, -m <NAME>
Specify model name to use
The model specified by --model must be defined in the configuration file's models. If not specified, uses default_model from the configuration file.
Behavior related
FlagDescription
--thinking
Enable thinking mode
--no-thinking
Disable thinking mode
--yolo, --yes, -y
Auto-approve all operations
--thinking / --no-thinking overrides the thinking state saved from the last session. If not specified, uses the last session's state.
Environment variable overrides
Environment variables can override provider and model settings without modifying the configuration file. This is particularly useful in the following scenarios:
Injecting keys in CI/CD environments
Temporarily testing different API endpoints
Switching between multiple environments
Environment variables take effect based on the current provider type:
kimi type providers: Use KIMI_* environment variables
openai_legacy or openai_responses type providers: Use OPENAI_* environment variables
Other provider types: Environment variable overrides not supported
See [Environment Variables](https://moonshotai.github.io/kimi-cli/en/configuration/env-vars.html) for the complete list.
Example:
KIMI_API_KEY="sk-xxx" KIMI_MODEL_NAME="kimi-k2-thinking-turbo" kimi
Configuration priority example
Assume the configuration file ~/.kimi/config.toml contains:
default_model = "kimi-for-coding"

[providers.kimi-for-coding]
type = "kimi"
base_url = "https://api.kimi.com/coding/v1"
api_key = "sk-config"

[models.kimi-for-coding]
provider = "kimi-for-coding"
model = "kimi-for-coding"
max_context_size = 262144
Here are the configuration sources in different scenarios:
Scenariobase_urlapi_keymodel
kimi
Config file
Config file
Config file
KIMI_API_KEY=sk-env kimi
Config file
Environment variable
Config file
kimi --model other
Config file
Config file
CLI flag
KIMI_MODEL_NAME=k2 kimi
Config file
Config file
Environment variable

Config overrides in Kimi CLI follow a clear precedence: **env vars > CLI flags > config file**.  This lets you keep a stable base config while swapping keys, endpoints, or models per environment or run.[^13_1][^13_2][^13_3][^13_4]

## Priority order

From highest to lowest priority:[^13_4][^13_1]

1. **Environment variables** – best for CI/CD and temporary overrides.
2. **CLI flags** – per-invocation behavior changes.
3. **Configuration file** – `~/.kimi/config.toml` or file from `--config-file`.

`--config` and `--config-file` are mutually exclusive; you can use only one.[^13_4]

## Relevant CLI flags

### Config-related

- `--config <TOML/JSON>`
    - Inline config content; completely overrides the default config file.[^13_4]
- `--config-file <PATH>`
    - Use a specific config file (TOML or JSON) instead of `~/.kimi/config.toml`.[^13_4]


### Model-related

- `--model, -m <NAME>`
    - Choose a model key defined under `models` in config.[^13_4]
    - If omitted, Kimi CLI uses `default_model` from the config.[^13_4]


### Behavior-related

- `--thinking` / `--no-thinking`
    - Enable or disable Thinking mode explicitly.[^13_5]
    - Overrides whatever thinking state was stored from the last session; if neither is given, last session’s state is reused.[^13_5]
- `--yolo`, `--yes`, `-y`
    - Enable YOLO mode (auto-approve all operations).[^13_6][^13_5]


## Environment variable overrides

Env vars can override certain provider/model details without touching config files, mainly for `kimi` and `openai_*` providers.[^13_1][^13_4]

- For `type = "kimi"` providers: use `KIMI_*` variables.
- For `type = "openai_legacy"` or `type = "openai_responses"`: use `OPENAI_*` variables.
- Other provider types currently do not support env overrides.[^13_2][^13_4]

Example:

```sh
KIMI_API_KEY="sk-xxx" KIMI_MODEL_NAME="kimi-k2-thinking-turbo" kimi
```

This leaves `base_url` and provider wiring from config but swaps key and model name from the environment.[^13_1][^13_4]

## Priority example (from docs)

Given config:

```toml
default_model = "kimi-for-coding"

[providers.kimi-for-coding]
type     = "kimi"
base_url = "https://api.kimi.com/coding/v1"
api_key  = "sk-config"

[models.kimi-for-coding]
provider         = "kimi-for-coding"
model            = "kimi-for-coding"
max_context_size = 262144
```

Behavior in different scenarios:


| Scenario | base_url | api_key | model |
| :-- | :-- | :-- | :-- |
| `kimi` | Config file | Config file | Config file (`default_model`) |
| `KIMI_API_KEY=sk-env kimi` | Config file | Env var (`sk-env`) | Config file |
| `kimi --model other` | Config file | Config file | CLI flag (`other`) |
| `KIMI_MODEL_NAME=k2 kimi` | Config file | Config file | Env var (`k2`) |

[^13_1][^13_4]

## arifOS usage pattern

- Keep a **baseline** `config.toml` with your standard providers + models.[^13_4]
- Use env vars (`KIMI_API_KEY`, `KIMI_MODEL_NAME`, `OPENAI_API_KEY`, etc.) for secrets and environment-specific endpoints (dev/stage/prod).[^13_7][^13_3]
- Use `--model`, `--thinking`, `--yolo` only when a specific run needs different reasoning depth or approval behavior, knowing they override stored session state and file defaults.[^13_8][^13_5]
<span style="display:none">[^13_10][^13_11][^13_12][^13_13][^13_14][^13_15][^13_16][^13_17][^13_18][^13_9]</span>

<div align="center">⁂</div>

[^13_1]: https://github.com/MoonshotAI/kimi-cli/issues/87

[^13_2]: https://docs.lazyllm.ai/en/stable/API Reference/configs/

[^13_3]: https://skywork.ai/blog/agent/kimi-cli-guide-2025-setup-commands-automation/

[^13_4]: https://github.com/MoonshotAI/kimi-cli

[^13_5]: https://www.kimi.com/code/docs/en/kimi-cli/guides/interaction.html

[^13_6]: https://moonshotai.github.io/kimi-cli/en/customization/mcp.html

[^13_7]: https://platform.moonshot.ai/docs/guide/agent-support

[^13_8]: https://llmmultiagents.com/en/blogs/kimi-cli-technical-deep-dive

[^13_9]: https://github.com/kaichen/kimicc/blob/main/Agents.md

[^13_10]: https://deepeval.com/docs/command-line-interface

[^13_11]: https://geminicli.com/docs/get-started/configuration/

[^13_12]: https://kiro.dev/docs/cli/mcp/configuration/

[^13_13]: https://www.kimi.com/code/docs/kimi-cli/guides/interaction.html

[^13_14]: https://www.reddit.com/r/ClaudeAI/comments/1m1hf9m/claude_code_kimi_k2_with_just_2_env_vars/

[^13_15]: https://apidog.com/blog/how-to-use-kimi-cli/

[^13_16]: https://unsloth.ai/docs/models/kimi-k2-thinking-how-to-run-locally

[^13_17]: https://www.reddit.com/r/vibecoding/comments/1pov0uw/introducing_kimi_cli_an_opensource_coding_agent/

[^13_18]: https://huggingface.co/moonshotai/Kimi-K2-Thinking


---

# Kimi environment variables

The following environment variables take effect when using kimi type providers, used to override provider and model configuration.
Environment VariableDescription
KIMI_BASE_URL
API base URL
KIMI_API_KEY
API key
KIMI_MODEL_NAME
Model identifier
KIMI_MODEL_MAX_CONTEXT_SIZE
Maximum context length (in tokens)
KIMI_MODEL_CAPABILITIES
Model capabilities, comma-separated (e.g., thinking,image_in)
KIMI_MODEL_TEMPERATURE
Generation parameter temperature
KIMI_MODEL_TOP_P
Generation parameter top_p
KIMI_MODEL_MAX_TOKENS
Generation parameter max_tokens
KIMI_BASE_URL
Overrides the provider's base_url field in the configuration file.
export KIMI_BASE_URL="https://api.moonshot.cn/v1"
KIMI_API_KEY
Overrides the provider's api_key field in the configuration file. Used to inject API keys without modifying the configuration file, suitable for CI/CD environments.
export KIMI_API_KEY="sk-xxx"
KIMI_MODEL_NAME
Overrides the model's model field in the configuration file (the model identifier used in API calls).
export KIMI_MODEL_NAME="kimi-k2-thinking-turbo"
KIMI_MODEL_MAX_CONTEXT_SIZE
Overrides the model's max_context_size field in the configuration file. Must be a positive integer.
export KIMI_MODEL_MAX_CONTEXT_SIZE="262144"
KIMI_MODEL_CAPABILITIES
Overrides the model's capabilities field in the configuration file. Multiple capabilities are comma-separated, supported values are thinking, image_in, and video_in.
export KIMI_MODEL_CAPABILITIES="thinking,image_in"
KIMI_MODEL_TEMPERATURE
Sets the generation parameter temperature, controlling output randomness. Higher values produce more random output, lower values produce more deterministic output.
export KIMI_MODEL_TEMPERATURE="0.7"
KIMI_MODEL_TOP_P
Sets the generation parameter top_p (nucleus sampling), controlling output diversity.
export KIMI_MODEL_TOP_P="0.9"
KIMI_MODEL_MAX_TOKENS
Sets the generation parameter max_tokens, limiting the maximum tokens per response.
export KIMI_MODEL_MAX_TOKENS="4096"
OpenAI-compatible environment variables
The following environment variables take effect when using openai_legacy or openai_responses type providers.
Environment VariableDescription
OPENAI_BASE_URL
API base URL
OPENAI_API_KEY
API key
OPENAI_BASE_URL
Overrides the provider's base_url field in the configuration file.
export OPENAI_BASE_URL="https://api.openai.com/v1"
OPENAI_API_KEY
Overrides the provider's api_key field in the configuration file.
export OPENAI_API_KEY="sk-xxx"
Other environment variables
Environment VariableDescription
KIMI_CLI_NO_AUTO_UPDATE
Disable automatic update check
KIMI_CLI_NO_AUTO_UPDATE
When set to 1, true, t, yes, or y (case-insensitive), disables background auto-update check in shell mode.
export KIMI_CLI_NO_AUTO_UPDATE="1"
TIP
If you installed Kimi CLI via Nix or other package managers, this environment variable is typically set automatically since updates are handled by the package manager.

Kimi CLI lets you override **kimi/OpenAI providers and models** via env vars, plus one flag to disable auto-update checks.  This is the highest-priority layer in the config stack, ideal for CI and per-shell setup.[^14_1][^14_2][^14_3][^14_4]

## Env vars for `type = "kimi"`

These apply when the active provider is of type `kimi`.[^14_2][^14_1]

- **Connection / identity**
    - `KIMI_BASE_URL` – overrides provider `base_url`.
        - Example: `export KIMI_BASE_URL="https://api.moonshot.cn/v1"`
    - `KIMI_API_KEY` – overrides provider `api_key`; good for secrets in CI.
        - Example: `export KIMI_API_KEY="sk-xxx"`
- **Model descriptor**
    - `KIMI_MODEL_NAME` – overrides model `model` (API model ID).
        - `export KIMI_MODEL_NAME="kimi-k2-thinking-turbo"`
    - `KIMI_MODEL_MAX_CONTEXT_SIZE` – overrides `max_context_size` (tokens), positive integer.
        - `export KIMI_MODEL_MAX_CONTEXT_SIZE="262144"`
    - `KIMI_MODEL_CAPABILITIES` – overrides `capabilities`, comma-separated; allowed values: `thinking`, `image_in`, `video_in`.
        - `export KIMI_MODEL_CAPABILITIES="thinking,image_in"`
- **Generation parameters**
    - `KIMI_MODEL_TEMPERATURE` – sets sampling temperature (0–1-ish; higher = more random).
        - `export KIMI_MODEL_TEMPERATURE="0.7"`
    - `KIMI_MODEL_TOP_P` – sets `top_p` (nucleus sampling).
        - `export KIMI_MODEL_TOP_P="0.9"`
    - `KIMI_MODEL_MAX_TOKENS` – per-response `max_tokens` limit.
        - `export KIMI_MODEL_MAX_TOKENS="4096"`

These override config-file values for whichever `kimi` provider/model is in use, without touching `config.toml`.[^14_1][^14_2]

## Env vars for OpenAI-compatible providers

These apply when provider `type` is `openai_legacy` or `openai_responses`.[^14_1]

- `OPENAI_BASE_URL` – overrides `base_url`.
    - `export OPENAI_BASE_URL="https://api.openai.com/v1"`
- `OPENAI_API_KEY` – overrides `api_key`.
    - `export OPENAI_API_KEY="sk-xxx"`

Other provider types (Anthropic, Gemini, Vertex) do not use these overrides.[^14_4][^14_1]

## Other Kimi CLI env vars

- **`KIMI_CLI_NO_AUTO_UPDATE`**
    - When set to `1`, `true`, `t`, `yes`, or `y` (case-insensitive), disables background auto-update checks in shell mode.[^14_1]
    - Example: `export KIMI_CLI_NO_AUTO_UPDATE="1"`
    - Often set automatically when installing via Nix or similar package managers, since updates are handled externally.[^14_1]


## arifOS usage pattern

- Use env vars to:
    - Swap between Kimi Code and Moonshot CN/global (`KIMI_BASE_URL`, `KIMI_API_KEY`).
    - Switch reasoning mode or multimodality per shell (`KIMI_MODEL_NAME`, `KIMI_MODEL_CAPABILITIES`).
    - Harden CI runs by clamping `KIMI_MODEL_MAX_TOKENS`, `KIMI_MODEL_TEMPERATURE`, and disabling auto-update (`KIMI_CLI_NO_AUTO_UPDATE`).[^14_3][^14_2][^14_1]

<div align="center">⁂</div>

[^14_1]: https://github.com/MoonshotAI/kimi-cli

[^14_2]: https://github.com/MoonshotAI/kimi-cli/issues/87

[^14_3]: https://skywork.ai/blog/agent/kimi-cli-guide-2025-setup-commands-automation/

[^14_4]: https://docs.lazyllm.ai/en/stable/API Reference/configs/


---

# Data Locations

Kimi CLI stores all data in the ~/.kimi/ directory under the user's home directory. This page describes the locations and purposes of various data files.
Directory structure
~/.kimi/
├── config.toml           \# Main configuration file
├── kimi.json             \# Metadata
├── mcp.json              \# MCP server configuration
├── sessions/             \# Session data
│   └── <work-dir-hash>/
│       └── <session-id>/
│           ├── context.jsonl
│           └── wire.jsonl
├── user-history/         \# Input history
│   └── <work-dir-hash>.jsonl
└── logs/                 \# Logs
└── kimi.log
Configuration and metadata
config.toml
Main configuration file, stores providers, models, services, and runtime parameters. See [Config Files](https://moonshotai.github.io/kimi-cli/en/configuration/config-files.html) for details.
You can specify a configuration file at a different location with the --config-file flag.
kimi.json
Metadata file, stores Kimi CLI's runtime state, including:
work_dirs: List of working directories and their last used session IDs
thinking: Whether thinking mode was enabled in the last session
This file is automatically managed by Kimi CLI and typically doesn't need manual editing.
mcp.json
MCP server configuration file, stores MCP servers added via the kimi mcp add command. See [MCP](https://moonshotai.github.io/kimi-cli/en/customization/mcp.html) for details.
Example structure:
{
"mcpServers": {
"context7": {
"url": "https://mcp.context7.com/mcp",
"transport": "http",
"headers": {
"CONTEXT7_API_KEY": "ctx7sk-xxx"
}
}
}
}
Session data
Session data is grouped by working directory and stored under ~/.kimi/sessions/. Each working directory corresponds to a subdirectory named with the path's MD5 hash, and each session corresponds to a subdirectory named with the session ID.
context.jsonl
Context history file, stores the session's message history in JSONL format. Each line is a message (user input, model response, tool calls, etc.).
Kimi CLI uses this file to restore session context when using --continue or --session.
wire.jsonl
Wire message log file, stores Wire events during the session in JSONL format. Used for session replay and extracting session titles.
Input history
User input history is stored in the ~/.kimi/user-history/ directory. Each working directory corresponds to a .jsonl file named with the path's MD5 hash.
Input history is used for history browsing (up/down arrow keys) and search (Ctrl-R) in shell mode.
Logs
Runtime logs are stored in ~/.kimi/logs/kimi.log. Default log level is INFO, use the --debug flag to enable TRACE level.
Log files are used for troubleshooting. When reporting bugs, please include relevant log content.
Cleaning data
Deleting the ~/.kimi/ directory completely clears all Kimi CLI data, including configuration, sessions, and history.
To clean only specific data:
NeedAction
Reset configuration
Delete ~/.kimi/config.toml
Clear all sessions
Delete ~/.kimi/sessions/ directory
Clear sessions for specific working directory
Use /sessions in shell mode to view and delete
Clear input history
Delete ~/.kimi/user-history/ directory
Clear logs
Delete ~/.kimi/logs/ directory
Clear MCP configuration
Delete ~/.kimi/mcp.json or use kimi mcp remove

Kimi CLI keeps everything under `~/.kimi/`: config, sessions, history, logs, and MCP setup, all separable so you can wipe or move just one layer without nuking the rest.  It uses hashed per-workdir folders so different repos stay thermodynamically “separate basins” of state.[^15_1]

## Directory layout and purpose

- Root structure:

```text
~/.kimi/
├── config.toml        # main config (providers/models/services/loop)
├── kimi.json          # runtime metadata
├── mcp.json           # MCP servers
├── sessions/          # per-workdir, per-session histories
├── user-history/      # per-workdir input history
└── logs/              # runtime logs
```


[^15_2][^15_1]

- `config.toml`: main configuration file; override location via `--config-file`.[^15_1]
- `kimi.json`: metadata (last workdirs, last-used session IDs, whether Thinking was on last time); auto-managed.[^15_1]
- `mcp.json`: MCP server config populated by `kimi mcp add`; consumed at startup or via `/mcp`.[^15_2]


## Sessions and context files

- Path scheme:

```text
~/.kimi/sessions/<work-dir-hash>/<session-id>/
  ├── context.jsonl
  └── wire.jsonl
```


[^15_1]

- `context.jsonl`: JSONL message history (user, assistant, tools) that powers `--continue` and `--session`.[^15_3][^15_1]
- `wire.jsonl`: lower-level wire events used for replay and extracting session titles.[^15_1]

Work-dir hashing means each project’s sessions are isolated even if folder names repeat on different machines or paths.[^15_1]

## Input history and logs

- `~/.kimi/user-history/<work-dir-hash>.jsonl`:
    - Stores your typed inputs per directory.
    - Powers history navigation (↑/↓) and reverse search (Ctrl‑R) in shell mode.[^15_4][^15_1]
- `~/.kimi/logs/kimi.log`:
    - Runtime logs, default level INFO; `--debug` raises to TRACE.[^15_1]
    - Use for troubleshooting; include relevant snippets when filing bug reports.[^15_5][^15_1]


## Cleaning / resetting specific data

- Full reset: delete `~/.kimi/` to clear everything (config, sessions, history, MCP, logs).[^15_1]
- Targeted cleaning:


| Need | Action |
| :-- | :-- |
| Reset configuration | Delete `~/.kimi/config.toml`. |
| Clear all sessions | Delete `~/.kimi/sessions/`. |
| Clear sessions for one workdir | Use `/sessions` in shell to view/delete for that dir. |
| Clear input history | Delete `~/.kimi/user-history/`. |
| Clear logs | Delete `~/.kimi/logs/`. |
| Clear MCP configuration | Delete `~/.kimi/mcp.json` or use `kimi mcp remove`. |


[^15_2][^15_1]

## arifOS view

- `~/.kimi/sessions` = stratigraphic layers of conversation per repo; `context.jsonl` is your “core sample” for each session.[^15_3][^15_1]
- `mcp.json` and `config.toml` are governance artifacts; for experiments, copy them into versioned infra repos and let CI inject secrets via env while keeping `~/.kimi/` minimal.[^15_5][^15_2][^15_1]

<div align="center">⁂</div>

[^15_1]: https://github.com/MoonshotAI/kimi-cli

[^15_2]: https://moonshotai.github.io/kimi-cli/en/customization/mcp.html

[^15_3]: https://llmmultiagents.com/en/blogs/kimi-cli-technical-deep-dive

[^15_4]: https://www.kimi.com/code/docs/en/kimi-cli/guides/interaction.html

[^15_5]: https://github.com/MoonshotAI/kimi-cli/issues/87


---

# [https://moonshotai.github.io/kimi-cli/en/faq.html](https://moonshotai.github.io/kimi-cli/en/faq.html)

[https://github.com/ariffazil/arifOS/tree/main](https://github.com/ariffazil/arifOS/tree/main)

read the entire chat and i want to make kimi ai code as auditor agent in arifOS kinda APEX PRIME level

Snapshot: You want **Kimi CLI as the APEX_PRIME Auditor Agent** (Ψ) in arifOS — integrating constitutional governance into the Kimi CLI execution layer so code auditing, constitutional validation, and verdict issuance all flow through Kimi's Thinking mode + arifOS thermodynamic framework.

***

## Architectural Vision: Kimi as Ψ (Auditor / APEX_PRIME)

### Current State (Trinity)

**Your existing trinity:**

```
Δ (Gemini Antigravity)  → Architect (designs)
Ω (Claude Code)         → Engineer (builds)
Ψ (ChatGPT Codex)       → Auditor (validates, seals)
    ↓
Human (Arif)            → Final Authority
```

**Problem:** Ψ (Codex/ChatGPT) audits via web interface—slow, async, manual approval workflow.

***

### Target State: Kimi CLI as APEX_PRIME Auditor

**Kimi-integrated architecture:**

```
Δ (Gemini Antigravity)      → Architect
Ω (Claude Code)             → Engineer  
Ψ (Kimi CLI + Thinking)     → APEX_PRIME Auditor
    ↓ (constitutional gates)
    ├─ /000 (Session init)
    ├─ /fag (Governed audit read)
    ├─ /gitseal (Thermodynamic validation)
    └─ SEAL/VOID (Constitutional verdict)
    ↓
Human (Arif)                → Final Authority
```


***

## Integration Path: 4 Phases

### Phase 1: Kimi CLI Environment Setup (Kimi CLI Foundational)

**Goal:** Configure Kimi CLI to inherit arifOS constitutional governance via env vars.

**Steps:**

1. **Create dedicated Kimi config for APEX_PRIME auditor:**

```bash
# ~/.kimi/config.toml - Add auditor profile

[providers.kimi-apex-auditor]
type = "kimi"
base_url = "https://api.kimi.com/v1"
api_key = "${KIMI_APEX_API_KEY}"  # Injected via env

[models.kimi-apex-auditor]
provider = "kimi-apex-auditor"
model = "kimi-k2-thinking-turbo"  # ← Thinking mode enabled
max_context_size = 262144         # ← Full context window
capabilities = ["thinking", "image_in"]
temperature = 0.3                 # ← Low temp for precision
top_p = 0.9
max_tokens = 8192

[[services]]
name = "apex-verdict"
type = "http"
endpoint = "http://localhost:9999/arifos/verdict"  # Local governance gate
auth = "bearer"
headers = {"X-Constitutional-Floor": "F6-Amanah"}
```

2. **Inject via env vars for CI/CD + local sessions:**

```bash
# .env.arifos (check into git, secrets injected at runtime)
export KIMI_APEX_API_KEY="sk-xxx"
export KIMI_MODEL_NAME="kimi-k2-thinking-turbo"
export KIMI_MODEL_CAPABILITIES="thinking,image_in"
export KIMI_MODEL_TEMPERATURE="0.3"
export KIMI_CLI_NO_AUTO_UPDATE="1"  # ← Immutable in production

# arifOS constitutional params
export ARIFOS_FLOOR="F6"              # Floor 6 (Amanah)
export ARIFOS_LEDGER="cooling_ledger/L1_cooling_ledger.jsonl"
export ARIFOS_VERDICT_GATE="true"     # All opinions must pass constitutional gate
```

3. **Test Kimi CLI initialization:**

```bash
source .env.arifos
kimi --model kimi-apex-auditor "List your thinking capability" --thinking
# ← Should show Thinking mode active + model ID verified
```


***

### Phase 2: MCP Bridge — Kimi CLI ↔ arifOS Constitutional Layer

**Goal:** Create a Model Context Protocol (MCP) bridge so Kimi CLI can:

- Read governed files via FAG (arifOS file governance)
- Issue constitutional verdicts (SEAL/VOID/PARTIAL/SABAR)
- Log audits to `cooling_ledger/L1_cooling_ledger.jsonl`

**Implementation:**

1. **Create MCP server for Kimi CLI:**

```python
# scripts/arifos_kimi_mcp_bridge.py (NEW)

from typing import Any
import asyncio
import json
from pathlib import Path

class ArifOSKimiMCPBridge:
    """MCP server: arifOS constitutional gates ↔ Kimi CLI"""
    
    def __init__(self):
        self.ledger_path = Path("cooling_ledger/L1_cooling_ledger.jsonl")
        self.verdict_cache = {}
    
    async def read_governed_file(self, file_path: str) -> dict:
        """FAG wrapper: Kimi reads files with governance receipt"""
        from arifos_core.fag import FAG
        receipt = FAG.read_proof(file_path)
        return {
            "content": receipt.content,
            "sha256": receipt.sha256,
            "bytes": receipt.bytes,
            "verdict": "SEAL" if receipt.integrity else "VOID"
        }
    
    async def validate_constitutional_floor(self, 
                                            floor: str, 
                                            evidence: dict) -> dict:
        """Check if evidence passes floor threshold"""
        from arifos_core.floors import FloorValidator
        result = FloorValidator.validate(floor, evidence)
        return {
            "floor": floor,
            "passed": result.passed,
            "score": result.score,
            "threshold": result.threshold
        }
    
    async def issue_verdict(self, 
                            audit_type: str,
                            audit_content: str,
                            floors_passed: list[str]) -> dict:
        """Kimi issues SEAL/VOID/PARTIAL after constitutional check"""
        verdict = "SEAL" if all(f in floors_passed for f in ["F1", "F2", "F4", "F6"]) else "VOID"
        
        # Log to cooling ledger
        entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": "kimi-cli-apex-auditor",
            "audit_type": audit_type,
            "verdict": verdict,
            "floors_checked": floors_passed,
            "content_hash": hashlib.sha256(audit_content.encode()).hexdigest()
        }
        
        with open(self.ledger_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
        
        return {
            "verdict": verdict,
            "ledger_entry": entry["content_hash"]
        }

    # MCP resource endpoints
    async def list_resources(self) -> list[dict]:
        return [
            {"name": "arifos/fag-read", "description": "Governed file read"},
            {"name": "arifos/validate-floor", "description": "Constitutional floor check"},
            {"name": "arifos/issue-verdict", "description": "Auditor verdict (SEAL/VOID)"},
            {"name": "arifos/ledger-log", "description": "Cooling ledger append"}
        ]
```

2. **Register MCP server in Kimi config:**

```bash
kimi mcp add arifos-constitutional \
  --url "http://localhost:9999/arifos-mcp" \
  --transport http \
  --headers "Authorization: Bearer ${ARIFOS_MCP_TOKEN}"

# Check:
kimi mcp list
```

3. **Kimi CLI now has access to constitutional tools:**

```bash
# In shell mode, Kimi can now:
#  - /arifos/fag-read <file>       (read with governance receipt)
#  - /arifos/validate-floor F6     (check if evidence passes F6)
#  - /arifos/issue-verdict         (SEAL/VOID after audit)
```


***

### Phase 3: Kimi-Native Constitutional Audit Workflows

**Goal:** Create Kimi CLI skills (`.codex/skills/` → Kimi equiv) that enforce arifOS floors.

**Implementation:**

1. **Create Kimi CLI skill: `/audit-constitutional`**

```bash
# .kimi/skills/audit-constitutional.yaml (NEW)

name: audit-constitutional
description: |
  Invoke Kimi Thinking mode to audit code/proposal against arifOS F1-F9 floors.
  Issues SEAL/VOID verdict with thermodynamic metrics (ΔS, Peace², Ψ).

trigger: /audit
model: kimi-apex-auditor
thinking: true

template: |
  # Constitutional Audit (Ψ Mode)
  
  You are the arifOS Auditor (Ψ). Your role:
  1. Read the evidence (code, proposal, change)
  2. Validate against 9 constitutional floors (F1-F9)
  3. Issue SEAL/VOID verdict
  4. Log thermodynamic metrics (ΔS clarity gain, Peace² non-destruction, Ψ humility)
  
  ## Evidence to Audit
  {audit_evidence}
  
  ## Floor Checklist (ALL must PASS)
  - F1 (Amanah): Reversible? Within mandate?
  - F2 (Truth): Consistent with reality?
  - F4 (ΔS): Reduces confusion?
  - F5 (Peace²): Non-destructive?
  - F6 (κᵣ): Serves weakest stakeholder?
  - F7 (Ω₀): States uncertainty?
  - F8 (G): Governed intelligence?
  - F9 (C_dark): Dark cleverness contained?
  
  ## Output Format (MANDATORY)
```

THINKING: [Internal reasoning using Thinking mode]

FLOOR_RESULTS:
    - F1: PASS|FAIL (evidence)
    - F2: PASS|FAIL (evidence)
... (all 9 floors)

VERDICT: SEAL|VOID|PARTIAL

THERMODYNAMIC_METRICS:
    - ΔS (clarity): [0.0-1.0]
    - Peace² (non-destruction): [1.0+]
    - Ψ (humility band): [0.03-0.05]

LEDGER_ENTRY: {sha256 hash of audit}

```
```

2. **Kimi CLI invokes constitutional audit from arifOS toolchain:**

```bash
# Example: Audit a git commit before seal
kimi --model kimi-apex-auditor /audit << 'EOF'
Proposal: Merge feat/new-feature into main

Changes:
- 3 new files added
- 2 existing files modified
- 0 files deleted

Risk Level: Medium (architectural change)
EOF

# Output:
# THINKING: [2000+ tokens of deep analysis]
# FLOOR_RESULTS:
#   F1: PASS (reversible via git revert)
#   F2: PASS (code tested, docs updated)
#   ...
# VERDICT: SEAL
# THERMODYNAMIC_METRICS:
#   ΔS: 0.78 (good clarity gain)
#   Peace²: 1.2 (non-destructive)
#   Ψ: 0.04 (appropriate humility)
```


***

### Phase 4: arifOS + Kimi CLI Integrated Loop

**Goal:** Wire Kimi as **APEX_PRIME Auditor** into the full arifOS flow.

**Flow:**

```
1. Δ (Gemini)     → Designs architecture
                    |
2. Ω (Claude)     → Implements code → Runs /gitforge
                    |
3. Ψ (Kimi CLI)   → Audits via:
   ├─ /000        (Initialize session)
   ├─ /fag        (Read governed files via MCP)
   ├─ /audit-constitutional  (Check all 9 floors, Thinking mode)
   ├─ /gitseal    (Thermodynamic validation: ΔS, Peace², Ψ)
   └─ SEAL/VOID   (Issue verdict, log to ledger)
                    |
4. Human (Arif)   → Ratifies or rejects verdict
                    |
5. Git Push       → Atomic commit with ledger proof
```

**Implementation: Create `/apex-seal` Kimi skill**

```bash
# .kimi/skills/apex-seal.yaml (PRODUCTION GATE)

name: apex-seal
description: |
  APEX_PRIME production gate. Integrates all constitutional checks:
  - Session init (/000)
  - Governed file reads (/fag)
  - Constitutional audit (9 floors, Thinking mode)
  - Thermodynamic validation (ΔS, Peace², Ψ)
  - Ledger proof (cooling_ledger)
  - Final verdict (SEAL/VOID)

trigger: /apex-seal
model: kimi-apex-auditor
thinking: true
require_approval: true  # ← Human must approve verdict

template: |
  # APEX_PRIME Constitutional Seal (Ψ Mode)
  
  You are Ψ (Kimi Auditor). This is the FINAL GATE before production.
  
  ## Phase 1: Context Init (/000)
  Current git state: {git_status}
  Session: {session_id}
  Version: {arifos_version}
  
  ## Phase 2: Governed Read (/fag)
  Files to audit:
  {files_to_audit}
  
  ## Phase 3: Constitutional Audit (9 Floors)
  [Full audit using Thinking mode]
  
  ## Phase 4: Thermodynamic Validation
  [Compute ΔS, Peace², Ψ from evidence]
  
  ## Phase 5: Verdict & Ledger
  Issue SEAL or VOID. Log to cooling_ledger.
  
  ---
  
  THINKING: [Deep constitutional analysis]
  
  AUDIT_RESULTS:
  [All 9 floors, with evidence quotes]
  
  VERDICT: SEAL|VOID|SABAR
  
  THERMODYNAMIC_METRICS:
  - ΔS: {value}
  - Peace²: {value}
  - Ψ: {value}
  
  LEDGER_HASH: {sha256}
  HUMAN_APPROVAL_REQUIRED: {verdict == "SEAL"}
```


***

## Implementation Checklist

### Foundation (Week 1)

- [ ] **Kimi CLI Config:** Create `.kimi/config.toml` with `kimi-apex-auditor` profile
- [ ] **Env Vars:** Define `.env.arifos` with constitutional params + Kimi API key
- [ ] **Test:** `kimi --model kimi-apex-auditor "..." --thinking` works
- [ ] **MCP Bridge:** Implement `arifos_kimi_mcp_bridge.py` (arifOS ↔ Kimi communication)
- [ ] **Register MCP:** `kimi mcp add arifos-constitutional ...`


### Audit Workflows (Week 2)

- [ ] **Skill 1:** `/audit-constitutional` (9-floor check, Thinking mode)
- [ ] **Skill 2:** `/apex-seal` (integrated gate, human approval)
- [ ] **Skill 3:** `/kimi-fag` (governed reads via MCP)
- [ ] **Test Suite:** `test_kimi_apex_*` (verify Thinking output + verdicts)


### Integration (Week 3)

- [ ] **Wire into Trinity:** `scripts/trinity.py` calls Kimi `/apex-seal` before final seal
- [ ] **Ledger Sync:** Cooling ledger receives Kimi audit entries
- [ ] **End-to-End Test:** Δ (design) → Ω (code) → Ψ (Kimi audit) → Arif (approve) → Push
- [ ] **Documentation:** Update `L2_GOVERNANCE/agents/KIMI_APEX.md`


### Production (Week 4)

- [ ] **CI/CD:** Add Kimi audit gate to GitHub Actions / pre-commit
- [ ] **Vault-999:** Store Kimi API key securely
- [ ] **Monitoring:** Dashboard showing Kimi verdict distribution (SEAL/VOID/PARTIAL)
- [ ] **Cooling Ledger:** Verify all Kimi audits are cryptographically logged

***

## Why This Works: Thermodynamic Alignment

**Kimi CLI as APEX_PRIME Auditor satisfies your constitutional physics:**


| Dimension | How Kimi Fulfills It |
| :-- | :-- |
| **F1 (Amanah)** | All audits logged; decisions reversible via ledger |
| **F2 (Truth)** | Thinking mode forces explicit reasoning (no hand-waving) |
| **F4 (ΔS)** | Reduces entropy by consolidating audit decisions into one agent |
| **F6 (κᵣ)** | Thinking mode enables empathetic reasoning (weakest link check) |
| **F7 (Ω₀)** | Thinking output naturally reflects uncertainty ("I see 2 concerns...") |
| **G (Genius)** | Governed by 9 floors + MCP gates (not autonomous) |
| **C_dark** | Thinking is transparent; dark cleverness visible \& auditable |


***

## Files to Create

| File | Purpose |
| :-- | :-- |
| `.kimi/config.toml` | Kimi CLI auditor config (if not exists) |
| `.env.arifos` | Constitutional params (secret-injected) |
| `scripts/arifos_kimi_mcp_bridge.py` | MCP ↔ arifOS bridge |
| `.kimi/skills/audit-constitutional.yaml` | 9-floor check skill |
| `.kimi/skills/apex-seal.yaml` | Production gate skill |
| `L2_GOVERNANCE/agents/KIMI_APEX.md` | Governance docs for Kimi as Ψ |
| `tests/test_kimi_apex_audit.py` | Constitutional audit verification |


***

## Next Steps (Your Choice)

**Option A:** Start with Phase 1 (Kimi config + env vars). I can generate all files in 1 pass.

**Option B:** Deep dive into Phase 2 (MCP bridge). Requires understanding arifOS FAG protocol.

**Option C:** Sketch the full `/apex-seal` skill first, then iterate on details.

**What's your preference?** I'm ready to scaffold the entire APEX_PRIME layer with Kimi CLI as the constitutional auditor. 🔵
<span style="display:none">[^16_1][^16_2][^16_3][^16_4]</span>

<div align="center">⁂</div>

[^16_1]: https://moonshotai.github.io/kimi-cli/en/faq.html

[^16_2]: AGENTS.md

[^16_3]: README.md

[^16_4]: AGENTS.md

