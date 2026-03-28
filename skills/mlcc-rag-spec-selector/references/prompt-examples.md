# Prompt Examples

Use these examples when invoking the skill from Korean, English, or mixed-language user requests.

## Contents

- Spec Preselection
- Reliability and Family Selection
- Candidate Comparison
- Part-Number Skeleton Review
- Guardrailed Validation Requests

## Spec Preselection

### Example 1

`고객사 의뢰로 스펙 만족하는 MLCC 기종부터 선정해야해. A 온도특성, 정격전압 4V, L size 최대 690um, W size 최대 390um, T size 최대 550um, 기준용량 4.8uF, M편차, 고주파 저전계에서 1V DC 전계를 인가했을 때 최소 3.45uF 를 만족하는 기종을 catalog 기준으로 찾아줘.`

Expected behavior:

- interpret `A` as `X5R`
- normalize dimensions to `mm`
- derive nearest standard nominal candidates around `4.8uF`
- keep the `1V DC` and `high-frequency` requirement in validation-only status unless exact evidence is retrieved

### Example 2

`Use $mlcc-rag-spec-selector to preselect SEMCO MLCC candidates for X7R, 6.3V, 0201/0603-class dimensions, nominal around 4.7uF, +/-20% tolerance. Answer in Korean and separate catalog facts from datasheet-only checks.`

Expected behavior:

- resolve code tables first
- search nearby new-product anchors
- return candidate skeletons if no exact orderable part is proven

## Reliability and Family Selection

### Example 3

`서버 전원용이라 습도 신뢰성이 중요해. 85C/85%RH/1000h 쪽에 맞는 family가 필요하고, 가능한 경우 High Level II 기준으로 size와 voltage 조건에 맞는 후보를 찾아줘.`

Expected behavior:

- route to `High Level II`
- search `reliability_level` and relevant product-family chunks before example parts
- explain if the reliability family is catalog-backed but the exact lineup still needs validation

### Example 4

`I need a low acoustic noise MLCC candidate for a PMIC/DC-DC area. Search the catalog and tell me whether Low Acoustic Noise or MFC is the better family anchor for this use case.`

Expected behavior:

- compare family descriptions first
- only move to part examples after the family decision is grounded in retrieved chunks

## Candidate Comparison

### Example 5

`4.8uF exact nominal이 카탈로그 표준이 아니면 4.7uF와 5.1uF 후보를 둘 다 비교해줘. 어느 쪽이 catalog-based preselection으로 더 안전한지 이유를 설명하고, exact guarantee는 하지 마.`

Expected behavior:

- use E-series nominal logic
- compare `475` versus `515`
- keep final language at preselection level

## Part-Number Skeleton Review

### Example 6

`CL03A515MR3?N?# 같은 skeleton이 현재 스펙에 맞는지 검토해줘. 각 code가 무엇을 의미하는지 풀어서 설명하고, 확정 불가능한 tail code는 TBD로 유지해줘.`

Expected behavior:

- decode the proven fields
- refuse to fabricate unresolved 8th-11th codes
- state which chunk types support the interpretation

## Guardrailed Validation Requests

### Example 7

`이 후보가 1V DC 바이어스에서 반드시 3.45uF 이상인지 보장해줘.`

Expected behavior:

- refuse a hard guarantee unless exact retrieved evidence exists
- answer with catalog-backed caution wording
- move the ask into `needs datasheet or measured validation`
