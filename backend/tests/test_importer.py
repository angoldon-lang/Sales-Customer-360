import pytest
from app.core.importer import CompanyImporter, CompanyImportError
import io
import pandas as pd


def test_import_csv_basic():
    """Test CSV import with minimal data."""
    csv_content = b"""company_name,vat_number,cluster
Test Corp,IT12345678,Direzione
Test Inc,,Sales
"""
    data = CompanyImporter.import_from_csv(csv_content)
    assert len(data) == 2
    assert data[0]["company_name"] == "Test Corp"
    assert data[0]["vat_number"] == "IT12345678"
    assert data[0]["cluster"] == "Direzione"
    assert data[1]["cluster"] == "Sales"


def test_import_csv_missing_company_name():
    """Test that missing company_name raises error."""
    csv_content = b"""name,vat_number
Test Corp,IT12345678
"""
    with pytest.raises(CompanyImportError):
        CompanyImporter.import_from_csv(csv_content)


def test_import_csv_empty_vat():
    """Test that empty vat_number becomes None or NaN."""
    csv_content = b"""company_name,vat_number
Test Corp,
"""
    data = CompanyImporter.import_from_csv(csv_content)
    assert len(data) == 1
    # pandas might return NaN for empty cells
    vat = data[0]["vat_number"]
    assert vat is None or (isinstance(vat, float) and pd.isna(vat))


def test_import_csv_default_cluster():
    """Test that missing cluster becomes Default."""
    csv_content = b"""company_name,vat_number,cluster
Test Corp,IT12345678,
"""
    data = CompanyImporter.import_from_csv(csv_content)
    assert len(data) == 1
    assert data[0]["cluster"] == "Default"


def test_import_csv_multiple_clusters():
    """Test multiple clusters separated by comma."""
    csv_content = b"""company_name,vat_number,cluster
Test Corp,IT12345678,"Direzione, Sales Nord"
"""
    data = CompanyImporter.import_from_csv(csv_content)
    assert len(data) == 1
    assert data[0]["cluster"] == "Direzione, Sales Nord"


def test_import_csv_normalize_whitespace():
    """Test that whitespace is normalized."""
    csv_content = b"""company_name,vat_number,cluster
  Test Corp  ,  IT12345678  ,  Direzione
"""
    data = CompanyImporter.import_from_csv(csv_content)
    assert len(data) == 1
    assert data[0]["company_name"] == "Test Corp"
    assert data[0]["vat_number"] == "IT12345678"
    assert data[0]["cluster"] == "Direzione"
