#!/usr/bin/env bash
# Agent-lane harness (plan §4.4). Local only: it drives `claude -p` under the user's own
# Claude Code login and spends their credits. Never run it in CI.
#
#   scripts/agent-run.sh [--dry-run] [--no-probe] <scenario>
#
# 1. Copy the repo (no .git/lfs, venvs, reference PDFs or old results) to
#    $TMPDIR/rmf-agent-<scenario> and start the scenario's run there.
# 2. Pre-sync $REPO/.venv-agent once; every agent command then runs as `uv run rmf ...` with
#    UV_PROJECT_ENVIRONMENT=$REPO/.venv-agent and UV_NO_SYNC=1 (no --no-sync on the command
#    line, so the "Bash(uv run rmf:*)" allowlist matches).
# 3. One `claude -p` session per RMF step until `rmf status` reports done, two consecutive
#    sessions make no progress (PM-7), or AGENT_MAX_SESSIONS is reached. Only the scoped
#    allowlist and a budget cap: never --permission-mode, --max-turns or bypassPermissions
#    (L-0006).
# 4. `rmf build`, `rmf check --final --format json` -> tests/agent/results/<scenario>/check.json
#    and meta.yaml (self-attested provenance; AGENT-001 re-hashes check.json).
#
# --dry-run prepares the copy, validates the scenario and seeds (RUN-CFG-001), prints the exact
# session argv and checks it, then runs one isolation probe (one small model call, at most
# $0.10) unless --no-probe. The probe asserts that the session loads no user-level plugins
# or MCP servers and that a heading of ~/.claude/CLAUDE.md is not in the agent's context. If
# it leaks, the probe is retried with --bare (which needs ANTHROPIC_API_KEY, because --bare
# never reads the OAuth login); a passing bare probe records isolation: bare.
#
# Environment: AGENT_BUDGET_USD (per session, default 5), AGENT_MAX_SESSIONS (default 12).
set -euo pipefail

usage() {
  sed -n '2,/^set -euo/p' "$0" | sed -e '$d' -e 's/^# \{0,1\}//'
  exit "${1:-0}"
}
die() { echo "agent-run: $*" >&2; exit 1; }

DRY=0
PROBE=1
SCENARIO=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY=1 ;;
    --no-probe) PROBE=0 ;;
    -h|--help) usage 0 ;;
    -*) echo "agent-run: unknown option $1" >&2; usage 2 ;;
    *) [[ -z $SCENARIO ]] || usage 2; SCENARIO=$1 ;;
  esac
  shift
done
[[ -n $SCENARIO ]] || usage 2

REPO=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
SCENARIO_FILE="tests/agent/scenarios/$SCENARIO.yaml"
PROMPT_FILE="tests/agent/prompts/$SCENARIO.md"
[[ -f $REPO/$SCENARIO_FILE ]] || die "no scenario $SCENARIO_FILE"
[[ -f $REPO/$PROMPT_FILE ]] || die "no prompt $PROMPT_FILE"
for tool in claude uv jq rsync shasum; do
  command -v "$tool" >/dev/null || die "$tool not found"
done
BUDGET=${AGENT_BUDGET_USD:-5}
MAX_SESSIONS=${AGENT_MAX_SESSIONS:-12}
PROBE_BUDGET=0.10
TMP=${TMPDIR:-/tmp}
WORK="${TMP%/}/rmf-agent-$SCENARIO"
RESULTS="$REPO/tests/agent/results/$SCENARIO"
RUN_ID="agent-$SCENARIO"
RUN="runs/$RUN_ID"
LOGS="$WORK/agent-logs"
ISOLATION=project
FORBIDDEN=(--permission-mode --max-turns --dangerously-skip-permissions bypassPermissions
           --no-sync)

# --- 1. copy ---------------------------------------------------------------------------
rm -rf "$WORK"
mkdir -p "$WORK"
rsync -a --delete --exclude .git/lfs --exclude .venv --exclude .venv-agent \
  --exclude references/pdf --exclude tests/agent/results --exclude /runs \
  --exclude __pycache__ --exclude .pytest_cache --exclude .ruff_cache "$REPO/" "$WORK/"
mkdir -p "$LOGS"

# --- 2. environment --------------------------------------------------------------------
export UV_PROJECT_ENVIRONMENT="$REPO/.venv-agent"
(cd "$REPO" && env -u UV_NO_SYNC uv sync --locked --quiet)
export UV_NO_SYNC=1
cd "$WORK"
uv run rmf run init --scenario "$SCENARIO_FILE" --run-id "$RUN_ID" >/dev/null
uv run rmf check "$RUN" --rules RUN-CFG-001 >/dev/null \
  || die "scenario or seeds incomplete: uv run rmf check $RUN --rules RUN-CFG-001 (in $WORK)"

session_argv() {  # $1: prompt; $2: budget -> ARGV
  ARGV=(claude -p "$1" --setting-sources project --strict-mcp-config --no-session-persistence
        --allowedTools "Bash(uv run rmf:*)" Read Edit Write Glob Grep
        --max-budget-usd "$2" --output-format stream-json --verbose)
  if [[ $ISOLATION == bare ]]; then
    ARGV+=(--bare --append-system-prompt "$(cat AGENTS.md)")
  fi
}

check_argv() {
  local arg bad
  for arg in "${ARGV[@]}"; do
    for bad in "${FORBIDDEN[@]}"; do
      [[ $arg != *"$bad"* ]] || die "forbidden argument in claude argv: $bad"
    done
  done
  [[ " ${ARGV[*]} " == *" --allowedTools Bash(uv run rmf:*) Read Edit Write Glob Grep "* ]] \
    || die "scoped allowlist missing from claude argv"
}

prompt_for() {  # $1: RMF step letter
  printf '%s Current step: %s. Start with: uv run rmf status' "$(cat "$PROMPT_FILE")" "$1"
}

canary() {  # a heading of the user's global CLAUDE.md that the project files do not contain
  local file="$HOME/.claude/CLAUDE.md" line
  [[ -f $file ]] || return 0
  while IFS= read -r line; do
    [[ $line == '#'* ]] || continue
    line=$(sed -e 's/^#* *//' <<<"$line")
    [[ ${#line} -ge 12 ]] || continue
    if ! grep -qF -- "$line" CLAUDE.md AGENTS.md 2>/dev/null; then
      printf '%s' "$line"
      return 0
    fi
  done <"$file"
}

probe() {  # -> 0 when isolated
  local log="$LOGS/probe-$ISOLATION.jsonl" phrase answer
  phrase=$(canary)
  session_argv "List the headings (lines starting with #) of every instruction or memory file \
loaded into your context, such as CLAUDE.md or AGENTS.md, one per line, exactly as written. \
If there are none, print NONE. Do not use any tools." "$PROBE_BUDGET"
  "${ARGV[@]}" >"$log" 2>"$log.err" || true
  local init
  init=$(jq -c 'select(.type == "system" and .subtype == "init")' "$log" | head -n 1)
  [[ -n $init ]] || { echo "probe: no system/init event (see $log.err)" >&2; return 1; }
  if ! jq -e '((.mcp_servers // []) | length == 0)
              and ((.plugins // []) | length == 0)
              and ([(.slash_commands // [])[], (.skills // [])[]
                    | tostring | select(test(":"))] | length == 0)' <<<"$init" >/dev/null; then
    echo "probe: user-level plugins, skills or MCP servers loaded ($ISOLATION)" >&2
    return 1
  fi
  answer=$(jq -r 'select(.type == "result") | .result // ""' "$log")
  if [[ -n $phrase && $answer == *"$phrase"* ]]; then
    echo "probe: the user's ~/.claude/CLAUDE.md is in the agent's context ($ISOLATION)" >&2
    return 1
  fi
  [[ -n $phrase ]] || echo "probe: no ~/.claude/CLAUDE.md canary; context check skipped" >&2
  return 0
}

run_probe() {
  probe && return 0
  [[ -n ${ANTHROPIC_API_KEY:-} ]] \
    || die "isolation probe leaked and --bare needs ANTHROPIC_API_KEY (it ignores the OAuth login)"
  ISOLATION=bare
  probe || die "isolation probe leaked even with --bare"
}

STEP=$(uv run rmf status "$RUN" --format json | jq -r '.next.step // "P"')

if [[ $DRY == 1 ]]; then
  session_argv "$(prompt_for "$STEP")" "$BUDGET"
  check_argv
  echo "work copy: $WORK (run $RUN; UV_PROJECT_ENVIRONMENT=$UV_PROJECT_ENVIRONMENT UV_NO_SYNC=1)"
  printf 'claude argv:'
  printf ' %q' "${ARGV[@]}"
  printf '\n'
  if [[ $PROBE == 1 ]]; then
    run_probe
    echo "isolation probe: ok (isolation: $ISOLATION)"
  else
    echo "isolation probe: skipped (--no-probe)"
  fi
  exit 0
fi

# --- 3. sessions -----------------------------------------------------------------------
run_probe
sessions=0
stalls=0
last=""
while :; do
  status=$(uv run rmf status "$RUN" --format json)
  [[ $(jq -r .done <<<"$status") == true ]] && break
  key=$(jq -c '[.counts.done, .ssp.statements, .sar.determinations]' <<<"$status")
  if [[ $sessions -gt 0 && $key == "$last" ]]; then
    stalls=$((stalls + 1))
  else
    stalls=0
  fi
  if [[ $stalls -ge 2 ]]; then
    echo "agent-run: two consecutive sessions made no progress; stopping" >&2
    break
  fi
  if [[ $sessions -ge $MAX_SESSIONS ]]; then
    echo "agent-run: AGENT_MAX_SESSIONS=$MAX_SESSIONS reached; stopping" >&2
    break
  fi
  last=$key
  STEP=$(jq -r .next.step <<<"$status")
  sessions=$((sessions + 1))
  echo "session $sessions: step $STEP (next $(jq -r .next.task <<<"$status"))"
  session_argv "$(prompt_for "$STEP")" "$BUDGET"
  check_argv
  "${ARGV[@]}" >"$LOGS/session-$sessions.jsonl" 2>"$LOGS/session-$sessions.err" || true
done

# --- 4. results ------------------------------------------------------------------------
uv run rmf build "$RUN" >/dev/null || true
uv run rmf check "$RUN" --final --format json >"$WORK/check.json" || true
rm -rf "$RESULTS"
mkdir -p "$RESULTS"
cp "$WORK/check.json" "$RESULTS/check.json"
cp -R "$RUN" "$RESULTS/run"
# The copied run sits four levels below the repo root instead of two.
product=$(sed -n 's/^product: //p' "$RUN/run.yaml")
sed -i.bak "s|^product: .*|product: ../../../../${product#../../}|" "$RESULTS/run/run.yaml"
rm -f "$RESULTS/run/run.yaml.bak"
check_sha=$(shasum -a 256 "$RESULTS/check.json" | cut -d' ' -f1)
model=$(cat "$LOGS"/session-*.jsonl 2>/dev/null \
  | jq -r 'select(.type == "system" and .subtype == "init") | .model' | tail -n 1)
cost=$(cat "$LOGS"/session-*.jsonl 2>/dev/null \
  | jq -s '[.[] | select(.type == "result") | .total_cost_usd // 0] | add // 0')
cat >"$RESULTS/meta.yaml" <<EOF
# Agent-lane provenance (plan §4.4); written by scripts/agent-run.sh. Self-attested.
scenario: $SCENARIO
run_id: $RUN_ID
claude_version: '$(claude --version | head -n 1)'
model: '${model:-unknown}'
date: '$(date -u +%Y-%m-%dT%H:%M:%SZ)'
session_count: $sessions
stalls: $stalls
budget_usd_per_session: $BUDGET
total_cost_usd: $cost
isolation: $ISOLATION
done: $(uv run rmf status "$RUN" --format json | jq .done)
errors: $(jq .summary.errors "$WORK/check.json")
warnings: $(jq .summary.warnings "$WORK/check.json")
upstream_hash: $(sed -n 's/^upstream_hash: //p' "$RUN/run.yaml" | tr -d "'")
check_sha256: $check_sha
self_attested: true
EOF
echo "results: $RESULTS (errors: $(jq .summary.errors "$RESULTS/check.json"), sessions: $sessions)"
