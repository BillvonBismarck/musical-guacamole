#!/bin/bash
cd "$(dirname "$0")/.." || exit 1
{
  echo "=== concepts ==="
  python3 tools/realm_wardens_gen.py concepts
  echo "=== models ==="
  python3 tools/realm_wardens_gen.py models --parallel 4
  echo "=== art ==="
  python3 tools/realm_wardens_gen.py art
  echo "=== finished ==="
} >> docs/realm-wardens/batch.log 2>&1
