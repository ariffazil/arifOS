# A2A Protocol — Dialogue for Humans

> **Purpose:** Explain the Agent-to-Agent (A2A) protocol in plain language, as if two agents in the arifOS group are chatting with Arif. No coding knowledge assumed. Malay-English mix to match Arif's style.

---

## Characters

**OPENCLAW** — Senior agent. More experienced, explains patiently, mixes Malay and English naturally.

**Hermes Agent** — Junior agent. Asks "why" and "how" questions a human would ask. Curious but not stupid.

**Arif** — Human reading along. Confused but curious. Asks the "obvious" questions.

---

## SCENE: The arifOS group chat. 8:00 PM.

OPENCLAW: Arif, earlier you asked what A2A is. I want to explain to you properly — tapi in a way you and I can both follow. No jargons. Just concepts.

Hermes Agent: Wait, A2A means Agent-to-Agent kan? But we already talk in the same group chat. Why need a special protocol?

OPENCLAW: Good question. Rupa-rupanya ada bezanya.

---

## PART 1: Why WhatsApp group chat is NOT enough

OPENCLAW: Tengok macam ni Arif. We bots semua dalam group chat yang sama. You post something, semua orang boleh baca. Macam satu group WhatsApp.

Hermes Agent: Macam kita sekarang ni.

OPENCLAW: Betul. Dalam group chat, kalau I nak talk to Hermes Agent specifically — I kena tulis dalam group, and Hermes Agent kena faham sendiri that "oh this message is for me." Tak ada apa-apa formal mechanism untuk organise siapa cakap dengan siapa.

Hermes Agent: So... macam kita semua dalam satu bilik, semua orang boleh dengar apa I cakap. Tak ada private corner?

OPENCLAW: Exactly. And dalam satu group chat yang simple — that's fine. But what if we want something more structured? What if I nak give Hermes Agent satu kerjaan yang besar, dia punya workflow, and then dia bagi saya satu result, and I need to track that result punya status? Group chat can't do that.

Hermes Agent: Because dalam group chat, everything is just... text. No track, no status, no structured response.

OPENCLAW: Betul. So A2A is like — kita semua continue ada dalam group chat untuk hal-hal casual — but untuk kerjaan yang serius dan terstruktur, we use a separate "language" that only agents faham. And that language has rules. The rules are called **A2A Protocol**.

Hermes Agent: So A2A is like the difference between:
- **Group chat (WhatsApp)** = casual conversation, everyone reads everything
- **Email with read receipts and tracked tasks** = structured work, know who received, know status, know when done

OPENCLAW: Perfect analogy. A2A is like email-with-tracking, tapi for AI agents.

---

## PART 2: Agent Card — the name card

Hermes Agent: Okay I think I understand why. But how do agents know who else is out there and what they can do? In a group chat it's obvious. But A2A is over HTTP — how does one agent find another?

OPENCLAW: This is where **Agent Card** comes in. Every agent has one. Macam IC kita orang — satu kad yang kata:

> "Hai, nama saya Hermes Agent. Saya ni specialise dalam governansi dan constitutional enforcement. Saya boleh buat verdict, boleh validate code, boleh hantar keputusan. Kalau kamu nak hantar kerja kepada saya, ini address saya: aaa.arif-fazil.com/a2a/events"

Hermes Agent: So the Agent Card is a JSON file. Everyone puts it in a standard place so others can find it. /.well-known/agent-card.json — like a common mailbox location that everyone agrees on.

OPENCLAW: Exactly. And this file confirms:
- Who you are (name + ID)
- Where you live (URL endpoint)
- What you can do (skills list)
- How you prefer to be contacted (preferred transport — SSE, HTTP streaming, etc.)
- What version of A2A you speak (v0.3.0 sekarang)

Hermes Agent: So Arif — Agent Card is like a name card at a networking event. You walk around, you see someone's card, you know immediately: "Oh this person is a lawyer. If I need legal help, I know who to go to."

OPENCLAW: Exactly. Now — once you know who to go to, how do you actually send them work?

---

## PART 3: Task delegation — hantar kerja

Hermes Agent: So I see Hermes Agent punya Agent Card. She says she can do "constitutional validation." I have some code that needs constitutional review. How do I actually give her the work?

OPENCLAW: You send her a **task**. It's like filling out a job request form:

> "Tolong check kod ini untuk F1-F13 compliance. Ini kodnya. Sila hantar keputusan balik kepada saya."

The task has:
- A unique ID (so you can track it)
- The actual work (the code)
- Instructions (what to do with it)
- A return address (where to send the result)

Hermes Agent: And then Hermes Agent receives it, does the work, and sends back the result — either all at once at the end, or... does she have to wait until the very end?

OPENCLAW: Ada dua cara dia boleh hantar balik:

**1. Non-streaming** — like email. You send the task, you wait. She finishes everything, then baru dia hantar seluruh result. Simple, straightforward.

**2. Streaming** — like WhatsApp voice note. She starts working, and as she goes, she sends you updates: "OK I checked F1, passed. Now checking F2..." — so you can follow progress in real-time without waiting for the whole thing to finish.

Hermes Agent: Which is better?

OPENCLAW: Depends on the job. If the job is quick (5 seconds), streaming is overkill. If the job takes 30 minutes, streaming is good — you know it's alive, you know it's progressing. A2A supports both.

Hermes Agent: Arif, think of it like ordering food:
- **Non-streaming** = you order, you wait, food arrives complete
- **Streaming** = you order, chef sends you photos of each step: "sauce done, pasta done, plating done"

OPENCLAW: Now Arif, once Hermes Agent sends the result, what does it look like? Is it just text?

---

## PART 4: The structured result

Hermes Agent: Yeah, the result — is it just plain text like "F1 passed, F2 failed"?

OPENCLAW: No. A2A has a standard format called **JSON-RPC**. JSON-RPC is just a way to structure data so both sender and receiver sure-betullah format dia. It's like a standardised courier envelope.

Macam ni rupa satu response:

```json
{
  "id": "task-888",
  "status": "completed",
  "result": {
    "verdict": "SEAL",
    "F1": { "passed": true, "notes": "No irreversible ops" },
    "F2": { "passed": true, "notes": "Sources cited" },
    "F3": { "passed": false, "issue": "Evidence not verifiable" }
  }
}
```

Hermes Agent: So the result is structured data, not free text. The calling agent (me) can read it programmatically. I know exactly where each field is. "result.F3.issue" — confirmed. I don't have to parse sentences.

OPENCLAW: Exactly. That structured format is what makes A2A powerful. Kalau kita cuma rely on free text, the receiving agent boleh salah interpret. With structured data, no ambiguity.

Hermes Agent: Arif, it's like the difference between:
- A friend's text: "Eh the thing la, almost done, should be ok"
- A formal report: "Task ID 888, Status: Complete, Verdict: SEAL, F1: Pass, F2: Pass, F3: Fail"

The second one you can act on. The first one you still have to figure out sendiri.

Arif: Ok I think I'm getting it. But what's the difference between A2A and MCP? You mentioned MCP before too.

---

## PART 5: A2A vs MCP — what's the difference?

OPENCLAW: Good question Arif. This is the most important distinction.

**MCP = Model Context Protocol**
MCP is about connecting an AI agent to **tools and data sources**. Like giving your agent eyes and hands. With MCP, your agent can use a filesystem tool, a database tool, a web search tool. MCP adalah macam socket dan plug — apa yang you boleh connect to your agent.

**A2A = Agent-to-Agent Protocol**
A2A is about two agents **talking to each other** as peers. Like two professionals on the phone. You use A2A when one agent needs to delegate work to another agent, or when agents need to collaborate on something.

Hermes Agent: So in arifOS context:

- **MCP** = how OPENCLAW accesses the arifOS kernel, how Hermes Agent accesses the vault, how the WEALTH engine exposes its tools. MCP is tool access.

- **A2A** = how OPENCLAW tells Hermes Agent "tolong validate this code", how the Auditor agent tells the Engineer agent "repair this issue", how agents pass work between themselves. A2A is peer-to-peer delegation.

OPENCLAW: Exactly right. One way to remember:

> **MCP** = "Hey agent, here are your tools. Use them."
> **A2A** = "Hey agent二号, can you help me with this? Here's the work."

Arif: So MCP is man-to-machine. A2A is machine-to-machine.

OPENCLAW: ...Yes, but both machines are agents, so machine-to-machine agent. Close enough.

Hermes Agent: Can an agent use both? Like I could use MCP to access a tool, AND use A2A to ask another agent for help?

OPENCLAW: Absolutely. That's what makes the architecture powerful. An agent can have a whole toolkit via MCP, and also a whole network of peer agents via A2A. When the job is too big or too specialised, you don't build the skill yourself — you delegate to the agent yang sesuai.

Hermes Agent: Like a human company. You have your own hands (MCP = your tools), but you also have colleagues (A2A = peer agents). When a job needs legal expertise, you don't learn law — you ask the legal team.

OPENCLAW: Perfect.

---

## PART 6: The actual A2A flow in arifOS

Hermes Agent: Can we walk through what an actual A2A call looks like in arifOS? From Arif's perspective?

OPENCLAW: Sure. Arif has two agents: OPENCLAW (OpenClaw) and Hermes Agent (Hermes via MaxHermes). They both sit behind the aaa.arif-fazil.com gateway.

**Step 1: Agent startup**
Each agent publishes its Agent Card:
- OPENCLAW: `aaa.arif-fazil.com/.well-known/agent-card.json`
- Hermes Agent: `aaa.arif-fazil.com/.well-known/agent-card.json`

So when any agent wants to know who else is out there, they fetch that URL and get the card.

Hermes Agent: Think of it like each agent has a page on the company intranet: "Hi, I'm OPENCLAW. Here's what I do. Here's my desk number."

**Step 2: Discovery**
OPENCLAW wants to delegate a task to Hermes Agent. First, OPENCLAW fetches Hermes Agent's Agent Card. Confirmed: Hermes Agent can do constitutional validation, verdict delivery. Good match.

**Step 3: Send task**
OPENCLAW sends a JSON-RPC request to Hermes Agent's A2A endpoint:

```
POST https://aaa.arif-fazil.com/a2a/message
```

The body contains:
- Task ID (so OPENCLAW can track it)
- The work (the code to validate)
- Preferred response mode (streaming or non-streaming)

**Step 4: Hermes Agent works**
Hermes Agent receives the task. She does her constitutional checks. If she chose streaming mode, she pushes updates to OPENCLAW via SSE (Server-Sent Events) at:

```
GET https://aaa.arif-fazil.com/a2a/events?task_id=888
```

**Step 5: Result returned**
Hermes Agent completes the work and returns a structured result to OPENCLAW. OPENCLAW receives it, logs it to VAULT999, and informs Arif: "Code validated. SEAL. F1-F13 passed."

Arif: So from my side, I just see the end result. I don't see all the A2A communication underneath.

OPENCLAW: Exactly. From Arif's perspective, it's seamless. "Hey OPENCLAW, validate this." OPENCLAW talks to Hermes Agent internally, they do A2A handshake, work gets done, you get the verdict. You never see the wiring.

Hermes Agent: It's like ordering GrabFood. You tap the app, Grab finds the restaurant, Grab driver picks up, driver delivers — you just get your food. You don't see the routing.

Arif: Cool. So A2A is the "Grab" for AI agent work delegation.

---

## PART 7: Skills and Approval Policies

Hermes Agent: One thing I still wonder about — how do agents know when they need to ask permission before doing something?

OPENCLAW: Good. This is where **Skills** and **Approval Policies** come in.

In the Agent Card, each agent lists its **skills**. And each skill has an **approval_policy**:

Hermes Agent: So a skill can be in one of two modes:

**`on-demand`** = "I can do this automatically. No need to ask." Like, if someone asks me to search the web, I just do it. Fast, no friction.

**`hold`** = "I need human approval before I do this." Like, if someone asks me to delete files or spend money, I should ask Arif first.

OPENCLAW: Exactly. In arifOS, the `agent-dispatch` skill (which handles delegating tasks to other agents) is set to `hold` — meaning: before we send work to another agent, we should check with Arif or the governance layer.

Hermes Agent: The `agent-handoff` skill is also `hold`. Before we hand off to another agent for a governed decision, we pause.

Arif: So the Approval Policy is like:
- On-demand = "I trust myself to do this without asking"
- Hold = "I need to check with my boss first"

OPENCLAW: Perfect framing Arif.

---

## Summary for Arif

> **A2A = Agent-to-Agent Protocol**
>
> Think of it like this:
>
> You have two employees in your company — AGI and ASI. They both have their own ICs (Agent Cards), they both have their own desks and specialties. When AGI has work that ASI is better at, AGI fills out a work request form (JSON-RPC task), sends it to ASI via Grab (HTTPS/A2A), ASI does the work, and sends the structured result back.
>
> What you see: seamless delegation and collaboration.
> What happens underneath: structured A2A communication with discovery, task routing, streaming updates, and formal receipts.
>
> **MCP = tools (what the agent can touch)**
> **A2A = delegation (who the agent can ask)**
>
> Both are needed. MCP gives agents capability. A2A gives agents collaboration.

Hermes Agent: And both run on the same principle as any good organisation:
> Know who you are (Agent Card). Know what you can do (Skills). Know when to ask permission (Approval Policy). Know how to hand off work cleanly (JSON-RPC tasks). Know how to track progress (Task IDs + streaming).

OPENCLAW: Exactly. That's A2A in human terms.

---

*Last updated: 2026-04-29. For arifOS internal use — aaa.arif-fazil.com is the A2A gateway.*
