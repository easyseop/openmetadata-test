#!/usr/bin/env bash
set -u

usage() {
  cat <<'EOF'
Usage: bash harness/registrations/kb-openmetadata/reconstruct_remaining_ids.sh

Prerequisites:
  1. Run from the verifier repository after: source harness/rehearsal_env.sh
  2. BANK-OM-001 must already be committed.
  3. Normally $OM_CODE_REPO is clean. If the previous run stopped after staging
     the next ID, rerunning this command resumes from that staged review.

The script applies BANK-OM-002 through BANK-OM-007 one at a time. For every ID it:
  - reconstructs the code,
  - stages all changes,
  - displays the commit candidate diff,
  - commits only after the operator types the exact BANK-OM ID.
EOF
}

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  usage
  exit 0
fi

if [[ -z "${OM_TEST_REPO:-}" || -z "${OM_CODE_REPO:-}" ]]; then
  echo "STOP: OM_TEST_REPO or OM_CODE_REPO is not set."
  echo "Run: source harness/rehearsal_env.sh"
  exit 2
fi

if [[ ! -d "${OM_CODE_REPO}/.git" && ! -f "${OM_CODE_REPO}/.git" ]]; then
  echo "STOP: OM_CODE_REPO is not a Git working tree: ${OM_CODE_REPO}"
  exit 2
fi

items=(
  "BANK-OM-002|restore QueryReport customization"
  "BANK-OM-003|restore Data Assertions customization"
  "BANK-OM-004|restore bank column display customization"
  "BANK-OM-005|restore Korean IME customization"
  "BANK-OM-006|restore Sybase customization"
  "BANK-OM-007|restore Tibero customization"
)

latest_id="$(git -C "${OM_CODE_REPO}" log --format='%(trailers:key=Customization-ID,valueonly)' -n 1)"
case "${latest_id}" in
  BANK-OM-001) start_index=0 ;;
  BANK-OM-002) start_index=1 ;;
  BANK-OM-003) start_index=2 ;;
  BANK-OM-004) start_index=3 ;;
  BANK-OM-005) start_index=4 ;;
  BANK-OM-006) start_index=5 ;;
  BANK-OM-007)
    echo "COMPLETE: the latest commit is already BANK-OM-007."
    exit 0
    ;;
  *)
    echo "STOP: the latest commit does not contain BANK-OM-001 through BANK-OM-007."
    echo "Latest Customization-ID: ${latest_id:-<missing>}"
    exit 2
    ;;
esac

resume_staged=0
if [[ -n "$(git -C "${OM_CODE_REPO}" status --porcelain)" ]]; then
  if git -C "${OM_CODE_REPO}" diff --cached --quiet; then
    echo "STOP: uncommitted files exist, but no staged ID candidate was found."
    git -C "${OM_CODE_REPO}" status --short
    exit 2
  fi
  if ! git -C "${OM_CODE_REPO}" diff --quiet; then
    echo "STOP: staged and unstaged changes are mixed. Review them manually."
    git -C "${OM_CODE_REPO}" status --short
    exit 2
  fi
  if git -C "${OM_CODE_REPO}" status --porcelain | grep -q '^??'; then
    echo "STOP: untracked files exist outside the staged candidate."
    git -C "${OM_CODE_REPO}" status --short
    exit 2
  fi
  resume_staged=1
  echo "RESUME: staged changes for the ID after ${latest_id} were found."
  echo "The script will review them without applying the same ID again."
fi

cd "${OM_TEST_REPO}" || exit 2

index=${start_index}
while [[ ${index} -lt ${#items[@]} ]]; do
  item="${items[${index}]}"
  id="${item%%|*}"
  title="${item#*|}"

  echo
  echo "============================================================"
  echo "Processing ${id}: ${title}"
  echo "============================================================"

  using_staged=0
  if [[ ${resume_staged} -eq 1 ]]; then
    echo "Using the staged ${id} candidate left by the previous run."
    using_staged=1
    resume_staged=0
  else
    PYTHONPATH=harness ./.venv/bin/python \
      harness/registrations/kb-openmetadata/reconstruct_series.py \
      --product "${OM_CODE_REPO}" \
      --snapshot "${OM_CODE_REPO}-snapshot" \
      --harness harness \
      --registration harness/registrations/kb-openmetadata \
      --id "${id}" || exit 3
  fi

  echo
  echo "[1/4] Changed files. Confirm that every path belongs to ${id}."
  git -C "${OM_CODE_REPO}" status --short || exit 3

  if [[ -z "$(git -C "${OM_CODE_REPO}" status --porcelain)" ]]; then
    echo "STOP: ${id} produced no changes."
    exit 3
  fi

  if [[ ${using_staged} -eq 0 ]]; then
    git -C "${OM_CODE_REPO}" add -A || exit 3
  fi

  echo
  echo "[2/4] Commit candidate files. M=modified, A=new file."
  git -C "${OM_CODE_REPO}" diff --cached --name-status || exit 3

  echo
  echo "[3/4] Commit candidate size. Stop on unexplained large deletions."
  git -C "${OM_CODE_REPO}" diff --cached --stat || exit 3

  echo
  echo "[4/4] Full commit candidate code. If a pager opens, press q after review."
  # Run the pager explicitly. Quitting `less` with q is a normal review action;
  # it must not propagate Git's SIGPIPE status and terminate before approval.
  git -C "${OM_CODE_REPO}" --no-pager diff --cached --color=always | less -R
  pager_status=$?
  if [[ ${pager_status} -ne 0 ]]; then
    echo "STOP: the diff viewer failed with exit code ${pager_status}."
    exit 3
  fi

  echo
  printf "Commit only if the code above belongs to %s. Type the exact ID to approve: " "${id}"
  IFS= read -r approval
  if [[ "${approval}" != "${id}" ]]; then
    echo "STOP: approval did not match ${id}. No commit was created."
    echo "The staged changes are preserved for inspection."
    exit 4
  fi

  git -C "${OM_CODE_REPO}" commit \
    -m "${title}" \
    -m "Customization-ID: ${id}" || exit 3

  recorded_id="$(git -C "${OM_CODE_REPO}" log --format='%(trailers:key=Customization-ID,valueonly)' -n 1)"
  if [[ "${recorded_id}" != "${id}" ]]; then
    echo "STOP: the new commit does not contain the expected Customization-ID."
    echo "Expected: ${id}"
    echo "Recorded: ${recorded_id:-<missing>}"
    exit 5
  fi

  if [[ -n "$(git -C "${OM_CODE_REPO}" status --porcelain)" ]]; then
    echo "STOP: uncommitted files remain after committing ${id}."
    git -C "${OM_CODE_REPO}" status --short
    exit 5
  fi

  echo "OK: ${id} was committed and the working tree is clean."
  index=$((index + 1))
done

echo
echo "COMPLETE: BANK-OM-002 through BANK-OM-007 were reviewed and committed."
echo "Next: run the chapter 7 candidate-branch checks."
