# CLAUDE.md — 전자책 제작 작업 지침 (AI용)

이 저장소에서 **새 설교 원고(HWP/DOC)를 EPUB 전자책으로 만드는 작업을 할 때 Claude가 따르는 절차서**다.
원고마다 내부 구조가 달라 "구조 인식"은 프로그램으로 일반화하지 않는다.
→ **원문 추출·표지·빌드는 결정론적 스크립트**, **구조화(manuscript.md·book.env 작성)는 Claude가 판단**으로 한다.

## 지원 원본 형식
- **HWP(.hwp 5.0)** — `shared/lib/hwp5.py` (1순위, 가장 깨끗)
- **DOCX(.docx)** — `shared/lib/docx.py` (2순위, 공백·문단 보존 양호)
- **DOC(구버전)** — 먼저 변환: `soffice --headless --convert-to docx 파일.doc` → 이후 .docx로 처리
- **PDF** — 최후 수단(줄바꿈 공백 유실·노이즈로 검토 부담 큼). 가급적 지양.
- 공통 원문 덤프: `python3 shared/lib/dump.py <파일.hwp|.docx>` (구조 판단용)

## 역할 분담
- 스크립트(고정): `shared/lib/hwp5.py`(HWP 원문 추출), `shared/lib/dump.py`(원문 덤프),
  `shared/lib/make_cover.py`(표지), `build.sh`(Calibre로 md→EPUB)
- Claude(판단): 덤프한 원문을 읽고 `books/<slug>/manuscript.md` 구조화 + `books/<slug>/book.env` 작성

## 새 책 만드는 절차 (Claude가 수행)
1. 폴더 생성: `./new-book.sh <slug> "제목"`  (예: `16-romans`). `original/`에 HWP를 둔다.
2. **원문 읽기**: `python3 shared/lib/dump.py books/<slug>/original/<파일>.hwp`
   - 전체 문단을 `[번호] 본문` 으로 출력. 이걸 읽고 구조를 파악한다(표제지/차례/머리말/장/판권/안내).
3. **이미지 추출**: `python3 shared/lib/dump.py books/<slug>/original/<파일>.hwp --images books/<slug>/images/_extracted`
   - 필요한 것만 `images/`로 올려 의미있는 이름을 준다: 로고→`logo.png`, 예배안내/지도→`church-info.png`.
4. **manuscript.md 작성** (아래 "마크업 규칙"대로). 본문은 **원문 그대로**, 빠뜨리거나 바꾸지 않는다.
5. **book.env 작성/수정** (아래 "book.env 필드"대로).
6. **검토(교정)**: `python3 shared/lib/review.py books/<slug>` 로 자동 점검 + `docs/검토체크리스트.md`로 사람 눈 검토.
   - 제목 오타·띄어쓰기, 장 누락, 본문/성경구절 정확성 등 **내용 교정은 여기서 manuscript.md를 직접 고친다**(빌드가 고치지 않음).
   - 통과하면 `book.env`에 `REVIEWED="yes"`, `REVIEW_DATE` 표시.
7. **표지**: `python3 shared/lib/make_cover.py books/<slug>` (book.env의 COVER_* 사용) 또는 직접 `cover.jpg` 교체.
8. **빌드**: `./build.sh books/<slug>`  → `books/<slug>/output/제목 - 제N판 vX (날짜).epub`
   - 주의: `build.sh`는 macOS의 Calibre(`/Applications/calibre.app/...`)를 호출한다. Claude 샌드박스에는
     Calibre가 없으므로 빌드는 보통 사용자 터미널에서 실행하거나, 사용자에게 명령을 전달한다.
9. **검증**: 생성된 EPUB을 풀어 목차/장 구성/한글/표지/판권(판·발행일·버전)을 확인한다.

## manuscript.md 마크업 규칙
Markdown + 일부 raw HTML(클래스 지정용). 스타일은 `shared/style.css`가 담당.

- **표제지**(맨 앞, 장으로 안 잡히게 `#` 안 씀):
  ```html
  <div class="title-page">
  <p class="logo"><img src="images/logo.png" alt="물줄기교회"/></p>   <!-- 로고 있으면 -->
  <p class="bk">아모스</p>            <!-- 성경책 이름(큰 글자) -->
  <p class="sub">아모스 강해</p>       <!-- 부제(책 제목) -->
  <p class="au">조춘숙 목사</p>
  <p class="pub">물줄기교회 출판부</p>
  <p class="vid">동영상 설교는 …</p>
  </div>
  ```
- **머리말**: `# 이 책을 읽는 분들께` + 문단들 + 서명 `<p class="sign">2024년 2월<br/>물줄기교회 목사 조춘숙</p>`
- **장**: 각 장 제목을 `# N. 제목` 으로 (H1 → 자동 목차/페이지나눔).
  - 바로 아래 본문 구절: `<p class="passage">아모스 1장 1~15절</p>`
  - 그 장 도입 성경 본문: 인용블록 `> 1유다 왕 웃시야의…` (절 번호 포함, 원문 그대로)
  - 본문 중 인용한 성경 구절 라벨: `<p class="ref">아모스 1장 1절</p>` 그 뒤 인용블록 `> …`
  - 해설(설교 본문): 일반 문단 (그대로)
- **판권**: `# 판권`
  ```html
  <div class="colophon">
  <p class="bk">아모스</p>
  <p class="subk">아모스 강해</p>
  <p class="pubinfo">제1판 발행  2024년 2월</p>   <!-- EDITION + RELEASE_DATE(한글) -->
  <p>지은이  조춘숙 목사</p>
  <p>제작·편집  물줄기교회 출판부</p>
  <p>주소  …</p><p>전화  …</p><p>홈페이지  …</p>
  <p class="ver">전자책 버전 1.0.0</p>            <!-- VERSION -->
  </div>
  ```
  ※ 판/발행일/버전은 book.env의 EDITION·RELEASE_DATE·VERSION 값과 **반드시 일치**시킨다.
- **교회 안내**(예배/지도 이미지 있으면 맨 뒤): `# 교회 안내` + `<p class="church-info"><img src="images/church-info.png" .../></p>`

사용 가능한 CSS 클래스: `title-page(.logo/.bk/.sub/.au/.pub/.vid)`, `sign`, `passage`, `ref`,
blockquote(성경 인용), `colophon(.bk/.subk/.pubinfo/.ver)`, `church-info`.

## book.env 필드 (한 줄 `키="값"`, 공백/한글은 따옴표)
| 키 | 설명 | 예 |
|----|------|----|
| `TITLE` | 책 제목(표지·메타데이터) | `"아모스 강해"` |
| `BOOK_NAME` | 성경책 이름(표지 큰 글자) | `"아모스"` |
| `AUTHORS` | 지은이 | `"조춘숙"` |
| `AUTHOR_TITLE` | 직함 | `"목사"` |
| `PUBLISHER` | 출판사 | `"물줄기교회 출판부"` |
| `LANGUAGE` | 언어 | `"ko"` |
| `OUTPUT_NAME` | 출력 파일명 베이스(비우면 TITLE) | `"아모스 강해"` |
| `TAGS` | 분류 태그(쉼표) | `"기독교,설교,아모스,강해"` |
| `COMMENTS` | 책 소개(메타데이터) | `"… 설교집 (제17권)."` |
| `EDITION` | 판(큰 개정 시 올림) | `"제1판"` |
| `VERSION` | 세부 버전(오탈자/디자인) | `"1.0.0"` |
| `RELEASE_DATE` | 발행일 `YYYY-MM`/`YYYY-MM-DD` | `"2024-02"` |
| `HWP_SOURCE` | original/ 내 HWP 파일명 | `"original/17 아모스.hwp"` |
| `BIBLE_REF` | 본문 성경책 이름(구절 인식용) | `"아모스"` |
| `VIDEO` | 표제지 동영상 안내 문구 | `"동영상 설교는 …"` |
| `PREFACE_SIGN` | 머리말 서명(`|`로 줄바꿈) | `"2024년 2월|물줄기교회 목사 조춘숙"` |
| `COLOPHON` | 판권 항목(`|`로 줄바꿈, 판/발행일/버전은 넣지 말 것) | `"지은이  …|주소  …|전화  …"` |
| `COVER_VERSE` | 표지 대표구절(`|`구분, 마지막=출처) | `"너희는 나를 찾으라|그리하면 살리라|아모스 5장 4절"` |
| `COVER_BG` / `COVER_ACCENT` | 표지 배경/강조색(hex) | `"1c3144"` / `"c9a25a"` |

build.sh는 book.env를 읽어 EPUB 메타데이터·파일명을 만든다. EDITION/VERSION/RELEASE_DATE → 파일명·발행일·설명에 반영.

## 버전 관리 규칙
- 원고/디자인 수정 → `VERSION` 올림(예 1.0.0→1.0.1). 큰 개정 → `EDITION` 올림(제1판→제2판) + VERSION 리셋.
- 수정 시 `git commit`, 배포 시 `git tag <slug>-vX.Y.Z`. 브랜치는 `main`.

## 품질 원칙 (중요)
- **빌드는 원고 내용을 수정하지 않는다.** 오타·띄어쓰기·구조 교정은 반드시 검토 단계에서 manuscript.md를 직접 고친다.
  (예: 9장 '예수그리스도'→'예수 그리스도'는 build가 아니라 manuscript에서 수정.)
- `build.sh`의 `fix_titles.py`는 콘텐츠 교정이 아니라 **패키징 정규화**다(Calibre가 비우는 각 문서 <title>을 장 제목으로 채움). 본문 텍스트는 건드리지 않는다.
- 설교 본문은 **원문 그대로**. 요약·의역·삭제·추가 금지. 절 번호 유지.
- HWP 원문 추출(hwp5.py)은 문단 단위라 공백·문단이 보존된다. PDF 추출은 줄바꿈에서 공백이 사라지므로 쓰지 않는다.
- 작업 후 EPUB을 실제로 열어 한글 깨짐/목차/표지/판권을 확인한다.

## 물줄기 강해 시리즈의 흔한 구조(참고)
표제지(책이름/강해/저자/동영상) → 차례(`N. 제목 …쪽`) → `이 책을 읽는 분들께` → 각 장(숫자·제목·`성경 N장 X절`·도입성경·해설, 중간중간 성경인용) → 판권 → (예배안내/오시는 길 이미지).
대부분 이 패턴이라, 표준형이면 참고용 자동초안 `shared/lib/extract_hwp.py books/<slug>` 를 돌려 1차 초안을 얻은 뒤 **반드시 검토·수정**해도 된다. 비표준이면 dump를 보고 직접 작성한다.

## 장기 목표(로드맵)
사용자가 **구글 드라이브에 원고를 올리면 자동으로 EPUB 발행**되는 흐름. (설계 메모는 `docs/automation.md` 참고)

## 작성·커밋 규칙 (필수)
- **git 커밋에 Claude/AI 공동작성 표기를 넣지 않는다.** `Co-Authored-By: Claude …`,
  "Generated with Claude Code" 같은 트레일러/문구 금지.
- **커밋 메시지는 영어로 간결히 작성한다.** (`feat:`/`fix:`/`ci:`/`docs:` 접두어 권장)
- **README·docs는 한국어로 작성한다.** (코드·명령·경로·식별자는 영문 그대로) CLAUDE.md 등 AI 지침서도 한국어 유지.
