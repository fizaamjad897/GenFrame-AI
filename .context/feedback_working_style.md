---
name: Feedback — Working style preferences for this codebase
description: How the user wants Claude to approach work in the Visual Engine backend
type: feedback
originSessionId: cea3306e-714a-4ee0-b3b9-ea3c39c2cba1
---
Match the exact file format when cloning patterns.

**Why:** User explicitly asked for `qms_dimensions.py` to use "exact same format for everything, same prompt structure" as `ooh_dimensions.py`. When asked to clone a pattern (dimensions file, recomposer, etc.), the output must mirror the source structure precisely — same TypedDict, same key names, same docstring block, same fallback function signatures.

**How to apply:** Before writing a new file that mirrors an existing one, read the source file fully first. Copy structural patterns exactly, including module docstring format, TypedDict definition, dict variable name conventions, helper function names, and the `get_profile()` signature.

---

Read main.py carefully before editing routing.

**Why:** `main.py` is ~4500+ lines. OOH routing logic is spread across multiple locations (the `OOH_MEDIA_SITE_DIMENSIONS` dict at ~line 1710, `_is_ooh_dimension()`, the `/resize` endpoint routing block, and the `/custom-resize` endpoint routing block). Editing one location without the others causes silent misroutes.

**How to apply:** Always grep for the relevant section before editing. Use `offset` + `limit` reads rather than reading the whole file.
