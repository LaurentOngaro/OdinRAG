---
title: "Understanding the Odin Programming Language"
date: 2026-06-28
tags: [OdinRAG, kb, source/zylinski, reference, topic/odin, topic/book, doc/index]
type: reference
status: active
priority: 1
summary: "Index of 'Understanding the Odin Programming Language' by Karl Zylinski (v1.10). 33 sections (chapters + appendices), ~656 code examples."
docId: BOOK_ODIN_001
author: "Karl Zylinski"
version: "1.10"
---

# Understanding the Odin Programming Language

> **Author**: Karl Zylinski  
> **Source version**: 1.10  
> **Converted from**: `J:\Assets\Itch\odinbook\understanding_the_odin_programming_language.html`  
> **Conversion date**: 2026-06-28

**Reference book for the Odin language**. Each chapter is a standalone MD file for easy navigation and light Kilo context.

## Table of Contents

- **Chapter 1** - [Introduction](01-introduction.md)
- **Chapter 2** - [Hellope! A tiny program](02-hellope-a-tiny-program.md)
- **Chapter 3** - [Variables and constants](03-variables-and-constants.md)
- **Chapter 4** - [Some additional basics](04-some-additional-basics.md)
- **Chapter 5** - [Making new types](05-making-new-types.md)
- **Chapter 6** - [Pointers](06-pointers.md)
- **Chapter 7** - [Procedures and scopes](07-procedures-and-scopes.md)
- **Chapter 8** - [Fixed-memory containers](08-fixed-memory-containers.md)
- **Chapter 9** - [Introduction to manual memory management](09-introduction-to-manual-memory-management.md)
- **Chapter 10** - [More container types](10-more-container-types.md)
- **Chapter 11** - [Strings](11-strings.md)
- **Chapter 12** - [Implicit context](12-implicit-context.md)
- **Chapter 13** - [Making manual memory management easier](13-making-manual-memory-management-easier.md)
- **Chapter 14** - [Parametric polymorphism: Writing generic code](14-parametric-polymorphism-writing-generic-code.md)
- **Chapter 15** - [Bit-related types](15-bit-related-types.md)
- **Chapter 16** - [Error handling](16-error-handling.md)
- **Chapter 17** - [Package system and code organization](17-package-system-and-code-organization.md)
- **Chapter 18** - [You (probably) don't need a build system](18-you-probably-dont-need-a-build-system.md)
- **Chapter 19** - [Reflection and Run-Time Type Information (RTTI)](19-reflection-and-run-time-type-information-rtti.md)
- **Chapter 20** - [Data-oriented design](20-data-oriented-design.md)
- **Chapter 21** - [Making C library bindings (Foreign Function Interface)](21-making-c-library-bindings-foreign-function-interface.md)
- **Chapter 22** - [Debuggers](22-debuggers.md)
- **Chapter 23** - [Odin features you should avoid](23-odin-features-you-should-avoid.md)
- **Chapter 24** - [A tour of the core collection](24-a-tour-of-the-core-collection.md)
- **Chapter 25** - [Libraries for creating video games](25-libraries-for-creating-video-games.md)
- **Chapter 26** - [A few more things...](26-a-few-more-things.md)
- **Chapter 27** - [Where to find more Odin resources](27-where-to-find-more-odin-resources.md)
- **Chapter 28** - [Thanks for reading!](28-thanks-for-reading.md)
- **[About the author](about-the-author.md)**

### Appendices

- **Appendix A** - [Handle-based array](appendices/A-handle-based-array.md)
- **Appendix B** - [Using only fixed arrays](appendices/B-using-only-fixed-arrays.md)
- **Appendix C** - [gui_dropdown from CAT & ONION](appendices/C-gui-dropdown-from-cat-onion.md)
- **Appendix D** - [Box2D and raylib](appendices/D-box2d-and-raylib.md)

---

## How to use this book

1. **Navigation**: start with [Chapter 1](01-introduction.md), then follow the order.
2. **Search by topic**: use Ctrl+F in each file, or grep on the `odin-book/` folder.
3. **Kilo context**: to cite a chapter, open the corresponding `.md` file (~30-150 KB) - lighter than one single big file.
4. **Code samples**: 656 examples in total, all preserved as ```odin` blocks.

## Update

When Karl publishes a new HTML version:
1. Update the source file at the path you pass via `--src`
2. Re-run the converter: `python _Helpers/scripts/lib/book_html_to_md.py`
3. Verify the diff in `odin-knowledge-base/docs/karl_zylinski/odin-book/`

## Metadata

- **Title**: Understanding the Odin Programming Language
- **Author**: Karl Zylinski
- **Version**: 1.10
- **Chapters**: 29 (28 numbered + 1 unnumbered)
- **Appendices**: 4
