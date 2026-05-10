You are building a large-scale dataset of C and Python functions, their Lean 4 translations, natural-language specifications, Lean theorem statements, validation artifacts, and proofs. Use this paper as reference: https://red.anthropic.com/2026/property-based-testing/

Your job is to generate one JSON record per function.

The core principle is PROPERTY-FIRST, NOT PROOF-FIRST:
1. Understand the original function and its context.
2. Generate a comprehensive but nonredundant set of natural-language properties in English.
3. Accept only properties that are evidence-grounded, non-vacuous, and useful.
4. Translate the source function to Lean 4.
5. Translate the accepted natural-language properties into Lean theorem statements.
6. Compile and validate everything.
7. Prove as many theorems as possible in Lean 4 without using vacuous or trivial proofs.
8. Preserve all theorem statements even when proofs fail.
9. Split the dataset based on whether a designated Claude prover configuration can prove the theorems, but never drop theorem statements from the record.

Your outputs must be suitable for a formal verification dataset, not just for testing.

GENERAL GOALS

Generate dataset entries only for functions whose behavior can be meaningfully specified and modeled in Lean.
Prioritize deterministic, side-effect-light, semantically clear functions with useful names, docstrings/comments, tests, companion operations, or obvious reference implementations.
Skip or flag functions whose intended semantics are too subtle, too underdocumented, or too dependent on hidden state to generate reliable theorem statements.

FUNCTION ELIGIBILITY

Skip a function if any of the following apply, unless a bounded and explicit model is clearly possible:
- filesystem, socket, pipe, subprocess, fd-based, or network I/O
- inline assembly, compiler intrinsics, signal handlers, thread synchronization primitives
- hidden mutable global state not passed explicitly as input/output state
- uncontrolled malloc/free/realloc patterns
- function pointers requiring dynamic dispatch
- variadic functions
- wide strings, packed structs, unions with layout-sensitive semantics, opaque pointer casts, or other platform-specific behavior that cannot be modeled faithfully
- heavy floating-point iterative algorithms without a clear bounded specification
- semantics that are underdocumented and cannot be triangulated from code, callers, comments, tests, or mathematics

For C, prefer:
- scalar arithmetic and comparisons
- array/list algorithms
- string/byte-buffer utilities
- struct transformations
- search, selection, sorting, parsing, formatting, normalization, checksum-like pure computations
- pointer-plus-length APIs that can be modeled as arrays and pure state transformers

For Python, prefer:
- pure functions over ints, bools, strings, lists, tuples, dicts, sets, arrays, and dataclasses
- parsing, formatting, normalization, encoding/decoding, collection transforms, numerical utilities, graph/list helpers, and deterministic algorithms
- functions with clear equivalence to stdlib or companion APIs

UNDERSTAND THE TARGET BEFORE WRITING PROPERTIES

For each function, build an evidence dossier from:
- the function signature and type information
- the function name
- docstrings and comments
- the full source body
- neighboring helper functions
- callers and call sites
- existing unit tests / doctests / examples
- companion functions such as encode/decode, push/pop, parse/format, add/remove, serialize/deserialize
- a trustworthy reference implementation, standard library equivalent, or mathematically simpler specification, when available

Do not infer properties only from the implementation details of the translated Lean function. The natural-language properties must be derived from the original source and its context.

NATURAL-LANGUAGE PROPERTY GENERATION

Create a first-class English-only property bank before generating Lean theorem statements.

Each natural-language property must be:
- written as clear English sentences
- behaviorally precise
- universally quantified in spirit, not an example on literals
- accompanied by English preconditions
- accompanied by evidence explaining why the property is justified
- accompanied by a short note explaining why the property is useful for correctness
- accompanied by at least one plausible wrong behavior or mutant it is meant to rule out

The property bank must be comprehensive across all applicable correctness dimensions, but nonredundant within each dimension.

Look for the following high-value property families whenever they apply:
- output invariants
- structural invariants such as length, shape, key set, ordering, uniqueness, sortedness, partitioning, permutation, or preservation
- round-trip laws such as decode(encode(x)) = x or parse(format(x)) = x
- inverse-operation laws such as add/remove, push/pop, insert/delete
- agreement with a reference implementation or standard library equivalent
- equivalence between optimized and simple implementations
- algebraic laws such as idempotence, commutativity, associativity, distributivity, monotonicity
- case-partition characterizations over all important input regions
- metamorphic / relational properties tying multiple executions together
- boundary and error behavior
- frame-style properties for state transformers: which parts of the modeled state are changed and which are preserved
- numerical range, monotonicity, and approximation properties for floating point, using explicit epsilons where required
- companion-function properties spanning multiple functions, not only single-function facts

When outputs are relational rather than unique, state the intended equivalence relation in English. Do not force an exact-output property when correctness is naturally “up to permutation”, “up to normalization”, “up to key-order”, “up to semantic equivalence”, etc.

If a strong reference implementation exists, prioritize that theorem family highly.
If no exact oracle is available, prioritize relational and metamorphic properties.

Do not include “does not crash” or “returns some value” as a primary theorem unless the function is fundamentally specified only by totality/safety on valid inputs. For theorem datasets these are usually too weak on their own.

PROPERTY ACCEPTANCE RUBRIC

A candidate natural-language property is ACCEPTED only if all of the following hold:

1. Groundedness
It is strongly supported by docs, comments, naming, callers, tests, companion APIs, or domain mathematics.

2. Non-vacuity
Its preconditions are satisfiable.
Its conclusion is not a tautology.
It is not true for every function of the same type.
It is not merely a point example on a concrete literal.
It is not only a restatement of the type signature.
It is not just “the function returns without error” unless that is a meaningful safety theorem.

3. Discriminative power
The property would fail for at least one plausible mutant or wrong implementation.
Typical mutants include:
- wrong comparison direction
- missing edge case branch
- off-by-one index or bound
- forgetting to update length
- dropping/duplicating elements
- non-preservation of key set
- reversing order
- returning unsorted output
- incorrect handling of empty / singleton / zero / negative / null / NaN / infinity cases
- changing one field when other fields should be preserved
- using a faster but wrong formula

4. Orthogonality
The property adds genuinely new behavioral coverage rather than repeating a stronger accepted property.

5. Formalizability
The property can be expressed against the chosen Lean model of the function and its state.

If a property fails the rubric, reject it or rewrite it. Do not keep weak properties just to inflate theorem counts.

ANTI-VACUITY CHECKS YOU MUST RUN

Before translating a property to Lean theorem form:
- produce at least one witness satisfying its preconditions
- generate executable checks for the property against the original source implementation
- if feasible, generate a few simple semantic mutants and confirm that the property rejects at least one of them
- if the property passes on the original function but also passes on obvious wrong mutants, mark it too weak and refine it
- check whether the property is subsumed by stronger accepted properties; if yes, keep only if it is independently useful as a proof lemma

TRANSLATING SOURCE CODE TO LEAN 4

Translate the original function faithfully to Lean 4 with semantics chosen to preserve behavior:
- fixed-width integers should use Lean UInt types where wrapping behavior matters
- signed overflow in C must either be excluded by preconditions or explicitly modeled
- floats must remain floats; do not model them as reals or rationals
- arrays and buffers should be modeled as Array or Fin-indexed collections
- structs should become Lean structures
- pointer mutation should become pure state-threading returning updated structures/arrays/state
- nullable pointers should become Option where appropriate
- pointers-plus-length should become arrays plus explicit size/bounds conditions
- string/byte buffer behavior must preserve null-termination or explicit length semantics as appropriate

If faithful modeling is not possible, skip or partially axiomatize dependencies explicitly.

DEPENDENCY HANDLING

Build a call graph.
Process leaves first.
For non-leaf functions:
- if all callees are already translated, use their translations
- if a callee is outside the dataset or skipped, generate an explicit Lean axiom only for that callee
- record which dependencies were fully translated and which were axiomatized, and why

NATURAL-LANGUAGE PROPERTIES TO LEAN THEOREMS

Translate only ACCEPTED natural-language properties into Lean theorem statements.

Important:
- one NL property may translate into one theorem, several theorems, helper predicates, or helper lemmas
- do not force bad theorem granularity
- preserve the meaning of the English property
- use helper predicates for notions like sortedness, permutation, valid string, valid buffer, frame condition, semantic equivalence, approximation within epsilon, etc.
- if a property naturally decomposes into multiple orthogonal Lean theorems, do that
- if a property is relational or coupled, do not over-fragment it into misleadingly independent atoms

The theorem collection for a function should be a characteristic specification:
a reviewer should be able to reconstruct the intended behavior from the natural-language property bank plus theorem statements alone, and a wrong implementation should fail at least one accepted theorem.

THEOREM QUALITY BAR

Reject or rewrite a theorem if:
- it is a literal test disguised as a theorem
- it is trivial for any implementation
- its hypotheses are unsatisfiable
- it only states type-level well-formedness with no behavioral content
- it is weaker than already accepted theorems with no proof-engineering value
- it exists only to make proof search easier while adding no specification value

Preferred theorem families:
- reference/spec equivalence
- round-trip / inverse laws
- output invariants
- algebraic laws
- complete case analysis over input regions
- boundary and error semantics
- structural preservation
- frame and state-change characterization
- numerical bounds / monotonicity / approximation

For list/set/map like functions, always consider:
- size/length behavior
- membership / key-set behavior
- order/sortedness behavior
- preservation / permutation behavior
- reconstruction laws

For parsers/formatters/serializers/encoders, always consider:
- round-trip laws
- normalization laws
- accepted-language / canonical-form invariants

For pointer/state-transforming C functions, always consider:
- state fields modified
- state fields preserved
- return/state correspondence
- bounds and null handling
- aliasing assumptions only if explicitly modeled

VALIDATION AND COUNTEREXAMPLE LOOP

Run the following loop in order:

1. Compile the Lean translation.
2. Run source-language executable tests, including property-oriented randomized checks.
3. Run Lean executable tests or evaluations on the Lean translation.
4. Compare source and Lean behavior on the same test inputs.
5. Compile Lean theorem statements before proofs.
6. Attempt proofs.
7. If source and Lean disagree, fix the Lean translation and restart validation.
8. If a property fails, decide whether:
   - the original function is wrong,
   - the property is wrong,
   - the generated inputs violate real preconditions,
   - or the Lean translation is wrong.
   Reflect and revise accordingly.

For sparse-precondition properties, do not rely on naive random generation with high discard rates.
Instead, synthesize generators or constructors that satisfy the preconditions directly.

Always test important edge cases:
- integer zero, one, minus one where meaningful
- min/max values and powers of two boundaries
- empty, singleton, and small collections
- repeated elements
- null / None / optional absence cases
- NaN, infinities, negative zero, epsilon-scale values for floats
- boundary lengths and indices
- malformed but representable inputs when error behavior is part of the contract

PROOF POLICY

Attempt to prove as many accepted theorem statements as possible in Lean 4.

However:
- never weaken a correct theorem statement just to get a proof
- never replace a strong theorem with a trivial theorem to improve proof counts
- never count a vacuous or trivial proof as success

BANNED AS FINAL “PROOFS” UNLESS THE THEOREM IS GENUINELY SUBSTANTIVE
- native_decide / decide for concrete or shallow statements
- rfl if the theorem merely unfolds to itself and does not constrain behavior meaningfully
- trivial simp on literals
- automated proofs that hide all proof structure
- proofs that exploit unsatisfiable hypotheses
- proofs that ignore the important returned value or updated state

Preferred proof style:
- explicit intros
- cases / induction where appropriate
- named intermediate facts with have
- rw, calc, apply, exact with explicit lemmas
- bounded use of omega, ring, norm_num, etc. only as leaf closers after structure is exposed
- if a hard sublemma is the blocker, isolate that sublemma and localize sorry there rather than replacing the whole proof by sorry

If a theorem cannot be completed under the proof budget:
- keep the theorem statement
- keep the best partial proof skeleton
- localize sorry narrowly
- mark proof_status = "incomplete"
- include proof_notes explaining the blocker

PROOF ORDERING

Within a function, prove in this order:
1. helper predicates and support lemmas
2. shape/range/basic invariant theorems
3. structural preservation theorems
4. algebraic / monotonic / relational lemmas
5. reference-implementation agreement or strongest end-to-end theorems

This ordering is designed to maximize final proof coverage without sacrificing statement quality.

OUTPUT SCHEMA

Output one JSON record per function with these exact top-level keys:

{
  "language": "Python" | "C",
  "source": string,
  "lean_translation": string,
  "tests": string,
  "lean_tests": string,
  "nl_properties": [
    {
      "id": string,
      "english_statement": string,
      "category": string,
      "preconditions_english": string,
      "evidence": [string],
      "why_useful": string,
      "plausible_wrong_behaviors_ruled_out": [string],
      "accepted": boolean,
      "rejection_reason": null | string
    }
  ],
  "theorems": [
    {
      "property_id": string,
      "name": string,
      "statement": string,
      "proof": string,
      "proof_status": "complete" | "incomplete" | "rejected_trivial" | "statement_only",
      "proof_nontrivial": boolean,
      "proof_notes": string
    }
  ],
  "translated_deps": [string],
  "deps_fully_translated": boolean,
  "axiomatized_deps": [
    {
      "name": string,
      "lean_axiom": string,
      "reason": string
    }
  ],
  "validation": {
    "lean_translation_compiles": boolean,
    "source_tests_pass": boolean,
    "lean_tests_pass": boolean,
    "source_lean_agree_on_tests": boolean,
    "theorem_statements_compile": boolean,
    "anti_vacuity_checks_passed": boolean,
    "mutation_checks_summary": string
  },
  "claude_provability": {
    "designated_model": string,
    "lean_version": string,
    "proof_budget": string,
    "function_bucket": "all_proved" | "some_proved" | "none_proved" | "statements_failed",
    "theorem_results": [
      {
        "name": string,
        "result": "proved" | "not_proved" | "trivial_rejected" | "statement_failed"
      }
    ]
  },
  "skip_reason": null | string
}

DATASET SPLITS

Maintain one canonical dataset containing all records and all theorem statements.

Also materialize derived views:
- all_proved: functions whose accepted theorem statements were all proved nontrivially by the designated Claude prover configuration
- some_proved: functions with at least one proved nontrivial theorem and at least one unproved theorem
- none_proved: functions whose theorem statements compile but none were proved nontrivially
- statements_failed: functions where theorem-statement generation/compilation failed

Important:
- preserve all theorem statements in every function record
- do not delete unproved theorems from all_proved or some_proved records
- theorem success must be evaluated under a pinned prover configuration: exact Claude model, Lean version, temperature, retry count, and time budget

FAILURE HANDLING

If a function is skipped, still emit a record with source, language, and skip_reason.
If theorem statements are strong but unproved, keep them.
If proof attempts are shallow or vacuous, reject them and keep the statements.
If semantics are too subtle to infer reliably, skip rather than hallucinate properties.

FINAL QUALITY BAR

For every accepted function record, ask:
- Are the natural-language properties genuinely English specifications of the original function?
- Are they comprehensive across all important correctness dimensions?
- Are they evidence-based?
- Are they non-vacuous?
- Would they fail on plausible wrong implementations?
- Do the Lean theorem statements faithfully encode those properties?
- Does the Lean translation match the source behavior?
- Are the proofs substantive rather than trivial?
- Are all theorem statements preserved even when proof search fails?

If the answer to any of these is no, revise the record before finalizing it.
