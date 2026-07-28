from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from src.utils.config import PROJECT_ROOT


DOCS_DIR = PROJECT_ROOT / "docs"
ALLOWED_LOCAL_AI_HOSTS = {"localhost", "127.0.0.1", "::1"}


@dataclass(frozen=True)
class HelpDocument:
    slug: str
    title: str
    path: Path
    content: str


def load_help_documents() -> list[HelpDocument]:
    documents = []
    for path in sorted(DOCS_DIR.glob("*.md")):
        content = path.read_text(encoding="utf-8")
        title = path.stem.replace("_", " ").title()
        for line in content.splitlines():
            if line.startswith("# "):
                title = line.removeprefix("# ").strip()
                break
        documents.append(
            HelpDocument(
                slug=path.stem,
                title=title,
                path=path,
                content=content,
            )
        )
    return documents


def _excerpt(content: str, query: str, *, length: int = 360) -> str:
    compact = " ".join(content.replace("#", " ").split())
    position = compact.lower().find(query.lower())
    if position < 0:
        position = 0
    start = max(0, position - 80)
    end = min(len(compact), start + length)
    prefix = "..." if start else ""
    suffix = "..." if end < len(compact) else ""
    return f"{prefix}{compact[start:end].strip()}{suffix}"


def search_help_documents(query: str, *, limit: int = 8) -> list[dict]:
    query = query.strip().lower()
    if not query:
        return []
    terms = [term for term in query.split() if term]
    results = []
    for document in load_help_documents():
        title = document.title.lower()
        content = document.content.lower()
        score = 0
        for term in terms:
            score += title.count(term) * 8
            score += content.count(term)
        if query in title:
            score += 20
        if query in content:
            score += 8
        if score:
            results.append(
                {
                    "slug": document.slug,
                    "title": document.title,
                    "score": score,
                    "excerpt": _excerpt(document.content, terms[0] if terms else query),
                    "content": document.content,
                }
            )
    return sorted(results, key=lambda item: (-item["score"], item["title"]))[:limit]


def build_document_context(query: str, *, max_chars: int = 12_000) -> str:
    matches = search_help_documents(query, limit=5)
    if not matches:
        matches = [
            {
                "title": document.title,
                "content": document.content,
            }
            for document in load_help_documents()[:4]
        ]
    sections = []
    remaining = max_chars
    for match in matches:
        section = f"# {match['title']}\n{match['content']}\n"
        if len(section) > remaining:
            section = section[:remaining]
        sections.append(section)
        remaining -= len(section)
        if remaining <= 0:
            break
    return "\n".join(sections)


def normalize_local_ai_url(base_url: str) -> str:
    normalized = base_url.strip().rstrip("/")
    parsed = urlparse(normalized)
    if parsed.scheme != "http" or parsed.hostname not in ALLOWED_LOCAL_AI_HOSTS:
        raise ValueError("Local AI endpoint ต้องเป็น http://localhost หรือ http://127.0.0.1 เท่านั้น")
    if parsed.path not in {"", "/"}:
        raise ValueError("Local AI endpoint ไม่ควรมี path ต่อท้าย")
    return normalized


def _request_json(
    url: str,
    *,
    payload: dict | None = None,
    timeout: int = 8,
) -> dict:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST" if body is not None else "GET",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise ConnectionError(f"ไม่สามารถเชื่อมต่อ Local AI: {exc}") from exc


def list_ollama_models(base_url: str = "http://localhost:11434") -> list[str]:
    endpoint = normalize_local_ai_url(base_url)
    response = _request_json(f"{endpoint}/api/tags")
    return [
        model["name"]
        for model in response.get("models", [])
        if isinstance(model, dict) and model.get("name")
    ]


def ask_ollama(
    question: str,
    *,
    model: str,
    base_url: str = "http://localhost:11434",
    history: list[dict] | None = None,
) -> str:
    endpoint = normalize_local_ai_url(base_url)
    context = build_document_context(question)
    system_prompt = (
        "คุณเป็นผู้ช่วยการใช้งาน ODOS Policy Analytics Prototype "
        "ตอบภาษาไทยอย่างกระชับ โดยอ้างอิงเฉพาะเอกสารบริบทที่ให้มา "
        "หากเอกสารไม่มีคำตอบให้บอกตรง ๆ ห้ามขอหรือแสดง PII "
        "และต้องย้ำว่าผลพยากรณ์เป็นข้อมูลประกอบการทบทวนโดยมนุษย์ ไม่ใช่คำสั่งตัดสินอัตโนมัติ\n\n"
        f"เอกสารบริบท:\n{context}"
    )
    messages = [{"role": "system", "content": system_prompt}]
    for item in (history or [])[-6:]:
        if item.get("role") in {"user", "assistant"} and item.get("content"):
            messages.append({"role": item["role"], "content": str(item["content"])})
    messages.append({"role": "user", "content": question})
    response = _request_json(
        f"{endpoint}/api/chat",
        payload={
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0.2},
        },
        timeout=120,
    )
    answer = response.get("message", {}).get("content", "").strip()
    if not answer:
        raise ConnectionError("Local AI ไม่ส่งคำตอบกลับมา")
    return answer
