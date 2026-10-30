#!/usr/bin/env bash
# traject-gtm path resolver: every path the traject-gtm family references must exist on disk.
# exit 0 = all referenced paths resolve
# exit 2 = at least one referenced path is dangling (or a --plant fixture was supplied)
# Usage:
#   verify_paths.sh                 # check the family
#   verify_paths.sh --plant <path>  # PLANTED FAILURE: force a dangling path, must exit 2
set -u

SKILLS_ROOT="/Users/rig128gb/Developer/rig-capabilities/capabilities/skills"
FAMILY_GLOB="${SKILLS_ROOT}/traject-gtm*/SKILL.md"
INSTALL_COPY="/Users/rig128gb/.aside/u/0/skills/user/traject-gtm/SKILL.md"

if [ "${1:-}" = "--plant" ]; then
  plant="${2:?--plant needs a path}"
  if [ -e "$plant" ]; then
    echo "PLANT-ERROR: planted path unexpectedly exists: $plant" >&2
    exit 3
  fi
  echo "PLANT: planted dangling path -> $plant"
  echo "MISSING: $plant"
  echo "RESULT: FAIL (planted)"
  exit 2
fi

files=$(ls $FAMILY_GLOB 2>/dev/null)
[ -f "$INSTALL_COPY" ] && files="$files $INSTALL_COPY"

if [ -z "${files// /}" ]; then
  echo "ERROR: no traject-gtm SKILL.md files found under $SKILLS_ROOT" >&2
  exit 2
fi

tmp=$(mktemp)
for f in $files; do
  grep -oE '/Users/[A-Za-z0-9_./@-]+' "$f"
  grep -oE '~/[A-Za-z0-9_./@-]+' "$f"
  grep -oE '(^|[^A-Za-z0-9_./-])traject-gtm[A-Za-z0-9_-]*/[A-Za-z0-9_./-]+' "$f" | grep -oE 'traject-gtm[A-Za-z0-9_-]*/[A-Za-z0-9_./-]+'
done | sed 's/[.,;:]$//' | sed 's|/$||' | sort -u > "$tmp"

missing=0
checked=0
while IFS= read -r p; do
  [ -z "$p" ] && continue
  case "$p" in
    /Users/*) target="$p" ;;
    ~/*) target="$HOME/${p#~/}" ;;
    traject-gtm*) target="${SKILLS_ROOT}/${p}" ;;
    *) continue ;;
  esac
  checked=$((checked+1))
  # Layer-2 skills are hidden from ~/.aside/u/0/skills/user; resolve them by the documented store order.
  if [ ! -e "$target" ]; then
    case "$target" in
      */.aside/u/0/skills/user/*)
        rel="${target#*/.aside/u/0/skills/user/}"
        for root in "$HOME/.hermes/skills" "$SKILLS_ROOT" "$HOME/.claude/skills" "$HOME/.rig/universal-skills-registry/skills" "$HOME/.aside/u/0/skill-library"; do
          if [ -e "$root/$rel" ]; then target="$root/$rel"; break; fi
        done ;;
    esac
  fi
  if [ -e "$target" ]; then
    printf 'OK: %s -> %s\n' "$p" "$target"
  else
    printf 'MISSING: %s -> %s\n' "$p" "$target"
    missing=$((missing+1))
  fi
done < "$tmp"
rm -f "$tmp"

echo "RESULT: checked=${checked} missing=${missing}"
if [ "$missing" -gt 0 ]; then
  exit 2
fi
exit 0
