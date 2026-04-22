# Plan: Extending VeriBench to Support C Programs

## 1. Background

[VeriBench](https://openreview.net/forum?id=rWkGFmnSNl) is an end-to-end formal verification benchmark for AI code generation in Lean 4. It currently takes **Python** source code (with documentation and specifications) and evaluates whether an LLM agent can produce a fully proved, machine-checkable Lean 4 implementation — including specifications, implementations, and correctness proofs.

**Goal:** Extend VeriBench so that it can also accept **C programs** as input, parse them, extract the necessary semantic information, and feed structured translation tasks to the LLM pipeline. The output remains Lean 4 with Mathlib4 proofs, but the source language is now C.

## 2. Key Challenges: C vs Python

| Aspect | Python (current) | C (proposed) |
|--------|------------------|--------------|
| Type system | Dynamic, inferred | Static, explicit, but with implicit casts and pointer arithmetic |
| Memory model | GC, references | Manual allocation, pointers, stack vs heap |
| Control flow | Exceptions, generators | `goto`, `longjmp`, signal handlers |
| Preprocessing | None | `#include`, `#define`, macros, conditional compilation |
| Undefined behavior | Rare | Pervasive (signed overflow, null deref, aliasing) |
| Standard library | High-level (`list`, `dict`) | Low-level (`malloc`, `memcpy`, `strlen`) |

## 3. Modules That Need Changes

### 3.1 Frontend / Parser Module

**Current state:** Uses Python AST (`ast` module) to parse Python source into a structured IR.

**Changes needed:**
- Add a **C parser frontend** using `pycparser` (pure Python C99 parser) or `tree-sitter` with the C grammar.
- Handle preprocessing: either require pre-processed input or integrate `gcc -E` as a preprocessing step.
- Extract: function signatures, struct definitions, typedefs, global variables, control flow graph.

### 3.2 Type Mapping Module

**Current state:** Maps Python types (via type hints or inference) to Lean 4 types.

**Changes needed:**
- New `c_type_mapper` module that maps C types to Lean 4:

| C Type | Lean 4 Type |
|--------|-------------|
| `int`, `int32_t` | `Int32` or `Int` |
| `unsigned int`, `uint32_t` | `UInt32` |
| `int64_t`, `long long` | `Int64` or `Int` |
| `float` | `Float` |
| `double` | `Float` (Lean 4 uses 64-bit) |
| `char` | `UInt8` or `Char` |
| `bool`, `_Bool` | `Bool` |
| `T*` (pointer) | `Array T` + index, or `Option (Ref T)` |
| `T[]` (array param) | `Array T` with length param |
| `struct S { ... }` | `structure S where ...` |
| `enum E { ... }` | `inductive E where ...` |
| `void` (return) | `Unit` |
| `NULL` | `Option.none` |
| `union` | `inductive` with shared memory note |

### 3.3 Specification Extractor

**Current state:** Extracts pre/post-conditions from Python docstrings and type hints.

**Changes needed:**
- Parse C-style doc comments (`/** ... */`, Doxygen-style `@param`, `@return`, `@pre`, `@post`).
- Extract specifications from ACSL-style annotations (`/*@ requires ... ensures ... */`) if present.
- Infer basic specs from `assert()` calls, `NULL` checks, and bounds checks.
- Handle `errno`-based error contracts.

### 3.4 IR / Intermediate Representation

**Current state:** Python AST → VeriBench IR → Lean 4 skeleton.

**Changes needed:**
- Extend the IR to represent C-specific constructs:
  - Pointer operations (dereference, address-of, arithmetic)
  - Manual memory management (`malloc`/`free` → modeled as `StateM` with an allocator)
  - `goto` statements (convert to structured control flow or explicit state machine)
  - `switch`/`case` with fallthrough
  - Bitwise operations
  - `sizeof`, casts, type punning
- Add UB (undefined behavior) annotation nodes so the Lean translation can add proof obligations for UB-freedom.

### 3.5 Lean 4 Code Generator

**Current state:** Generates Lean 4 skeleton from Python-derived IR.

**Changes needed:**
- Memory model encoding: model heap as `HashMap Nat (Σ α, α)` or use Lean 4's `ST` monad for mutable state.
- Pointer arithmetic → array indexing with bounds proof obligations.
- Generate `sorry`-annotated proof obligations for:
  - No null pointer dereference
  - No buffer overflow
  - No signed integer overflow
  - No use-after-free
  - No double-free
- Emit `#check` / `#eval` test harnesses.

### 3.6 Prompt Generator

**Current state:** Generates structured prompts for the LLM to fill in proofs.

**Changes needed:**
- Add C-specific prompt context: memory model explanation, UB proof obligations.
- Include C standard library semantics hints (e.g., `strlen` specification).
- Reference Mathlib4 lemmas relevant to bitvector arithmetic (`Mathlib.Data.BitVec`).

### 3.7 Evaluation / Checker Module

**Current state:** Validates Lean 4 output compiles and proofs close.

**Changes needed:**
- Add C-specific evaluation metrics:
  - UB-freedom proof coverage (what % of UB obligations are discharged)
  - Memory safety proof coverage
  - Functional equivalence (test-based: compile C with known inputs, compare to Lean `#eval`)
- Optional: integrate with CompCert-style semantics for ground-truth checking.

## 4. New Modules to Create

### 4.1 `c_preprocessor.py` — C Preprocessing Adapter

```
function preprocess_c(source_path: str, include_dirs: list[str]) -> str:
    """Run gcc -E to expand macros and includes, return preprocessed source."""
    result = run_command(["gcc", "-E", "-P", "-nostdinc"] + 
                         [f"-I{d}" for d in include_dirs] + 
                         [source_path])
    if result.returncode != 0:
        raise PreprocessError(result.stderr)
    return strip_line_markers(result.stdout)
```

### 4.2 `c_parser.py` — C AST Parser

```
function parse_c(preprocessed_source: str) -> C_AST:
    """Parse preprocessed C into a structured AST."""
    parser = pycparser.CParser()
    ast = parser.parse(preprocessed_source)
    return ast

function extract_functions(ast: C_AST) -> list[FunctionDef]:
    """Walk AST, extract function definitions with signatures, bodies, and doc comments."""
    visitor = FunctionVisitor()
    visitor.visit(ast)
    return visitor.functions

function extract_structs(ast: C_AST) -> list[StructDef]:
    """Extract struct/union/enum definitions."""
    visitor = TypeDefVisitor()
    visitor.visit(ast)
    return visitor.type_defs

function extract_globals(ast: C_AST) -> list[GlobalVar]:
    """Extract global variable declarations."""
    visitor = GlobalVisitor()
    visitor.visit(ast)
    return visitor.globals
```

### 4.3 `c_to_ir.py` — C AST to VeriBench IR

```
function c_ast_to_ir(func: FunctionDef, type_map: TypeMapper) -> IR_Function:
    """Convert a C function AST to VeriBench intermediate representation."""
    
    # Step 1: Resolve types
    params = [(p.name, type_map.map_c_type(p.type)) for p in func.params]
    ret_type = type_map.map_c_type(func.return_type)
    
    # Step 2: Convert body, handling C-specific constructs
    body = convert_body(func.body)
    
    # Step 3: Identify pointer operations and annotate with proof obligations
    obligations = extract_ub_obligations(func.body)
    
    # Step 4: Convert goto to structured control flow
    body = degoify(body)  # Peterson's algorithm or similar
    
    return IR_Function(
        name=func.name,
        params=params,
        return_type=ret_type,
        body=body,
        proof_obligations=obligations,
        doc=func.doc_comment
    )

function degoify(body: IR_Body) -> IR_Body:
    """Convert goto-based control flow to structured control flow."""
    cfg = build_control_flow_graph(body)
    structured = structural_analysis(cfg)  # Sharir's algorithm
    return structured

function extract_ub_obligations(body: C_AST_Body) -> list[ProofObligation]:
    """Identify all potential undefined behavior and create proof obligations."""
    obligations = []
    for node in walk(body):
        if is_pointer_deref(node):
            obligations.append(ProofObligation("not_null", node.pointer, node.loc))
        if is_array_access(node):
            obligations.append(ProofObligation("in_bounds", node.index, node.loc))
        if is_signed_arithmetic(node):
            obligations.append(ProofObligation("no_overflow", node, node.loc))
        if is_free_call(node):
            obligations.append(ProofObligation("valid_free", node.arg, node.loc))
    return obligations
```

### 4.4 `c_spec_extractor.py` — Extract Specifications from C Code

```
function extract_specs(source: str, func: FunctionDef) -> Specification:
    """Extract pre/post-conditions from doc comments, ACSL annotations, and assert()s."""
    
    spec = Specification()
    
    # 1. Parse Doxygen/ACSL comments
    doc = parse_doc_comment(func.doc_comment)
    if doc.preconditions:
        spec.requires = [parse_condition(p) for p in doc.preconditions]
    if doc.postconditions:
        spec.ensures = [parse_condition(p) for p in doc.postconditions]
    
    # 2. Infer from NULL checks at function entry
    for stmt in func.body.leading_checks():
        if is_null_check(stmt):
            spec.requires.append(Condition("not_null", stmt.variable))
        if is_bounds_check(stmt):
            spec.requires.append(Condition("in_bounds", stmt.variable, stmt.bound))
    
    # 3. Infer from assert() calls
    for assert_call in find_asserts(func.body):
        spec.invariants.append(parse_assert_condition(assert_call))
    
    return spec
```

### 4.5 `c_lean_generator.py` — Generate Lean 4 from C-derived IR

```
function generate_lean_from_c(ir_func: IR_Function, spec: Specification) -> str:
    """Generate Lean 4 code skeleton from C-derived IR."""
    
    lean = LeanBuilder()
    
    # Imports
    lean.add_import("Mathlib.Data.Int.Basic")
    lean.add_import("Mathlib.Data.Array.Basic")
    if ir_func.has_bitvec_ops:
        lean.add_import("Mathlib.Data.BitVec")
    
    # Memory model (if function uses pointers)
    if ir_func.uses_pointers:
        lean.add_memory_model_prelude()  # StateM-based heap model
    
    # Struct definitions
    for struct in ir_func.referenced_structs:
        lean.add_structure(struct)
    
    # Specification as Lean propositions
    for req in spec.requires:
        lean.add_precondition(req)
    for ens in spec.ensures:
        lean.add_postcondition(ens)
    
    # Function definition
    lean.begin_def(ir_func.name, ir_func.params, ir_func.return_type)
    lean.add_body(ir_func.body)
    lean.end_def()
    
    # Proof obligations (sorry-annotated)
    for obligation in ir_func.proof_obligations:
        lean.add_theorem(
            name=f"{ir_func.name}_{obligation.kind}",
            statement=obligation.to_lean_prop(),
            proof="sorry"
        )
    
    return lean.build()
```

## 5. Proposed Directory Structure

```
veribench/
├── frontend/
│   ├── python_parser.py      # (existing)
│   ├── c_preprocessor.py     # NEW
│   ├── c_parser.py           # NEW
│   └── c_spec_extractor.py   # NEW
├── ir/
│   ├── ir_types.py           # Extended with C constructs
│   ├── python_to_ir.py       # (existing)
│   └── c_to_ir.py            # NEW
├── backend/
│   ├── lean_generator.py     # Extended
│   ├── c_lean_generator.py   # NEW (C-specific Lean generation)
│   └── prompt_generator.py   # Extended with C context
├── evaluation/
│   ├── checker.py            # Extended
│   └── c_evaluator.py        # NEW (C-specific metrics)
├── data/
│   ├── python_benchmarks/    # (existing)
│   └── c_benchmarks/         # NEW
└── config/
    └── c_type_mappings.yaml  # NEW
```

## 6. Implementation Phases

### Phase 1: Basic C Parsing (Week 1-2)
- Implement `c_preprocessor.py` and `c_parser.py` using `pycparser`.
- Implement `c_type_mapper` for primitive types and structs.
- Handle simple C functions (no pointers, no dynamic memory).

### Phase 2: Memory Model (Week 3-4)
- Design and implement the Lean 4 heap/memory model.
- Handle pointer operations, array access, and `malloc`/`free`.
- Generate UB proof obligations.

### Phase 3: Specification Extraction (Week 5)
- Implement Doxygen/ACSL comment parsing.
- Infer specs from `assert()` and null checks.
- Generate Lean 4 pre/post-condition theorems.

### Phase 4: Evaluation (Week 6)
- Curate C benchmark suite (candidates: small coreutils, crypto primitives, data structures).
- Implement C-specific evaluation metrics.
- Run baseline LLM evaluations.

## 7. Dependencies

- **`pycparser`** — Pure Python C99 parser (preferred for portability).
- **`tree-sitter`** + `tree-sitter-c` — Alternative parser with better error recovery.
- **`gcc`** — For preprocessing (`gcc -E`). Required on the system.
- **Lean 4 toolchain** — For compilation checking.
- **Mathlib4** — Specifically `Data.BitVec`, `Data.Int`, `Data.Array`.

## 8. Open Questions

1. **Scope of C support:** Full C11? Or restrict to a "safe C" subset (no `goto`, no `setjmp`, no VLAs)?
2. **Memory model fidelity:** Full byte-level CompCert-style semantics, or simplified array-based model?
3. **Preprocessing strategy:** Require users to provide preprocessed files, or bundle `gcc -E`?
4. **Benchmark selection:** Which C codebases are best for benchmarking? Candidates:
   - s2n-bignum (AWS crypto, already has [a benchmark](https://arxiv.org/html/2603.14628))
   - SQLite (complex but well-tested)
   - Small coreutils (`wc`, `cat`, `sort`)
   - Embedded systems code (bounded, no dynamic allocation)
5. **Integration with existing C verification tools:** Should we compare against or build on Frama-C/ACSL, VST, or CompCert outputs?
