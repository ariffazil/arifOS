#!/usr/bin/env bash
# arifOS 60-second governance demo — runner.
#
# Picks an interpreter that can import the repo's own kernel, scrubs the
# notifier credentials so a HOLD verdict cannot page a human, then runs demo.py.
#
#   ./run.sh                       # normal run
#   ./run.sh | tee TRANSCRIPT.txt  # capture a transcript
#   ARIFOS_PYTHON=/path/to/python ./run.sh
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"

candidates=()
[ -n "${ARIFOS_PYTHON:-}" ] && candidates+=("$ARIFOS_PYTHON")
candidates+=("$REPO/.venv/bin/python" "python3" "/usr/bin/python3")

PY=""
for candidate in "${candidates[@]}"; do
  if [ -x "$candidate" ] || command -v "$candidate" >/dev/null 2>&1; then
    if "$candidate" -c "import sys; sys.path.insert(0, '$REPO'); import arifosmcp" >/dev/null 2>&1; then
      PY="$candidate"
      break
    fi
  fi
done

if [ -z "$PY" ]; then
  echo "ERROR: no interpreter on this host can import 'arifosmcp' from $REPO" >&2
  echo "       set one explicitly:  ARIFOS_PYTHON=/path/to/python $0" >&2
  echo "       candidates tried: ${candidates[*]}" >&2
  exit 2
fi

exec env -u NOTIFIER_TELEGRAM_BOT_TOKEN -u NOTIFIER_TELEGRAM_CHAT_ID \
  "$PY" "$HERE/demo.py" "$@"
