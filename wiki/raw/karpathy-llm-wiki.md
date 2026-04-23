Title: llm-wiki · GitHub

Description: llm-wiki. GitHub Gist: instantly share code, notes, and snippets.

Source: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

---

[Skip to content](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f#start-of-content)
[All gists](https://gist.github.com/discover)
[Back to GitHub](https://github.com)
[Sign in](https://gist.github.com/auth/github?return_to=https%3A%2F%2Fgist.github.com%2Fkarpathy%2F442a6bf555914893e9891c11519de94f)
[Sign up](https://gist.github.com/join?return_to=https%3A%2F%2Fgist.github.com%2Fkarpathy%2F442a6bf555914893e9891c11519de94f&source=header-gist)
[Sign in](https://gist.github.com/auth/github?return_to=https%3A%2F%2Fgist.github.com%2Fkarpathy%2F442a6bf555914893e9891c11519de94f)
[Sign up](https://gist.github.com/join?return_to=https%3A%2F%2Fgist.github.com%2Fkarpathy%2F442a6bf555914893e9891c11519de94f&source=header-gist)
[Reload](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
[Reload](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
[Reload](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
Instantly share code, notes, and snippets.

# [karpathy](https://gist.github.com/karpathy)/[llm-wiki.md](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
[karpathy](https://gist.github.com/karpathy)
[llm-wiki.md](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
- 


    [Download ZIP](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f/archive/ac46de1ad27f92b28ac95459c782c07f6b8c964a.zip)


[Download ZIP](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f/archive/ac46de1ad27f92b28ac95459c782c07f6b8c964a.zip)
- 
          [Star

          5,000+
          (5,000+)](https://gist.github.com/login?return_to=https%3A%2F%2Fgist.github.com%2Fkarpathy%2F442a6bf555914893e9891c11519de94f)You must be signed in to star a gist


- 
            [Fork

          2,540
          (2,540)](https://gist.github.com/login?return_to=https%3A%2F%2Fgist.github.com%2Fkarpathy%2F442a6bf555914893e9891c11519de94f)You must be signed in to fork a gist


[Star

          5,000+
          (5,000+)](https://gist.github.com/login?return_to=https%3A%2F%2Fgist.github.com%2Fkarpathy%2F442a6bf555914893e9891c11519de94f)
[Fork

          2,540
          (2,540)](https://gist.github.com/login?return_to=https%3A%2F%2Fgist.github.com%2Fkarpathy%2F442a6bf555914893e9891c11519de94f)
- 





    Embed













        Select an option





























           Embed
      Embed this gist in your website.














           Share
      Copy sharable link for this gist.














          Clone via HTTPS
      Clone using the web URL.








              No results found


              [Learn more about clone URLs](https://docs.github.com/articles/which-remote-url-should-i-use)




        Clone this repository at &lt;script src=&quot;https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f.js&quot;&gt;&lt;/script&gt;





























- 










           Embed
      Embed this gist in your website.



- 










           Share
      Copy sharable link for this gist.



- 










          Clone via HTTPS
      Clone using the web URL.



- 



Save karpathy/442a6bf555914893e9891c11519de94f to your computer and use it in GitHub Desktop.

# Select an option
- 










           Embed
      Embed this gist in your website.



- 










           Share
      Copy sharable link for this gist.



- 










          Clone via HTTPS
      Clone using the web URL.

[Learn more about clone URLs](https://docs.github.com/articles/which-remote-url-should-i-use)
[Code](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
[Revisions
        1](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f/revisions)
[Stars
        5,000+](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f/stargazers)
[Forks
        2,540](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f/forks)

- 










           Embed
      Embed this gist in your website.



- 










           Share
      Copy sharable link for this gist.



- 










          Clone via HTTPS
      Clone using the web URL.

[Learn more about clone URLs](https://docs.github.com/articles/which-remote-url-should-i-use)
[Download ZIP](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f/archive/ac46de1ad27f92b28ac95459c782c07f6b8c964a.zip)
[Raw](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f/raw/ac46de1ad27f92b28ac95459c782c07f6b8c964a/llm-wiki.md)
[llm-wiki.md](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f#file-llm-wiki-md)

A pattern for building personal knowledge bases using LLMs.
This is an idea file, it is designed to be copy pasted to your own LLM Agent (e.g. OpenAI Codex, Claude Code, OpenCode / Pi, or etc.). Its goal is to communicate the high level idea, but your agent will build out the specifics in collaboration with you.

Most people's experience with LLMs and documents looks like RAG: you upload a collection of files, the LLM retrieves relevant chunks at query time, and generates an answer. This works, but the LLM is rediscovering knowledge from scratch on every question. There's no accumulation. Ask a subtle question that requires synthesizing five documents, and the LLM has to find and piece together the relevant fragments every time. Nothing is built up. NotebookLM, ChatGPT file uploads, and most RAG systems work this way.
The idea here is different. Instead of just retrieving from raw documents at query time, the LLM incrementally builds and maintains a persistent wiki — a structured, interlinked collection of markdown files that sits between you and the raw sources. When you add a new source, the LLM doesn't just index it for later retrieval. It reads it, extracts the key information, and integrates it into the existing wiki — updating entity pages, revising topic summaries, noting where new data contradicts old claims, strengthening or challenging the evolving synthesis. The knowledge is compiled once and then kept current, not re-derived on every query.
This is the key difference: the wiki is a persistent, compounding artifact. The cross-references are already there. The contradictions have already been flagged. The synthesis already reflects everything you've read. The wiki keeps getting richer with every source you add and every question you ask.
You never (or rarely) write the wiki yourself — the LLM writes and maintains all of it. You're in charge of sourcing, exploration, and asking the right questions. The LLM does all the grunt work — the summarizing, cross-referencing, filing, and bookkeeping that makes a knowledge base actually useful over time. In practice, I have the LLM agent open on one side and Obsidian open on the other. The LLM makes edits based on our conversation, and I browse the results in real time — following links, checking the graph view, reading the updated pages. Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase.
This can apply to a lot of different contexts. A few examples:
- Personal: tracking your own goals, health, psychology, self-improvement — filing journal entries, articles, podcast notes, and building up a structured picture of yourself over time.
- Research: going deep on a topic over weeks or months — reading papers, articles, reports, and incrementally building a comprehensive wiki with an evolving thesis.
- Reading a book: filing each chapter as you go, building out pages for characters, themes, plot threads, and how they connect. By the end you have a rich companion wiki. Think of fan wikis like [Tolkien Gateway](https://tolkiengateway.net/wiki/Main_Page) — thousands of interlinked pages covering characters, places, events, languages, built by a community of volunteers over years. You could build something like that personally as you read, with the LLM doing all the cross-referencing and maintenance.
- Business/team: an internal wiki maintained by LLMs, fed by Slack threads, meeting transcripts, project documents, customer calls. Possibly with humans in the loop reviewing updates. The wiki stays current because the LLM does the maintenance that no one on the team wants to do.
- Competitive analysis, due diligence, trip planning, course notes, hobby deep-dives — anything where you're accumulating knowledge over time and want it organized rather than scattered.
[Tolkien Gateway](https://tolkiengateway.net/wiki/Main_Page)

## Architecture
There are three layers:
Raw sources — your curated collection of source documents. Articles, papers, images, data files. These are immutable — the LLM reads from them but never modifies them. This is your source of truth.
The wiki — a directory of LLM-generated markdown files. Summaries, entity pages, concept pages, comparisons, an overview, a synthesis. The LLM owns this layer entirely. It creates pages, updates them when new sources arrive, maintains cross-references, and keeps everything consistent. You read it; the LLM writes it.
The schema — a document (e.g. CLAUDE.md for Claude Code or AGENTS.md for Codex) that tells the LLM how the wiki is structured, what the conventions are, and what workflows to follow when ingesting sources, answering questions, or maintaining the wiki. This is the key configuration file — it's what makes the LLM a disciplined wiki maintainer rather than a generic chatbot. You and the LLM co-evolve this over time as you figure out what works for your domain.

## Operations
Ingest. You drop a new source into the raw collection and tell the LLM to process it. An example flow: the LLM reads the source, discusses key takeaways with you, writes a summary page in the wiki, updates the index, updates relevant entity and concept pages across the wiki, and appends an entry to the log. A single source might touch 10-15 wiki pages. Personally I prefer to ingest sources one at a time and stay involved — I read the summaries, check the updates, and guide the LLM on what to emphasize. But you could also batch-ingest many sources at once with less supervision. It's up to you to develop the workflow that fits your style and document it in the schema for future sessions.
Query. You ask questions against the wiki. The LLM searches for relevant pages, reads them, and synthesizes an answer with citations. Answers can take different forms depending on the question — a markdown page, a comparison table, a slide deck (Marp), a chart (matplotlib), a canvas. The important insight: good answers can be filed back into the wiki as new pages. A comparison you asked for, an analysis, a connection you discovered — these are valuable and shouldn't disappear into chat history. This way your explorations compound in the knowledge base just like ingested sources do.
Lint. Periodically, ask the LLM to health-check the wiki. Look for: contradictions between pages, stale claims that newer sources have superseded, orphan pages with no inbound links, important concepts mentioned but lacking their own page, missing cross-references, data gaps that could be filled with a web search. The LLM is good at suggesting new questions to investigate and new sources to look for. This keeps the wiki healthy as it grows.

## Indexing and logging
Two special files help the LLM (and you) navigate the wiki as it grows. They serve different purposes:
index.md is content-oriented. It's a catalog of everything in the wiki — each page listed with a link, a one-line summary, and optionally metadata like date or source count. Organized by category (entities, concepts, sources, etc.). The LLM updates it on every ingest. When answering a query, the LLM reads the index first to find relevant pages, then drills into them. This works surprisingly well at moderate scale (~100 sources, ~hundreds of pages) and avoids the need for embedding-based RAG infrastructure.
log.md is chronological. It's an append-only record of what happened and when — ingests, queries, lint passes. A useful tip: if each entry starts with a consistent prefix (e.g. ## [2026-04-02] ingest | Article Title), the log becomes parseable with simple unix tools — grep "^## \[" log.md | tail -5 gives you the last 5 entries. The log gives you a timeline of the wiki's evolution and helps the LLM understand what's been done recently.

```
## [2026-04-02] ingest | Article Title
```


```
grep "^## \[" log.md | tail -5
```

## Optional: CLI tools
At some point you may want to build small tools that help the LLM operate on the wiki more efficiently. A search engine over the wiki pages is the most obvious one — at small scale the index file is enough, but as the wiki grows you want proper search. [qmd](https://github.com/tobi/qmd) is a good option: it's a local search engine for markdown files with hybrid BM25/vector search and LLM re-ranking, all on-device. It has both a CLI (so the LLM can shell out to it) and an MCP server (so the LLM can use it as a native tool). You could also build something simpler yourself — the LLM can help you vibe-code a naive search script as the need arises.

## Tips and tricks
- Obsidian Web Clipper is a browser extension that converts web articles to markdown. Very useful for quickly getting sources into your raw collection.
- Download images locally. In Obsidian Settings → Files and links, set "Attachment folder path" to a fixed directory (e.g. raw/assets/). Then in Settings → Hotkeys, search for "Download" to find "Download attachments for current file" and bind it to a hotkey (e.g. Ctrl+Shift+D). After clipping an article, hit the hotkey and all images get downloaded to local disk. This is optional but useful — it lets the LLM view and reference images directly instead of relying on URLs that may break. Note that LLMs can't natively read markdown with inline images in one pass — the workaround is to have the LLM read the text first, then view some or all of the referenced images separately to gain additional context. It's a bit clunky but works well enough.
- Obsidian's graph view is the best way to see the shape of your wiki — what's connected to what, which pages are hubs, which are orphans.
- Marp is a markdown-based slide deck format. Obsidian has a plugin for it. Useful for generating presentations directly from wiki content.
- Dataview is an Obsidian plugin that runs queries over page frontmatter. If your LLM adds YAML frontmatter to wiki pages (tags, dates, source counts), Dataview can generate dynamic tables and lists.
- The wiki is just a git repo of markdown files. You get version history, branching, and collaboration for free.

```
raw/assets/
```

## Why this works
The tedious part of maintaining a knowledge base is not the reading or the thinking — it's the bookkeeping. Updating cross-references, keeping summaries current, noting when new data contradicts old claims, maintaining consistency across dozens of pages. Humans abandon wikis because the maintenance burden grows faster than the value. LLMs don't get bored, don't forget to update a cross-reference, and can touch 15 files in one pass. The wiki stays maintained because the cost of maintenance is near zero.
The human's job is to curate sources, direct the analysis, ask good questions, and think about what it all means. The LLM's job is everything else.
The idea is related in spirit to Vannevar Bush's Memex (1945) — a personal, curated knowledge store with associative trails between documents. Bush's vision was closer to this than to what the web became: private, actively curated, with the connections between documents as valuable as the documents themselves. The part he couldn't solve was who does the maintenance. The LLM handles that.

## Note
This document is intentionally abstract. It describes the idea, not a specific implementation. The exact directory structure, the schema conventions, the page formats, the tooling — all of that will depend on your domain, your preferences, and your LLM of choice. Everything mentioned above is optional and modular — pick what's useful, ignore what isn't. For example: your sources might be text-only, so you don't need image handling at all. Your wiki might be small enough that the index file is all you need, no search engine required. You might not care about slide decks and just want markdown pages. You might want a completely different set of output formats. The right way to use this is to share it with your LLM agent and work together to instantiate a version that fits your needs. The document's only job is to communicate the pattern. Your LLM can figure out the rest.

### [Anboias](https://gist.github.com/Anboias) commented [Apr 7, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6086619#gistcomment-6086619)
[Anboias](https://gist.github.com/Anboias)
[Apr 7, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6086619#gistcomment-6086619)
I have my bot CONSTANTLY push gists... when in mid development - Ill often tell them "OK Great, now publish all this to a gist, give visuals, diagrams as SVGs - include mermaid and sankey logic as appropriate, give me the link" <-- Its a wonderful tool, then I just push Gists between frontiers, like having [@grok](https://github.com/grok) read them, then publish a response for claude and my agents etc... USE MORE GISTS!!
This one might prove handy too [https://saved.md](https://saved.md)
Sorry, something went wrong.

### Uh oh!
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

### [monksy](https://gist.github.com/monksy) commented [Apr 7, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6086642#gistcomment-6086642)
[monksy](https://gist.github.com/monksy)
[Apr 7, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6086642#gistcomment-6086642)
Any work being done on Joplin for this?
Sorry, something went wrong.

### Uh oh!
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

### [visakadev](https://gist.github.com/visakadev) commented [Apr 7, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6086647#gistcomment-6086647)
[visakadev](https://gist.github.com/visakadev)
[Apr 7, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6086647#gistcomment-6086647)
wdyt about this, sounds like a neat implementation of the principles ? [https://github.com/milla-jovovich/mempalace](https://github.com/milla-jovovich/mempalace)
MemPalace is solid, but it's solving a different problem than the wiki pattern. It's a semantic search engine — you ask "how does auth work?" and it finds relevant chunks across your repos. That's RAG, not a wiki. Karpathy's key insight is compilation over retrieval. Instead of re-finding and re-piecing together the answer every time, the AI writes it down once as interlinked markdown pages and keeps them current. The knowledge compounds — cross-references are already there, contradictions already flagged. Where MemPalace fits really well is as the discovery layer underneath the wiki. During ingest, the AI uses MemPalace to find the right source files across repos, then compiles that into wiki pages. During queries, it's the fallback when the wiki doesn't cover something yet. But the wiki is what turns scattered search results into connected understanding. tl;dr: MemPalace finds things. A wiki connects things. They're complementary layers
Sorry, something went wrong.

### Uh oh!
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

### [torchy55](https://gist.github.com/torchy55) commented [Apr 7, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6086665#gistcomment-6086665)
[torchy55](https://gist.github.com/torchy55)
[Apr 7, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6086665#gistcomment-6086665)
g of me demonstrating this. This is most certainly the way, as far as I am concerned. T
Can you post how?
Sorry, something went wrong.

### Uh oh!
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

### [asong56](https://gist.github.com/asong56) commented [Apr 7, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6086671#gistcomment-6086671)
[asong56](https://gist.github.com/asong56)
[Apr 7, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6086671#gistcomment-6086671)
One disadvantage might be that AI hallucinations can become permanently embedded as facts, causing errors to propagate. It also has maintenance burden, you have to check and clean the notes.
Sorry, something went wrong.

### Uh oh!
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

### [jeovanimeza92-code](https://gist.github.com/jeovanimeza92-code) commented [Apr 7, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6086676#gistcomment-6086676)
[jeovanimeza92-code](https://gist.github.com/jeovanimeza92-code)
[Apr 7, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6086676#gistcomment-6086676)
?
Sorry, something went wrong.

### Uh oh!
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

### [asakin](https://gist.github.com/asakin) commented [Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6086743#gistcomment-6086743)
[asakin](https://gist.github.com/asakin)
[Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6086743#gistcomment-6086743)
I built this out. [github.com/asakin/llm-context-base](https://github.com/asakin/llm-context-base) I've been running a version of this pattern as my "personal operating system" for a few months. Some things I learned that went into the implementation:
- No index.md - the AI scans summaries and tags at query time instead of maintaining a central index. Scales better and nothing gets stale. ([@bitsofchris](https://github.com/bitsofchris) this addresses the "what happens at 1000 files" concern)
- Bold-field metadata over YAML - Type: knowledge instead of frontmatter. Every LLM parses it correctly, it renders in any markdown viewer, and non-technical users don't need to learn YAML syntax.
- Training period - the system starts chatty, asks questions, learns your conventions, then goes quiet. 30 days (configurable) of calibration, then it just executes. The wiki literally trains its own AI agent.
- Decision learning loops - decisions have an Outcome section you fill in later. When you're making a new decision, the AI surfaces past decisions and what actually happened. Your wiki learns from your mistakes.
- Context optimization - the system periodically reviews its own instruction efficiency. Flags bloated files, suggests splitting, compacts with your approval. The wiki maintains itself.
[@bitsofchris](https://github.com/bitsofchris)
Works with Claude Code, Cursor, Copilot, Windsurf, Codex CLI, Gemini CLI - ships as an Obsidian vault.
Built from patterns refined over months of daily use, and adapted to comply with [@karpathy](https://github.com/karpathy) 's pattern. Happy to answer questions.
Sorry, something went wrong.

### Uh oh!
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

### [andresfelzul](https://gist.github.com/andresfelzul) commented [Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6086744#gistcomment-6086744) • edited Loading Uh oh! There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).
[andresfelzul](https://gist.github.com/andresfelzul)
[Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6086744#gistcomment-6086744)

### Uh oh!
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).
[@karpathy](https://github.com/karpathy) Hace un año y medio falleció mi mamá. Y, como muchos, me quedé con conversaciones pendientes… preguntas sin hacer… y respuestas que solo el tiempo empieza a revelar.
Mi mamá escribió un libro: “El Parkinson, mi amigo, mi maestro”. Un testimonio profundo, valiente y lleno de aprendizajes sobre la vida, la resiliencia y el sentido.
Hace unos meses tomé una decisión poco convencional: subí su libro a un sistema de IA tipo RAG. aquí comparto mi publicación: [https://www.linkedin.com/posts/andres-felipe-zuluaga-echeverry-a5185421_ia-ia-ia-activity-7347605447505244161-PDd1?utm_source=social_share_send&utm_medium=member_desktop_web&rcm=ACoAAASTJd0BVlK3PwZxp0sMR36aXx8EE3X-qNE](https://www.linkedin.com/posts/andres-felipe-zuluaga-echeverry-a5185421_ia-ia-ia-activity-7347605447505244161-PDd1?utm_source=social_share_send&utm_medium=member_desktop_web&rcm=ACoAAASTJd0BVlK3PwZxp0sMR36aXx8EE3X-qNE)
Y empezó a pasar algo poderoso.
Comencé a tener “conversaciones” con ese conocimiento. Le hacía preguntas… y de alguna manera, mi mamá a través de sus palabras me respondía, me cuestionaba, me aterrizaba.
No era magia. Era memoria estructurada.
Pero ahora, con la evolución hacia modelos como LLM Wiki y herramientas como ElevenLabs, me doy cuenta de algo aún más profundo:
👉 Ya no se trata solo de consultar información. 👉 Se trata de reconstruir una presencia.
Hoy veo la posibilidad de ir más allá del libro:
- integrar sus videos
- incluir mensajes de voz
- correos
- reflexiones sueltas
- incluso momentos cotidianos
Y convertir todo eso en una “wiki viva” de su pensamiento, su esencia y su forma de ver el mundo.
No para reemplazarla. Eso es imposible.
Sino para preservar algo invaluable: su manera de hacer preguntas. su forma de interpretar la vida. su voz interior.
Esto abre una conversación mucho más grande:
¿Y si la tecnología no solo sirve para automatizar… sino para amplificar lo más humano que tenemos?
¿Y si podemos construir legados vivos, que sigan inspirando, cuestionando y acompañando a quienes vienen después?
Para mí, esto ya no es solo tecnología. Es una nueva forma de memoria. Una nueva forma de conexión. Y, de alguna manera… una nueva forma de amor.
Sorry, something went wrong.

### Uh oh!
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

### [earaizapowerera](https://gist.github.com/earaizapowerera) commented [Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6086745#gistcomment-6086745)
[earaizapowerera](https://gist.github.com/earaizapowerera)
[Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6086745#gistcomment-6086745)
Strongly agree with the idea of a structured, accumulative knowledge wiki. I’ve been working on a related OpenClaw skill around personal knowledge management — especially for tracing how an idea, stance, or method becomes mature over time, and how later scattered events contribute back to an earlier core proposition. [https://clawhub.ai/lakendocean/idea-trace](https://gist.github.com/karpathy/url)
I tried the link. Didn't work. (404)
Sorry, something went wrong.

### Uh oh!
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

### [earaizapowerera](https://gist.github.com/earaizapowerera) commented [Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6086747#gistcomment-6086747)
[earaizapowerera](https://gist.github.com/earaizapowerera)
[Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6086747#gistcomment-6086747)
Hace un año y medio falleció mi mamá. Y, como muchos, me quedé con conversaciones pendientes… preguntas sin hacer… y respuestas que solo el tiempo empieza a revelar.
Mi mamá escribió un libro: “El Parkinson, mi amigo, mi maestro”. Un testimonio profundo, valiente y lleno de aprendizajes sobre la vida, la resiliencia y el sentido.
Hace unos meses tomé una decisión poco convencional: subí su libro a un sistema de IA tipo RAG. aquí comparto mi publicación: [https://www.linkedin.com/posts/andres-felipe-zuluaga-echeverry-a5185421_ia-ia-ia-activity-7347605447505244161-PDd1?utm_source=social_share_send&utm_medium=member_desktop_web&rcm=ACoAAASTJd0BVlK3PwZxp0sMR36aXx8EE3X-qNE](https://www.linkedin.com/posts/andres-felipe-zuluaga-echeverry-a5185421_ia-ia-ia-activity-7347605447505244161-PDd1?utm_source=social_share_send&utm_medium=member_desktop_web&rcm=ACoAAASTJd0BVlK3PwZxp0sMR36aXx8EE3X-qNE)
Y empezó a pasar algo poderoso.
Comencé a tener “conversaciones” con ese conocimiento. Le hacía preguntas… y de alguna manera, mi mamá a través de sus palabras me respondía, me cuestionaba, me aterrizaba.
No era magia. Era memoria estructurada.
Pero ahora, con la evolución hacia modelos como LLM Wiki y herramientas como ElevenLabs, me doy cuenta de algo aún más profundo:
👉 Ya no se trata solo de consultar información. 👉 Se trata de reconstruir una presencia.
Hoy veo la posibilidad de ir más allá del libro:

```
* integrar sus videos * incluir mensajes de voz * correos * reflexiones sueltas * incluso momentos cotidianos
```


```
* integrar sus videos * incluir mensajes de voz * correos * reflexiones sueltas * incluso momentos cotidianos
```

Y convertir todo eso en una “wiki viva” de su pensamiento, su esencia y su forma de ver el mundo.
No para reemplazarla. Eso es imposible.
Sino para preservar algo invaluable: su manera de hacer preguntas. su forma de interpretar la vida. su voz interior.
Esto abre una conversación mucho más grande:
¿Y si la tecnología no solo sirve para automatizar… sino para amplificar lo más humano que tenemos?
¿Y si podemos construir legados vivos, que sigan inspirando, cuestionando y acompañando a quienes vienen después?
Para mí, esto ya no es solo tecnología. Es una nueva forma de memoria. Una nueva forma de conexión. Y, de alguna manera… una nueva forma de amor.
muy interesante. ¿El libro lo divide en capítulos o "pedazos" más pequeños? o cómo estructuró el wiki? De acuerdo que programar/automatizar solo es una de mil aplicaciones.
Sorry, something went wrong.

### Uh oh!
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

### [earaizapowerera](https://gist.github.com/earaizapowerera) commented [Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6086756#gistcomment-6086756)
[earaizapowerera](https://gist.github.com/earaizapowerera)
[Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6086756#gistcomment-6086756)
wdyt about this, sounds like a neat implementation of the principles ? [https://github.com/milla-jovovich/mempalace](https://github.com/milla-jovovich/mempalace)
Clever project, but it solves a different problem. MemPalace is about recall — "what did I say 3 months ago?" It stores conversations verbatim and searches them. Karpathy's approach is about compiled knowledge — the LLM doesn't just store, it builds structured understanding with connections and summaries. That's a fundamentally different thing. I've been building along Karpathy's line but for teams — hierarchical knowledge with automatic inheritance, where every element knows its place in the structure. The quick explanation in: [https://waykee.com/](https://waykee.com/) (open source in a few days)
Sorry, something went wrong.

### Uh oh!
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

### [aarora79](https://gist.github.com/aarora79) commented [Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6086770#gistcomment-6086770)
[aarora79](https://gist.github.com/aarora79)
[Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6086770#gistcomment-6086770)
My take on this idea -> [https://github.com/aarora79/personal-knowledge-base](https://github.com/aarora79/personal-knowledge-base), extends it by saying we can have a Claude Skill do the raw -> wiki conversion -> query | lint; generate a visual graph that you can see linking the concepts.
Sorry, something went wrong.

### Uh oh!
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

### [arpitnath](https://gist.github.com/arpitnath) commented [Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6086861#gistcomment-6086861)
[arpitnath](https://gist.github.com/arpitnath)
[Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6086861#gistcomment-6086861)
I have been running a version of this similar pattern. Started from a DNS analogy, instead of everything being a blob of text, what if we have typed records, each record has a type (SUMMARY, META, SOURCE, ALIAS, COLLECTION) that tells the agent how to consume it. So when the agent searches for "obsidian sync", the library knows the introduction file is the canonical answer and not one of the 42 other files that mention it.
Ran benchmarks on 3 public corpora (quartz -76 files, obsidian help - 171 files, mdn - 14k files), on mdn, grep returns 1212 files per query unranked and blink-query returns 5 ranked in 10ms. The speed gap gets bigger as corpus grows , 28x faster on small wikis, 83x on mdn. On the 14k files, grep returns an average of 1212 unranked files per query because common terms like "Promise" appear in 1314 files, "DOM" in 9363. blink returns top 5 ranked. Therefore, the agent reads ~242x fewer files to find the answer.
Where it currently breaks or struggles: entity queries on very common terms where BM25 can't pick the canonical page without graph-aware signals.
Whole benchmark is one command: npm run benchmark​ [https://github.com/arpitnath/blink-query](https://github.com/arpitnath/blink-query)

```
npm run benchmark​
```

Sorry, something went wrong.

### Uh oh!
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

### [xoai](https://gist.github.com/xoai) commented [Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6086902#gistcomment-6086902)
[xoai](https://gist.github.com/xoai)
[Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6086902#gistcomment-6086902)
Here are some updates from [sage-wiki](https://github.com/xoai/sage-wiki) as I work on [building a comprehensive tool](https://x.com/xoai/status/2040936964799795503) based on this idea.
- 
TUI (Text User Interface): In addition to using Obsidian as a viewer for your wiki, you now have two built-in alternatives: a web UI and a TUI. The TUI offers a four-tab terminal dashboard, allowing you to browse articles with rendered Markdown, perform fuzzy searches with previews, engage in streaming Q&A with citations, and access a live compile dashboard that monitors your sources and automatically recompiles them. Remember, this is your data and your tool, so you are free to choose whichever viewer you feel most comfortable with.

- 
Cost Optimization: This feature is particularly beneficial for those with a large vault of documents (for example, 10,000 or more). It includes prompt caching (saving 50-90% on input tokens from providers like Anthropic, Gemini, or OpenAI), batch API support (using compile --batch for a 50% discount via asynchronous processing), and cost tracking that provides a breakdown after every compile. You can also use compile --estimate to preview costs before committing. Additionally, there's an auto-batch mode that activates when you have more than ten sources to process. The compile pipeline now clearly shows what you're spending and where your costs are coming from, which is crucial once your wiki expands beyond just a few dozen sources.

TUI (Text User Interface): In addition to using Obsidian as a viewer for your wiki, you now have two built-in alternatives: a web UI and a TUI. The TUI offers a four-tab terminal dashboard, allowing you to browse articles with rendered Markdown, perform fuzzy searches with previews, engage in streaming Q&A with citations, and access a live compile dashboard that monitors your sources and automatically recompiles them. Remember, this is your data and your tool, so you are free to choose whichever viewer you feel most comfortable with.
Cost Optimization: This feature is particularly beneficial for those with a large vault of documents (for example, 10,000 or more). It includes prompt caching (saving 50-90% on input tokens from providers like Anthropic, Gemini, or OpenAI), batch API support (using compile --batch for a 50% discount via asynchronous processing), and cost tracking that provides a breakdown after every compile. You can also use compile --estimate to preview costs before committing. Additionally, there's an auto-batch mode that activates when you have more than ten sources to process. The compile pipeline now clearly shows what you're spending and where your costs are coming from, which is crucial once your wiki expands beyond just a few dozen sources.

```
compile --batch
```


```
compile --estimate
```

sage-wiki is a single, cross-platform binary that works with any provider. Just drop your files into a folder, and you'll have a wiki ready to go. You can even turn it into an MCP so any LLM can work with your "second brain" easily.
Feel free to provide feedback and contribute more.
Sorry, something went wrong.

### Uh oh!
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

### [marciopuga](https://gist.github.com/marciopuga) commented [Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6086969#gistcomment-6086969)
[marciopuga](https://gist.github.com/marciopuga)
[Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6086969#gistcomment-6086969)
Amazing thinking as usual [@karpathy](https://github.com/karpathy)! I particularly loved the Memex reference
The Memex was a hypothetical device — envisioned as a mechanized desk with microfilm storage — that would let a person store all their books, records, and communications, then retrieve and link them together through associative "trails." Bush argued that the human mind works by association rather than indexing, and that our tools for managing knowledge should reflect that.
This was my take on Personal Knowledge over text: [https://github.com/marciopuga/cog](https://github.com/marciopuga/cog)
Sorry, something went wrong.

### Uh oh!
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

### [Pratiyush](https://gist.github.com/Pratiyush) commented [Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6087018#gistcomment-6087018)
[Pratiyush](https://gist.github.com/Pratiyush)
[Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6087018#gistcomment-6087018)
[https://github.com/Pratiyush/llm-wiki](https://github.com/Pratiyush/llm-wiki) - Work in progress - HELP in Issues and Suggestions Needed
Sorry, something went wrong.

### Uh oh!
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

### [anzal1](https://gist.github.com/anzal1) commented [Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6087062#gistcomment-6087062)
[anzal1](https://gist.github.com/anzal1)
[Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6087062#gistcomment-6087062)
Took this pattern and built it into a zero-config CLI: npx quicky-wiki init auto-detects your API keys and picks the best model. Full pipeline — ingest, query, lint, prune, serve.

```
npx quicky-wiki init
```


```
ingest
```


```
query
```


```
lint
```


```
prune
```


```
serve
```

A few things I added beyond the core pattern:
- Confidence-scored claims — every fact gets a confidence score and source citation. Single-source claims stay low-confidence; corroborated claims across sources get promoted. Helps with [@asong56](https://github.com/asong56)'s hallucination concern — contested claims are surfaced, not buried.
- Temporal tracking — claims are timestamped so you can see knowledge evolution and flag stale facts.
- Live dashboard — Obsidian-style force-directed graph (Canvas 2D with level-of-detail for performance at 300+ nodes), plus built-in LLM chat for querying the wiki directly.
- Multi-provider — Anthropic, OpenAI, Gemini, Ollama, or any openai-compatible endpoint (Groq, Together, vLLM, LM Studio).
[@asong56](https://github.com/asong56)
Works with markdown files, URLs, or any text source. One command to get started:

```
npx quicky-wiki init
```


```
npx quicky-wiki init
```

[https://github.com/anzal1/quicky-wiki](https://github.com/anzal1/quicky-wiki)
Sorry, something went wrong.

### Uh oh!
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

### [dolzenko](https://gist.github.com/dolzenko) commented [Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6087135#gistcomment-6087135)
[dolzenko](https://gist.github.com/dolzenko)
[Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6087135#gistcomment-6087135)
Is there any tool (or will it even make sense at all) to route all my recorded codex cli sessions to something like this to build the KB out of months of work with the agent?
Sorry, something went wrong.

### Uh oh!
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

[Bytekron](https://gist.github.com/Bytekron)
[Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6087197#gistcomment-6087197)
This is one of the first writeups on “LLM + knowledge base” that actually clicks for me, because it shifts the focus away from pure retrieval and toward accumulation. The line of thinking that stood out most is that most document workflows keep forcing the model to rediscover the same patterns over and over again, while a maintained wiki turns that repeated effort into a durable asset. That feels much closer to how people actually build expertise.
What I like here is that this is not just “RAG but nicer.” The important difference is the idea of synthesis as a first-class artifact. Instead of treating every answer as disposable chat output, the useful parts get promoted into pages, relationships, summaries, contradictions, and cross-links. That is a much better mental model for long-term work, especially when the source material is messy, repetitive, or constantly changing.
I also think this pattern becomes especially powerful in narrow domains where there is a lot of semi-structured information and a lot of recurring questions. For example, I run projects in the Minecraft ecosystem like Minelist and MinecraftServer.buzz, and one thing that becomes obvious very quickly is how much information piles up around servers, versions, gamemodes, metadata quality, vote systems, SEO content, duplicate detection, moderation notes, and historical changes. A traditional search layer helps you retrieve fragments, but it does not really “understand the estate” over time. A maintained wiki layer could.
In that kind of setting, an LLM-maintained wiki could become the connective tissue between raw scraped data, editorial notes, taxonomy decisions, and user-facing content. One page could track how a specific server evolved over time. Another could map tag ambiguity across categories like SMP, survival, vanilla, or modded. Another could explain why certain duplicate-host patterns appear across listings. Over weeks or months, that becomes much more valuable than a pile of disconnected documents or one-off prompts.
I also really agree with the point that the hardest part of knowledge systems is not storing information, it is maintenance. Humans are usually willing to create a page once, but they are much less willing to update ten related pages, fix broken links, revise old claims, and keep a taxonomy coherent. That is exactly the kind of repetitive but context-sensitive work LLMs are surprisingly well suited for. Not because they are always right, but because they make the cost of maintaining structure low enough that the structure can actually survive.
The “wiki is the codebase” analogy is also very strong. It suggests a workflow where the human’s role is curation, judgment, and direction, while the model handles the mechanical burden of integration and refactoring. That feels like a more realistic and productive division of labor than pretending the model should simply answer everything on demand from a pile of uploads.
One thing I would be very interested in is how people handle quality control once the wiki grows beyond a hobby-sized vault. For example, how do you best represent confidence, source freshness, disagreements between sources, and unresolved ambiguities without turning the whole thing into bureaucratic overhead? There is probably a sweet spot where the schema is structured enough to keep the system disciplined, but not so rigid that the workflow becomes annoying.
I also wonder whether the best implementations of this idea will end up being domain-specific rather than universal. A personal research wiki, a company knowledge base, and a vertical operational system probably want different page types, different update policies, and different notions of truth. The pattern feels general, but the actual payoff probably comes from tailoring it hard to a specific domain.
Either way, this gist describes something much more interesting than the usual “chat with your docs” framing. It treats knowledge work as something cumulative, revisable, and alive. Im gonna use it as a reference for a blog post on [Minelist](https://minelist.io) and [MinecraftServer.buzz](https://minecraftserver.buzz) about LLM's and Minecraft. That feels much closer to how serious research, operations, and even niche content businesses actually work in practice.

### [Bytekron](https://gist.github.com/Bytekron) commented [Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6087197#gistcomment-6087197)
Sorry, something went wrong.

### Uh oh!
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

### [MehmetGoekce](https://gist.github.com/MehmetGoekce) commented [Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6087198#gistcomment-6087198)
[MehmetGoekce](https://gist.github.com/MehmetGoekce)
[Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6087198#gistcomment-6087198)
Built an implementation using Claude Code + Logseq/Obsidian with a two-layer cache architecture: L1 (auto-loaded rules in Claude's memory) + L2 (on-demand wiki in Logseq/Obsidian). The key insight was that not all knowledge belongs in the wiki — critical rules must be auto-loaded every session. Includes a /wiki skill with ingest, query, lint, and a schema that enforces page types and cross-references. Setup in 5 minutes via ./setup.sh. Full write-up: [https://mehmetgoekce.substack.com/p/i-built-karpathys-llm-wiki-with-claude](https://mehmetgoekce.substack.com/p/i-built-karpathys-llm-wiki-with-claude) Repo: [https://github.com/MehmetGoekce/llm-wiki](https://github.com/MehmetGoekce/llm-wiki)
Sorry, something went wrong.

### Uh oh!
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

### [jakob1379](https://gist.github.com/jakob1379) commented [Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6087204#gistcomment-6087204)
[jakob1379](https://gist.github.com/jakob1379)
[Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6087204#gistcomment-6087204)
Is there any tool (or will it even make sense at all) to route all my recorded codex cli sessions to something like this to build the KB out of months of work with the agent?
bash?
for convo in $(insert command that yields each conversation to an array); do <codex|claude|...|> add this to my wiki; done

```
for convo in $(insert command that yields each conversation to an array); do <codex|claude|...|> add this to my wiki; done
```

Sorry, something went wrong.

### Uh oh!
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

### [shibing624](https://gist.github.com/shibing624) commented [Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6087206#gistcomment-6087206)
[shibing624](https://gist.github.com/shibing624)
[Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6087206#gistcomment-6087206)
Great writeup! Re: the CLI tools section where you mention qmd as a local search engine for the wiki — wanted to share an alternative approach we've been working on: [TreeSearch](https://github.com/shibing624/TreeSearch).
The core difference: two fundamentally different retrieval philosophies.
QMD takes the RAG-enhanced route: chunk documents → BM25 + vector search → LLM query expansion → LLM re-ranking. It runs 3 local models (~2GB) and gets strong semantic results, but at the cost of model loading and inference latency.
TreeSearch takes the structure-first route: no chunking, no embeddings, no models at all. Instead of splitting documents into fixed-size chunks and retrieving by vector similarity (which destroys heading hierarchy), it parses documents into tree structures based on their natural heading hierarchy, then uses SQLite FTS5 keyword matching with structure-aware scoring (title match, term overlap, IDF weighting, generic section demotion). Zero models, pure CPU, millisecond latency.
Quick comparison:
For the wiki pattern specifically, TreeSearch is a good fit because wiki pages are inherently well-structured markdown with heading hierarchies — exactly the kind of documents where structure-aware retrieval shines. And since it's zero-dependency (just SQLite), it adds no infrastructure overhead to the wiki setup.

```
pip install pytreesearch treesearch "How does auth work?" wiki/
```

Both tools are complementary — QMD for when you need deep semantic understanding, TreeSearch for when structure and speed matter most. The right choice depends on your wiki's size and query patterns.
Sorry, something went wrong.

### Uh oh!
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

### [a-ml](https://gist.github.com/a-ml) commented [Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6087287#gistcomment-6087287)
[a-ml](https://gist.github.com/a-ml)
[Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6087287#gistcomment-6087287)
Been thinking about this a lot lately. We've been trying to do this with cognition. Not the things you know, but the way you actually think. The heuristics you apply without noticing, the tensions between things you believe, the mental models that shape every decision before you're even aware you're making one.
The hard part isn't storage, it's extraction. You can't just ask someone what their values are. You have to start from a real decision. What did you reject? What tradeoff actually mattered to you? What rule did you apply on instinct? Our approach, an LLM reads through conversation transcripts on a schedule and classifies what it finds against a strict hierarchy of types. Decision rule, framework, tension, preference. "Idea" is last resort. Everything gets a confidence score and an epistemic tag so the system knows the difference between something you're sure about and something you're still working out.
Typed edges rather than a flat list. Supports, contradicts, evolved_into, depends_on. That's what makes it traversable rather than just searchable. An agent can walk the contradictions in your own reasoning, find connections between domains you never explicitly linked, or surface something you've been circling for weeks without naming it.
Nodes decay too, which felt important. Values hold. Ideas fade fast. The graph is supposed to model what's live in your thinking right now, not accumulate everything you've ever said, but that's probably a personal choice.
Mine has 8,000+ nodes at this point, 16 MCP tools, runs as an npx server. Curious whether the decay model resonates with you or whether you'd approach that part differently.
[https://github.com/multimail-dev/thinking-mcp](https://github.com/multimail-dev/thinking-mcp)
Very interesting
Sorry, something went wrong.

### Uh oh!
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

### [xoai](https://gist.github.com/xoai) commented [Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6087294#gistcomment-6087294)
[xoai](https://gist.github.com/xoai)
[Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6087294#gistcomment-6087294)
Is there any tool (or will it even make sense at all) to route all my recorded codex cli sessions to something like this to build the KB out of months of work with the agent?
[sage-wiki](https://github.com/xoai/sage-wiki) can act as an MCP (Model Context Protocol) server, letting you save knowledge directly from your AI conversations into your wiki. Instead of losing insights when a chat session ends, you can tell your AI to capture them.
Say you're debugging a performance issue with your AI and discover that the bottleneck is in the database connection pool, not the query itself. At the end of the session:
"Capture the key findings from this debugging session. Tag with postgres, performance."
The AI extracts items like:
- "connection-pool-bottleneck" - The actual performance issue was exhausted connections, not slow queries
- "pgbouncer-transaction-mode" - Transaction-level pooling resolved the issue; session-level was causing connection hoarding
These become source files that the compiler weaves into your wiki's knowledge graph. For old conversations, you can export data from ChatGPT or Claude and put it in your wiki folder.
Sorry, something went wrong.

### Uh oh!
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

### [Helleeni](https://gist.github.com/Helleeni) commented [Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6087328#gistcomment-6087328)
[Helleeni](https://gist.github.com/Helleeni)
[Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6087328#gistcomment-6087328)
This is so brilliant! I built a personal Wiki containing my programming projects over a lunch hour (though burnt through my tokens for one Claude Code session :-). Anyway, great idea and so easy to implement. Just sharing the prompt! Thank you so much!
Sorry, something went wrong.

### Uh oh!
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

### [ZimoLiao](https://gist.github.com/ZimoLiao) commented [Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6087344#gistcomment-6087344)
[ZimoLiao](https://gist.github.com/ZimoLiao)
[Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6087344#gistcomment-6087344)
This resonates deeply — and it’s exciting to see this idea articulated so clearly.
We’ve actually been building something along these lines with [ScholarAIO](https://github.com/ZimoLiao/scholaraio), but pushing it one step further toward a fully executable system.
The core alignment is strong: instead of treating knowledge as something to retrieve at query time, we treat it as something to compile, structure, and continuously evolve into a persistent, navigable knowledge base. In practice, this looks very much like an LLM-maintained wiki layer that grows over time.
Where ScholarAIO goes beyond the “LLM Wiki” concept is in closing the loop between knowledge and action.
- The wiki is not just a passive memory — it becomes an operational substrate for agents.
- Knowledge doesn’t stop at summaries or cross-references — it is directly translated into executable workflows, scripts, and tool interactions.
- Every interaction (successful or failed) can be written back, turning the system into a self-improving research environment, not just a knowledge store.
In other words, instead of:
sources → wiki → answers
we are building toward:
sources → evolving wiki → agents → tools → results → wiki
Another key difference is scalability. Because the system is built around modular ingestion + schema-driven structuring + tool abstraction, it can expand to new domains at near-zero marginal cost. Adding a new field is no longer a matter of rebuilding pipelines — it’s simply a matter of plugging in new documentation and tool interfaces, and letting the system compile itself.
What emerges is less a “better RAG” and more a domain-agnostic knowledge-to-action engine.
Really exciting direction — it feels like this pattern (LLM as compiler of living knowledge systems) is going to underpin a lot of the next generation of agentic software.
Sorry, something went wrong.

### Uh oh!
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

### [KaifAhmad1](https://gist.github.com/KaifAhmad1) commented [Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6087371#gistcomment-6087371)
[KaifAhmad1](https://gist.github.com/KaifAhmad1)
[Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6087371#gistcomment-6087371)
[@karpathy](https://github.com/karpathy) This framing of compilation over retrieval really resonates. We’ve been building something similar with Semantica — a semantic layer that turns unstructured data into structured, explainable knowledge graphs with provenance and reasoning. Feels like this could become a core layer for agent systems. [https://github.com/Hawksight-AI/semantica](https://github.com/Hawksight-AI/semantica)
Sorry, something went wrong.

### Uh oh!
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

### [realaaa](https://gist.github.com/realaaa) commented [Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6087430#gistcomment-6087430)
[realaaa](https://gist.github.com/realaaa)
[Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6087430#gistcomment-6087430)
this is a great concept - thanks for sharing ! I was thinking along the lined of doing such for my personal PKI based on TiddlyWiki
plus also for commercial ones in my case those would be Nextcloud Collectives type wikis
Sorry, something went wrong.

### Uh oh!
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

### [Foroutsweg](https://gist.github.com/Foroutsweg) commented [Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6087431#gistcomment-6087431)
[Foroutsweg](https://gist.github.com/Foroutsweg)
[Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6087431#gistcomment-6087431)
Nice
Sorry, something went wrong.

### Uh oh!
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

### [aaronmrosenthal](https://gist.github.com/aaronmrosenthal) commented [Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6087492#gistcomment-6087492) • edited Loading Uh oh! There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).
[aaronmrosenthal](https://gist.github.com/aaronmrosenthal)
[Apr 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6087492#gistcomment-6087492)

### Uh oh!
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).
Added to ToolKode, Thank you. [https://www.npmjs.com/package/@toolkit-cli/toolkode](https://www.npmjs.com/package/@toolkit-cli/toolkode) WikiGraph engine. Knowledge compounds across sessions.
Sorry, something went wrong.

### Uh oh!
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).
[Sign up for free](https://gist.github.com/join?source=comment-gist)
[Sign in to comment](https://gist.github.com/login?return_to=https%3A%2F%2Fgist.github.com%2Fkarpathy%2F442a6bf555914893e9891c11519de94f)

- 
            [Terms](https://docs.github.com/site-policy/github-terms/github-terms-of-service)

- 
            [Privacy](https://docs.github.com/site-policy/privacy-policies/github-privacy-statement)

- 
            [Security](https://github.com/security)

- 
            [Status](https://www.githubstatus.com/)

- 
            [Community](https://github.community/)

- 
            [Docs](https://docs.github.com/)

- 
            [Contact](https://support.github.com?tags=dotcom-footer)

- 


       Manage cookies



- 


      Do not share my personal information



[Terms](https://docs.github.com/site-policy/github-terms/github-terms-of-service)
[Privacy](https://docs.github.com/site-policy/privacy-policies/github-privacy-statement)
[Security](https://github.com/security)
[Status](https://www.githubstatus.com/)
[Community](https://github.community/)
[Docs](https://docs.github.com/)
[Contact](https://support.github.com?tags=dotcom-footer)

