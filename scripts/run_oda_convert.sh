#!/usr/bin/env zsh

# Usage:
#   scripts/run_oda_convert.sh input.dxf output_dir
# Converts DXF to ACAD 2018 using ODAFileConverter if available.

set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <input_dxf> <output_dir>" >&2
  exit 2
fi

INPUT="$1"
OUTDIR="$2"

if [[ ! -f "$INPUT" ]]; then
  echo "Input file not found: $INPUT" >&2
  exit 2
fi

mkdir -p "$OUTDIR"

# Try common locations for ODAFileConverter
ODA_BIN="$(command -v ODAFileConverter || true)"
if [[ -z "$ODA_BIN" ]]; then
  for p in \
    "/Applications/ODAFileConverter.app/Contents/MacOS/ODAFileConverter" \
    "/Applications/TeighaFileConverter.app/Contents/MacOS/TeighaFileConverter" \
    "$HOME/Applications/ODAFileConverter.app/Contents/MacOS/ODAFileConverter"; do
    if [[ -x "$p" ]]; then
      ODA_BIN="$p"
      break
    fi
  done
fi

if [[ -z "$ODA_BIN" ]]; then
  echo "ODAFileConverter CLI not found. Install ODA File Converter and ensure the CLI is available." >&2
  echo "Expected app path: /Applications/ODAFileConverter.app" >&2
  exit 127
fi

echo "Using ODAFileConverter: $ODA_BIN"

# ODA expects directory inputs; copy to temp dir for conversion
WORKDIR="$(mktemp -d)"
cp "$INPUT" "$WORKDIR"/

# Parameters:
#   inDir outDir inType outType recurse [Index|Off] [Audit|NoAudit] [Older|Newer]
# Common example: DXF -> DXF R2018 (ACAD 2018)

"$ODA_BIN" "$WORKDIR" "$OUTDIR" DXF DXF 0 Index Audit Newer || {
  echo "Conversion failed." >&2
  rm -rf "$WORKDIR"
  exit 1
}

rm -rf "$WORKDIR"
echo "Conversion complete. Outputs in: $OUTDIR"
