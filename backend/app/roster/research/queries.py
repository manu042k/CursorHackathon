"""Build site-restricted Reddit search queries from the owner's product fields."""

from __future__ import annotations

from app.contracts import CreateExperimentRequest

DECISION_WORDS = ("price", "plan", "churn", "switch", "competitor", "renew", "contract", "seat")
STOPWORDS = frozenset(
    {
        "always",
        "their",
        "own",
        "with",
        "from",
        "that",
        "this",
        "they",
        "your",
        "into",
        "only",
        "come",
        "back",
        "for",
        "and",
        "the",
        "a",
        "an",
        "of",
        "to",
        "in",
    }
)
CATEGORY_SUBREDDITS = {
    "saas": ("saas", "sysadmin", "msp"),
    "snacks": ("subscriptionboxes", "frugal"),
}
DEFAULT_CATEGORY = "saas"


def infer_category(body: CreateExperimentRequest) -> str:
    text = f"{body.product_name} {body.product_description}".lower()
    if "subscription box" in text or "snack" in text:
        return "snacks"
    return DEFAULT_CATEGORY


def allowlisted_subreddits(category: str) -> tuple[str, ...]:
    return CATEGORY_SUBREDDITS.get(category, CATEGORY_SUBREDDITS[DEFAULT_CATEGORY])


def _description_tokens(description: str, *, limit: int = 4) -> list[str]:
    tokens: list[str] = []
    for raw in description.replace(",", " ").replace(".", " ").split():
        word = raw.strip().lower()
        if len(word) < 5 or word in STOPWORDS:
            continue
        if word in tokens:
            continue
        tokens.append(word)
        if len(tokens) >= limit:
            break
    return tokens


def build_reddit_queries(body: CreateExperimentRequest) -> list[str]:
    category = infer_category(body)
    subs = allowlisted_subreddits(category)
    name = body.product_name.strip()
    tokens = _description_tokens(body.product_description)
    decision = " OR ".join(DECISION_WORDS[:5])
    queries: list[str] = []
    for sub in subs:
        base = f"site:reddit.com/r/{sub}"
        queries.append(f'{base} "{name}" {category} ({decision})')
        if tokens:
            extra = " OR ".join(tokens)
            queries.append(f"{base} {category} ({extra}) ({decision})")
        queries.append(f'{base} inurl:comments "{name}" {category} ({decision})')
    return queries
