#!/usr/bin/env bash

cd "$(dirname "$0")"

# Sorting is locale-dependent, so force sort to use a locale that's always
# available for consistency.
export LC_ALL=C

all_sorted="true"

for file in "whitelist.txt" flake8_spellcheck/*.txt; do
  if [[ "$(sort < "$file")" != "$(<"$file")" ]]; then
    echo "$file is not sorted correctly" >&2
    all_sorted="false"
  fi
done

if [[ "$all_sorted" == "false" ]]; then
  exit 1
fi
