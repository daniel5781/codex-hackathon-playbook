#!/usr/bin/env bash
# 공개 범용 지침만 배치한다. 네트워크, 의존성 설치, Codex 설정, Git 작업은 하지 않는다.
set -euo pipefail

usage() {
  printf '%s\n' '사용법: bash scripts/setup.sh [--check | --apply] /path/to/task' \
    '  --check (기본): 파일을 쓰지 않고 예정 경로와 충돌을 확인한다.' \
    '  --apply: 제출 규칙상 추가 파일이 허용됨을 확인한 뒤 지침을 배치한다.'
}
fail() { printf '중단: %s\n' "$*" >&2; exit 1; }
present() { [ -e "$1" ] || [ -L "$1" ]; }

check_only=true
case "${1:-}" in
  --help) usage; exit 0 ;;
  --check) shift ;;
  --apply) check_only=false; shift ;;
  -*) usage >&2; exit 2 ;;
esac
[ "$#" -eq 1 ] || { usage >&2; exit 2; }
[ -d "$1" ] || fail '대상 프로젝트 디렉터리가 없다.'

script_dir=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
source_dir=$(CDPATH= cd -- "$script_dir/.." && pwd -P)
task_dir=$(CDPATH= cd -- "$1" && pwd -P)
case "$task_dir" in
  /|"$source_dir"|"$source_dir"/*) fail '과제 루트를 지정하라. 시스템 루트나 플레이북 저장소에는 적용하지 않는다.' ;;
esac

has_readme=false
for file in "$task_dir"/[Rr][Ee][Aa][Dd][Mm][Ee]*; do
  if [ -f "$file" ]; then has_readme=true; break; fi
done
$has_readme || fail 'README가 있는 실제 과제 루트를 지정하라. README를 임의로 생성하지 마라.'

bundle_dir="$task_dir/.codex-playbook"
sources=("$source_dir/AGENTS.md" "$source_dir/PLAYBOOK.md" "$source_dir/QUICKSTART.md" "$source_dir/UI_ASSETS.md" "$source_dir/prompts/start.txt")
names=('AGENTS.md' 'PLAYBOOK.md' 'QUICKSTART.md' 'UI_ASSETS.md' 'START_PROMPT.txt')

# 충돌을 먼저 검사하여 기존 파일을 덮어쓰지 않는다.
[ ! -L "$bundle_dir" ] || fail '.codex-playbook이 심볼릭 링크다. 기존 경로를 보존하고 수동으로 확인하라.'
if present "$bundle_dir" && [ ! -d "$bundle_dir" ]; then
  fail '.codex-playbook 경로에 다른 파일이 있다.'
fi
for i in "${!sources[@]}"; do
  [ -f "${sources[$i]}" ] && [ -r "${sources[$i]}" ] || fail "원본 문서 누락: ${names[$i]}"
  destination="$bundle_dir/${names[$i]}"
  if present "$destination"; then
    [ ! -L "$destination" ] && [ -f "$destination" ] || fail "기존 경로 충돌: $destination"
    cmp -s "${sources[$i]}" "$destination" || fail "기존 문서와 내용이 다르다: $destination (덮어쓰지 않음)"
  fi
done

create_bridge=true
if present "$task_dir/AGENTS.md" || present "$task_dir/AGENTS.override.md"; then
  create_bridge=false
fi

printf '대상 과제: %s\n' "$task_dir"
printf '배치할 범용 문서: %s\n' "$bundle_dir"
printf '  %s\n' "${names[@]}"
if $create_bridge; then
  printf '%s\n' '루트 AGENTS.md: 새 연결 지침을 생성한다.'
else
  printf '%s\n' '루트 지침: 기존 파일을 보존한다. 시작 프롬프트로 보조 문서를 명시해 읽는다.'
fi
if $check_only; then
  printf '%s\n' '점검 완료. 파일을 변경하지 않았다. 제출 규칙을 자동 검증한 결과는 아니다.' \
    '추가 파일의 허용·수집 범위를 확인한 경우에만 --apply로 적용하라.'
  printf '파일 배치 없이 참조할 지침: %s/AGENTS.md\n' "$source_dir"
  exit 0
fi

mkdir -p "$bundle_dir"
for i in "${!sources[@]}"; do
  destination="$bundle_dir/${names[$i]}"
  if present "$destination"; then
    printf '유지: %s\n' "$destination"
  else
    # 검사 이후 파일이 생겨도 noclobber로 보호한다.
    (set -C; cat "${sources[$i]}" > "$destination")
    printf '생성: %s\n' "$destination"
  fi
done
if $create_bridge; then
  (set -C; cat > "$task_dir/AGENTS.md" <<'GUIDANCE'
# 프로젝트 작업 지침

- 과제의 공식 요구사항, README와 기존 디렉터리별 지침을 우선하라.
- [.codex-playbook/AGENTS.md](.codex-playbook/AGENTS.md)의 최소 규칙을 읽어 적용하고 보조 문서는 필요한 때만 참조하라.
- Computer Use를 절대 사용하지 마라.
GUIDANCE
  )
fi

printf '\n지침 경로: %s/AGENTS.md\n' "$bundle_dir"
printf '%s\n' '세팅 완료. 위 경로와 아래 요청을 과제의 Codex에 전달하라. 보조 문서는 필요할 때만 읽는다.'
printf '\n'
cat "$bundle_dir/START_PROMPT.txt"
