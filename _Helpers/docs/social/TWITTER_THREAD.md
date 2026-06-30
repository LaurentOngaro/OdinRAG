# X / Twitter - thread

## Full Version (6 tweets)

### Tweet 1/6

> Built a curated RAG KB for #OdinLang game dev - entirely with MiniMax-M3 via Kilo Code as my agentic IDE.
> Scrapers, subagents, 6 Kilo skills, daily planning, indexing workflow. M3 was the structural engineer; I was the curator.
> Check OdinRAG on GitHub:https://github.com/LaurentOngaro/OdinRAG
>
> 🧵👇
> #MinimaxM3

#### Tweet 2/6

> What's in the box:
> • `_Helpers/` - idempotent Python scrapers (Skool + odin-lang.org + zylinski.se), pure stdlib + BeautifulSoup/markdownify
> • `.kilo/agents/odin-gamedev.md` - subagent that cites `file:line` from the KB
> • `.kilo/skills/` - 6 specialized skills

#### Tweet 3/6

> How M3 actually helped (not "vibe coding"):
> • Designed the frontmatter schema (Cours / Module / ID / Durée / topic/\*)
> • Wrote `_Helpers/scrape_skool.py` with re-entrancy + `--check` dry-run
> • Authored the subagent prompt with citation discipline
> • Created 6 skills following progressive disclosure

### Tweet 4/6

> Deliberate non-decisions:
> • No scraped content pushed to public repo (see `.gitignore`)
> • No vector DB at < 5000 files - context + frontmatter filtering is enough
> • No manual edits to scraped files (they're auto-generated)

#### Tweet 5/6

> Real example:
> "What's the Odin pattern for arena allocators?"
> → routes to `odin-gamedev` subagent
> → cites `docs/karl_zylinski/temporary-allocator-your-first-arena.md:42`

#### Tweet 6/6

> Public repo, scrapers, and AGENTS.md already shipped 👇
> #MinimaxM3 #GameDev #RAG #OdinLang

---

## Simple Version (less than 280 characters)

```
Built a curated RAG KB for #OdinLang game dev entirely with MiniMax-M3 + Kilo Code 🤖

Scrapers, subagent, 6 skills, daily planning.
Check OdinRAG on GitHub:https://github.com/LaurentOngaro/OdinRAG

How M3 was used 👇

#MinimaxM3 #GameDev #RAG
```
