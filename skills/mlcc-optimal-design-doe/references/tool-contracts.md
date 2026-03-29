# Tool Contracts

이 reference는 DOE 최적설계 skill이 의존하는 두 tool의 계약을 설명한다.

## Contents

- check_optimal_design
- optimal_design
- 공통 해석 규칙

## check_optimal_design

목적:

- 주어진 `lot_id`가 DOE 시뮬레이션 기준 reference로 사용 가능한지 확인한다.

입력:

- `lot_id`: string

출력:

- `충족인자`: reference에 이미 존재해서 시뮬레이션에 사용할 수 있는 인자 목록
- `부족인자`: reference에 없어서 현재 이 `lot_id`로는 시뮬레이션을 진행할 수 없는 인자 목록

사용 규칙:

- 새 `lot_id`가 들어오면 가장 먼저 호출한다.
- `부족인자`가 하나라도 있으면 `optimal_design`을 호출하지 않는다.
- `부족인자`는 사용자가 직접 채워넣는 값이 아니라, 대개 reference LOT을 바꿔야 해결되는 조건으로 취급한다.

권장 응답 해석:

- `충족인자`는 이후 payload를 만들 때 reference에서 가져올 수 있는 기반 정보다.
- `부족인자`는 사용자에게 그대로 보여주고 다른 `lot_id` 또는 다른 reference를 요청한다.

## optimal_design

목적:

- reference LOT과 사용자가 원하는 target, DOE 입력값을 받아 최적 설계 후보를 계산한다.

입력:

- `lot_id`
- `targets.*`
- `params.*`

현재 가정:

- `targets.*`는 약 4개다.
- `params.*`는 약 10개다.
- 현재 payload는 `절대값` 기준이다.

### params.* 값 형식 — 초기 실행 vs 재실행

**초기 실행 (ref lot 기반 DOE)**:

각 `params.*` 필드에는 ref lot 값을 중심으로 사용자가 지정한 범위(예: ±5%)에 걸친 **다중 포인트 리스트**를 채운다.

예시 — 사용자가 "스크린 L 사이즈는 ref 대비 ±5%까지 21포인트로" 요청한 경우:

- ref lot의 Screen L = 100 um
- `params.screen_l`: `[95.0, 95.5, 96.0, 96.5, 97.0, 97.5, 98.0, 98.5, 99.0, 99.5, 100.0, 100.5, 101.0, 101.5, 102.0, 102.5, 103.0, 103.5, 104.0, 104.5, 105.0]`

즉, 절대값을 등간격으로 나열한 리스트다. 이 리스트의 길이와 간격은 사용자가 요청한 범위와 포인트 수에 따라 결정된다.

**재실행 (특정 설계 랭크 기반)**:

사용자가 top 5 중 특정 후보의 설계값을 base로 일부만 변경해 재실행할 때, `params.*`는 해당 후보의 설계값을 기준으로 **단일 값 리스트** `[value]`를 채운다.

예시 — 사용자가 "3번 후보에서 Sheet T만 5.2로 바꿔서 다시" 요청한 경우:

- 3번 후보의 전체 설계값을 base로 복사
- `params.sheet_t`: `[5.2]` (사용자가 변경한 값)
- `params.electrode_w`: `[680]` (3번 후보의 값 그대로)
- `params.margin_l`: `[85]` (3번 후보의 값 그대로)
- ... (나머지도 각각 단일 값 리스트)

이 구분이 중요한 이유: 초기 실행은 넓은 탐색 공간에서 최적 조합을 찾는 DOE이고, 재실행은 이미 선택된 후보를 미세 조정하는 단일 포인트 시뮬레이션이다.

출력:

- `top 5` 최적 설계 후보
- 각 후보의 전체 설계값
- 각 후보의 예측 결과값

중요 규칙:

- 각 후보의 `전체 설계값`이 반환되므로, 후속 rerun 시 그 후보를 base로 사용한다.
- 사용자가 특정 후보의 일부만 바꾸라고 하면, 해당 후보의 전체 설계값을 복사하고 지정한 필드만 덮어써서 새 payload를 만든다.

## search_rag (공정검사표준 검증용)

목적:

- 시뮬레이션 결과의 각 설계값이 공정검사표준(Process Inspection Standard) 범위 안에 있는지 확인한다.
- 사용자에게 결과를 보여주기 **전에** 이 검증을 수행한다.

입력:

- `query`: 검증하려는 설계 항목과 관련 키워드. 예: `"공정검사표준 Sheet 두께 범위"`, `"공정검사표준 전극 폭 상한 하한"`, `"검사표준 Margin L 허용범위"`
- `top_k`: 기본 3~5

출력:

- 관련 공정검사표준 청크 (표준 항목명, 상한/하한, 단위, 적용 조건 등)

사용 규칙:

- `optimal_design` 결과가 나온 직후, top 5 각 후보의 핵심 설계값(Sheet T, Electrode W, Margin L, Margin W, Cover T, 전극수 등)에 대해 공정검사표준을 검색한다.
- 설계 항목별로 검색하되, 유사한 항목은 묶어서 쿼리할 수 있다. 예: Sheet T와 Cover T를 `"공정검사표준 두께 Sheet Cover 허용범위"`로 한 번에 검색.
- 검색된 표준에서 상한/하한이 확인되면, 각 후보의 해당 값이 범위 안인지 비교한다.
- 범위를 벗어나면 `⚠️ 공정검사표준 초과`로 표시한다.
- 해당 설계 항목에 대한 표준 정보가 검색되지 않으면 `공정검사표준 미확인`으로 표시하고 넘어간다.

## 공통 해석 규칙

- 실제 field 이름은 tool schema를 우선한다.
- skill 문서에 적힌 `targets.*`, `params.*`는 개념적 그룹명이다.
- 실제 tool description에 field 이름이 나오면 그 이름으로 payload를 만든다.
- nested schema보다 flat schema를 우선 해석한다.

예:

- `targets.capacity`
- `targets.thickness`
- `targets.length`
- `targets.width`

또는 tool이 flat schema라면:

- `target_capacity`
- `target_thickness`
- `target_length`
- `target_width`

둘 중 무엇을 쓰든 실제 tool contract를 따른다.
