#!/usr/bin/env python3
"""CLI script that reads a C or Python source file and outputs a structured prompt for translating it to compilable Lean 4."""

import argparse
import sys
from pathlib import Path

LANG_HINTS = {
    ".c": "C",
    ".h": "C",
    ".py": "Python",
    ".pyx": "Python (Cython)",
}

PROMPT_TEMPLATE = """\
You are an expert Lean 4 programmer with deep knowledge of Mathlib4. Your task is to \
translate the following {lang} source code into semantics-preserving, compilable Lean 4 code.

## Source Code ({lang})

File: `{filename}`

```{lang_lower}
{source_code}
```

## Translation Requirements

### Semantics Preservation
- The Lean 4 output must preserve the **exact same control flow** as the original: all branches, \
loops, early returns, and error paths must be faithfully represented.
- Recursive functions must remain recursive. Iterative loops should be translated to tail-recursive \
functions or `for`/`while` do-notation as appropriate.
- Side effects (I/O, mutation) must be captured in the appropriate monad (`IO`, `ST`, `StateM`, etc.).

### Type Handling
- **Explicitly annotate all top-level definitions** with their Lean 4 types.
- Map source-language types to Lean 4 types as follows:
  - `int` / `long` → `Int` (or `UInt32` / `UInt64` if overflow semantics matter)
  - `float` / `double` → `Float`
  - `char` → `Char`
  - `bool` → `Bool`
  - `void` (return) → `Unit` or the appropriate monad return
  - Arrays / lists → `Array α` or `List α`
  - Pointers → model with `Array` + index, or `Ref` in `ST`/`IO` when mutation is needed
  - Structs / classes → `structure` definitions
  - Enums → `inductive` types
  - `None` / `NULL` → `Option α`
- If the source uses generic or polymorphic patterns, use Lean 4 universe-polymorphic types.

### Lean 4 / Mathlib4 Conventions
- Use `import Mathlib` only for the specific modules needed (e.g., `import Mathlib.Data.List.Basic`).
- Follow Lean 4 naming conventions: `camelCase` for definitions, `PascalCase` for types/structures.
- Use `do` notation for monadic code.
- Add `deriving Repr, DecidableEq, Hashable` to structures/inductives where useful.
- Use `#check` and `#eval` comments to show how the translated code can be verified.
- Ensure the output compiles with `lake build` against a recent Mathlib4 toolchain.

### Error Handling
- Translate exceptions / error returns to `Except ε α` or `Option α`.
- Translate assertions to `if ... then panic! ...` or `dbg_trace` as appropriate.

### Documentation
- Add a module-level docstring explaining what the original code does.
- Add brief inline comments where the translation is non-obvious.

## Output Format

Return ONLY the Lean 4 source code (no explanations outside the code). The code must:
1. Be a single, self-contained `.lean` file.
2. Compile without errors against Lean 4 / Mathlib4 (latest stable toolchain).
3. Include necessary `import` statements at the top.
4. Include a `#check` or `#eval` example at the bottom demonstrating usage.
"""


def detect_language(filepath: Path) -> str:
    """Detect source language from file extension."""
    ext = filepath.suffix.lower()
    lang = LANG_HINTS.get(ext)
    if lang is None:
        print(
            f"Warning: unrecognized extension '{ext}', defaulting to C.",
            file=sys.stderr,
        )
        return "C"
    return lang


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a structured LLM prompt to translate C or Python source code into compilable Lean 4.",
    )
    parser.add_argument(
        "source_file",
        type=str,
        help="Path to a C (.c/.h) or Python (.py) source file to translate.",
    )
    parser.add_argument(
        "--lang",
        type=str,
        default=None,
        help="Override language detection (e.g., 'C' or 'Python').",
    )
    args = parser.parse_args()

    filepath = Path(args.source_file)
    if not filepath.is_file():
        print(f"Error: file not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    source_code = filepath.read_text(encoding="utf-8")
    if not source_code.strip():
        print(f"Error: file is empty: {filepath}", file=sys.stderr)
        sys.exit(1)

    lang = args.lang if args.lang else detect_language(filepath)

    prompt = PROMPT_TEMPLATE.format(
        lang=lang,
        lang_lower=lang.lower(),
        filename=filepath.name,
        source_code=source_code,
    )

    print(prompt)


if __name__ == "__main__":
    main()
