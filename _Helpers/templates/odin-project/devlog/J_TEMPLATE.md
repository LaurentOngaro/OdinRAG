# J_TEMPLATE

> How to use this file:
>
> 1. Copy this file into one of the two supported locations:
>    - `code/projects/<your-project>/devlog/J_YYYY-MM-DD_<topic>.md` (legacy, alongside the code)
>    - `_Private/devlogs/<your-project>/J_YYYY-MM-DD_<topic>.md` (preferred, privacy by location)
> 2. Fill in the date in the H1 heading
> 3. Check off tasks as you go
> 4. Fill in the bilan at end of day
>
> See `_Private/docs/003_devlog_location.md` for the rationale behind the two locations. The
> short version: `_Private/` is preferred because privacy is explicit at the path, not
> inherited from a parent folder that might one day become public.
>
> Note: the devlog folder is **per-project**. For KB-maintenance notes (about the OdinRAG
> repo itself), use the same per-project devlog - just adjust the path accordingly.

```markdown
# J_YYYY-MM-DD - Session topic

## Goal

> _One sentence: what must be delivered._

## Tasks

- [ ] First step
- [ ] Second step
- [ ] Step N

## Blockers / Decisions

> Anything that blocks progress, or an open question for Kilo.

- _None for now_

## Learnings

> What I learned about Odin (patterns, pitfalls, idioms). Serves as history.

- \_e.g. `tracking_allocator` only makes sense with a global `context.allocator`
  - see Karl 13.1.1\_
- _e.g. `using` on a struct field unpacks the fields into the parent scope
  (Karl 5.1.2) - pitfall_

## KB sources consulted

> The files that helped you today (relative paths).

- _e.g. `odin-knowledge-base/.../rpg/088-26-tracking-allocator.md`_
- _e.g. `odin-knowledge-base/docs/karl_zylinski/odin-book/13-making-manual-memory-management-easier.md`_

## Bilan (end of session)

- **Delivered**:
- **Postponed**:
- **Note**:
```
