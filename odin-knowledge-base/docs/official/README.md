# odin-knowledge-base/docs/official/ - Odin official documentation (MIT-style)

> This folder contains the scraped mirror of the official Odin language docs.
> These files are publicly licensed (Odin source is BSD-3 / MIT-style) - they ship
> **inside** the repo with attribution to the Odin team.

## Sources

- Upstream: <https://odin-lang.org/docs/>
- List curated list: [`awesome-odin`](https://github.com/jakubtomsu/awesome-odin)
  (mirrored in `awesome-odin.md`).
- See [`../../../SOURCES.md`](../../../SOURCES.md) § 1 for the licence breakdown.

## How this folder was populated

`odin-knowledge-base/docs/official/*.md` (and `odin-knowledge-base/docs/official/awesome-odin.md`) are produced by
`_Helpers/scripts/scrappers/scrape_official.py` (sitemap + crawl + static fallback). Re-running is
idempotent - already-scraped files are skipped unless you pass `--force`.

```bash
python _Helpers/scripts/scrappers/scrape_official.py            # re-entrant: skip existing
python _Helpers/scripts/scrappers/scrape_official.py --force    # force re-write
```

## Files produced

| File              | Source URL                                   |
| ----------------- | -------------------------------------------- |
| `overview.md`     | <https://odin-lang.org/docs/overview/>       |
| `install.md`      | <https://odin-lang.org/docs/install/>        |
| `packages.md`     | <https://odin-lang.org/docs/packages/>       |
| `testing.md`      | <https://odin-lang.org/docs/testing/>        |
| `faq.md`          | <https://odin-lang.org/docs/faq/>            |
| `spec.md`         | <https://odin-lang.org/docs/spec/>           |
| `odin-book.md`    | <https://odin-lang.org/docs/odin-book/>      |
| `nightly.md`      | <https://odin-lang.org/docs/nightly/>        |
| `examples.md`     | <https://odin-lang.org/docs/examples/>       |
| `demo.md`         | <https://odin-lang.org/docs/demo/>           |
| `awesome-odin.md` | <https://github.com/jakubtomsu/awesome-odin> |

> The list above reflects what the scraper currently produces (11 files). The Odin docs sitemap evolves - re-run `scrape-official.py` to pick up new pages. Missing pages (editor, guidelines, install sub-pages, etc.) may appear on future scrapes if the upstream site is updated.

## Attribution

All content in this folder is © the Odin language team (Bill Hall et al.). It is
mirrored here under the Odin's open licence. If you're a contributor and want a
change reflected, you can either open a PR upstream on
[github.com/odin-lang/Odin](https://github.com/odin-lang/Odin) and re-run the
scraper, or edit the `.md` file here directly (the scraper won't overwrite a file
that's larger than the upstream unless `--force` is passed).

## See also

- [`../karl_zylinski/`](../karl_zylinski/) - zylinski.se public index
- [`../newsletters/`](../newsletters/) - Odin newsletters index
- [`../../../SOURCES.md`](../../../SOURCES.md) - source procurement guide
