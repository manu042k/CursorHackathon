from pathlib import Path
import re

plan = Path("docs/superpowers/plans/2026-08-15-owner-flow-revision.md")
text = plan.read_text(encoding="utf-8")
chunks = re.findall(
    r'id="(\w+)",\n        one_liner=.*?\n        mindset=\(\n((?:            ".*"\n)+)        \),',
    text,
)
print("found", len(chunks))
for key, body in chunks:
    joined = "".join(re.findall(r'"([^"]*)"', body))
    words = len(joined.split())
    print(f"{key:16} chars={len(joined):4} words={words:3} ok={150 <= words <= 250}")
