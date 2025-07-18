<!-- @format -->

# Clean Bible Processing Pipeline

This directory contains a clean, organized, and reproducible pipeline for processing Bible translation JSON files into Parquet format. The pipeline includes validation, flexible handling of known verse/chapter variations, and robust reporting.

## Directory Structure

- `json_data/`: Contains all cleaned JSON Bible translation files.
- `parquet_output/`: Contains all Parquet output files.
- `scripts/`: Contains all processing and validation scripts.
- `utils/`: Contains utility scripts for validation and processing.
- `constants/`: Contains mappings and constants used across the pipeline.

## Usage

1. Place cleaned JSON files in the `json_data/` directory.
2. Run the validation and processing scripts from the `scripts/` directory.
3. Parquet outputs will be saved in the `parquet_output/` directory.

## Scripts

- `validate_bible.py`: Validates JSON files for structural and content accuracy.
- `bible_processor.py`: Processes JSON files into Parquet format.

## Notes

- Known verse/chapter variations are documented and handled using the `KNOWN_VARIATIONS` mapping in the `constants/` directory.
- Ensure Python 3.12+ is installed for compatibility with modernized scripts.
