# 죽어야만 사는 나라 — 제작 노트

이 책의 EPUB을 만들 때 참고. (저장소 루트에서 실행, 폴더명에 공백이 있으니 따옴표로 감쌀 것)

## 개요
- **제목**: 죽어야만 사는 나라 / **저자**: 조춘숙 목사
- **성경/주제**: (주제형/여러 책)
- **장 수**: 12
- **판/발행**: 제1판 · 2008-04 · 전자책 v1.0.0
- **검토(REVIEWED)**: (미검토)

## 원본 & 추출
- **원본**: `original/01 죽어야만 사는나라.hwp`
- **방법**: 표준 추출기 shared/lib/extract_hwp.py
- **특이사항**: 주제형(인물별: 노아·욥·요나·다니엘·에스더·바울 등). 장마다 성경책이 달라 BIBLE_REF 비움→전체 성경 참조. 장 범위 구절 포함.

## 재생성 / 빌드
```bash
python3 shared/lib/extract_hwp.py "books/01. 죽어야만 사는 나라"   # 기존 manuscript.md 보존(--force로 덮어쓰기)
python3 shared/lib/make_cover.py "books/01. 죽어야만 사는 나라"
python3 shared/lib/review.py "books/01. 죽어야만 사는 나라"
./build.sh "books/01. 죽어야만 사는 나라"
```

## 주의
- 내용 교정은 `manuscript.md`를 직접 고친다(빌드는 내용 미수정). 공통 규칙은 루트 `CLAUDE.md` 참고.
