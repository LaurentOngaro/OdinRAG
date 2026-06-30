---
title: "Understanding the Odin Programming Language"
date: 2026-06-28
tags: [OdinRAG, kb, source/zylinski, reference, topic/odin, topic/book, doc/index]
type: reference
status: active
priority: 1
summary: "Index de 'Understanding the Odin Programming Language' par Karl Zylinski (v1.10). 33 sections (chapitres + appendices), ~656 exemples de code."
docId: BOOK_ODIN_001
author: "Karl Zylinski"
version: "1.10"
---

# Understanding the Odin Programming Language

> **Auteur** : Karl Zylinski
> **Version source** : 1.10
> **Converti depuis** : `J:\Assets\Itch\odinbook\understanding_the_odin_programming_language.html`
> **Date conversion** : 2026-06-28

**Livre de référence du langage Odin**. Chaque chapitre est un fichier MD indépendant pour navigation facile et contexte Kilo léger.

## Table of Contents

- **Chapter 1** — [Introduction](01-introduction.md)
- **Chapter 2** — [Hellope! A tiny program](02-hellope-a-tiny-program.md)
- **Chapter 3** — [Variables and constants](03-variables-and-constants.md)
- **Chapter 4** — [Some additional basics](04-some-additional-basics.md)
- **Chapter 5** — [Making new types](05-making-new-types.md)
- **Chapter 6** — [Pointers](06-pointers.md)
- **Chapter 7** — [Procedures and scopes](07-procedures-and-scopes.md)
- **Chapter 8** — [Fixed-memory containers](08-fixed-memory-containers.md)
- **Chapter 9** — [Introduction to manual memory management](09-introduction-to-manual-memory-management.md)
- **Chapter 10** — [More container types](10-more-container-types.md)
- **Chapter 11** — [Strings](11-strings.md)
- **Chapter 12** — [Implicit context](12-implicit-context.md)
- **Chapter 13** — [Making manual memory management easier](13-making-manual-memory-management-easier.md)
- **Chapter 14** — [Parametric polymorphism: Writing generic code](14-parametric-polymorphism-writing-generic-code.md)
- **Chapter 15** — [Bit-related types](15-bit-related-types.md)
- **Chapter 16** — [Error handling](16-error-handling.md)
- **Chapter 17** — [Package system and code organization](17-package-system-and-code-organization.md)
- **Chapter 18** — [You (probably) don't need a build system](18-you-probably-dont-need-a-build-system.md)
- **Chapter 19** — [Reflection and Run-Time Type Information (RTTI)](19-reflection-and-run-time-type-information-rtti.md)
- **Chapter 20** — [Data-oriented design](20-data-oriented-design.md)
- **Chapter 21** — [Making C library bindings (Foreign Function Interface)](21-making-c-library-bindings-foreign-function-interface.md)
- **Chapter 22** — [Debuggers](22-debuggers.md)
- **Chapter 23** — [Odin features you should avoid](23-odin-features-you-should-avoid.md)
- **Chapter 24** — [A tour of the core collection](24-a-tour-of-the-core-collection.md)
- **Chapter 25** — [Libraries for creating video games](25-libraries-for-creating-video-games.md)
- **Chapter 26** — [A few more things...](26-a-few-more-things.md)
- **Chapter 27** — [Where to find more Odin resources](27-where-to-find-more-odin-resources.md)
- **Chapter 28** — [Thanks for reading!](28-thanks-for-reading.md)
- **[About the author](about-the-author.md)**

### Appendices

- **Appendix A** — [Handle-based array](appendices/A-handle-based-array.md)
- **Appendix B** — [Using only fixed arrays](appendices/B-using-only-fixed-arrays.md)
- **Appendix C** — [gui_dropdown from CAT & ONION](appendices/C-gui-dropdown-from-cat-onion.md)
- **Appendix D** — [Box2D and raylib](appendices/D-box2d-and-raylib.md)

---

## Comment utiliser ce livre

1. **Navigation** : commencer par le [Chapter 1](01-introduction.md), puis suivre l'ordre.
2. **Recherche par topic** : utiliser Ctrl+F dans chaque fichier, ou grep sur le dossier `odin-book/`.
3. **Context Kilo** : pour citer un chapitre, ouvrir le fichier `.md` correspondant (~30-150 KB) — plus léger qu'un seul gros fichier.
4. **Code samples** : 656 exemples au total, tous préservés comme blocs ```odin`.

## Mise à jour

Quand Karl publie une nouvelle version du HTML :

1. Remplacer le fichier `J:\Assets\Itch\odinbook\understanding_the_odin_programming_language.html`
2. Re-lancer le convertisseur : `python _Helpers/lib/book_html_to_md.py`
3. Vérifier le diff dans `docs/karl_zylinski/odin-book/`

## Métadonnées

- **Titre** : Understanding the Odin Programming Language
- **Auteur** : Karl Zylinski
- **Version** : 1.10
- **Chapitres** : 29 (28 numérotés + 1 non-numérotés)
- **Appendices** : 4
