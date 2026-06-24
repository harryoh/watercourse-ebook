# 물줄기교회 전자책 제작 (watercourse-ebook)

설교 강해집 원고(HWP·DOCX 등)를 **표준 도구로 재현 가능하게** EPUB 전자책으로 만드는 저장소입니다.

`books/sample` 은 파이프라인이 실제로 동작하는 **예제(아모스 강해)** 입니다.
이것으로 흐름을 익힌 뒤, 실제 원고를 한 권씩 `books/` 아래에 추가하면 됩니다.

## 변환 파이프라인

```
HWP/DOC ─(1)추출─▶ manuscript.md+이미지+표지 ─(2)검토·교정─▶ (검토완료) ─(3)Calibre CLI─▶ EPUB ─(4)epubcheck
            (결정론적·재현가능)                                       (ebook-convert)
```

- **(1) 추출**: `shared/lib/extract_hwp.py` 가 한글(.hwp 5.0) 본문을 그대로 뽑아 `manuscript.md`를 만듭니다. 외부 라이브러리 없이 동작하며, 같은 HWP면 항상 같은 결과가 나옵니다. (= 변환 "가정"이 코드로 기록됨)
- **(2) 빌드**: `build.sh` 가 Calibre의 `ebook-convert` 명령으로 `manuscript.md` → `EPUB`을 만듭니다. 모든 변환 옵션이 스크립트에 적혀 있어 그대로 재실행·수정 가능합니다.

> 결과물은 **EPUB 3** 표준이라 Windows·Mac·iOS(Apple Books)·Android(Play Books·리디 등) 어디서나 열립니다.

## 폴더 구조

```
watercourse-ebook/
├─ build.sh                 # md → EPUB 빌드 (Calibre CLI)
├─ new-book.sh              # 새 책 폴더 생성 (템플릿 book.env 포함)
├─ templates/book.env       # book.env 템플릿 (주석 포함)
├─ shared/
│  ├─ style.css             # 전자책 공통 디자인 (여기를 고치면 모든 책에 반영)
│  └─ lib/
│     ├─ hwp5.py            # HWP 5.0 파서 (의존성 없음)
│     ├─ extract_hwp.py     # HWP → manuscript.md + 이미지 추출
│     └─ make_cover.py      # 표지 이미지 생성 (Pillow)
└─ books/
   └─ sample/               # ← 예제(아모스 강해). 새 책은 이걸 복제해서 만든다.
      ├─ book.env           # 이 책의 메타데이터·설정 (제목/저자/표지문구 등)
      ├─ original/          # 원본 HWP
      ├─ images/            # 본문용 이미지 (logo.png, church-info.png …)
      │  └─ _extracted/     # HWP에서 자동 추출된 원본 이미지 (참고용)
      ├─ manuscript.md      # ★ 편집용 마스터 원고 (내용 수정은 여기서)
      ├─ cover.jpg          # 표지
      └─ output/            # 생성된 EPUB (git 제외)
```

## 사전 준비 — Calibre 설치 (한 번만)

Calibre는 무료 오픈소스(GPLv3)입니다.

- **macOS**: https://calibre-ebook.com/download_osx 에서 받아 `응용 프로그램`에 설치
  (또는 Homebrew: `brew install --cask calibre`)
- 설치 후 `ebook-convert` 명령이 함께 깔립니다. macOS 앱 내장 경로:
  `/Applications/calibre.app/Contents/MacOS/ebook-convert`

표지를 새로 만들려면 Python의 Pillow가 필요합니다: `pip3 install pillow`
(직접 만든 `cover.jpg`를 그대로 쓰면 Pillow 없이도 빌드됩니다.)

## 사용법

### EPUB 빌드 (가장 자주 쓰는 명령)
```bash
cd watercourse-ebook
./build.sh books/sample
# → books/sample/output/아모스 강해.epub
```

### 원고 검토 (출판 전 필수)
빌드는 원고를 고치지 않습니다. 내용 교정은 이 단계에서 합니다.

```bash
python3 shared/lib/review.py books/sample   # 자동 점검(보고 전용)
```
그 뒤 `docs/검토체크리스트.md`로 사람 눈 검토 → 통과하면 `book.env`에 `REVIEWED="yes"` 표시 → 빌드.

### 내용 수정
`books/sample/manuscript.md` 를 텍스트 편집기로 고친 뒤 다시 `./build.sh books/sample` 실행.

### 디자인(폰트 크기·인용박스·색 등) 수정
`shared/style.css` 를 고친 뒤 다시 빌드. 모든 책에 공통 적용됩니다.

### 표지 수정
`books/sample/book.env` 의 `COVER_*` 값(문구·색)을 바꾸고
`python3 shared/lib/make_cover.py books/sample` 실행. 직접 만든 이미지를 `cover.jpg`로 덮어써도 됩니다.

### HWP에서 원고 다시 추출 (원본이 바뀐 경우)
```bash
python3 shared/lib/extract_hwp.py books/sample
```
⚠️ `manuscript.md`를 새로 덮어씁니다. 손으로 편집한 내용이 있으면 백업 후 실행하세요.

## 실제 원고 추가하기 (book.env 직접 안 만들어도 됨)

`book.env`는 그냥 `키="값"` 텍스트 파일입니다. 매번 새로 쓸 필요 없이 **스크립트로 폴더를 만들면 템플릿 `book.env`가 함께 생성**됩니다.

```bash
./new-book.sh 16-romans "로마서 강해"      # books/16-romans/ 생성 (+ 템플릿 book.env)
```
그 다음:
1. `books/16-romans/original/` 에 원본 HWP 넣기
2. `books/16-romans/book.env` 열어서 값 채우기 (제목·`BOOK_NAME`·`BIBLE_REF`·`HWP_SOURCE`·발행일·표지문구 등)
3. `python3 shared/lib/extract_hwp.py books/16-romans`   # HWP → manuscript.md
4. `python3 shared/lib/make_cover.py books/16-romans`    # 표지 생성 (선택)
5. `./build.sh books/16-romans`                          # EPUB 빌드

> 템플릿 원본은 `templates/book.env` 에 주석과 함께 있습니다. 손으로 만들고 싶으면 이 파일을 복사해 고치면 됩니다.


## 변환 가정(기록)
- 본문은 HWP의 **문단 단위**로 추출 → 원본 공백·줄간격 보존 (PDF 추출의 공백 유실 문제 회피)
- 차례의 "N. 제목 …쪽" 패턴으로 장 제목 수집
- 장 시작 = "숫자 단독 문단 + 제목 + 성경 구절(BIBLE_REF N장)" 구조로 탐지
- 각 장 도입 성경 본문과 "BIBLE_REF N장 …" 인용은 인용 블록으로, 그 외는 본문 문단으로 표기
- 표제지·판권은 `book.env` 값으로 생성

## 버전 관리
두 축으로 관리합니다.

1. **소스 이력 — git**: `manuscript.md`·`book.env`·`style.css`를 고칠 때마다 커밋.
   배포 시점엔 태그를 답니다.
   ```bash
   git add -A && git commit -m "아모스: 7장 오탈자 수정"
   git tag sample-v1.0.1
   ```
2. **출간 버전 — book.env**: 책마다 `EDITION`(판)·`VERSION`·`RELEASE_DATE`를 둡니다.
   빌드 시 자동으로
   - 출력 파일명:  `아모스 강해 - 제1판 v1.0.0 (2024-02).epub`
   - EPUB 메타데이터(발행일·설명)에 버전 기록
   `output/` 에 버전별 파일이 쌓이므로 이전 버전도 남습니다.

권장 흐름: 원고 수정 → `VERSION` 올림(또는 큰 개정이면 `EDITION`) → `git commit`/`git tag` → `./build.sh books/<책>`

## 자동 빌드 (GitHub Actions)
이 저장소를 GitHub에 올리면, `books/**`·`shared/**`·`build.sh` 변경을 푸시할 때
`.github/workflows/build.yml` 이 **러너에 Calibre를 설치하고 동일한 `build.sh`로 EPUB을 빌드**합니다.

- 결과 EPUB은 Actions 실행의 **Artifacts**에서 다운로드.
- 태그(`git tag v1.0.0 && git push --tags`)를 올리면 **Release에 EPUB 첨부**.
- 수동 실행: Actions 탭 → Build EPUB → Run workflow (특정 책만 빌드하려면 `books/<slug>` 입력).
- 빌드 로그가 CI에 남아 **변환 과정이 자동 기록**됩니다(엔진은 Mac과 동일한 Calibre).
- 빌드 후 **epubcheck**로 EPUB 규격을 자동 검증합니다(오류 시 빌드 실패). 리더기별 렌더링 문제의 상당수는 규격 위반에서 오므로 1차 방어선이 됩니다.

작업 흐름: (로컬/AI) `manuscript.md`·`book.env` 작성 → `git commit && git push` → GitHub Actions가 빌드.
