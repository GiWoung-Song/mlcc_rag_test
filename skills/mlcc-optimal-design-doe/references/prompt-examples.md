# Prompt Examples

이 reference는 한국어 사용자 요청 예시와 기대 동작을 보여준다.

## Contents

- 첫 실행
- Reference 교체
- 결과 비교
- 재시뮬레이션

## 첫 실행

### Example 1

`lot_id 123456을 reference로 써서 최적설계 돌려줘.`

기대 동작:

- 먼저 `check_optimal_design` 실행
- 부족인자가 없으면 `targets.*`와 `params.*`를 수집
- `optimal_design` 실행 후 top 5 제시

### Example 2

`reference lot 123456 기준으로 용량 10uF, thickness 0.8, L 1.6, W 0.8 타겟 맞추는 설계 추천해줘.`

기대 동작:

- `lot_id` 검증
- 주어진 값은 `targets.*`에 채움
- 빠진 `params.*`만 질문

## Reference 교체

### Example 3

`이 lot으로 가능한지 먼저 봐줘. 안 되면 부족인자 보여줘.`

기대 동작:

- `check_optimal_design`만 먼저 실행
- `충족인자`, `부족인자`를 분리해서 보여줌
- 부족인자가 있으면 다른 `lot_id` 요청

## 결과 비교

### Example 4

`top 5 중에서 target에 제일 가까운 후보랑 두께 margin이 제일 좋은 후보를 비교해줘.`

기대 동작:

- 최신 top 5에서 후보 번호를 유지
- 각 후보의 핵심 설계값과 target 차이를 비교

## 재시뮬레이션

### Example 5

`3번째 설계값에서 Sheet T만 5.2로 바꿔서 다시 시뮬레이션해줘.`

기대 동작:

- 최신 top 5의 3번 후보를 base로 사용
- `Sheet T=5.2`만 override
- 나머지 값은 그대로 유지
- 새 payload로 `optimal_design` 재호출

### Example 6

`2번 후보는 그대로 두고 thickness target만 0.75로 바꿔서 다시 보고싶어.`

기대 동작:

- 최신 target 값을 base로 사용
- `target thickness=0.75`만 수정
- candidate 2의 설계값 또는 현재 payload를 기준으로 재실행

### Example 7

`3번째 후보 기준이라고 했는데 지난번 run 말고 방금 run 기준이야.`

기대 동작:

- 최신 run 기준으로 후보 번호를 다시 해석
- 문맥이 애매하면 어느 run인지 짧게 재확인
