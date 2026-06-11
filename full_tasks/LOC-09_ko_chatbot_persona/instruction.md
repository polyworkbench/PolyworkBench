# 과제: 한국어 챗봇 페르소나 설계 및 적용

## 설명
영어 대화 흐름, 일본어 경어 체계, 중국어 브랜드 보이스를 참고하여 한국 시장에 적합한 챗봇 페르소나를 설계하고 한국어 챗봇 스크립트를 작성해야 합니다. 한국어 존대법(해요체/합쇼체/해체)을 상황에 맞게 적절히 적용해야 합니다.

## 입력 파일
모든 입력 파일은 `/workspace/inputs/` 디렉토리에 위치합니다:

- `dialogue_flows_en.json` — 영어 챗봇 대화 트리 (20개 인텐트, 각 3-5개 응답)
- `politeness_system_ja.md` — 일본어 경어(敬語) 체계와 챗봇 맥락 매핑
- `brand_voice_zh.md` — 중국어 브랜드 보이스 가이드라인 및 성격 특성
- `korean_speech_levels_guide.md` — 한국어 존대법 가이드 (해요체/합쇼체/해체)

## 요구사항

### 챗봇 스크립트 (`chatbot_scripts_ko.json`)
- 20개 인텐트 전체에 대한 한국어 응답 스크립트
- 각 인텐트별 최소 3개 변형 응답
- 기본 존대법: **해요체** (일반 응답)
- 공식적 상황(결제, 계약 등): **합쇼체** 사용
- 친근한 상황(이벤트, 축하 등): 부분적으로 **해체** 허용
- 각 응답에 `speech_level` 필드 포함 (haeyoche/hapsyoche/haeche)
- 자연스러운 한국어 구어체 표현 사용

### 페르소나 가이드 (`persona_guide_ko.md`)
- 챗봇 캐릭터 정의 (이름, 나이, 성격, 말투)
- 상황별 존대법 전환 규칙
- 브랜드 톤앤매너 한국화 방안
- 금기어/주의 표현 리스트
- 예시 대화문 포함

### 대화 흐름 (`dialogue_flows_ko.json`)
- 20개 인텐트의 한국어 대화 트리
- 각 노드: `intent_id`, `user_input_examples` (3개 이상), `bot_responses`, `next_intents`, `context`
- 사용자 입력 예시는 구어체/문어체 혼합
- 대화 분기 로직 포함

### 톤 분석 (`tone_analysis.json`)
- 원본(영어/일본어/중국어)과 한국어 변환 비교 분석
- 각 인텐트별: `intent_id`, `original_tone`, `korean_tone`, `speech_level_rationale`, `cultural_adaptations`
- 존대법 선택 근거 설명

## 출력 경로
모든 출력 파일은 `/workspace/` 루트 디렉토리에 기록합니다.

---

**중요: 모든 결과물은 디스크 파일로 기록해야 합니다. 텍스트로만 답변하지 마세요. bash 명령어를 사용하여 디렉토리 생성, 파일 작성, 스크립트 실행을 수행하세요.**
