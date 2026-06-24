#!/usr/bin/env bash
# 새 책 폴더 생성:  ./new-book.sh <폴더이름> ["책 제목"]
#   예) ./new-book.sh "19. 새책 제목" "표지 제목"
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
SLUG="${1:?사용법: ./new-book.sh <폴더이름> [\"책 제목\"]  예: ./new-book.sh 16-romans \"로마서 강해\"}"
TITLE="${2:-}"
DEST="$ROOT/books/$SLUG"
[ -e "$DEST" ] && { echo "✗ 이미 존재합니다: books/$SLUG" >&2; exit 1; }
mkdir -p "$DEST/original" "$DEST/images"
cp "$ROOT/templates/book.env" "$DEST/book.env"
[ -n "$TITLE" ] && { sed -i.bak "s|^TITLE=.*|TITLE=\"$TITLE\"|" "$DEST/book.env"; rm -f "$DEST/book.env.bak"; }
cat <<EOF
✓ books/$SLUG 생성됨

다음 순서로 진행하세요:
 1) books/$SLUG/original/ 에 원본 HWP 넣기
 2) books/$SLUG/book.env 열어서 값 채우기
    (TITLE, BOOK_NAME, BIBLE_REF, HWP_SOURCE, RELEASE_DATE, 표지 문구 등)
 3) python3 shared/lib/extract_hwp.py books/$SLUG     # HWP → manuscript.md
 4) python3 shared/lib/make_cover.py books/$SLUG      # 표지 생성 (선택)
 5) ./build.sh books/$SLUG                            # EPUB 빌드
EOF
