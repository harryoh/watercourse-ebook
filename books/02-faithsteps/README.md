# 믿음의 계단 — 제작 노트

이 책의 전자책(EPUB)을 만들 때 참고할 내용. (저장소 루트에서 명령 실행)

## 개요
- **제목**: 믿음의 계단  /  **저자**: 조춘숙 목사
- **성경/주제**: (주제형/여러 책)
- **장 수**: 8계단 (머리말·판권 포함 총 10섹션)
- **판/발행**: 제1판 · 2020-10 · 전자책 v1.0.0
- **검토 상태(REVIEWED)**: (미검토)

## 원본 & 추출 방법
- **원본**: `(원본 HWP 없음 — EPUB 기반)`
- **방법**: 출판 EPUB → manuscript.md (커스텀 빌더)
- **특이사항**: HWP 없음 → **출판 EPUB**(iBooks Author, `content*.xhtml`)에서 변환. 8계단(각 계단=제목doc+본문doc). 한글이 숫자 엔티티라 `html.unescape` 필요.

## 재생성 / 빌드
```bash
# 1) 원고 재생성(원본에서 다시 뽑을 때만)
python3 books/02-faithsteps/build_manuscript.py   # 소스 EPUB 위치 의존(다운로드 폴더)
# 2) 표지(필요 시)
python3 shared/lib/make_cover.py books/02-faithsteps
# 3) 검토
python3 shared/lib/review.py books/02-faithsteps
# 4) EPUB 빌드
./build.sh books/02-faithsteps
```

## 주의
- 내용 교정은 `manuscript.md`를 직접 고친다(빌드는 내용을 수정하지 않음).
- 손편집 후에는 재추출하지 말 것(덮어쓰기 위험). 공통 규칙은 루트 `CLAUDE.md` 참고.
