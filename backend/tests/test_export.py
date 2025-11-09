"""Tests for export functionality (PDF, Excel, CSV)."""
import requests
import os
from datetime import date, timedelta

BASE_URL = "http://127.0.0.1:8777/api"


def _check_file_exists(file_path):
    """Check if file exists, handling both absolute and relative paths."""
    if os.path.isabs(file_path):
        return os.path.exists(file_path)

    # Try relative to current directory
    if os.path.exists(file_path):
        return True

    # Try relative to backend directory
    backend_path = os.path.join('backend', file_path)
    if os.path.exists(backend_path):
        return True

    # Try in root exports directory
    root_path = os.path.join('exports', os.path.basename(file_path))
    if os.path.exists(root_path):
        return True

    return False


def test_export_transactions_pdf():
    """Test exporting transactions to PDF."""
    print("\n=== Test: Export Transactions to PDF ===")

    response = requests.post(f"{BASE_URL}/export/transactions/pdf")
    assert response.status_code == 200, f"Failed: {response.text}"

    result = response.json()
    assert 'filename' in result, "Missing filename"
    assert 'file_path' in result, "Missing file_path"
    assert 'file_size' in result, "Missing file_size"
    assert result['format'] == 'pdf', "Wrong format"
    assert result['export_type'] == 'transactions', "Wrong export type"

    # Verify file exists
    assert _check_file_exists(result['file_path']), f"File not created: {result['file_path']}"
    assert result['file_size'] > 0, "File is empty"

    print(f"✓ Exported transactions to PDF: {result['filename']} ({result['file_size']} bytes)")

    return result


def test_export_transactions_pdf_with_filters():
    """Test exporting transactions to PDF with date filters."""
    print("\n=== Test: Export Transactions to PDF with Filters ===")

    end_date = date.today()
    start_date = end_date - timedelta(days=30)

    response = requests.post(
        f"{BASE_URL}/export/transactions/pdf",
        params={
            'start_date': str(start_date),
            'end_date': str(end_date)
        }
    )
    assert response.status_code == 200, f"Failed: {response.text}"

    result = response.json()
    assert _check_file_exists(result['file_path']), "File not created"

    print(f"✓ Exported filtered transactions to PDF: {result['filename']}")

    return result


def test_export_transactions_excel():
    """Test exporting transactions to Excel."""
    print("\n=== Test: Export Transactions to Excel ===")

    response = requests.post(f"{BASE_URL}/export/transactions/excel")
    assert response.status_code == 200, f"Failed: {response.text}"

    result = response.json()
    assert result['format'] == 'excel', "Wrong format"
    assert result['filename'].endswith('.xlsx'), "Wrong file extension"
    assert _check_file_exists(result['file_path']), "File not created"

    print(f"✓ Exported transactions to Excel: {result['filename']} ({result['file_size']} bytes)")

    return result


def test_export_transactions_csv():
    """Test exporting transactions to CSV."""
    print("\n=== Test: Export Transactions to CSV ===")

    response = requests.post(f"{BASE_URL}/export/transactions/csv")
    assert response.status_code == 200, f"Failed: {response.text}"

    result = response.json()
    assert result['format'] == 'csv', "Wrong format"
    assert result['filename'].endswith('.csv'), "Wrong file extension"
    assert _check_file_exists(result['file_path']), "File not created"

    print(f"✓ Exported transactions to CSV: {result['filename']} ({result['file_size']} bytes)")

    return result


def test_export_financial_summary_pdf():
    """Test exporting financial summary to PDF."""
    print("\n=== Test: Export Financial Summary to PDF ===")

    response = requests.post(f"{BASE_URL}/export/financial-summary/pdf")
    assert response.status_code == 200, f"Failed: {response.text}"

    result = response.json()
    assert result['format'] == 'pdf', "Wrong format"
    assert result['export_type'] == 'financial_summary', "Wrong export type"
    assert _check_file_exists(result['file_path']), "File not created"
    assert result['file_size'] > 0, "File is empty"

    print(f"✓ Exported financial summary to PDF: {result['filename']} ({result['file_size']} bytes)")

    return result


def test_export_investment_portfolio_pdf():
    """Test exporting investment portfolio to PDF."""
    print("\n=== Test: Export Investment Portfolio to PDF ===")

    response = requests.post(f"{BASE_URL}/export/investment-portfolio/pdf")
    assert response.status_code == 200, f"Failed: {response.text}"

    result = response.json()
    assert result['format'] == 'pdf', "Wrong format"
    assert result['export_type'] == 'investment_portfolio', "Wrong export type"
    assert _check_file_exists(result['file_path']), "File not created"

    print(f"✓ Exported investment portfolio to PDF: {result['filename']} ({result['file_size']} bytes)")

    return result


def test_export_investment_portfolio_excel():
    """Test exporting investment portfolio to Excel."""
    print("\n=== Test: Export Investment Portfolio to Excel ===")

    response = requests.post(f"{BASE_URL}/export/investment-portfolio/excel")
    assert response.status_code == 200, f"Failed: {response.text}"

    result = response.json()
    assert result['format'] == 'excel', "Wrong format"
    assert result['filename'].endswith('.xlsx'), "Wrong file extension"
    assert _check_file_exists(result['file_path']), "File not created"

    print(f"✓ Exported investment portfolio to Excel: {result['filename']} ({result['file_size']} bytes)")

    return result


def test_export_debt_report_pdf():
    """Test exporting debt report to PDF."""
    print("\n=== Test: Export Debt Report to PDF ===")

    response = requests.post(f"{BASE_URL}/export/debt-report/pdf")
    assert response.status_code == 200, f"Failed: {response.text}"

    result = response.json()
    assert result['format'] == 'pdf', "Wrong format"
    assert result['export_type'] == 'debt_report', "Wrong export type"
    assert _check_file_exists(result['file_path']), "File not created"

    print(f"✓ Exported debt report to PDF: {result['filename']} ({result['file_size']} bytes)")

    return result


def test_list_exports():
    """Test listing all export files."""
    print("\n=== Test: List Exports ===")
    
    response = requests.get(f"{BASE_URL}/export/list")
    assert response.status_code == 200, f"Failed: {response.text}"
    
    exports = response.json()
    assert isinstance(exports, list), "Expected list of exports"
    
    print(f"✓ Found {len(exports)} export files")
    
    if exports:
        print(f"  Latest export: {exports[0]['filename']} ({exports[0]['export_type']})")
    
    return exports


def test_download_export(filename):
    """Test downloading an export file."""
    print(f"\n=== Test: Download Export ({filename}) ===")
    
    response = requests.get(f"{BASE_URL}/export/download/{filename}")
    assert response.status_code == 200, f"Failed: {response.text}"
    
    # Check content type
    content_type = response.headers.get('content-type', '')
    assert content_type != '', "Missing content-type header"
    
    # Check content length
    content_length = len(response.content)
    assert content_length > 0, "Downloaded file is empty"
    
    print(f"✓ Downloaded file: {filename} ({content_length} bytes, {content_type})")


def test_download_nonexistent_file():
    """Test downloading a non-existent file."""
    print("\n=== Test: Download Non-existent File ===")
    
    response = requests.get(f"{BASE_URL}/export/download/nonexistent.pdf")
    assert response.status_code == 404, "Expected 404 for non-existent file"
    
    print("✓ Correctly returned 404 for non-existent file")


def test_export_with_type_filter():
    """Test exporting transactions with type filter."""
    print("\n=== Test: Export Transactions with Type Filter ===")

    # Export only income transactions
    response = requests.post(
        f"{BASE_URL}/export/transactions/pdf",
        params={'transaction_type': 'income'}
    )
    assert response.status_code == 200, f"Failed: {response.text}"

    result = response.json()
    assert _check_file_exists(result['file_path']), "File not created"

    print(f"✓ Exported income transactions to PDF: {result['filename']}")

    # Export only expense transactions
    response = requests.post(
        f"{BASE_URL}/export/transactions/excel",
        params={'transaction_type': 'expense'}
    )
    assert response.status_code == 200, f"Failed: {response.text}"

    result = response.json()
    assert _check_file_exists(result['file_path']), "File not created"

    print(f"✓ Exported expense transactions to Excel: {result['filename']}")


def test_export_investment_with_type_filter():
    """Test exporting investment portfolio with type filter."""
    print("\n=== Test: Export Investment Portfolio with Type Filter ===")

    response = requests.post(
        f"{BASE_URL}/export/investment-portfolio/pdf",
        params={'investment_type': 'stock'}
    )
    assert response.status_code == 200, f"Failed: {response.text}"

    result = response.json()
    assert _check_file_exists(result['file_path']), "File not created"

    print(f"✓ Exported stock investments to PDF: {result['filename']}")


def run_all_tests():
    """Run all export tests."""
    print("\n" + "="*60)
    print("DATA EXPORT TESTS")
    print("="*60)
    
    try:
        # Transaction exports
        pdf_result = test_export_transactions_pdf()
        test_export_transactions_pdf_with_filters()
        excel_result = test_export_transactions_excel()
        csv_result = test_export_transactions_csv()
        
        # Financial summary export
        test_export_financial_summary_pdf()
        
        # Investment portfolio exports
        test_export_investment_portfolio_pdf()
        test_export_investment_portfolio_excel()
        
        # Debt report export
        test_export_debt_report_pdf()
        
        # List and download
        exports = test_list_exports()
        
        # Download test (use first PDF file)
        if pdf_result:
            test_download_export(pdf_result['filename'])
        
        # Error handling
        test_download_nonexistent_file()
        
        # Filtered exports
        test_export_with_type_filter()
        test_export_investment_with_type_filter()
        
        print("\n" + "="*60)
        print("✓ ALL TESTS PASSED!")
        print("="*60 + "\n")
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}\n")
        raise
    except Exception as e:
        print(f"\n✗ ERROR: {e}\n")
        raise


if __name__ == "__main__":
    run_all_tests()

