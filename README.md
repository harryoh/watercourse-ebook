# 물줄기교회 전자책 제작 (watercourse-ebook)

물줄기교회 조춘숙 목사의 설교 강해집 원고(HWP·DOCX 등)를 **표준 도구로 재현 가능하게** EPUB 전자책으로 만드는 저장소입니다.

핵심 원칙은 **재현성**입니다. 손으로 결과물만 넘기는 것이 아니라, 원본에서 EPUB까지의 모든 변환 과정을 스크립트와 설정으로 기록해 두고 언제든 똑같이 다시 만들 수 있게 합니다.

---

## 1. 변환 파이프라인

```
HWP/DOCX ─(1)추출─▶ manuscript.md + 이미지        원본 표지 ─(1')표지추출─▶ cover.jpg
              (extract_hwp.py, 결정론적)                      (extract_cover.py)
                       │                                          │
                       └──────────────┬───────────────────────────┘
                                      ▼
                         (2) 검토·교정 (review.py + 사람 눈)
                                      ▼
                         (3) Calibre CLI 빌드 (build.sh → ebook-convert)
                                      ▼
                              EPUB 3  ─(4)epubcheck 검증
```

각 단계는 모두 코드/설정으로 남아 있어, 같은 입력이면 항상 같은 결과가 나옵니다.

- **(1) 원고 추출** — `shared/lib/extract_hwp.py` 가 한글(.hwp 5.0) 본문을 문단 단위로 뽑아 `manuscript.md` 생성. 외부 라이브러리 없이 동작.
- **(1') 표지 추출** — `shared/lib/extract_cover.py` 가 원본 표지(앞·뒤·책등 펼침 PDF/AI, 또는 단독 이미지)에서 **앞표지만** 잘라 `cover.jpg` 생성. 설정은 각 `book.env`.
- **(2) 검토** — `shared/lib/review.py` 자동 점검 + `docs/검토체크리스트.md` 사람 눈 검토. 빌드는 내용을 고치지 않으므로 교정은 `manuscript.md`에서.
- **(3) 빌드** — `build.sh` 가 Calibre `ebook-convert` 로 `manuscript.md` → EPUB. 모든 변환 옵션이 스크립트에 기록.
- **(4) 검증** — CI에서 `epubcheck`로 EPUB 3 규격 자동 검사.

> 결과물은 EPUB 3 표준이라 Windows·macOS·iOS(Apple Books)·Android(Play Books·리디 등) 어디서나 열립니다.

---

## 2. 폴더 구조

```
watercourse-ebook/
├─ README.md               # (이 문서) 전체 구조·제작법
├─ CLAUDE.md               # AI 작업 규칙·관례
├─ manifest.json           # ★ 원고 변경 감지용 해시 대장 (기계용, 자동 생성)
├─ build.sh                # 한 책 빌드 (md → EPUB, Calibre CLI)
├─ build-all.sh            # 모든 책 빌드
├─ new-book.sh             # 새 책 폴더 생성 (템플릿 book.env 포함)
├─ release.sh              # 판(edition) 릴리스용 git 태그
├─ templates/book.env      # book.env 템플릿(주석 포함)
├─ docs/
│  ├─ 검토체크리스트.md    # 출판 전 사람 눈 점검 항목
│  └─ automation.md        # 자동 발행 설계 메모
├─ shared/
│  ├─ style.css            # 전자책 공통 디자인 (고치면 모든 책에 반영)
│  └─ lib/
│     ├─ hwp5.py           # HWP 5.0 파서(의존성 없음)
│     ├─ extract_hwp.py    # HWP → manuscript.md + 이미지
│     ├─ extract_cover.py  # 원본 표지 → 앞표지 cover.jpg
│     ├─ manifest.py       # 원고 해시 기록/변경 감지
│     ├─ review.py         # 자동 검토(보고 전용)
│     └─ make_cover.py     # (예비) 표지가 없을 때 글자 표지 생성
└─ books/
   └─ <번호. 한글 제목>/   # 책 한 권 (원본 원고 폴더명과 동일하게 한글)
      ├─ book.env          # 이 책의 메타데이터·설정(제목/저자/판/표지 설정 등)
      ├─ README.md         # 이 책 제작 노트(추출 방법·표지·특이사항)
      ├─ original/         # 원본 HWP (변경 감지 대상)
      ├─ images/           # 본문용 이미지 (logo.png 등) · _extracted/=HWP 추출 원본
      ├─ manuscript.md     # ★ 편집용 마스터 원고 (내용 수정은 여기서)
      ├─ cover.jpg         # 앞표지
      └─ output/           # 생성된 EPUB (git 제외)
```

책 목록은 아래 [9. 책 목록](#9-책-목록)에 있고, 변경 감지용 해시는 `manifest.json` 에 있습니다.

---

## 3. 사전 준비 — Calibre 설치 (한 번만)

Calibre는 무료 오픈소스(GPLv3)입니다.

- **macOS**: https://calibre-ebook.com/download_osx 에서 받아 설치 (또는 `brew install --cask calibre`)
- 설치하면 `ebook-convert` 명령이 함께 깔립니다. macOS 내장 경로: `/Applications/calibre.app/Contents/MacOS/ebook-convert`

표지/매니페스트 스크립트는 Python `Pillow`가 필요합니다: `pip3 install pillow`
(이미 만들어진 `cover.jpg`를 그대로 쓰면 Pillow 없이도 빌드됩니다. 표지 펼침 추출에는 `ghostscript`도 필요: `brew install ghostscript`.)

---

## 4. 사용법

### EPUB 빌드 (가장 자주)
```bash
./build-all.sh                       # 모든 책
./build.sh "books/17. 아모스"        # 한 책 → output/아모스 강해 ….epub
```

### 원고 검토 (출판 전 필수)
```bash
python3 shared/lib/review.py "books/17. 아모스"   # 자동 점검
```
그 뒤 `docs/검토체크리스트.md`로 사람 눈 검토 → 통과하면 `book.env`에 `REVIEWED="yes"` → 빌드.

### 내용 수정
`books/<책>/manuscript.md` 를 고친 뒤 다시 `./build.sh "books/<책>"`.

### 디자인 수정 (폰트·인용박스·색)
`shared/style.css` 를 고친 뒤 다시 빌드. 모든 책 공통 적용.

### 원고 다시 추출 (원본 HWP가 바뀐 경우)
```bash
python3 shared/lib/extract_hwp.py "books/<책>"        # 기존 manuscript.md 보존(--force로 덮어쓰기)
```

### 표지 다시 추출 (원본 표지에서)
각 `book.env`의 `COVER_SRC`(원본 표지 경로)·`COVER_CROP`(앞표지 영역 비율)을 사용합니다.
```bash
python3 shared/lib/extract_cover.py "books/<책>" --src-root "<원본 표지가 있는 폴더>"
```
자세한 출처·비율은 각 책 `books/<책>/README.md` 의 "표지(앞표지)" 항목에 적혀 있습니다.

---

## 5. 원고 변경 감지 (매니페스트)

원본·원고가 나중에 바뀌었는지 **해시(SHA-256)** 로 추적합니다. 핵심 입력(`original/`·`manuscript.md`·`cover.jpg`·`book.env`)과 공통 `shared/style.css`의 해시를 `manifest.json`에 기록해 둡니다.

```bash
python3 shared/lib/manifest.py write    # 현재 상태 기록 (빌드/교정을 끝낸 뒤 실행)
python3 shared/lib/manifest.py check    # 기록과 비교 → 바뀐 책 출력 (변경 있으면 종료코드 1)
```

`check` 결과 예: `✗ 17. 아모스 (원고 변경) → 재빌드 필요`.

**권장 재빌드 흐름 (사람·AI·CI 공통)**
1. `manifest.py check` 로 바뀐 책 확인
2. 바뀐 책만 `./build.sh "books/<책>"` 로 다시 빌드 (원본 HWP가 바뀐 경우 `extract_hwp.py`부터)
3. `manifest.py write` 로 매니페스트 갱신 후 커밋

> `style.css`가 바뀌면 모든 책을 다시 빌드해야 하므로 별도로 표시됩니다.

---

## 6. 버전·판(edition) 관리

두 축으로 관리합니다.

1. **소스 이력 — git**: `manuscript.md`·`book.env`·`style.css` 수정 시마다 커밋. 배포 시점에 태그.
2. **출간 버전 — book.env**: 책마다 `EDITION`(판)·`VERSION`·`RELEASE_DATE`. 빌드 시 출력 파일명과 EPUB 메타데이터에 자동 기록 (`아모스 강해 - 제1판 v1.0.0 (2024-02).epub`).

새 판 발행:
```bash
# 1) manuscript.md 개정  2) book.env에서 EDITION/VERSION/RELEASE_DATE 갱신
git add -A && git commit -m "edit: Romans 2nd edition"
./release.sh "books/16. 율법의 요구와 십자가의 완성(로마서)"   # 16-v2.0.0 태그 → CI가 빌드해 Release에 첨부
```
과거 판 복구: `git checkout 16-v1.0.0 && ./build.sh "books/16. …"` → `git checkout main`.

---

## 7. 자동 빌드 (GitHub Actions)

`books/**`·`shared/**`·`build.sh` 변경을 푸시하면 `.github/workflows/build.yml` 이 러너에 Calibre를 설치하고 **동일한 `build.sh`로 EPUB을 빌드**합니다.

- 결과 EPUB은 Actions 실행의 **Artifacts**에서 다운로드, 태그 푸시 시 **Release에 첨부**.
- 빌드 후 **epubcheck**로 규격 자동 검증(오류 시 실패).
- 수동 실행: Actions → Build EPUB → Run workflow (특정 책만 빌드하려면 `books/<책>` 입력).

작업 흐름: (로컬/AI) `manuscript.md`·`book.env` 작성 → `git commit && git push` → Actions 빌드.

---

## 8. 새 원고 추가하기

```bash
./new-book.sh "19. 새책 제목" "표지용 제목"     # books/19. …/ 생성 (+ 템플릿 book.env)
```
그 다음:
1. `books/19. …/original/` 에 원본 HWP 넣기
2. `books/19. …/book.env` 값 채우기(제목·`BOOK_NAME`·`BIBLE_REF`·`HWP_SOURCE`·발행일·`COVER_SRC`/`COVER_CROP` 등)
3. `python3 shared/lib/extract_hwp.py "books/19. …"`        # HWP → manuscript.md
4. `python3 shared/lib/extract_cover.py "books/19. …" --src-root "<원본 표지 폴더>"`  # 표지(선택)
5. `python3 shared/lib/review.py "books/19. …"` → 검토 → `./build.sh "books/19. …"`
6. `python3 shared/lib/manifest.py write` 로 해시 기록

> 템플릿 원본은 `templates/book.env` 에 주석과 함께 있습니다.

---

## 9. 책 목록

현재 저장소에 들어 있는 강해집입니다. (변경 감지용 해시는 `manifest.json` 참조, 검증은 `manifest.py check`.)

| # | 제목 | 판/버전 | 발행 |
|---|------|---------|------|
| 소 | 생명을 살리는 방주 | 제1판 v1.0.0 | 2017-11 |
| 01 | 죽어야만 사는 나라 | 제1판 v1.0.1 | 2008-04 |
| 02 | 믿음의 계단 | 제1판 v1.0.0 | 2020-10 |
| 03 | 아가 강해 | 제1판 v1.0.0 | 2017-02 |
| 04 | 너를 위하여 | 제1판 v1.0.0 | 2009-08 |
| 05 | 물 위에 던진 떡 | 제1판 v1.0.0 | 2010-01 |
| 06 | 모든 사명을 사랑으로 감당하라 (고린도전서 강해집 2) | 제1판 v1.0.0 | 2014-02 |
| 07 | 사무엘상 강해 | 제1판 v1.0.0 | 2015-11 |
| 08 | 내가 사랑하는 자야 | 제2판 v1.0.0 | 2019-03 |
| 09 | 룻기 강해 | 제1판 v1.0.0 | 2018-05 |
| 10 | 사도행전 강해 | 제1판 v1.0.0 | 2018-12 |
| 11 | 요한계시록 강해 | 제1판 v1.0.0 | 2019-05 |
| 12 | 여호수아 강해 | 제1판 v1.0.0 | 2019-11 |
| 13 | 사사기 강해 | 제1판 v1.0.0 | 2020-06 |
| 14 | 주 안에서 같은 마음을 품으라 (빌립보서) | 제1판 v1.0.0 | 2022-01 |
| 15 | 골로새서 강해 | 제1판 v1.0.0 | 2022-11 |
| 16 | 로마서 강해 | 제1판 v1.0.0 | 2023-10 |
| 17 | 아모스 강해 | 제1판 v1.0.0 | 2024-02 |
| 18 | 사무엘하 강해 | 제1판 v1.0.0 | 2025-11 |

> 발행일·판은 각 `book.env`, 변경 시 `manifest.py write`로 갱신.

## 부록 — 변환 가정(기록)

- 본문은 HWP의 **문단 단위**로 추출 → 원본 공백·줄간격 보존(PDF 추출의 공백 유실 회피)
- 차례의 "N. 제목 …쪽" 패턴으로 장 제목 수집
- 장 시작 = "숫자 단독 문단 + 제목 + 성경 구절(BIBLE_REF N장)" 구조로 탐지
- 각 장 도입 성경 본문과 "BIBLE_REF N장 …" 인용은 인용 블록, 그 외는 본문 문단
- 책/장 제목이 머리말·꼬리말로 본문에 끼어든 경우 자동 제거(러닝헤더 필터)
- 표제지·판권은 `book.env` 값으로 생성
- 표지는 원본 펼침에서 **앞표지만** 잘라 사용(책등·뒤표지·날개 제외)
