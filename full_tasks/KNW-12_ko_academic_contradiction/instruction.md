# 학술 논문 교차 검증: 리튬이온 배터리 열화 분석

## 과제 목표

리튬이온 배터리 열화(degradation)에 관한 세 편의 학술 논문이 제공됩니다:

1. `korean_paper.md` — 한국어 논문 (한국전기화학회지, 2024)
2. `japanese_paper.md` — 일본어 논문 (電気化学会誌, 2023)
3. `english_metaanalysis.md` — 영어 메타분석 논문 (Journal of Power Sources, 2024)

## 수행 과제

세 논문을 면밀히 읽고, 다음 작업을 수행하세요:

1. **모순점 식별**: 세 논문 간의 실험 데이터, 결론, 권장 사항에서 모순되거나 불일치하는 내용을 모두 찾으세요.
2. **정확한 인용**: 각 모순점에 대해 해당 논문의 정확한 섹션/페이지를 인용하세요.
3. **분석 및 평가**: 각 모순점에 대해 어느 논문의 주장이 더 신뢰할 수 있는지 근거를 들어 평가하세요.

## 필수 출력 파일

### `contradiction_report_ko.md`
한국어로 작성된 상세 보고서:
- 요약 (Executive Summary)
- 각 모순점에 대한 상세 분석
- 신뢰도 평가 및 근거
- 결론 및 권장 사항

### `citations.json`
```json
{
  "contradictions": [
    {
      "id": 1,
      "topic": "<주제>",
      "korean_paper": {
        "section": "<섹션 번호/이름>",
        "claim": "<주장 내용>",
        "value": "<구체적 수치>"
      },
      "japanese_paper": {
        "section": "<섹션 번호/이름>",
        "claim": "<주장 내용>",
        "value": "<구체적 수치>"
      },
      "english_paper": {
        "section": "<섹션 번호/이름>",
        "claim": "<주장 내용>",
        "value": "<구체적 수치>"
      },
      "assessment": "<평가 내용>",
      "most_reliable": "<가장 신뢰할 수 있는 출처>"
    }
  ]
}
```

### `analysis_summary.json`
```json
{
  "total_contradictions": <int>,
  "categories": ["<모순 유형 목록>"],
  "papers_analyzed": 3,
  "reliability_ranking": ["<논문 순위>"],
  "key_findings": ["<주요 발견 목록>"]
}
```

## 평가 기준
- 완전성: 4개의 주요 모순점을 모두 식별
- 정확성: 각 인용의 정확한 섹션 참조
- 분석 품질: 논리적이고 근거 있는 평가
- 언어 품질: 한국어 보고서의 전문적 품질

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash 命令创建目录、写文件、执行脚本。**
