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
python3 shared/lib/make_cover.py "books/02. 믿음의 계단"
python3 shared/lib/review.py "books/02. 믿음의 계단"
./build.sh "books/02. 믿음의 계단"
```

## 주의
- 내용 교정은 `manuscript.md`를 직접 고친다(빌드는 내용 미수정). 공통 규칙은 루트 `CLAUDE.md` 참고.
