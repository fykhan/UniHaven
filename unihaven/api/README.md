# UniHaven REST API endpoints

RESTful API for off-campus accommodation listings and reservations for HKU students and CEDARS staff.

---

## Address Lookup

### POST `/api/address-lookup/`
Retrieve latitude, longitude, and geo_address using the DATA.GOV.HK API.

#### Request Body
```json
{
  "address": "Haking Wong Building"
}
```
### Example Response
```json
{
  "latitude": "22.2839",
  "longitude": "114.1376",
  "geo_address": "Haking Wong Building"
}
```
## Accommodations/Reservations/Ratings
(replace accommodations with reservations/ratings depending on data)

### `GET /api/accommodations/`
- List all accommodations

### `POST /api/accommodations/`
- Create a new accommodation
- Request Body:
```json
{
  "title": "Modern Studio",
  "property_type": "AP",
  "price": 8200.00,
  "beds": 1,
  "bedrooms": 1,
  "address": "Haking Wong Building",
  "available_from": "2025-05-01",
  "available_to": "2025-08-01",
  "owner": 1,
  "created_by": 1
}
```
### GET /api/accommodations/<id>/
Retrieve details of a specific accommodation.

### PUT /api/accommodations/<id>/
Update an accommodation.

### DELETE /api/accommodations/<id>/
Delete an accommodation.




