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

출력:

- `top 5` 최적 설계 후보
- 각 후보의 전체 설계값
- 각 후보의 예측 결과값

중요 규칙:

- 각 후보의 `전체 설계값`이 반환되므로, 후속 rerun 시 그 후보를 base로 사용한다.
- 사용자가 특정 후보의 일부만 바꾸라고 하면, 해당 후보의 전체 설계값을 복사하고 지정한 필드만 덮어써서 새 payload를 만든다.

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
