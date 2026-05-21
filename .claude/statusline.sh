#!/usr/bin/env bash
# Claude Code statusline: content preview | tokens ↑↓ | 5h% resets | 7d% resets
# Save to ~/.claude/statusline.sh and chmod +x it
# Then in ~/.claude/settings.json:
#   { "statusLine": { "type": "command", "command": "~/.claude/statusline.sh" } }

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

# ── Read stdin ───────────────────────────────────────────────────────────────
INPUT=$(cat)

# ── Helper: color-code a percentage ─────────────────────────────────────────
pct_color() {
  local p
  p=$(printf '%.0f' "${1:-0}")
  if   (( p < 50 )); then printf '%s' "$GREEN"
  elif (( p < 70 )); then printf '%s' "$YELLOW"
  elif (( p < 90 )); then printf '%s' "$ORANGE"
  else printf '%s' "$RED"
  fi
}

# ── Helper: format resets_at (Unix epoch seconds) as "Xh Ym" from now ──────
resets_in() {
  local ts="$1"
  [[ -z "$ts" || "$ts" == "null" ]] && echo "--" && return

  # resets_at is a Unix epoch integer per the Claude Code JSON schema
  local epoch="$ts"

  local now
  now=$(date +%s)
  local diff=$(( epoch - now ))
  (( diff <= 0 )) && echo "now" && return

  local h=$(( diff / 3600 ))
  local m=$(( (diff % 3600) / 60 ))
  printf '%dh%02dm' "$h" "$m"
}

# ── Extract fields ────────────────────────────────────────────────────────────

# Model
MODEL=$(echo "$INPUT" | jq -r '.model.display_name // "Claude"')

# Last user message content (truncated to 45 chars)
CONTENT=$(echo "$INPUT" | jq -r '.content // ""' 2>/dev/null)
if [[ -z "$CONTENT" || "$CONTENT" == "null" ]]; then
  # Fallback: try transcript_path for last user turn
  TRANSCRIPT=$(echo "$INPUT" | jq -r '.transcript_path // ""')
  if [[ -n "$TRANSCRIPT" && -f "$TRANSCRIPT" ]]; then
    CONTENT=$(grep -o '"role":"user","content":"[^"]*' "$TRANSCRIPT" 2>/dev/null | \
              tail -1 | sed 's/.*"content":"//;s/\\n/ /g' | cut -c1-45)
  fi
fi
if [[ -n "$CONTENT" && "$CONTENT" != "null" ]]; then
  CONTENT=$(echo "$CONTENT" | cut -c1-45)
  [[ ${#CONTENT} -ge 45 ]] && CONTENT="${CONTENT}…"
else
  CONTENT=""
fi

# Context window
CTX_PCT=$(echo "$INPUT" | jq -r '.context_window.used_percentage // 0' | awk '{printf "%.0f", $1}')

# Token counters (current turn)
TOK_IN=$(echo "$INPUT"  | jq -r '.current_usage.input_tokens              // 0')
TOK_CACHE_CREATE=$(echo "$INPUT" | jq -r '.current_usage.cache_creation_input_tokens // 0')
TOK_CACHE_READ=$(echo  "$INPUT"  | jq -r '.current_usage.cache_read_input_tokens     // 0')
TOK_OUT=$(echo "$INPUT" | jq -r '.current_usage.output_tokens             // 0')

# Total session tokens
TOK_IN_TOTAL=$(echo  "$INPUT" | jq -r '.total_input_tokens  // 0')
TOK_OUT_TOTAL=$(echo "$INPUT" | jq -r '.total_output_tokens // 0')

# Rate limits (5h and 7d)
RL_5H_PCT=$(echo     "$INPUT" | jq -r '.rate_limits.five_hour.used_percentage // empty')
RL_5H_RESET=$(echo   "$INPUT" | jq -r '.rate_limits.five_hour.resets_at       // empty')
RL_7D_PCT=$(echo     "$INPUT" | jq -r '.rate_limits.seven_day.used_percentage // empty')
RL_7D_RESET=$(echo   "$INPUT" | jq -r '.rate_limits.seven_day.resets_at       // empty')

# ── Format numbers ─────────────────────────────────────────────────────────
fmt_k() {
  local n="${1:-0}"
  if (( n >= 1000 )); then
    awk "BEGIN{printf \"%.1fk\", $n/1000}"
  else
    echo "$n"
  fi
}

# ── Build output ─────────────────────────────────────────────────────────────
SEP="${GRAY} │ ${RESET}"

# 1. Model
OUT="${BOLD}${CYAN}${MODEL}${RESET}"

# 2. Content preview
if [[ -n "$CONTENT" ]]; then
  OUT+="${SEP}${GRAY}\"${CONTENT}\"${RESET}"
fi

# 3. Context bar + %
CTX_COLOR=$(pct_color "$CTX_PCT")
BAR_FILLED=$(( CTX_PCT / 10 ))
BAR=""
for (( i=0; i<10; i++ )); do
  (( i < BAR_FILLED )) && BAR+="▓" || BAR+="░"
done
OUT+="${SEP}${CTX_COLOR}${BAR} ${CTX_PCT}%${RESET}"

# 4. Tokens ↑ (in) / ↓ (out) — current turn, skip zeros
IN_TOT=$(( TOK_IN + TOK_CACHE_CREATE + TOK_CACHE_READ ))
if (( IN_TOT > 0 || TOK_OUT > 0 )); then
  OUT+="${SEP}${BLUE}↑$(fmt_k "$IN_TOT")${RESET} ${GRAY}↓$(fmt_k "$TOK_OUT")${RESET}"
fi

# 5. Session totals (if available and non-zero)
if (( TOK_IN_TOTAL > 0 )); then
  OUT+="${SEP}${GRAY}sess ↑$(fmt_k "$TOK_IN_TOTAL") ↓$(fmt_k "$TOK_OUT_TOTAL")${RESET}"
fi

# 6. 5h rate limit — bar + % + countdown (or just countdown when no %)
if [[ -n "$RL_5H_RESET" ]]; then
  RESET_IN=$(resets_in "$RL_5H_RESET")
  if [[ -n "$RL_5H_PCT" ]]; then
    RL5_INT=$(echo "$RL_5H_PCT" | awk '{printf "%.0f", $1}')
    C=$(pct_color "$RL5_INT")
    RL5_FILLED=$(( RL5_INT / 10 ))
    RL5_BAR=""
    for (( i=0; i<10; i++ )); do
      (( i < RL5_FILLED )) && RL5_BAR+="▓" || RL5_BAR+="░"
    done
    OUT+="${SEP}${GRAY}5h ${RESET}${C}${RL5_BAR} ${RL5_INT}% ↺${RESET_IN}${RESET}"
  else
    OUT+="${SEP}${GRAY}5h ↺${RESET_IN}${RESET}"
  fi
else
  OUT+="${SEP}${GRAY}5h --${RESET}"
fi

# 7. 7d rate limit — bar + % + countdown (or just countdown when no %)
if [[ -n "$RL_7D_RESET" ]]; then
  RESET_IN=$(resets_in "$RL_7D_RESET")
  if [[ -n "$RL_7D_PCT" ]]; then
    RL7_INT=$(echo "$RL_7D_PCT" | awk '{printf "%.0f", $1}')
    C=$(pct_color "$RL7_INT")
    RL7_FILLED=$(( RL7_INT / 10 ))
    RL7_BAR=""
    for (( i=0; i<10; i++ )); do
      (( i < RL7_FILLED )) && RL7_BAR+="▓" || RL7_BAR+="░"
    done
    OUT+="${SEP}${GRAY}7d ${RESET}${C}${RL7_BAR} ${RL7_INT}% ↺${RESET_IN}${RESET}"
  else
    OUT+="${SEP}${GRAY}7d ↺${RESET_IN}${RESET}"
  fi
else
  OUT+="${SEP}${GRAY}7d --${RESET}"
fi

printf '%b\n' "$OUT"
