# 너를 위하여 — 제작 노트

이 책의 전자책(EPUB)을 만들 때 참고할 내용. (저장소 루트에서 명령 실행)

## 개요
- **제목**: 너를 위하여  /  **저자**: 조춘숙 목사
- **성경/주제**: 마태복음
- **장 수**: 본문 14개 (전체 섹션 17개: 머리말·판권·교회안내 포함)
- **판/발행**: 제1판 · 2009-08 · 전자책 v1.0.0
- **검토 상태(REVIEWED)**: (미검토)

## 원본 & 추출 방법
- **원본**: `original/04 너를 위하여(산상후순).hwp`
- **방법**: 표준 추출기 `shared/lib/extract_hwp.py`
- **특이사항**: 주제 에세이형. 9~14장은 도입 성경구절이 없어 "번호+제목"으로 장 인식. 9장 번호가 `09`(0채움). 표지/제목은 "너를 위하여".

## 재생성 / 빌드
```bash
# 1) 원고 재생성(원본에서 다시 뽑을 때만)
python3 shared/lib/extract_hwp.py books/04-sermononmount   # (기존 manuscript.md 보존; --force로 덮어쓰기)
# 2) 표지(필요 시)
python3 shared/lib/make_cover.py books/04-sermononmount
# 3) 검토
python3 shared/lib/review.py books/04-sermononmount
# 4) EPUB 빌드
./build.sh books/04-sermononmount
```

## 주의
- 내용 교정은 `manuscript.md`를 직접 고친다(빌드는 내용을 수정하지 않음).
- 손편집 후에는 재추출하지 말 것(덮어쓰기 위험). 공통 규칙은 루트 `CLAUDE.md` 참고.
