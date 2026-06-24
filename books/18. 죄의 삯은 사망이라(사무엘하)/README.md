# 사무엘하 강해 — 제작 노트

이 책의 EPUB을 만들 때 참고. (저장소 루트에서 실행, 폴더명에 공백이 있으니 따옴표로 감쌀 것)

## 개요
- **제목**: 사무엘하 강해 / **저자**: 조춘숙 목사
- **성경/주제**: 사무엘하
- **장 수**: 25
- **판/발행**: 제1판 · 2025-11 · 전자책 v1.0.0
- **검토(REVIEWED)**: (미검토)

## 원본 & 추출
- **원본**: `original/사무엘하 합본.hwp`
- **방법**: 표준 추출기 shared/lib/extract_hwp.py
- **특이사항**: 사무엘하 25장. 신형식.

## 재생성 / 빌드
```bash
python3 shared/lib/extract_hwp.py "books/18. 죄의 삯은 사망이라(사무엘하)"   # 기존 manuscript.md 보존(--force로 덮어쓰기)
python3 shared/lib/make_cover.py "books/18. 죄의 삯은 사망이라(사무엘하)"
python3 shared/lib/review.py "books/18. 죄의 삯은 사망이라(사무엘하)"
./build.sh "books/18. 죄의 삯은 사망이라(사무엘하)"
```

## 주의
- 내용 교정은 `manuscript.md`를 직접 고친다(빌드는 내용 미수정). 공통 규칙은 루트 `CLAUDE.md` 참고.
