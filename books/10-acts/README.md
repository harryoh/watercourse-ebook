# 사도행전 강해 — 제작 노트

이 책의 전자책(EPUB)을 만들 때 참고할 내용. (저장소 루트에서 명령 실행)

## 개요
- **제목**: 사도행전 강해  /  **저자**: 조춘숙 목사
- **성경/주제**: 사도행전
- **장 수**: 본문 5개 (전체 섹션 8개: 머리말·판권·교회안내 포함)
- **판/발행**: 제1판 · 2018-12 · 전자책 v1.0.0
- **검토 상태(REVIEWED)**: (미검토)

## 원본 & 추출 방법
- **원본**: `original/스데반+본문+목사님+최종+수정본(1220).hwp`
- **방법**: 표준 추출기 `shared/lib/extract_hwp.py`
- **특이사항**: 사도행전(스데반의 믿음) 5장. 표준 추출기.

## 재생성 / 빌드
```bash
# 1) 원고 재생성(원본에서 다시 뽑을 때만)
python3 shared/lib/extract_hwp.py books/10-acts   # (기존 manuscript.md 보존; --force로 덮어쓰기)
# 2) 표지(필요 시)
python3 shared/lib/make_cover.py books/10-acts
# 3) 검토
python3 shared/lib/review.py books/10-acts
# 4) EPUB 빌드
./build.sh books/10-acts
```

## 주의
- 내용 교정은 `manuscript.md`를 직접 고친다(빌드는 내용을 수정하지 않음).
- 손편집 후에는 재추출하지 말 것(덮어쓰기 위험). 공통 규칙은 루트 `CLAUDE.md` 참고.
