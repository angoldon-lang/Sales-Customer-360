import pandas as pd
from typing import List, Dict, Any
import io


class CompanyImportError(Exception):
    pass


class CompanyImporter:
    """Import companies from CSV or Excel files."""

    @staticmethod
    def import_from_csv(content: bytes) -> List[Dict[str, Any]]:
        """Parse CSV content and return list of company dicts."""
        try:
            df = pd.read_csv(io.BytesIO(content))
            return CompanyImporter._validate_and_normalize(df)
        except Exception as e:
            raise CompanyImportError(f"Failed to parse CSV: {str(e)}")

    @staticmethod
    def import_from_excel(content: bytes) -> List[Dict[str, Any]]:
        """Parse Excel content and return list of company dicts."""
        try:
            df = pd.read_excel(io.BytesIO(content))
            return CompanyImporter._validate_and_normalize(df)
        except Exception as e:
            raise CompanyImportError(f"Failed to parse Excel: {str(e)}")

    @staticmethod
    def _validate_and_normalize(df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Validate and normalize DataFrame."""
        required_cols = {"company_name"}
        optional_cols = {"vat_number", "cluster"}

        actual_cols = set(df.columns)

        # Normalize column names to lowercase
        df.columns = df.columns.str.lower()
        actual_cols = set(df.columns)

        if not required_cols.issubset(actual_cols):
            missing = required_cols - actual_cols
            raise CompanyImportError(f"Missing required columns: {missing}")

        # Filter to only expected columns
        expected_cols = required_cols | optional_cols
        df = df[[col for col in expected_cols if col in actual_cols]]

        # Remove rows where company_name is empty
        df = df[df["company_name"].notna() & (df["company_name"] != "")]

        # Normalize data
        df = df.fillna("")
        df["company_name"] = df["company_name"].str.strip()
        if "vat_number" in df.columns:
            df["vat_number"] = df["vat_number"].astype(str).str.strip()
            df.loc[df["vat_number"] == "", "vat_number"] = None
        if "cluster" in df.columns:
            df["cluster"] = df["cluster"].astype(str).str.strip()
            df.loc[df["cluster"] == "", "cluster"] = "Default"

        return df.to_dict("records")
