#!/bin/bash

# Config
OLLAMA_URL="http://localhost:9999/chat/ollama"
RUNNER_URL="http://localhost:9999/chat/runner"

PROMPTS=(
  "What is the capital of France?"
  "List three countries in Europe and their capitals."
  "Explain the process of photosynthesis in a few sentences."
  "Compare and contrast classical and quantum computing."
  "Write a short story involving a robot, a dragon, and time travel."
)

# To collect results
declare -a ollama_times
declare -a runner_times

# Util functions
get_time_ms() {
  if command -v gdate &>/dev/null; then
    gdate +%s%3N
  else
    date +%s%N
  fi
}

compute_elapsed() {
  local start=$1
  local end=$2
  if [[ "$end" =~ ^[0-9]{19}$ ]]; then
    echo $(( (end - start) / 1000000 ))
  else
    echo $((end - start))
  fi
}

call_and_time() {
  local url=$1
  local prompt=$2
  local label=$3

  local start=$(get_time_ms)
  local response=$(curl -s -X POST "$url" \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"$prompt\"}")
  local end=$(get_time_ms)

  local elapsed=$(compute_elapsed "$start" "$end")
  local preview=$(echo "$response" | tr '\n' ' ' | sed 's/  */ /g' | cut -c1-80)

  echo "$label took ${elapsed}ms"
  echo "Response: ${preview}..."
  echo

  eval "$4=$elapsed"
}

# Loop prompts and store timings
for i in "${!PROMPTS[@]}"; do
  prompt="${PROMPTS[$i]}"
  echo "Prompt $((i + 1)): \"$prompt\""
  echo "---------------------------------------------"

  call_and_time "$RUNNER_URL" "$prompt" "Docker Runner" runner_elapsed
  call_and_time "$OLLAMA_URL" "$prompt" "Ollama" ollama_elapsed

  ollama_times[$i]=$ollama_elapsed
  runner_times[$i]=$runner_elapsed
done

# Final comparison
echo
echo "Final Comparison Table"
printf "%-3s | %-60s | %-12s | %-12s\n" "#" "Prompt" "Ollama (ms)" "Runner (ms)"
echo "----|--------------------------------------------------------------|--------------|--------------"

for i in "${!PROMPTS[@]}"; do
  prompt="${PROMPTS[$i]}"
  printf "%-3s | %-60s | %-12s | %-12s\n" \
    "$((i + 1))" \
    "${prompt:0:60}" \
    "${ollama_times[$i]}" \
    "${runner_times[$i]}"
done
