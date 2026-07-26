#!/bin/sh
set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
root_dir=$(CDPATH= cd -- "$script_dir/.." && pwd)

exec python3 "$script_dir/validate.py" "$root_dir"
