#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -m isa_c_mapping.cli artifacts/gs1_product_with_sustainability_data.json -o out/isa_c.json
