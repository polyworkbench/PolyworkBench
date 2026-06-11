# 학술 논문 동료 평가 시뮬레이션

`/workspace/inputs/` 디렉토리에 다음 파일이 있습니다:

- `paper_draft_en.md` — 영어 논문 초고: "Multimodal Learning for Cross-lingual Transfer" (~1500 단어)
- `reference_paper_zh.md` — 중국어 참조 논문 (유사 주제의 기존 연구 결과)
- `reference_paper_ja.md` — 일본어 참조 논문 (관련 분야의 최근 연구)
- `review_criteria_en.json` — 평가 기준: 참신성, 방법론, 명확성, 중요성
- `conference_guidelines_ko.txt` — 한국어 학술대회 투고 지침

## 요구사항

- `review_comments_ko.md` 작성: 한국어로 상세한 리뷰 코멘트를 작성하세요
  - 논문의 강점과 약점을 구체적으로 기술
  - 참조 논문과의 비교를 통한 참신성 평가
  - 방법론적 문제점 및 개선 방안 제시
  - 실험 설계의 적절성 평가
  - 학술대회 투고 지침 준수 여부 점검
- `evaluation_matrix.json` 생성: 각 평가 기준(참신성, 방법론, 명확성, 중요성)에 대해 1-10점 점수와 근거 제시
- `revision_suggestions_ko.json` 작성: 최소 8개의 구체적인 수정 제안을 우선순위별로 제시 (각 제안: 위치, 현재 문제점, 제안 내용, 우선순위 상/중/하)
- `reference_comparison.json` 작성: 논문과 두 참조 논문 간의 비교 분석 (방법론 차이, 실험 규모, 성능 비교, 기여도 차이점)

## 출력

모든 파일을 `/workspace/output/`에 저장하세요:
- `review_comments_ko.md`
- `evaluation_matrix.json`
- `revision_suggestions_ko.json`
- `reference_comparison.json`

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash 命令创建目录、写文件、执行脚本。**
