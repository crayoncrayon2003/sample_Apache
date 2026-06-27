#!/bin/bash
# Remove only generated files; keep git-managed source (data.csv, *.hpl, metadata/).
cd "$(dirname "$0")"

# Pipeline run artifacts inside the (tracked) project folder
sudo rm -f hop_projects/duckdb.db hop_projects/*_output.json

# Runtime-only mount dir (created by 00_mkdir.sh, nothing tracked)
sudo rm -rf hop_files
