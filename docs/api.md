# REST API Endpoints

## Base URL
`http://<host>/api/`

## Endpoints

### 1. GET `/parcels/`
Returns a **GeoJSON FeatureCollection** of cadastral parcels.

**Status**: Placeholder - models not yet implemented

#### Query Parameters (Future)
- `parcel_id`: Filter by exact parcel ID (string)
- `cadastral_municipality`: Filter by municipality name (string)
- `bbox`: Comma-separated bounding box in EPSG:4326 (minLon,minLat,maxLon,maxLat)
- `limit`, `offset`: Pagination

#### Response (200 OK)
```json
{
  "message": "Cadastral parcels endpoint - models not yet implemented",
  "features": []
}
```

### 2. GET `/admin_boundaries/`
Returns administrative boundaries.

**Status**: Placeholder - models not yet implemented

#### Query Parameters (Future)
- `name`: Filter by name substring
- `admin_type`: Filter by "Municipality" / "County"
- `limit`, `offset`

#### Response (200 OK)
```json
{
  "message": "Administrative boundaries endpoint - models not yet implemented",
  "features": []
}
```

---

**Note**: Full API documentation will be available once database models are implemented.

