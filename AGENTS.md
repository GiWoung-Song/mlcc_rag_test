이 레포지토리 프로젝트의 목적은 삼성전기 MLCC 개발자가 고객사가 요청한 SPEC을 만족하기 위해 정보를 찾을때 도와주는 skill.md를 구축하기 위한 프로젝트이다.

*파일설명*
MLCC_2512.pdf : 삼성전기 MLCC catalog 원문.
mlcc_catalog_rag_chunks.jsonl : catalog를 vectorDB에 넣기 위해 만들어둔 chunks
mlcc_catalog_rag_master_ko : chunk에 대한 설명 정리본. 

*목적*
사용자가 "고객사 의뢰로 스펙 만족하는 MLCC 기종부터 선정해야해. A 온도특성, 정격전압 4V, L size 최대 690㎛, W size 최대 390㎛, T size 최대 550㎛, 기준용량 4.8㎌, M편차, 고주파 저전계에서 1V DC 전계를 인가하였을 때 최소 3.45㎌ 를 만족하는 기종을 설계해줘."
이런식으로 질문을 했을때,
mlcc_catalog_rag_chunks.jsonl 가 들어있는 vectorDB를 잘 검색하여 결과를 도출해 낼수 있도록 하는 skill를 개발하는게 이 프로젝트의 목적이다. 

*참고사항*
이 skill을 사용하는 에이전트는 사내 폐쇄망 환경이기 때문에 웹서치가 불가능하며, 순수하게 해당 vectorDB만 검색할수 있는 function tool을 하나 가지고 있다. (tool_name : search_rag). 에이전트가 사용하는 llm은 GPT-OSS 120B 수준이다.