# 너를 위하여 — 제작 노트

이 책의 EPUB을 만들 때 참고. (저장소 루트에서 실행, 폴더명에 공백이 있으니 따옴표로 감쌀 것)

## 개요
- **제목**: 너를 위하여 / **저자**: 조춘숙 목사
- **성경/주제**: 마태복음
- **장 수**: 14
- **판/발행**: 제1판 · 2009-08 · 전자책 v1.0.0
- **검토(REVIEWED)**: (미검토)

## 원본 & 추출
- **원본**: `original/04 너를 위하여(산상후순).hwp`
- **방법**: 표준 추출기 shared/lib/extract_hwp.py
- **특이사항**: 주제 에세이형. 9~14장 도입 성경구절 없음 → 번호+제목으로 인식. 9장 번호 09(0채움).

## 재생성 / 빌드
```bash
python3 shared/lib/extract_hwp.py "books/04. 너를 위하여 (산상수훈-팔복)"   # 기존 manuscript.md 보존(--force로 덮어쓰기)
python3 shared/lib/make_cover.py "books/04. 너를 위하여 (산상수훈-팔복)"
python3 shared/lib/review.py "books/04. 너를 위하여 (산상수훈-팔복)"
./build.sh "books/04. 너를 위하여 (산상수훈-팔복)"
```

## 주의
- 내용 교정은 `manuscript.md`를 직접 고친다(빌드는 내용 미수정). 공통 규칙은 루트 `CLAUDE.md` 참고.
