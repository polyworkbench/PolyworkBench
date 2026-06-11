# 게임 대사 한국어 현지화

## 과제

일본어 게임 대사와 영어 게임 디자인 문서를 바탕으로 한국어 게임 텍스트를 현지화하세요. 일본어 경어 체계를 한국어 존댓말/반말 체계로 적절히 변환하고, 문화적 적응 노트를 작성하세요.

## 소스 파일

모든 파일은 `/workspace/inputs/`에 있습니다:

- `dialogue_ja.json` — 일본어 게임 대사 40줄 (캐릭터명, 감정, 컨텍스트 포함)
- `game_design_en.md` — 영어 게임 디자인 문서 (캐릭터 설정, 세계관)
- `honorifics_guide_ja.md` — 게임에서 사용되는 일본어 경어 체계 가이드
- `korean_gaming_terms.json` — 한국 게임 용어 참조

## 요구사항

- 40줄의 대사를 모두 한국어로 번역
- 캐릭터별 말투 일관성 유지 (존댓말/반말/해요체 등)
- 일본어 경어를 한국어 존대법으로 적절히 변환
- 캐릭터 이름을 한국어에 자연스럽게 표기 (카타카나→한글)
- 게임 용어는 한국 게이머에게 익숙한 표현 사용
- 문화적 차이가 있는 부분에 적응 노트 작성
- 캐릭터별 음성 가이드 작성 (말투, 어미, 특징)
- QA 플래그로 주의가 필요한 번역 표시

## 출력 파일

결과를 `/workspace/outputs/`에 저장하세요:

- `game_dialogue_ko.json` — 한국어 번역된 대사
- `adaptation_notes_ko.md` — 문화적 적응 노트 (한국어)
- `character_voice_guide_ko.md` — 캐릭터별 음성 가이드 (한국어)
- `qa_flags.json` — QA 플래그 (주의 필요 항목)

## game_dialogue_ko.json 형식

```json
[
  {
    "id": "dialogue_001",
    "character": "캐릭터명",
    "original_ja": "원문 일본어",
    "translated_ko": "한국어 번역",
    "speech_level": "존댓말|반말|해요체",
    "emotion": "감정",
    "context": "장면 설명"
  }
]
```

## qa_flags.json 형식

```json
[
  {
    "dialogue_id": "dialogue_001",
    "flag_type": "cultural|honorific|terminology|ambiguous",
    "description": "플래그 설명",
    "suggestion": "제안 사항"
  }
]
```

**중요: 모든 산출물은 디스크 파일로 기록해야 합니다. 텍스트로만 응답하지 마세요. bash 명령어를 사용하여 디렉토리 생성, 파일 작성, 스크립트 실행을 수행하세요.**
