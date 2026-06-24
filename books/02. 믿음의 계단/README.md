# 믿음의 계단 — 제작 노트

이 책의 EPUB을 만들 때 참고. (저장소 루트에서 실행, 폴더명에 공백이 있으니 따옴표로 감쌀 것)

## 개요
- **제목**: 믿음의 계단 / **저자**: 조춘숙 목사
- **성경/주제**: (주제형/여러 책)
- **장 수**: 8
- **판/발행**: 제1판 · 2020-10 · 전자책 v1.0.0
- **검토(REVIEWED)**: (미검토)

## 원본 & 추출
- **원본**: `(HWP 없음 — EPUB 기반)`
- **방법**: 출판 EPUB → manuscript.md (커스텀 빌더)
- **특이사항**: HWP 없음 → 출판 EPUB(iBooks, content*.xhtml)에서 변환. 8계단. 한글 숫자엔티티 unescape.

## 재생성 / 빌드
```bash
python3 "books/02. 믿음의 계단/build_manuscript.py"   # 출판 EPUB 기반(소스 위치 의존)
python3 shared/lib/review.py "books/02. 믿음의 계단"
./build.sh "books/02. 믿음의 계단"
```

## 표지(앞표지)

- **원본 표지**: `출판/images/front.jpg` — 앞표지만 있는 **단독 이미지**(펼침/책등/날개 없음).
- **추출**: 잘라내기 불필요. 그대로(필요 시 폭 1400px 축소) cover.jpg로 사용.
- **book.env**: `COVER_SRC="출판/images/front.jpg"`  (COVER_CROP 없음)
- **재현**(book.env의 COVER_SRC/COVER_CROP 사용):
```bash
python3 shared/lib/extract_cover.py "books/02. 믿음의 계단" --src-root "<원본 표지가 있는 폴더>"
```

## 주의
- 내용 교정은 `manuscript.md`를 직접 고친다(빌드는 내용 미수정). 공통 규칙은 루트 `CLAUDE.md` 참고.
