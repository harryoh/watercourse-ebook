# 아가 강해 — 제작 노트

이 책의 EPUB을 만들 때 참고. (저장소 루트에서 실행, 폴더명에 공백이 있으니 따옴표로 감쌀 것)

## 개요
- **제목**: 아가 강해 / **저자**: 조춘숙 목사
- **성경/주제**: 아가
- **장 수**: 15
- **판/발행**: 제1판 · 2017-02 · 전자책 v1.0.0
- **검토(REVIEWED)**: (미검토)

## 원본 & 추출
- **원본**: `original/아가서본문.hwp`
- **방법**: 표준 추출기 shared/lib/extract_hwp.py
- **특이사항**: 장식형 차례(│차례│/점선). 표준 추출기.

## 재생성 / 빌드
```bash
python3 shared/lib/extract_hwp.py "books/03. 아름다운 노래(아가)"   # 기존 manuscript.md 보존(--force로 덮어쓰기)
python3 shared/lib/make_cover.py "books/03. 아름다운 노래(아가)"
python3 shared/lib/review.py "books/03. 아름다운 노래(아가)"
./build.sh "books/03. 아름다운 노래(아가)"
```

## 주의
- 내용 교정은 `manuscript.md`를 직접 고친다(빌드는 내용 미수정). 공통 규칙은 루트 `CLAUDE.md` 참고.
