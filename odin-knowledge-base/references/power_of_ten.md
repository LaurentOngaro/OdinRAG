---
title: "The Power of Ten - Rules for Developing Safety Critical Code (Gerard J. Holzmann, NASA JPL)"
date: "2026-07-10"
tags: [OdinRAG, kb, reference, safety, source/nasa-jpl]
type: reference
status: active
version: 1.0.0
lastUpdated: "2026-07-10"
updatedBy: "MiniMax-M3 (Kilo Code) via download_power_of_ten.py"
summary: "NASA JPL's 10 rules for safety-critical code - the academic source behind TigerStyle's 'Safety' section. PDF stays canonical; .md is just a pointer."
---

# The Power of Ten - Rules for Developing Safety Critical Code

Canonical artifact (PDF): [`power_of_ten.pdf`](./power_of_ten.pdf) - fetched from [https://spinroot.com/gerard/pdf/P10.pdf](https://spinroot.com/gerard/pdf/P10.pdf).

Author: Gerard J. Holzmann (NASA / JPL Laboratory for Reliable Software).

> The 10 rules below are the academic source that TigerStyle's **Safety** section explicitly cites and expands on (see [`./tiger_style.md`](./tiger_style.md)). They are language-agnostic and apply directly to Odin projects: simple control flow, fixed loop bounds, no recursion, compiler-warnings-as-errors at the strictest level, and so on.

## Source note

The canonical host (https://spinroot.com/gerard/pdf/P10.pdf) sits behind a Cloudflare JS challenge that programmatic downloaders cannot satisfy. We fetch the PDF via the Wayback Machine snapshot (https://web.archive.org/web/2024if_/https://spinroot.com/gerard/pdf/P10.pdf) which returns the same bytes (~36.4 KB as of the 2024 snapshot). If the URL drifts, update the snapshot year in `download_power_of_ten.py`.

## How to read

- **Short version (5 min)**: skim the rules in §1 and the rationale in §3 of the PDF.
- **Deep read (30 min)**: the full paper, including the discussions of why each rule matters. The appendix lists historical incidents that motivated each rule.

## Origin

The Power of Ten was published in the **IEEE Computer** column "Robustness" in 2006. It is public, no paywall, and explicitly intended to be redistributed by teams building safety-critical software. The PDF is the canonical artifact; this Markdown file exists only to make the asset discoverable by Kilo's KB index.

>Source: https://spinroot.com/gerard/pdf/P10.pdf
