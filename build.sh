#!/usr/bin/env bash
# md -> EPUB 빌드 (Calibre ebook-convert 사용)
# 사용법:  ./build.sh books/17-amos
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
BOOK="${1:?사용법: ./build.sh <book_dir>  (예: ./build.sh books/17-amos)}"
BOOK="$(cd "$BOOK" && pwd)"
# shellcheck disable=SC1091
source "$BOOK/book.env"

# 검토 단계 확인 (빌드는 내용을 고치지 않는다 — 교정은 검토 단계에서)
if [ "${REVIEWED:-}" != "yes" ]; then
  echo "⚠ 검토 완료 표시가 없습니다(book.env REVIEWED=\"yes\")." >&2
  echo "  먼저 점검:  python3 shared/lib/review.py $1   /  체크리스트: docs/검토체크리스트.md" >&2
fi

# ebook-convert 경로 탐색 (macOS 앱 내장 / PATH / Linux)
EC="${EBOOK_CONVERT:-}"
if [ -z "${EC}" ]; then
  if [ -x "/Applications/calibre.app/Contents/MacOS/ebook-convert" ]; then
    EC="/Applications/calibre.app/Contents/MacOS/ebook-convert"
  elif command -v ebook-convert >/dev/null 2>&1; then
    EC="ebook-convert"
  else
    echo "✗ Calibre의 ebook-convert를 찾지 못했습니다. README의 설치 안내를 보세요." >&2; exit 1
  fi
fi

mkdir -p "$BOOK/output"
# 버전 정보 (book.env). 파일명·메타데이터에 반영.
EDITION="${EDITION:-}"
VERSION="${VERSION:-}"
RELEASE_DATE="${RELEASE_DATE:-$(date +%Y-%m-%d)}"
# 파일명:  "제목 - 제1판 v1.0.0 (2024-02).epub"
NAME="${OUTPUT_NAME:-$TITLE}"
[ -n "$EDITION" ] && NAME="$NAME - $EDITION"
[ -n "$VERSION" ] && NAME="$NAME v$VERSION"
NAME="$NAME ($RELEASE_DATE)"
OUT="$BOOK/output/${NAME}.epub"
# 버전을 설명(comments)에도 기록
VERNOTE="버전 ${VERSION:-?} · ${EDITION:-?} · 발행 ${RELEASE_DATE}"
FULL_COMMENTS="${COMMENTS:-}${COMMENTS:+  }[$VERNOTE]"

echo "▶ ebook-convert 실행 명령:"
set -x
"$EC" "$BOOK/manuscript.md" "$OUT" \
  --title "$TITLE" \
  --authors "$AUTHORS" \
  --language "${LANGUAGE:-ko}" \
  --publisher "$PUBLISHER" \
  --pubdate "$RELEASE_DATE" \
  --tags "${TAGS:-}" \
  --comments "$FULL_COMMENTS" \
  --book-producer "$PUBLISHER" \
  --cover "$BOOK/cover.jpg" \
  --extra-css "$ROOT/shared/style.css" \
  --formatting-type markdown \
  --level1-toc "//h:h1" \
  --chapter "//h:h1" \
  --chapter-mark none \
  --page-breaks-before "//h:h1" \
  --change-justification justify \
  --epub-version 3 \
  --no-default-epub-cover
set +x

# 후처리: 각 문서 <title>을 장 제목으로 정리(Calibre의 '알 수 없음' 보정)
python3 "$ROOT/shared/lib/fix_titles.py" "$OUT" "$TITLE" || echo "  (title 정리 건너뜀)"

echo "✓ 완료: $OUT"
