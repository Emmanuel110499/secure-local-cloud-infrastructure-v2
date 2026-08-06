from __future__ import annotations

from difflib import SequenceMatcher
from pathlib import Path
import re
import unicodedata


BASE_DIR = Path(__file__).resolve().parents[1]
DOCS_DIR = BASE_DIR / "knowledge" / "docs"

STOP_WORDS = {
    "a", "au", "aux", "avec", "ce", "ces", "cest",
    "dans", "de", "des", "du", "elle", "en", "est",
    "et", "ils", "je", "la", "le", "les", "leur",
    "lui", "ma", "mais", "mes", "mon", "ne", "nos",
    "notre", "nous", "on", "ou", "par", "pas", "pour",
    "que", "quel", "quelle", "quels", "quelles", "qui",
    "quoi", "sa", "se", "ses", "son", "sur", "ta",
    "tes", "toi", "ton", "tu", "un", "une", "vos",
    "votre", "vous", "comment", "pourquoi", "explique",
    "expliquer", "sert", "servent", "fonctionne",
}

SYNONYMS = {
    "ram": {"memoire", "memory"},
    "memoire": {"ram", "memory"},
    "cpu": {"processeur", "charge"},
    "conteneur": {"container", "docker"},
    "conteneurs": {"containers", "docker"},
    "metrique": {"mesure", "indicateur", "statistique"},
    "metriques": {"mesures", "indicateurs", "statistiques"},
    "indisponible": {"down", "arrete", "horsligne"},
    "disponible": {"up", "actif", "operationnel"},
    "securite": {"protection", "zero", "trust"},
}


def normalize(value: str) -> str:
    value = unicodedata.normalize(
        "NFD",
        str(value).lower(),
    )

    value = "".join(
        character
        for character in value
        if unicodedata.category(character) != "Mn"
    )

    value = re.sub(r"[^a-z0-9\s_-]", " ", value)
    value = re.sub(r"\s+", " ", value).strip()

    return value


def tokenize(value: str) -> set[str]:
    words = {
        word
        for word in normalize(value).split()
        if len(word) > 1 and word not in STOP_WORDS
    }

    expanded = set(words)

    for word in words:
        expanded.update(SYNONYMS.get(word, set()))

    return expanded


def split_document(content: str) -> list[dict[str, str]]:
    chunks: list[dict[str, str]] = []
    current_title = "Documentation"
    current_lines: list[str] = []

    def flush() -> None:
        nonlocal current_lines

        text = "\n".join(current_lines).strip()

        if text:
            chunks.append({
                "title": current_title,
                "content": text,
            })

        current_lines = []

    for raw_line in content.splitlines():
        line = raw_line.strip()

        if line.startswith("#"):
            flush()
            current_title = line.lstrip("#").strip()
            continue

        if not line:
            if current_lines:
                current_lines.append("")
            continue

        current_lines.append(line)

        if len("\n".join(current_lines)) >= 900:
            flush()

    flush()

    return chunks


def score_chunk(
    question: str,
    title: str,
    content: str,
) -> float:
    question_normalized = normalize(question)
    question_words = tokenize(question)

    candidate = f"{title} {content}"
    candidate_normalized = normalize(candidate)
    candidate_words = tokenize(candidate)

    if not question_words:
        return 0.0

    intersection = question_words & candidate_words
    overlap = len(intersection) / len(question_words)

    fuzzy_title = SequenceMatcher(
        None,
        question_normalized,
        normalize(title),
    ).ratio()

    phrase_bonus = 0.0

    if question_normalized in candidate_normalized:
        phrase_bonus = 0.5

    important_bonus = min(
        len(intersection) * 0.08,
        0.4,
    )

    return (
        overlap * 2.2
        + fuzzy_title * 0.45
        + phrase_bonus
        + important_bonus
    )


def search(
    question: str,
    limit: int = 3,
    min_score: float = 0.25,
) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []

    if not DOCS_DIR.exists():
        return results

    for file in DOCS_DIR.glob("*.md"):
        try:
            content = file.read_text(encoding="utf-8")
        except OSError:
            continue

        for chunk in split_document(content):
            score = score_chunk(
                question,
                chunk["title"],
                chunk["content"],
            )

            if score < min_score:
                continue

            results.append({
                "source": file.name,
                "title": chunk["title"],
                "content": chunk["content"],
                "score": round(score, 4),
            })

    results.sort(
        key=lambda item: float(item["score"]),
        reverse=True,
    )

    return results[:limit]



def build_documentation_answer(
    question: str,
) -> str | None:
    """Construit une réponse à partir de la documentation locale."""

    results = search(
        question,
        limit=3,
        min_score=0.25,
    )

    if not results:
        return None

    best = results[0]

    answer_parts = [
        f"📘 {best['title']}",
        "",
        str(best["content"]).strip(),
    ]

    sources = []

    for result in results:
        source = str(result["source"])

        if source not in sources:
            sources.append(source)

    if sources:
        answer_parts.extend([
            "",
            "────────────────────",
            "📚 Sources documentaires",
            *[
                f"✓ {source}"
                for source in sources
            ],
        ])

    return "\n".join(answer_parts)
