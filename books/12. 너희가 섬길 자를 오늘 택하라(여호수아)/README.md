# 여호수아 강해 — 제작 노트

이 책의 EPUB을 만들 때 참고. (저장소 루트에서 실행, 폴더명에 공백이 있으니 따옴표로 감쌀 것)

## 개요
- **제목**: 여호수아 강해 / **저자**: 조춘숙 목사
- **성경/주제**: 여호수아
- **장 수**: 33
- **판/발행**: 제1판 · 2019-11 · 전자책 v1.0.0
- **검토(REVIEWED)**: (미검토)

## 원본 & 추출
- **원본**: `original/여호수아본문_1109.hwp`
- **방법**: 표준 추출기 shared/lib/extract_hwp.py
- **특이사항**: 여호수아 33장. 차례 [N] 대괄호 + 러닝헤더 제거.

## 재생성 / 빌드
```bash
python3 shared/lib/extract_hwp.py "books/12. 너희가 섬길 자를 오늘 택하라(여호수아)"   # 기존 manuscript.md 보존(--force로 덮어쓰기)
python3 shared/lib/make_cover.py "books/12. 너희가 섬길 자를 오늘 택하라(여호수아)"
python3 shared/lib/review.py "books/12. 너희가 섬길 자를 오늘 택하라(여호수아)"
./build.sh "books/12. 너희가 섬길 자를 오늘 택하라(여호수아)"
```

## 주의
- 내용 교정은 `manuscript.md`를 직접 고친다(빌드는 내용 미수정). 공통 규칙은 루트 `CLAUDE.md` 참고.
