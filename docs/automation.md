# 자동 발행 로드맵 (구글 드라이브 → EPUB)

목표: **구글 드라이브에 원고(HWP)를 올리면 자동으로 EPUB이 만들어지는** 흐름.

## 핵심 제약 (먼저 이해)
- **구조화는 AI가 개입해야 한다.** 원고마다 내부 구조가 달라 "구조 인식"을 순수 스크립트로 일반화 불가
  (사용자도 동의한 지점). 따라서 "사람·AI 개입 0"의 완전 자동은 불가능하고,
  **AI(에이전트)가 구조화를 맡는 반자동**이 현실적인 최선이다.
- **빌드 엔진 위치**: 데스크톱 수작업은 Calibre(`build.sh`). 그러나 무인 자동화(클라우드 에이전트)는
  Mac의 Calibre를 직접 못 쓴다. 자동화용 빌드는 에이전트 환경에서 되는 **pandoc(표준 도구)** 또는
  저장소 내장 파이썬 조립기를 쓴다. (둘 다 동일 `manuscript.md`/`style.css`로 동작하게 유지)

## 권장 폴더 구조 (드라이브)
```
물줄기 좋은 씨앗/
  _inbox/        ← 새 HWP를 여기 올린다 (트리거)
  watercourse-ebook/   ← 이 저장소 (books/<slug>/…)
  _published/    ← 완성된 EPUB 출력
```

## 처리 파이프라인 (에이전트가 수행)
1. `_inbox/`에서 새 HWP 감지
2. `books/<slug>/` 생성(new-book.sh) + HWP 배치
3. `dump_hwp.py`로 원문 읽기 → CLAUDE.md 규칙대로 `manuscript.md` 구조화 + `book.env` 작성
4. 이미지 추출/배치, 표지 생성
5. 빌드(pandoc 또는 Calibre) → EPUB
6. `_published/`에 저장, git commit/tag
7. 완료 알림(메일/슬랙 등)

## 빌드 실행 위치 — GitHub Actions (확정 방향)
Mac/클라우드 대신 **GitHub Actions 러너에서 Calibre를 설치해 빌드**한다(.github/workflows/build.yml).
→ Calibre 단일 엔진 유지 + 무인 빌드 + CI 로그로 과정 기록 + 릴리스 산출물. 트리거는 git push.
드라이브 연동은 추후 'Drive→GitHub 동기화' 다리로 붙인다.

## (참고) 그 외 트리거 방식 후보
- **A. 예약 작업**(Cowork 스케줄): 매일/매시간 `_inbox` 확인 → 있으면 처리. 가장 "자동"에 가깝다.
- **B. 한마디 트리거**: 사용자가 "새 원고 처리해줘"라고 하면 에이전트가 일괄 처리. 통제·검토 쉬움.
- **C. Mac 로컬 자동화**(launchd/폴더액션 + Calibre): 빌드는 로컬에서, 단 구조화는 결국 AI 필요 → 부분만 가능.

## 발행(스토어 업로드)
EPUB 생성까지가 1차 목표. 이후 Google Play Books(Partner Center)·Apple Books·리디 등 업로드는
별도 단계(반자동: 브라우저 자동화 가능, 단 약관/가격/심사는 사람이 확인).

## 현 상태
- 결정론 부분(원문추출·표지·빌드) + AI 구조화 절차(CLAUDE.md) 완비. 샘플(아모스) 동작 검증 단계.
- 다음: 트리거 방식(A/B) 확정 → `_inbox` 신설 → 빌드 엔진 자동화용(pandoc) 추가 → 예약/온디맨드 연결.
