# X / Twitter - thread

## Full Version (6 tweets)

### Tweet 1/6

```text
Built a curated RAG KB for #OdinLang game dev - entirely with MiniMax-M3 via Kilo Code as my agentic IDE.
Scrapers, subagents, skills, daily planning, indexing workflow. M3 was the structural engineer; I was the curator.
Check OdinRAG on GitHub:https://github.com/LaurentOngaro/OdinRAG
#MinimaxM3
```

#### Tweet 2/6

```text
What's in the box:
- `_Helpers/` - idempotent Python scrapers (Skool + odin-lang.org + zylinski.se), pure stdlib + BeautifulSoup/markdownify
- `.kilo/agents/odin-gamedev.md` - subagent that cites `file:line` from the KB
- `.kilo/skills/` - specialized skills
```

#### Tweet 3/6

```text
How M3 actually helped:
- Designed the frontmatter schema (Cours / Module / ID / Durée / topic/\*)
- Wrote `_Helpers/scrape_skool.py` with re-entrancy + `--check` dry-run
- Authored the subagent prompt with citation discipline
- Created 6 skills following progressive disclosure
```

### Tweet 4/6

```text
Deliberate non-decisions:
- No scraped content pushed to public repo (see `.gitignore`)
- No vector DB at < 5000 files - context + frontmatter filtering is enough
- No manual edits to scraped files (they're auto-generated)
```

#### Tweet 5/6

```text
Real example:
"What's the Odin pattern for arena allocators?"
→ routes to `odin-gamedev` subagent
→ cites `docs/karl_zylinski/temporary-allocator-your-first-arena.md:42`
```

#### Tweet 6/6

```text
Public repo, scrapers, and AGENTS.md already shipped 👇
# MinimaxM3 #GameDev #RAG #OdinLang
```

## Simple Version (less than 280 characters)

```text
Built a curated RAG KB for #OdinLang game dev entirely with MiniMax-M3 + Kilo Code 🤖
Scrapers, subagent, 6 skills, daily planning.

Check OdinRAG on GitHub:https://github.com/LaurentOngaro/OdinRAG

How M3 was used 👇

#MinimaxM3 #GameDev #RAG
```
