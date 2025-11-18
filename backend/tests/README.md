# Backend Test Suite

Comprehensive test coverage for the cadastral backend application following Python testing best practices.

## Test Structure

The test suite is organized into the following modules:

### `test_models.py`
Tests for all Django models:
- Model metadata (db_table, managed, verbose names)
- Field relationships (ForeignKeys, related names)
- String representations (`__str__` methods)
- Geometry field configurations
- Model ordering and constraints

### `test_serializers.py`
Tests for all DRF serializers:
- Serializer field definitions
- Nested relationship serialization
- Read-only field configurations
- Geometry field handling (GeoJSON)
- Field validation

### `test_viewsets_integration.py`
Comprehensive integration tests for all API endpoints:
- **List endpoints**: Testing GET requests to list resources
- **Detail endpoints**: Testing GET requests for individual resources
- **Filtering**: Testing all filter parameters
- **Search**: Testing search functionality across fields
- **BBox queries**: Testing spatial bounding box filtering
- **Pagination**: Testing limit/offset pagination
- **Error handling**: Testing 404, 400, and other error responses

### `test_filters.py`
Tests for all django-filter FilterSets:
- Filter field definitions
- Lookup expressions (icontains, exact, gte, lte, etc.)
- Relationship filtering (foreign key traversals)
- Filter labels and metadata
- Filter combinations

### `test_urls.py`
Tests for URL routing:
- URL resolution (matching URLs to views)
- Reverse lookups (generating URLs from view names)
- URL parameter handling
- Edge cases (invalid URLs, trailing slashes)

### `test_cadastral_viewsets.py`
Unit tests for viewset configuration:
- Serializer class assignments
- BBox filter field configuration
- Router registration

## Test Fixtures

Located in `conftest.py`:
- `sample_point`: Sample Point geometry in EPSG:3765
- `sample_polygon`: Sample Polygon geometry in EPSG:3765
- `sample_multipolygon`: Sample MultiPolygon geometry in EPSG:3765
- `sample_bbox`: Sample bounding box string for testing
- `sample_datetime`: Sample datetime for testing
- `api_client`: DRF APIClient for making API requests
- `api_request_factory`: DRF APIRequestFactory for creating requests

## Running Tests

### Run all tests:
```bash
pytest
```

### Run specific test file:
```bash
pytest tests/test_models.py
```

### Run with coverage:
```bash
pytest --cov=cadastral --cov-report=html
```

### Run with verbose output:
```bash
pytest -v
```

### Run specific test class:
```bash
pytest tests/test_viewsets_integration.py::TestCadastralParcelViewSet
```

### Run specific test:
```bash
pytest tests/test_viewsets_integration.py::TestCadastralParcelViewSet::test_list_cadastral_parcels
```

## Test Coverage

The test suite covers:
- ✅ All 12 models (Country, County, Municipality, Settlement, PostalOffice, Street, StreetFeature, Address, CadastralMunicipality, CadastralParcel, Building, Usage)
- ✅ All 11 serializers
- ✅ All 11 viewsets (plus LayerCatalogView)
- ✅ All 11 FilterSets
- ✅ All URL routes and reverse lookups
- ✅ API endpoint integration tests
- ✅ Error handling and edge cases

## Best Practices Followed

1. **Test Organization**: Tests are organized by component (models, serializers, viewsets, etc.)
2. **Test Naming**: Clear, descriptive test names following `test_<what>_<expected_behavior>` pattern
3. **Test Isolation**: Each test is independent and can run in any order
4. **Fixtures**: Reusable test fixtures for common test data
5. **Parametrization**: Using `@pytest.mark.parametrize` for testing multiple similar cases
6. **Database Usage**: Proper use of `@pytest.mark.django_db` decorator
7. **Assertions**: Clear, specific assertions with helpful error messages
8. **Edge Cases**: Testing error conditions, invalid inputs, and boundary cases
9. **Integration Tests**: Full API integration tests, not just unit tests
10. **Documentation**: Docstrings explaining what each test verifies

## Notes

- Models are read-only (`managed=False`) and point to existing database tables
- Tests use the actual database schema but don't modify data
- Some tests may return 404 if no data exists in the database (expected behavior)
- Tests are designed to work with or without actual data in the database

