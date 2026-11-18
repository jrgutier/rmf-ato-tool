#!/usr/bin/env bash
# Idempotent toolchain setup for rmf-tool. Safe to re-run; every step checks first.
#
#   scripts/bootstrap.sh              base tools + venv (no AGPL, no OCR)
#   EXTRACT=1 scripts/bootstrap.sh    also the [extract] extra (PyMuPDF, AGPL; see NOTICE)
#   OCR=1 scripts/bootstrap.sh        also ocrmypdf + tesseract
#   OSCAL_CLI=1 scripts/bootstrap.sh  also NIST oscal-cli into .tools/ (OSCAL-003; needs Java 11+)
set -euo pipefail

cd "$(dirname "$0")/.."

log() { printf '==> %s\n' "$*"; }
have() { command -v "$1" >/dev/null 2>&1; }

os="$(uname -s)"

brew_install() {  # brew_install <command> <formula>
  if have "$1"; then return; fi
  log "brew install $2"
  brew install "$2"
}

apt_missing=()
apt_want() {  # apt_want <command> <package>
  if ! have "$1"; then apt_missing+=("$2"); fi
}
apt_flush() {
  if [ "${#apt_missing[@]}" -eq 0 ]; then return; fi
  log "apt-get install ${apt_missing[*]}"
  sudo apt-get update
  sudo apt-get install -y "${apt_missing[@]}"
  apt_missing=()
}

case "$os" in
  Darwin)
    if ! have brew; then
      echo "Homebrew is required on macOS: https://brew.sh" >&2
      exit 2
    fi
    brew_install uv uv
    brew_install jq jq
    brew_install qpdf qpdf
    brew_install git-lfs git-lfs
    if [ "${OCR:-0}" = "1" ]; then
      brew_install ocrmypdf ocrmypdf
      brew_install tesseract tesseract
    fi
    ;;
  Linux)
    apt_want jq jq
    apt_want qpdf qpdf
    apt_want git-lfs git-lfs
    if [ "${OCR:-0}" = "1" ]; then
      apt_want ocrmypdf ocrmypdf
      apt_want tesseract tesseract-ocr
    fi
    apt_flush
    if ! have uv; then
      log "installing uv"
      curl -LsSf https://astral.sh/uv/install.sh | sh
      export PATH="$HOME/.local/bin:$PATH"
    fi
    ;;
  *)
    echo "unsupported OS: $os (install uv, jq, qpdf and git-lfs manually)" >&2
    exit 2
    ;;
esac

log "git lfs install --local"
git lfs install --local >/dev/null

log "uv python install 3.12"
uv python install 3.12

sync_args=(--group dev)
if [ "${EXTRACT:-0}" = "1" ]; then
  sync_args+=(--extra extract)
fi
if [ -n "${CI:-}" ]; then
  sync_args+=(--locked)
fi
log "uv sync ${sync_args[*]}"
uv sync "${sync_args[@]}"

# NIST oscal-cli for OSCAL-003, pinned by version and SHA-256 (Maven Central). Optional.
OSCAL_CLI_VERSION=3.2.0
OSCAL_CLI_SHA256=e001b353ee245da6f4ff0ad930c4dfaa88083c63243ca004bd5f5bcef44e8ec8
if [ "${OSCAL_CLI:-0}" = "1" ] && [ ! -x .tools/oscal-cli/bin/oscal-cli ]; then
  if ! have java; then
    echo "OSCAL_CLI=1 needs Java 11 or later on PATH" >&2
    exit 2
  fi
  zip="oscal-cli-enhanced-${OSCAL_CLI_VERSION}-oscal-cli.zip"
  url="https://repo1.maven.org/maven2/dev/metaschema/oscal/oscal-cli-enhanced/${OSCAL_CLI_VERSION}/${zip}"
  log "oscal-cli ${OSCAL_CLI_VERSION} into .tools/oscal-cli"
  mkdir -p .tools
  curl -fsSL -o ".tools/${zip}" "$url"
  echo "${OSCAL_CLI_SHA256}  .tools/${zip}" | sha256sum -c - >/dev/null 2>&1 \
    || shasum -a 256 -c <<<"${OSCAL_CLI_SHA256}  .tools/${zip}" >/dev/null
  rm -rf .tools/oscal-cli && unzip -q ".tools/${zip}" -d .tools/oscal-cli && rm ".tools/${zip}"
fi

log "rmf doctor"
uv run rmf doctor
