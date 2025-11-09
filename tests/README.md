# FIN-DASH Tests

This directory contains test files for the FIN-DASH application.

## 📁 Test Structure

```
tests/
├── README.md                 # This file
├── test_card_api.py         # Card API tests
└── test_csv_read.py         # CSV reading tests

backend/tests/
├── test_analytics.py        # Analytics service tests
├── test_api.py              # General API tests
├── test_currency.py         # Currency service tests
├── test_export.py           # Export functionality tests
├── test_investment.py       # Investment tracking tests
├── test_recurring.py        # Recurring transactions tests
├── test_week4_api.py        # Week 4 API tests
└── test_week6_backend.py    # Week 6 backend tests
```

## 🧪 Running Tests

### Backend Tests

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install test dependencies
pip install pytest pytest-cov

# Run all backend tests
pytest tests/

# Run specific test file
pytest tests/test_analytics.py

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

### Frontend Tests

```bash
# Install test dependencies
npm install --save-dev vitest @testing-library/react @testing-library/jest-dom

# Run tests (when implemented)
npm test
```

## 📝 Test Coverage

Current test coverage includes:
- ✅ Analytics service
- ✅ API endpoints
- ✅ Currency conversion
- ✅ Export functionality (PDF/Excel)
- ✅ Investment tracking
- ✅ Recurring transactions
- ✅ Card API
- ✅ CSV reading

## 🎯 Testing Best Practices

1. **Write tests for new features** - All new features should include tests
2. **Test edge cases** - Don't just test the happy path
3. **Use fixtures** - Reuse test data with pytest fixtures
4. **Mock external dependencies** - Use mocks for file I/O, API calls, etc.
5. **Keep tests isolated** - Each test should be independent
6. **Use descriptive names** - Test names should describe what they test

## 🔧 Adding New Tests

To add a new test file:

1. Create a new file in the appropriate directory (`tests/` or `backend/tests/`)
2. Name it `test_<feature>.py`
3. Import pytest and the code you're testing
4. Write test functions starting with `test_`
5. Run the tests to verify they pass

Example:
```python
import pytest
from backend.services.my_service import MyService

def test_my_feature():
    """Test that my feature works correctly."""
    service = MyService()
    result = service.do_something()
    assert result == expected_value
```

## 📊 Test Reports

Test reports and coverage reports are generated in:
- `htmlcov/` - HTML coverage reports (gitignored)
- `.coverage` - Coverage data file (gitignored)

View coverage report:
```bash
# Generate and open coverage report
pytest tests/ --cov=. --cov-report=html
# Open htmlcov/index.html in your browser
```

---

For more information on testing, see the [pytest documentation](https://docs.pytest.org/).

