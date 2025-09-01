# ISA-C Mapping (Minimal CLI)

Purpose: map a GS1-like product JSON (see `artifacts/gs1_product_with_sustainability_data.json`) to a normalized ISA_C JSON.

## Usage
```bash
python -m isa_c_mapping.cli artifacts/gs1_product_with_sustainability_data.json -o out/isa_c.json
```

Outputs `out/isa_c.json`.
