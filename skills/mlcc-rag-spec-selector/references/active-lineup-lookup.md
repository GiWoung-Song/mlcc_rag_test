# Active Lineup Lookup

Use this reference when a request is partial, ambiguous, or requires checking whether a matching product is currently flowing in the internal DB.

## Contents

- Purpose
- When to Invoke the DB Lookup
- Tool Contract
- Pattern Construction
- Result Handling
- Follow-up Question Strategy
- Output Template

## Purpose

The catalog tells you what is electrically plausible and how the code system works. The DB lookup tells you whether matching `chip_prod_id` rows exist in the `mdh_continous_view_3` view right now.

Use the two data sources together:

- `search_rag` for code interpretation, family logic, thickness logic, and catalog anchors
- active-lineup DB lookup for current `chip_prod_id` matches from a partial or full pattern

## When to Invoke the DB Lookup

Invoke the DB lookup when any of these are true:

- the user gives only part of the code or only part of the electrical constraints
- unresolved code slots remain after catalog reasoning
- the user asks whether such a chip is currently flowing
- multiple catalog-feasible skeletons remain and you need to show active candidates before asking the next question

Do not wait for a perfect full code if a useful partial pattern already exists.
Do not tell the user that you will check the DB in a future turn if the tool is already available now.

## Tool Contract

The skill assumes an active-lineup function tool exists with a flat input schema.

Preferred contract:

- input parameter: `chip_prod_id`
- type: `string`
- output: list of matching rows or at least a list of matching `chip_prod_id` values

Recommended behavior for the tool description:

- state that the tool searches `mdh_continous_view_3`
- state that it matches against the `chip_prod_id` column
- state whether `chip_prod_id` should be passed as a raw code fragment or as a SQL-like wildcard pattern
- state what the returned list contains

Preferred schema style:

- keep the tool flat with one top-level string argument
- avoid nested filter objects unless the implementation truly requires them

If the actual tool name differs, use the function whose description explicitly says it searches `chip_prod_id`.

## Pattern Construction

Build two related artifacts:

1. `candidate skeleton`
   - human-readable catalog reasoning form
   - examples: `CL03A515MR3?N?#`, `CL32[X5R TBD]106[tol TBD]O[...]`
2. `chip_prod_id lookup pattern`
   - DB-facing form for the lookup tool
   - preserve known literal code positions
   - use `_` for each unknown single-character slot
   - use `%` only when the tool expects SQL-style variable-length matching

Rules:

- preserve `CL` and known size code
- preserve known temperature-characteristic, capacitance, tolerance, voltage, and thickness codes
- replace each unresolved single-character position with `_`
- if the remainder length is uncertain or the backend expects contains search, wrap with `%` as the actual tool contract requires

Examples:

- catalog reasoning says `size=32`, `capacitance=106`, `voltage=O`, but temperature characteristic and several tail fields are unresolved
  - human skeleton: `CL32[TCC TBD]106[TOL TBD]O[...]`
  - DB lookup pattern if the tool accepts fixed-length pattern: `CL32_106_O____`
  - DB lookup pattern if the tool expects surrounding SQL wildcards: `%CL32_106_O____%`
- catalog reasoning says `CL03A515MR3` is the proven front section but the remaining four slots are unresolved
  - DB lookup pattern: `CL03A515MR3____`
  - or `%CL03A515MR3____%` if the tool requires wildcard framing

Prefer the narrowest useful pattern. Do not replace the whole suffix with `%` if several code positions are already known.

## Result Handling

### Zero Hits

- state that no current DB hits were found for the pattern
- keep the catalog-feasible skeletons visible
- ask whether the user can relax one unresolved field such as temperature characteristic, tolerance, family, or nominal capacitance

### One Hit

- show the returned `chip_prod_id`
- state that it is a current DB hit, not automatic proof of every electrical requirement
- continue validation against catalog guardrails and any remaining user constraints

### Multiple Hits

- show the list, or the top subset if it is long
- summarize the major differences if visible from the returned codes
- ask exactly one targeted follow-up question that removes the biggest ambiguity

Examples of good follow-up axes:

- missing temperature characteristic
- missing tolerance
- missing reliability family
- preference between nearest standard nominal values

Do not choose one active hit arbitrarily when multiple plausible hits remain.

## Follow-up Question Strategy

Ask one short question that discriminates the unresolved slot with the highest payoff.

Good examples:

- `현재 흐르는 품목은 여러 개입니다. 온도특성은 X5R과 X7R 중 어느 쪽이 필요합니까?`
- `현행품은 찾았지만 M편차와 K편차가 섞여 있습니다. 허용 편차를 확정해 주세요.`
- `현재 DB hit는 Standard와 High Level II가 함께 나옵니다. 산업용 신뢰성이 필요한지 확인해 주세요.`

Avoid broad questions like:

- `원하는 조건을 더 알려주세요.`

## Output Template

When a DB lookup was used, include:

1. `chip_prod_id lookup pattern`
2. `active lineup hits from DB`
3. `what remains ambiguous`
4. `next question`

Example wording:

- `chip_prod_id lookup pattern: CL32_106_O____`
- `active lineup hits from DB: [ ... ]`
- `current DB hits confirm that this front-side code family exists in the current lineup, but temperature characteristic and tail-code selection remain unresolved.`
- `next question: 온도특성은 X5R(A)와 X7R(B) 중 어느 쪽이 필요합니까?`
