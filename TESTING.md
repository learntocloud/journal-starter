# Testing Guide for Journal API

This guide explains how to run and write tests for the Journal API project.

## Table of Contents

- [Quick Start](#quick-start)
- [Running Tests](#running-tests)
- [Understanding Test Results](#understanding-test-results)
- [Test Structure](#test-structure)
- [Writing New Tests](#writing-new-tests)
- [Continuous Integration](#continuous-integration)
- [Troubleshooting](#troubleshooting)

## Quick Start

1. **Install test dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

2. **Make sure the database is running:**
   ```bash
   docker ps  # Check if postgres container is running
   ```

3. **Run all tests:**
   ```bash
   pytest
   ```

   Or use the test runner script:
   ```bash
   ./run_tests.sh
   ```

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Tests with Verbose Output

```bash
pytest -v
```

### Run Tests from a Specific File

```bash
pytest tests/test_api.py
pytest tests/test_models.py
pytest tests/test_service.py
```

### Run a Specific Test Class

```bash
pytest tests/test_api.py::TestCreateEntry
```

### Run a Specific Test Function

```bash
pytest tests/test_api.py::TestCreateEntry::test_create_entry_success
```

### Run Tests with Coverage

```bash
pip install pytest-cov
pytest --cov=api --cov-report=html
```

Then open `htmlcov/index.html` in your browser.

## Understanding Test Results

### Test Status Indicators

- ✅ **PASSED**: The test passed successfully - your code works as expected!
- ❌ **FAILED**: The test failed - there's a bug or the code doesn't meet requirements
- ⚠️ **SKIPPED**: The test was skipped, usually because:
  - A feature isn't implemented yet (e.g., `GET /entries/{id}`)
  - The test is marked as optional
  - Test prerequisites aren't met

### Example Output

```
tests/test_api.py::TestCreateEntry::test_create_entry_success PASSED    [✓]
tests/test_api.py::TestGetSingleEntry::test_get_entry_by_id SKIPPED     [⚠]
```

**Skipped tests are normal!** Some tests check endpoints you haven't implemented yet. As you complete the development tasks, more tests will pass.

## Test Structure

The test suite is organized into three main files:

### 1. `tests/test_api.py` - API Endpoint Tests

Tests all REST API endpoints including:
- Creating entries (`POST /entries`)
- Retrieving entries (`GET /entries`, `GET /entries/{id}`)
- Updating entries (`PATCH /entries/{id}`)
- Deleting entries (`DELETE /entries/{id}`, `DELETE /entries`)
- AI analysis (`POST /entries/{id}/analyze`)
- Error handling (404s, validation errors)

### 2. `tests/test_models.py` - Data Model Tests

Tests Pydantic models and validation:
- `EntryCreate` model (user input)
- `Entry` model (internal representation)
- `AnalysisResponse` model (AI analysis results)
- Field validation (max length, required fields, etc.)
- Auto-generated fields (ID, timestamps)

### 3. `tests/test_service.py` - Service Layer Tests

Tests business logic and database interactions:
- Creating entries through the service
- Retrieving entries (all and by ID)
- Updating entries
- Deleting entries
- Error handling for non-existent entries

## Writing New Tests

### Test Fixtures

The project uses pytest fixtures defined in `tests/conftest.py`:

- **`test_client`**: Async HTTP client for making API requests
- **`test_db`**: Database connection for direct database operations
- **`sample_entry_data`**: Standard entry data for testing
- **`created_entry`**: Pre-created entry for tests that need existing data
- **`cleanup_database`**: Automatically cleans database before/after each test

### Example: Writing a New API Test

```python
async def test_my_new_endpoint(test_client: AsyncClient):
    """Test description here."""
    # Arrange: Set up test data
    data = {"work": "Test", "struggle": "Test", "intention": "Test"}
    
    # Act: Call the API
    response = await test_client.post("/entries", json=data)
    
    # Assert: Check the results
    assert response.status_code == 200
    result = response.json()
    assert result["detail"] == "Entry created successfully"
```

### Example: Writing a New Model Test

```python
def test_entry_validation():
    """Test that invalid data is rejected."""
    invalid_data = {
        "work": "a" * 300,  # Exceeds max length
        "struggle": "Test",
        "intention": "Test"
    }
    
    with pytest.raises(Exception):  # Pydantic raises ValidationError
        Entry(**invalid_data)
```

### Best Practices

1. **Use descriptive test names** that explain what you're testing
2. **Follow the AAA pattern**: Arrange, Act, Assert
3. **Test one thing per test** - keep tests focused
4. **Use fixtures** to avoid code duplication
5. **Test both success and error cases**
6. **Add docstrings** to explain what the test validates

## Continuous Integration

This project includes a GitHub Actions workflow that automatically runs tests on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

### CI Configuration

The workflow (`.github/workflows/test.yml`) will:
1. Set up Python 3.12
2. Start a PostgreSQL database
3. Install dependencies
4. Set up the database schema
5. Run all tests
6. Report results

### Viewing CI Results

1. Go to your repository on GitHub
2. Click the "Actions" tab
3. Click on the latest workflow run
4. View test results and logs

## Troubleshooting

### Database Connection Errors

**Error:** `ValueError: DATABASE_URL environment variable is missing`

**Solution:** Create a `.env` file with:
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/career_journal
```

**Error:** `Connection refused to localhost:5432`

**Solution:** Make sure PostgreSQL is running:
```bash
docker ps  # Check if postgres container is running
docker start postgres  # Start it if stopped
```

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'pytest'`

**Solution:** Install test dependencies:
```bash
pip install -e ".[dev]"
```

### Tests Passing Locally but Failing in CI

**Common causes:**
1. **Database not cleaned up** - The CI uses a fresh database, but local tests might have old data
   - Solution: The `cleanup_database` fixture handles this automatically
2. **Environment variables** - CI uses different environment variables
   - Solution: CI workflow creates `.env` automatically
3. **Python version differences** - CI uses Python 3.12
   - Solution: Test locally with Python 3.12

### Debugging Failed Tests

1. **Run with verbose output:**
   ```bash
   pytest -v
   ```

2. **Run with detailed tracebacks:**
   ```bash
   pytest --tb=long
   ```

3. **Run a single failing test:**
   ```bash
   pytest tests/test_api.py::TestCreateEntry::test_create_entry_success -v
   ```

4. **Add print statements or use breakpoint():**
   ```python
   async def test_something(test_client):
       response = await test_client.get("/entries")
       print(f"Response: {response.json()}")  # Debug output
       breakpoint()  # Python debugger
       assert response.status_code == 200
   ```

## Need Help?

- **Read the error message carefully** - it usually tells you what went wrong
- **Check the test file** - tests show you how the API should behave
- **Review the API code** - understand what the endpoint is supposed to do
- **Ask for help** - open an issue or ask your instructor

---

Happy testing! 🧪✨
