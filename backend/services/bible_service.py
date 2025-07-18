import pyarrow.parquet as pq
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional
from loguru import logger


class BibleService:
    def __init__(self, parquet_dir: str):
        self.parquet_dir = Path(parquet_dir)
        self.bibles: Dict[str, pd.DataFrame] = self._load_bibles()

    def _load_bibles(self) -> Dict[str, pd.DataFrame]:
        bibles = {}
        logger.info(f"Loading Bible translations from: {self.parquet_dir}")
        if not self.parquet_dir.is_dir():
            logger.error(f"Parquet directory not found at: {self.parquet_dir}")
            return bibles

        for file_path in self.parquet_dir.glob("*.parquet"):
            try:
                # Extract the abbreviation (e.g., KJV, ESV) from the filename
                translation = file_path.stem.split("_")[-1]
                if translation in bibles:
                    logger.warning(
                        f"Duplicate translation key '{translation}' found. "
                        f"Skipping file: {file_path.name}"
                    )
                    continue

                bibles[translation] = pq.read_table(file_path).to_pandas()
                logger.success(
                    f"Successfully loaded '{translation}' from {file_path.name}"
                )
            except Exception as e:
                logger.error(f"Failed to load {file_path.name}: {e}")

        if not bibles:
            logger.warning("No Bible translation files were loaded.")

        return bibles

    def get_translations(self) -> List[str]:
        return list(self.bibles.keys())

    def get_books(self, translation: str) -> Optional[List[str]]:
        if translation in self.bibles:
            return self.bibles[translation]["book"].unique().tolist()
        return None

    def get_chapters(self, translation: str, book: str) -> Optional[List[int]]:
        if translation in self.bibles:
            df = self.bibles[translation]
            return df[df["book"] == book]["chapter"].unique().tolist()
        return None

    def get_verses(self, translation: str, book: str, chapter: int) -> Optional[Dict]:
        if translation in self.bibles:
            df = self.bibles[translation]
            verses_df = df[(df["book"] == book) & (df["chapter"] == chapter)]
            return verses_df.to_dict("records")
        return None

    def search(self, translation: str, query: str) -> Optional[List[Dict]]:
        if translation in self.bibles:
            df = self.bibles[translation]
            results_df = df[df["text"].str.contains(query, case=False)]
            return results_df.to_dict("records")
        return None


# Example usage:
if __name__ == "__main__":
    bible_service = BibleService(parquet_dir="KoinoniaHouse/db/bibles/parquet/")
    print("Available translations:", bible_service.get_translations())
    print("Books in KJV:", bible_service.get_books("KJV"))
