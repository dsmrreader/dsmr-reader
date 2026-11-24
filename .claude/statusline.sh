#!/usr/bin/env bash
# Claude Code statusline: model | last prompt | context bar | tokens ↑↓ | 5h limit | 7d limit
# Configured as the `statusLine` command in ~/.claude/settings.json.
# Input: the JSON document Claude Code writes to stdin (https://code.claude.com/docs/en/statusline).

# ── Colors (ANSI 256-color) ──────────────────────────────────────────────────
RESET="\033[0m"
GRAY="\033[38;5;245m"
GREEN="\033[38;5;77m"
YELLOW="\033[38;5;220m"
ORANGE="\033[38;5;208m"
RED="\033[38;5;196m"
CYAN="\033[38;5;81m"
BLUE="\033[38;5;75m"
BOLD="\033[1m"

PREVIEW_CHARS=45
ABSENT="-"

# ── Extract all fields with a single jq call (tab separated, session name last) ──
INPUT=$(cat)
PARSED=$(
  jq -r --arg absent "$ABSENT" '[
    (.model.display_name // "Claude"),
    ((.context_window.used_percentage // 0) | round),
    (.context_window.current_usage.input_tokens // 0),
    (.context_window.current_usage.cache_creation_input_tokens // 0),
    (.context_window.current_usage.cache_read_input_tokens // 0),
    (.context_window.current_usage.output_tokens // 0),
    (.context_window.total_input_tokens // 0),
    (.context_window.total_output_tokens // 0),
    (.rate_limits.five_hour.used_percentage // $absent),
    (.rate_limits.five_hour.resets_at // $absent),
    (.rate_limits.seven_day.used_percentage // $absent),
    (.rate_limits.seven_day.resets_at // $absent),
    (.transcript_path // $absent),
    (.session_name // $absent)
  ] | map(tostring) | join("\t")' <<<"$INPUT" 2>/dev/null
)
if [[ -z "$PARSED" ]]; then
  printf '%b\n' "${BOLD}${CYAN}Claude${RESET}"
  exit 0
fi
IFS=$'\t' read -r MODEL CTX_PCT TOK_IN TOK_CACHE_CREATE TOK_CACHE_READ TOK_OUT TOK_IN_TOTAL TOK_OUT_TOTAL \
  RL_5H_PCT RL_5H_RESET RL_7D_PCT RL_7D_RESET TRANSCRIPT SESSION_NAME <<<"$PARSED"

# ── Helpers ──────────────────────────────────────────────────────────────────
# Color for a percentage.
pct_color() {
  local p
  p=$(printf '%.0f' "${1:-0}")
  if   (( p < 50 )); then printf '%s' "$GREEN"
  elif (( p < 70 )); then printf '%s' "$YELLOW"
  elif (( p < 90 )); then printf '%s' "$ORANGE"
  else printf '%s' "$RED"
  fi
}

# 10-cell bar for a percentage.
bar() {
  local filled=$(( ${1:-0} / 10 )) out="" i
  (( filled > 10 )) && filled=10
  for (( i=0; i<10; i++ )); do
    (( i < filled )) && out+="▓" || out+="░"
  done
  printf '%s' "$out"
}

# Time until a Unix epoch timestamp as "XhYYm".
resets_in() {
  local diff=$(( $1 - $(date +%s) ))
  (( diff <= 0 )) && { printf 'now'; return; }
  printf '%dh%02dm' $(( diff / 3600 )) $(( (diff % 3600) / 60 ))
}

# Thousands with one decimal: 1234 -> 1.2k
fmt_k() {
  local n="${1:-0}"
  if (( n >= 1000 )); then
    awk -v n="$n" 'BEGIN{printf "%.1fk", n/1000}'
  else
    printf '%s' "$n"
  fi
}

# One rate-limit segment: label, used percentage, reset epoch.
rate_limit() {
  local label="$1" pct="$2" reset="$3" int color
  if [[ "$reset" == "$ABSENT" ]]; then
    printf '%s%s --%s' "$GRAY" "$label" "$RESET"
  elif [[ "$pct" == "$ABSENT" ]]; then
    printf '%s%s ↺%s%s' "$GRAY" "$label" "$(resets_in "$reset")" "$RESET"
  else
    int=$(printf '%.0f' "$pct")
    color=$(pct_color "$int")
    printf '%s%s %s%s %s %s%% ↺%s%s' "$GRAY" "$label" "$RESET" "$color" "$(bar "$int")" "$int" "$(resets_in "$reset")" "$RESET"
  fi
}

# Last typed user prompt of the session (the stdin document carries no prompt text).
# Reads only the tail of the transcript. Entries whose content is a tag (commands, reminders) are skipped.
last_prompt() {
  local transcript="$1"
  [[ "$transcript" != "$ABSENT" && -f "$transcript" ]] || return 0
  tail -n 300 "$transcript" 2>/dev/null | jq -Rr '
    fromjson?
    | select(.type == "user" and ((.message.content | type) == "string"))
    | .message.content
    | select(startswith("<") | not)
    | gsub("\\s+"; " ")' 2>/dev/null | tail -n 1
}

# ── Build output ─────────────────────────────────────────────────────────────
SEP="${GRAY} │ ${RESET}"

# 1. Model
OUT="${BOLD}${CYAN}${MODEL}${RESET}"

# 2. Last prompt preview, falling back to the session name
CONTENT=$(last_prompt "$TRANSCRIPT")
[[ -z "$CONTENT" && "$SESSION_NAME" != "$ABSENT" ]] && CONTENT="$SESSION_NAME"
if [[ -n "$CONTENT" ]]; then
  if (( ${#CONTENT} > PREVIEW_CHARS )); then
    CONTENT="${CONTENT:0:PREVIEW_CHARS}…"
  fi
  OUT+="${SEP}${GRAY}\"${CONTENT}\"${RESET}"
fi

# 3. Context bar + %
OUT+="${SEP}$(pct_color "$CTX_PCT")$(bar "$CTX_PCT") ${CTX_PCT}%${RESET}"

# 4. Tokens ↑ (in, including cache) / ↓ (out) of the latest API response
IN_TOT=$(( TOK_IN + TOK_CACHE_CREATE + TOK_CACHE_READ ))
if (( IN_TOT > 0 || TOK_OUT > 0 )); then
  OUT+="${SEP}${BLUE}↑$(fmt_k "$IN_TOT")${RESET} ${GRAY}↓$(fmt_k "$TOK_OUT")${RESET}"
fi

# 5. Totals reported by Claude Code (context_window.total_*_tokens)
if (( TOK_IN_TOTAL > 0 )); then
  OUT+="${SEP}${GRAY}tot ↑$(fmt_k "$TOK_IN_TOTAL") ↓$(fmt_k "$TOK_OUT_TOTAL")${RESET}"
fi

# 6/7. Rate limits (only present for subscribers, after the first API response)
OUT+="${SEP}$(rate_limit 5h "$RL_5H_PCT" "$RL_5H_RESET")"
OUT+="${SEP}$(rate_limit 7d "$RL_7D_PCT" "$RL_7D_RESET")"

printf '%b\n' "$OUT"
