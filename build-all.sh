#!/usr/bin/env bash
# 모든 책을 한 번에 EPUB으로 빌드한다.
# 사용법:  ./build-all.sh
# (각 책은 build.sh로 빌드 → books/<슬러그>/output/*.epub)
set -uo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
total=0; ok=0; fail=0; failed=()
for d in books/*/; do
  b="${d%/}"
  [ -f "$b/book.env" ] || continue
  [ -f "$b/manuscript.md" ] || { echo "⏭  건너뜀(원고 없음): $b"; continue; }
  total=$((total+1))
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "▶ 빌드: $b"
  if bash build.sh "$b"; then ok=$((ok+1)); else fail=$((fail+1)); failed+=("$b"); fi
done
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "완료: 성공 $ok / 실패 $fail (총 $total)"
if [ "$fail" -ne 0 ]; then printf '  ✗ %s\n' "${failed[@]}"; exit 1; fi
echo "✓ 전체 EPUB이 각 books/<슬러그>/output/ 에 생성되었습니다."
