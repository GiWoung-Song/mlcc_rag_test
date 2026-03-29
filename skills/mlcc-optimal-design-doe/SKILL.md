---
name: mlcc-optimal-design-doe
description: Reference LOT 기반 MLCC DOE 최적설계 시뮬레이션 skill. 사용자가 `lot_id 기준으로 최적설계 돌려줘`, `reference lot 검증해줘`, `타겟 용량/두께/L/W를 만족하는 설계 추천해줘`, `DOE 범위를 정해서 optimal_design 돌려줘`, `top 5 후보 보여줘`, `3번째 설계값에서 Sheet T만 5.2로 바꿔 다시 시뮬레이션해줘` 같은 요청을 할 때 사용한다. `check_optimal_design`로 reference 유효성을 확인하고, `targets.*`와 `params.*`를 수집해 `optimal_design` payload를 만들고, 결과 top 5와 후속 재시뮬레이션 대화를 관리한다.
---

# MLCC DOE 최적설계

Reference LOT을 기준으로 DOE 시뮬레이션을 오케스트레이션한다. 이 skill의 역할은 계산 자체가 아니라 `reference 검증 -> 입력 수집 -> tool 호출 -> 결과 비교 -> 재시뮬레이션` 흐름을 안정적으로 진행하는 것이다.

필요할 때 아래 reference를 읽는다.

- `references/tool-contracts.md`: `check_optimal_design`, `optimal_design`의 입력/출력 계약
- `references/workflow-details.md`: 상태 관리, 질문 순서, payload 조립, rerun 규칙
- `references/prompt-examples.md`: 한국어 사용자 질의와 응답 패턴

## 핵심 원칙

- `lot_id`가 없으면 가장 먼저 `lot_id`를 요청한다.
- `lot_id`가 새로 들어오면 반드시 먼저 `check_optimal_design`을 호출한다.
- `check_optimal_design` 결과에 `부족인자`가 있으면 `optimal_design`을 호출하지 않는다.
- `targets.*`와 `params.*`는 현재 기준으로 `절대값` payload를 우선 사용한다.
- 이미 알고 있는 값은 다시 묻지 않는다.
- 사용자가 `3번째 후보에서 Sheet T만 5.2`처럼 말하면 최신 top 5 결과에서 해당 후보를 base로 삼고, 지정한 필드만 override해서 다시 실행한다.
- 현재 대화에 최신 top 5 결과가 없는데 사용자가 `3번째 후보`처럼 참조하면 어느 run의 후보인지 먼저 확인한다.

## 진행 순서

1. `lot_id` 확보
2. `check_optimal_design` 실행
3. `충족인자`, `부족인자` 해석
4. reference가 유효하면 `targets.*` 수집
5. `params.*` 수집
6. `optimal_design` payload 조립
7. `optimal_design` 실행
8. top 5 후보를 번호와 함께 제시
9. 사용자의 수정 지시가 오면 기존 후보를 base로 override 후 재시뮬레이션

## 대화 규칙

- `targets.*`는 보통 4개 수준이므로 빠진 값만 한 번에 묻는다.
- `params.*`는 약 10개 수준이므로 너무 길면 두 묶음으로 나눠 묻되, 이미 있는 값은 제외한다.
- 질문은 항상 `지금 실행을 위해 무엇이 빠졌는지` 기준으로만 한다.
- 결과를 보여줄 때는 각 후보의 `번호`, `핵심 설계값`, `예측 결과`, `target과의 차이`를 함께 요약한다.
- 내부적으로는 최신 `lot_id`, 최신 `targets`, 최신 `params`, 최신 `top_candidates`를 유지한다고 가정하고 대화를 이어간다.

## 실패 처리

- `부족인자`가 있으면 어떤 인자가 부족한지 그대로 보여주고 다른 `lot_id`를 요청한다.
- `optimal_design` 실행이 실패하면 payload를 추측 수정하지 말고, tool 오류 메시지 기준으로 부족하거나 잘못된 필드만 바로잡는다.
- 사용자가 존재하지 않는 후보 번호를 말하면 현재 보이는 후보 번호 범위를 다시 안내한다.
- 사용자가 존재하지 않는 설계 필드를 수정하려 하면 실제 candidate design 값에 있는 필드명으로 다시 확인한다.
