#!/usr/bin/env bash
# 판(edition) 릴리스: 현재 상태를 git 태그로 고정하고 푸시 → CI가 EPUB을 Release에 첨부.
# 사용법:  ./release.sh "books/16. 율법의 요구와 십자가의 완성(로마서)"
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
BOOK="${1:?사용법: ./release.sh <book_dir>  (예: ./release.sh "books/16. 율법의 요구와 십자가의 완성(로마서)")}"
BOOK="$(cd "$BOOK" && pwd)"
# shellcheck disable=SC1091
source "$BOOK/book.env"
slug="$(basename "$BOOK")"
num="$(printf '%s' "$slug" | grep -oE '^[0-9]+' || true)"
tag="${num:-book}-v${VERSION}"
title="${OUTPUT_NAME:-$TITLE} ${EDITION} v${VERSION} (${RELEASE_DATE})"
git -C "$ROOT" tag -a "$tag" -m "$title"
git -C "$ROOT" push origin "$tag"
echo "✓ 태그 푸시: $tag  —  $title"
echo "  GitHub Actions가 이 판을 빌드해 Release에 EPUB을 첨부합니다."
echo "  과거 판 복구:  git checkout $tag  &&  ./build.sh $1"
