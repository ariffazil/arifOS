#!/usr/bin/env python3
"""Workspace memory pipeline: retain -> recall -> reflect (+ semantic v1.1).

Canonical source:
  - workspace/memory/YYYY-MM-DD.md (human-editable markdown)

Derived stores:
  - workspace/.memory/index.sqlite   (SQLite + FTS5)
  - Qdrant collection (optional): openclaw_workspace_memory
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sqlite3
import stat
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path


RETAIN_HEADING = re.compile(r"^##\s+Retain\s*$", re.IGNORECASE)
HEADING = re.compile(r"^##\s+")
BULLET = re.compile(r"^-\s+")
FACT_PATTERN = re.compile(r"^(W|B|S|O(?:\(c=([0-9.]+)\))?)\s*(.*)$")
ENTITY_PATTERN = re.compile(r"@([A-Za-z0-9_.-]+)")
RETAIN_BULLET_PATTERN = re.compile(r"^\s*-\s+")
ENV_KEY_PATTERN = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=")

DEFAULT_ENV_FILE = "/root/XXX/.env.master"
DEFAULT_ENV_LINK = "/root/openclaw_data/.env"
REQUIRED_ENV_KEYS = (
    "QDRANT_URL",
    "QDRANT_API_KEY",
    "MEMORY_EMBED_MODEL",
    "MEMORY_QDRANT_COLLECTION",
)


@dataclass
class Fact:
    kind: str
    confidence: float | None
    content: str
    entities: list[str]
    source_path: str
    source_line: int
    source_date: str
    fact_hash: str


def ensure_dirs(workspace: Path) -> None:
    (workspace / ".memory").mkdir(parents=True, exist_ok=True)
    (workspace / "bank").mkdir(parents=True, exist_ok=True)
    (workspace / "bank" / "entities").mkdir(parents=True, exist_ok=True)


def db_connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def db_init(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS facts (
            id INTEGER PRIMARY KEY,
            kind TEXT NOT NULL,
            confidence REAL,
            content TEXT NOT NULL,
            entities_json TEXT NOT NULL,
            source_path TEXT NOT NULL,
            source_line INTEGER NOT NULL,
            source_date TEXT NOT NULL,
            fact_hash TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS facts_fts USING fts5(
            content,
            content='facts',
            content_rowid='id'
        );

        CREATE TRIGGER IF NOT EXISTS facts_ai AFTER INSERT ON facts BEGIN
            INSERT INTO facts_fts(rowid, content) VALUES (new.id, new.content);
        END;

        CREATE TRIGGER IF NOT EXISTS facts_ad AFTER DELETE ON facts BEGIN
            INSERT INTO facts_fts(facts_fts, rowid, content) VALUES ('delete', old.id, old.content);
        END;

        CREATE TRIGGER IF NOT EXISTS facts_au AFTER UPDATE ON facts BEGIN
            INSERT INTO facts_fts(facts_fts, rowid, content) VALUES ('delete', old.id, old.content);
            INSERT INTO facts_fts(rowid, content) VALUES (new.id, new.content);
        END;
        """
    )
    conn.commit()


def safe_json_get(url: str, headers: dict[str, str] | None = None) -> dict:
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=12) as resp:
        return json.loads(resp.read().decode("utf-8"))


def safe_json_post(
    url: str, payload: dict, headers: dict[str, str] | None = None
) -> dict:
    merged_headers = {"Content-Type": "application/json"}
    if headers:
        merged_headers.update(headers)
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=merged_headers,
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def safe_json_put(
    url: str, payload: dict, headers: dict[str, str] | None = None
) -> dict:
    merged_headers = {"Content-Type": "application/json"}
    if headers:
        merged_headers.update(headers)
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=merged_headers,
        method="PUT",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def parse_retain_facts(file_path: Path, workspace: Path) -> list[Fact]:
    lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    in_retain = False
    facts: list[Fact] = []
    source_date = file_path.stem

    for idx, raw_line in enumerate(lines, start=1):
        line = raw_line.rstrip()
        if RETAIN_HEADING.match(line):
            in_retain = True
            continue
        if in_retain and HEADING.match(line):
            in_retain = False
        if not in_retain:
            continue
        if not BULLET.match(line):
            continue

        bullet_text = BULLET.sub("", line).strip()
        match = FACT_PATTERN.match(bullet_text)
        if not match:
            kind = "summary"
            confidence = None
            content = bullet_text
        else:
            prefix, conf_raw, remainder = match.groups()
            kind_map = {"W": "world", "B": "experience", "S": "summary"}
            if prefix.startswith("O"):
                kind = "opinion"
                confidence = float(conf_raw) if conf_raw else 0.70
            else:
                kind = kind_map.get(prefix, "summary")
                confidence = None
            content = remainder.strip(" :")

        entities = sorted(set(ENTITY_PATTERN.findall(content)))
        rel_path = str(file_path.relative_to(workspace))
        fact_hash = hashlib.sha1(
            f"{rel_path}:{idx}:{content}".encode("utf-8")
        ).hexdigest()
        facts.append(
            Fact(
                kind=kind,
                confidence=confidence,
                content=content,
                entities=entities,
                source_path=rel_path,
                source_line=idx,
                source_date=source_date,
                fact_hash=fact_hash,
            )
        )

    return facts


def _extract_embedding(data: dict) -> list[float] | None:
    emb = data.get("embedding")
    if isinstance(emb, list) and emb:
        return [float(x) for x in emb]
    embs = data.get("embeddings")
    if isinstance(embs, list) and embs:
        first = embs[0]
        if isinstance(first, list) and first:
            return [float(x) for x in first]
    return None


def _resolve_embed_model() -> str:
    explicit = os.environ.get("MEMORY_EMBED_MODEL", "").strip()
    if explicit:
        return explicit

    base = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    candidates = [
        "bge-m3",
        "nomic-embed-text",
        "mxbai-embed-large",
        "bge-small-en-v1.5",
        "qwen2.5:3b",
    ]

    try:
        tags = safe_json_get(f"{base}/api/tags")
        names = {m.get("name", "") for m in tags.get("models", [])}
        for candidate in candidates:
            if candidate in names:
                return candidate
    except Exception:  # noqa: BLE001
        pass

    return "qwen2.5:3b"


def get_embedding(text: str) -> list[float]:
    """Get embedding from local Ollama, with endpoint compatibility fallback."""
    model = _resolve_embed_model()
    base = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434")

    errors: list[str] = []
    for endpoint, payload in (
        ("/api/embed", {"model": model, "input": text}),
        ("/api/embeddings", {"model": model, "prompt": text}),
    ):
        try:
            data = safe_json_post(f"{base}{endpoint}", payload)
            emb = _extract_embedding(data)
            if emb:
                return emb
            errors.append(f"{endpoint}: missing embedding payload")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{endpoint}: {exc}")

    raise RuntimeError(
        "Embedding failed for model "
        f"{model}. Set MEMORY_EMBED_MODEL or pull an embedding-capable model. "
        f"Details: {'; '.join(errors)}"
    )


def qdrant_headers() -> dict[str, str]:
    key = os.environ.get("QDRANT_API_KEY", "")
    return {"api-key": key} if key else {}


def ensure_qdrant_collection(name: str, vector_size: int) -> None:
    url = os.environ.get("QDRANT_URL", "http://127.0.0.1:6333")
    headers = qdrant_headers()
    try:
        meta = safe_json_get(f"{url}/collections/{name}", headers=headers)
        existing_size = (
            meta.get("result", {})
            .get("config", {})
            .get("params", {})
            .get("vectors", {})
            .get("size")
        )
        if existing_size is not None and int(existing_size) != int(vector_size):
            raise RuntimeError(
                "Qdrant collection dimension mismatch for "
                f"{name}: existing={existing_size}, embedding={vector_size}. "
                "Choose another MEMORY_QDRANT_COLLECTION or switch MEMORY_EMBED_MODEL."
            )
        return
    except urllib.error.HTTPError as exc:
        if exc.code != 404:
            raise

    safe_json_put(
        f"{url}/collections/{name}",
        {
            "vectors": {"size": vector_size, "distance": "Cosine"},
            "on_disk_payload": True,
        },
        headers=headers,
    )


def cmd_index(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).expanduser().resolve()
    ensure_dirs(workspace)
    db_path = workspace / ".memory" / "index.sqlite"
    conn = db_connect(db_path)
    db_init(conn)

    if args.rebuild:
        conn.execute("DELETE FROM facts")
        conn.commit()

    memory_dir = workspace / "memory"
    if not memory_dir.exists():
        print(f"No memory directory at {memory_dir}")
        return 1

    files = sorted(memory_dir.glob("*.md"))
    inserted = 0
    for md in files:
        for fact in parse_retain_facts(md, workspace):
            conn.execute(
                """
                INSERT OR REPLACE INTO facts
                (kind, confidence, content, entities_json, source_path, source_line, source_date, fact_hash, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                """,
                (
                    fact.kind,
                    fact.confidence,
                    fact.content,
                    json.dumps(fact.entities),
                    fact.source_path,
                    fact.source_line,
                    fact.source_date,
                    fact.fact_hash,
                ),
            )
            inserted += 1
    conn.commit()
    total = conn.execute("SELECT COUNT(*) AS c FROM facts").fetchone()["c"]
    print(f"Indexed facts: {inserted} (total in db: {total})")
    return 0


def fetch_sql_rows(
    conn: sqlite3.Connection, args: argparse.Namespace
) -> list[sqlite3.Row]:
    where = []
    params: list[object] = []

    if args.kind:
        where.append("f.kind = ?")
        params.append(args.kind)
    if args.entity:
        where.append("f.entities_json LIKE ?")
        params.append(f'%"{args.entity}"%')
    if args.since_days:
        cutoff = (dt.date.today() - dt.timedelta(days=args.since_days)).isoformat()
        where.append("f.source_date >= ?")
        params.append(cutoff)

    if args.query:
        sql = (
            "SELECT f.* FROM facts_fts x "
            "JOIN facts f ON f.id = x.rowid "
            "WHERE x.content MATCH ?"
        )
        params = [args.query] + params
        if where:
            sql += " AND " + " AND ".join(where)
        sql += " ORDER BY f.source_date DESC, f.source_line ASC LIMIT ?"
    else:
        sql = "SELECT f.* FROM facts f"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY f.source_date DESC, f.source_line ASC LIMIT ?"

    params.append(args.k)
    return conn.execute(sql, params).fetchall()


def print_rows(rows: list[sqlite3.Row], prefix: str = "") -> None:
    for row in rows:
        entities = ", ".join(json.loads(row["entities_json"])) or "-"
        confidence = ""
        if row["confidence"] is not None:
            confidence = f" (c={row['confidence']:.2f})"
        print(
            f"{prefix}- [{row['kind']}{confidence}] {row['content']}\n"
            f"{prefix}  source: {row['source_path']}:{row['source_line']} | date: {row['source_date']} | entities: {entities}"
        )


def semantic_search(query: str, k: int, collection: str) -> list[dict]:
    url = os.environ.get("QDRANT_URL", "http://127.0.0.1:6333")
    headers = qdrant_headers()
    vector = get_embedding(query)
    res = safe_json_post(
        f"{url}/collections/{collection}/points/search",
        {
            "vector": vector,
            "limit": k,
            "with_payload": True,
            "with_vector": False,
        },
        headers=headers,
    )
    return res.get("result", [])


def cmd_recall(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).expanduser().resolve()
    db_path = workspace / ".memory" / "index.sqlite"
    if not db_path.exists():
        print("Index not found. Run: memory_pipeline.py index --rebuild")
        return 1
    conn = db_connect(db_path)

    rows = fetch_sql_rows(conn, args)
    if args.hybrid and args.query:
        collection = os.environ.get(
            "MEMORY_QDRANT_COLLECTION", "openclaw_workspace_memory"
        )
        try:
            sem = semantic_search(args.query, args.k, collection)
            sem_ids = []
            for hit in sem:
                payload = hit.get("payload", {})
                fid = payload.get("fact_id")
                if isinstance(fid, int):
                    sem_ids.append(fid)
            if sem_ids:
                placeholders = ",".join(["?"] * len(sem_ids))
                sem_rows = conn.execute(
                    f"SELECT * FROM facts WHERE id IN ({placeholders})", sem_ids
                ).fetchall()
                by_id = {r["id"]: r for r in rows}
                for r in sem_rows:
                    by_id.setdefault(r["id"], r)
                rows = list(by_id.values())[: args.k]
        except Exception as exc:  # noqa: BLE001
            print(f"Hybrid semantic fallback warning: {exc}")

    if not rows:
        print("No memory hits.")
        return 0

    print_rows(rows)
    return 0


def write_bank_file(path: Path, title: str, rows: list[sqlite3.Row]) -> None:
    lines = [
        f"# {title}",
        "",
        f"Updated: {dt.datetime.now().isoformat(timespec='seconds')}",
        "",
    ]
    if not rows:
        lines.append("No entries yet.")
    else:
        for row in rows:
            lines.append(
                f"- {row['content']}  \n"
                f"  Source: `{row['source_path']}:{row['source_line']}` ({row['source_date']})"
            )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def cmd_reflect(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).expanduser().resolve()
    db_path = workspace / ".memory" / "index.sqlite"
    if not db_path.exists():
        print("Index not found. Run: memory_pipeline.py index --rebuild")
        return 1
    conn = db_connect(db_path)

    world_rows = conn.execute(
        "SELECT * FROM facts WHERE kind='world' ORDER BY source_date DESC, source_line ASC LIMIT 200"
    ).fetchall()
    exp_rows = conn.execute(
        "SELECT * FROM facts WHERE kind='experience' ORDER BY source_date DESC, source_line ASC LIMIT 200"
    ).fetchall()
    op_rows = conn.execute(
        "SELECT * FROM facts WHERE kind='opinion' ORDER BY source_date DESC, source_line ASC LIMIT 200"
    ).fetchall()

    bank = workspace / "bank"
    entities_dir = bank / "entities"
    bank.mkdir(exist_ok=True)
    entities_dir.mkdir(exist_ok=True)

    write_bank_file(bank / "world.md", "bank/world.md", world_rows)
    write_bank_file(bank / "experience.md", "bank/experience.md", exp_rows)
    write_bank_file(bank / "opinions.md", "bank/opinions.md", op_rows)

    entity_names = set()
    for row in conn.execute("SELECT entities_json FROM facts").fetchall():
        for entity in json.loads(row["entities_json"]):
            entity_names.add(entity)

    for entity in sorted(entity_names):
        rows = conn.execute(
            "SELECT * FROM facts WHERE entities_json LIKE ? ORDER BY source_date DESC, source_line ASC LIMIT 80",
            (f'%"{entity}"%',),
        ).fetchall()
        write_bank_file(entities_dir / f"{entity}.md", f"entity/{entity}", rows)

    print(
        f"Reflection complete: world={len(world_rows)}, experience={len(exp_rows)}, "
        f"opinions={len(op_rows)}, entities={len(entity_names)}"
    )
    return 0


def cmd_semantic_upsert(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).expanduser().resolve()
    db_path = workspace / ".memory" / "index.sqlite"
    if not db_path.exists():
        print("Index not found. Run: memory_pipeline.py index --rebuild")
        return 1
    conn = db_connect(db_path)
    collection = os.environ.get("MEMORY_QDRANT_COLLECTION", "openclaw_workspace_memory")

    facts = conn.execute("SELECT * FROM facts ORDER BY id ASC").fetchall()
    if not facts:
        print("No facts in index. Nothing to upsert.")
        return 0

    first_vec = get_embedding(facts[0]["content"])
    ensure_qdrant_collection(collection, len(first_vec))

    points = []
    for row in facts:
        vector = get_embedding(row["content"])
        payload = {
            "fact_id": row["id"],
            "kind": row["kind"],
            "source_path": row["source_path"],
            "source_line": row["source_line"],
            "source_date": row["source_date"],
            "entities": json.loads(row["entities_json"]),
            "content": row["content"],
            "confidence": row["confidence"],
        }
        points.append({"id": int(row["id"]), "vector": vector, "payload": payload})

    url = os.environ.get("QDRANT_URL", "http://127.0.0.1:6333")
    headers = qdrant_headers()
    safe_json_put(
        f"{url}/collections/{collection}/points",
        {"points": points},
        headers=headers,
    )
    print(f"Semantic upsert complete: {len(points)} points -> collection {collection}")
    return 0


def cmd_semantic_search(args: argparse.Namespace) -> int:
    collection = os.environ.get("MEMORY_QDRANT_COLLECTION", "openclaw_workspace_memory")
    hits = semantic_search(args.query, args.k, collection)
    if not hits:
        print("No semantic hits.")
        return 0
    for hit in hits:
        payload = hit.get("payload", {})
        score = hit.get("score", 0.0)
        print(
            f"- [semantic score={score:.4f}] {payload.get('content', '')}\n"
            f"  source: {payload.get('source_path', '?')}:{payload.get('source_line', '?')} | "
            f"date: {payload.get('source_date', '?')} | entities: {payload.get('entities', [])}"
        )
    return 0


def cmd_retain_add(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).expanduser().resolve()
    day = args.date or dt.date.today().isoformat()
    day_file = workspace / "memory" / f"{day}.md"
    day_file.parent.mkdir(parents=True, exist_ok=True)

    if not day_file.exists():
        day_file.write_text(f"## {day} Session Notes\n\n## Retain\n", encoding="utf-8")

    lines = day_file.read_text(encoding="utf-8", errors="ignore").splitlines()
    entry = f"- {args.entry.strip()}"

    found = False
    insert_at = len(lines)
    for i, line in enumerate(lines):
        if RETAIN_HEADING.match(line):
            found = True
            insert_at = i + 1
            j = i + 1
            while j < len(lines) and (lines[j].startswith("-") or not lines[j].strip()):
                insert_at = j + 1
                j += 1
            break

    if not found:
        if lines and lines[-1].strip():
            lines.append("")
        lines.append("## Retain")
        lines.append(entry)
    else:
        lines.insert(insert_at, entry)

    day_file.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"Added retain bullet to {day_file}")
    return 0


def cmd_retain_daily(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).expanduser().resolve()
    day = args.date or dt.date.today().isoformat()
    day_file = workspace / "memory" / f"{day}.md"
    day_file.parent.mkdir(parents=True, exist_ok=True)

    if not day_file.exists():
        day_file.write_text(
            f"## {day} Session Notes\n\n## Retain\n\n## Notes\n",
            encoding="utf-8",
        )

    lines = day_file.read_text(encoding="utf-8", errors="ignore").splitlines()

    has_retain = any(RETAIN_HEADING.match(line) for line in lines)
    if not has_retain:
        if lines and lines[-1].strip():
            lines.append("")
        lines.extend(["## Retain", "", "## Notes"])
        day_file.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
        lines = day_file.read_text(encoding="utf-8", errors="ignore").splitlines()

    in_retain = False
    retain_count = 0
    for line in lines:
        if RETAIN_HEADING.match(line):
            in_retain = True
            continue
        if in_retain and HEADING.match(line):
            in_retain = False
            continue
        if in_retain and RETAIN_BULLET_PATTERN.match(line):
            retain_count += 1

    min_count = max(0, int(args.min_count))
    status = "ok" if retain_count >= min_count else "needs-retain"
    print(
        f"retain-daily: {status} | file={day_file} | "
        f"retain_bullets={retain_count} | min={min_count}"
    )
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    print("Memory Doctor")
    print("=============")

    # Ollama models
    try:
        tags = safe_json_get("http://127.0.0.1:11434/api/tags")
        names = [m.get("name", "?") for m in tags.get("models", [])]
        print(
            f"Ollama: ok ({len(names)} models) -> {', '.join(names) if names else '-'}"
        )
    except Exception as exc:  # noqa: BLE001
        print(f"Ollama: unavailable ({exc})")

    # Embedding model smoke
    embed_dim = None
    embed_model = _resolve_embed_model()
    try:
        emb = get_embedding("memory pipeline healthcheck")
        embed_dim = len(emb)
        print(f"Embeddings: ok via Ollama (dim={len(emb)}) model={embed_model}")
    except Exception as exc:  # noqa: BLE001
        print(f"Embeddings: unavailable ({exc})")

    # Qdrant
    headers = qdrant_headers()
    url = os.environ.get("QDRANT_URL", "http://127.0.0.1:6333")
    try:
        cols = safe_json_get(f"{url}/collections", headers=headers)
        names = [
            c.get("name", "?") for c in cols.get("result", {}).get("collections", [])
        ]
        print(
            f"Qdrant: ok ({len(names)} collections) -> {', '.join(names) if names else '-'}"
        )
        if names:
            preferred = os.environ.get(
                "MEMORY_QDRANT_COLLECTION", "openclaw_workspace_memory"
            )
            target = preferred if preferred in names else names[0]
            meta = safe_json_get(f"{url}/collections/{target}", headers=headers)
            dim = (
                meta.get("result", {})
                .get("config", {})
                .get("params", {})
                .get("vectors", {})
                .get("size")
            )
            if dim is not None:
                print(f"Qdrant vector size ({target}): {dim}")
            if dim == 384:
                print("Embedding hint: vector size 384 (common: bge-small family)")
            if embed_dim is not None and dim is not None and int(embed_dim) != int(dim):
                print(
                    "Warning: embedding dimension does not match Qdrant collection. "
                    "Set MEMORY_EMBED_MODEL to a model matching collection dimension."
                )
    except urllib.error.HTTPError as exc:
        print(f"Qdrant: auth required or unavailable ({exc.code})")
    except Exception as exc:  # noqa: BLE001
        print(f"Qdrant: unavailable ({exc})")

    return 0


def _read_env_keys(path: Path) -> set[str]:
    keys: set[str] = set()
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = ENV_KEY_PATTERN.match(line)
        if match:
            keys.add(match.group(1))
    return keys


def cmd_env_lint(args: argparse.Namespace) -> int:
    issues: list[str] = []
    warnings: list[str] = []

    env_file = Path(args.env_file).expanduser().resolve()
    if not env_file.exists():
        issues.append(f"env file missing: {env_file}")
    else:
        mode = stat.S_IMODE(env_file.stat().st_mode)
        if mode != 0o600:
            warnings.append(
                f"env file permissions are {oct(mode)} (recommended: 0o600)"
            )
        keys = _read_env_keys(env_file)
        missing = [k for k in REQUIRED_ENV_KEYS if k not in keys]
        if missing:
            issues.append(f"missing env keys in {env_file}: {', '.join(missing)}")

    env_link_raw = Path(args.env_link).expanduser()
    if not env_link_raw.exists():
        issues.append(f"env link missing: {env_link_raw}")
    elif not env_link_raw.is_symlink():
        issues.append(f"env link is not symlink: {env_link_raw}")
    else:
        link_target = env_link_raw.resolve()
        if link_target != env_file:
            issues.append(
                f"env link target drift: {env_link_raw} -> {link_target} (expected {env_file})"
            )

    try:
        proc = subprocess.run(
            ["crontab", "-l"], check=False, capture_output=True, text=True
        )
        if proc.returncode == 0:
            lines = [
                l for l in proc.stdout.splitlines() if "memory_tools/run_cycle.sh" in l
            ]
            if not lines:
                issues.append(
                    "memory cron line missing (run_cycle.sh not found in crontab)"
                )
            else:
                for line in lines:
                    if "OPENCLAW_ENV_FILE=" not in line:
                        issues.append("memory cron missing OPENCLAW_ENV_FILE binding")
                    if "QDRANT_API_KEY=" in line:
                        issues.append(
                            "memory cron still inlines QDRANT_API_KEY (must use env file)"
                        )
                    if "MEMORY_EMBED_MODEL=" in line:
                        issues.append(
                            "memory cron still inlines MEMORY_EMBED_MODEL (must use env file)"
                        )
        else:
            warnings.append("crontab unavailable; skipped cron lint")
    except Exception as exc:  # noqa: BLE001
        warnings.append(f"cron lint skipped: {exc}")

    if warnings:
        for w in warnings:
            print(f"WARN: {w}")
    if issues:
        for issue in issues:
            print(f"FAIL: {issue}")
        print("env-lint: failed")
        return 1

    print(
        "env-lint: ok | "
        f"env_file={env_file} | env_link={env_link_raw} | required_keys={len(REQUIRED_ENV_KEYS)}"
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Workspace memory pipeline")
    parser.add_argument(
        "--workspace",
        default="~/.openclaw/workspace",
        help="OpenClaw workspace path (default: ~/.openclaw/workspace)",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_index = sub.add_parser(
        "index", help="Index memory/YYYY-MM-DD.md retain bullets into SQLite"
    )
    p_index.add_argument(
        "--rebuild", action="store_true", help="Rebuild index from scratch"
    )
    p_index.set_defaults(func=cmd_index)

    p_recall = sub.add_parser("recall", help="Recall facts from SQLite FTS index")
    p_recall.add_argument("query", nargs="?", default="", help="FTS query text")
    p_recall.add_argument("--k", type=int, default=12, help="Max results")
    p_recall.add_argument(
        "--kind", choices=["world", "experience", "opinion", "summary"]
    )
    p_recall.add_argument("--entity", help="Entity slug without @")
    p_recall.add_argument(
        "--since-days", type=int, default=0, help="Filter by recent days"
    )
    p_recall.add_argument(
        "--hybrid",
        action="store_true",
        help="Merge FTS recall with semantic Qdrant recall",
    )
    p_recall.set_defaults(func=cmd_recall)

    p_reflect = sub.add_parser(
        "reflect", help="Generate bank/*.md and bank/entities/*.md summaries"
    )
    p_reflect.set_defaults(func=cmd_reflect)

    p_upsert = sub.add_parser(
        "semantic-upsert", help="Embed SQLite facts and upsert into Qdrant"
    )
    p_upsert.set_defaults(func=cmd_semantic_upsert)

    p_sem = sub.add_parser(
        "semantic-search", help="Semantic search over Qdrant memory collection"
    )
    p_sem.add_argument("query", help="Semantic query")
    p_sem.add_argument("--k", type=int, default=8, help="Max semantic hits")
    p_sem.set_defaults(func=cmd_semantic_search)

    p_retain = sub.add_parser(
        "retain-add", help="Append one retain bullet to a daily memory file"
    )
    p_retain.add_argument("entry", help="Retain entry text, e.g. W @Arif: ...")
    p_retain.add_argument("--date", help="Date YYYY-MM-DD (default: today)")
    p_retain.set_defaults(func=cmd_retain_add)

    p_retain_daily = sub.add_parser(
        "retain-daily",
        help="Ensure today's memory file/Retain section exists and report bullet count",
    )
    p_retain_daily.add_argument("--date", help="Date YYYY-MM-DD (default: today)")
    p_retain_daily.add_argument(
        "--min-count",
        type=int,
        default=3,
        help="Target minimum retain bullets for daily consistency",
    )
    p_retain_daily.set_defaults(func=cmd_retain_daily)

    p_doctor = sub.add_parser("doctor", help="Check Ollama/Qdrant/embeddings")
    p_doctor.set_defaults(func=cmd_doctor)

    p_env_lint = sub.add_parser(
        "env-lint",
        help="Validate canonical env wiring (env file, symlink, cron, required keys)",
    )
    p_env_lint.add_argument(
        "--env-file",
        default=DEFAULT_ENV_FILE,
        help=f"Canonical env file path (default: {DEFAULT_ENV_FILE})",
    )
    p_env_lint.add_argument(
        "--env-link",
        default=DEFAULT_ENV_LINK,
        help=f"Expected symlink path (default: {DEFAULT_ENV_LINK})",
    )
    p_env_lint.set_defaults(func=cmd_env_lint)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
