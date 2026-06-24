# 사사기 강해 — 제작 노트

이 책의 EPUB을 만들 때 참고. (저장소 루트에서 실행, 폴더명에 공백이 있으니 따옴표로 감쌀 것)

## 개요
- **제목**: 사사기 강해 / **저자**: 조춘숙 목사
- **성경/주제**: 사사기
- **장 수**: 23
- **판/발행**: 제1판 · 2020-06 · 전자책 v1.0.0
- **검토(REVIEWED)**: (미검토)

## 원본 & 추출
- **원본**: `original/사사기_0718.hwp`
- **방법**: 표준 추출기 shared/lib/extract_hwp.py
- **특이사항**: 사사기 23장. 차례 [N] 대괄호.

## 재생성 / 빌드
```bash
python3 shared/lib/extract_hwp.py "books/13. 너희가 내 목소리를 듣지 아니하였으니 어찌하여 그리하였느냐(사사기)"   # 기존 manuscript.md 보존(--force로 덮어쓰기)
python3 shared/lib/review.py "books/13. 너희가 내 목소리를 듣지 아니하였으니 어찌하여 그리하였느냐(사사기)"
./build.sh "books/13. 너희가 내 목소리를 듣지 아니하였으니 어찌하여 그리하였느냐(사사기)"
```

## 표지(앞표지)

- **원본 표지**: `출판/images/front.jpg` — 앞표지만 있는 **단독 이미지**(펼침/책등/날개 없음).
- **추출**: 잘라내기 불필요. 그대로(필요 시 폭 1400px 축소) cover.jpg로 사용.
- **book.env**: `COVER_SRC="출판/images/front.jpg"`  (COVER_CROP 없음)
- **재현**(book.env의 COVER_SRC/COVER_CROP 사용):
```bash
python3 shared/lib/extract_cover.py "books/13. 너희가 내 목소리를 듣지 아니하였으니 어찌하여 그리하였느냐(사사기)" --src-root "<원본 표지가 있는 폴더>"
```

## 주의
- 내용 교정은 `manuscript.md`를 직접 고친다(빌드는 내용 미수정). 공통 규칙은 루트 `CLAUDE.md` 참고.
