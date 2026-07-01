---
title: "README - diagnostic"
date: "2026-07-01"
tags: [OdinRAG, reference]
type: reference
status: active
version: 1.0.0
lastUpdated: "2026-07-01"
updatedBy: "MiniMax-M3 (Kilo Code)"
---

# README - diagnostic

## Contents

- `audit_public_safety.py` - verifies the tracked tree does not contain copyrighted or private content.
- `auditReadmeCoherence.py` - checks README files against their host directory.

## Usage

```bash
python _Helpers/scripts/diagnostic/audit_public_safety.py --verbose
python _Helpers/scripts/diagnostic/auditReadmeCoherence.py --scope _Helpers
```

## Cross-references

Full folder tree: [`001_folder_structure.md`](../../../docs/001_folder_structure.md)
