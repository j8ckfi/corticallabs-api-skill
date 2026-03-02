# External Context Coverage

This skill extends the direct docs mirror with three external source groups:

1. `cl-sdk` source repository
- Purpose: authoritative API signatures, defaults, and class/method availability.
- Snapshot output: `sdk-signatures.md`

2. `cl-api-doc` notebook repository
- Purpose: practical runnable examples and tutorial workflows.
- Snapshot output: `cl-api-doc-index.md`

3. CL API whitepaper (`arXiv:2602.11632`)
- Purpose: design intent and contract-based semantics context.
- Snapshot outputs:
  - `whitepaper/whitepaper-abstract.txt`
  - `whitepaper/whitepaper-fulltext.txt` (when PDF text extraction succeeds)

## Version lock

Use `source-lock.json` to verify:
- external repo commit SHAs
- detected `cl-sdk` version from `pyproject.toml`
- timestamp of the generated snapshot

## Precedence order

When answering questions or implementing code:
1. `sdk-signatures.md` (source-derived signatures)
2. `upstream-text/*.txt` docs mirror and module references
3. `cl-api-doc-index.md` examples
4. whitepaper context (design rationale, not API surface)

If an answer is not backed by these sources, mark it as unknown and propose verification steps.
