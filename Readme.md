# Fitness Studio Booking API (FastAPI)

## Features
- List classes (`GET /classes`) with timezone conversion
- Book a class (`POST /book`)
- View bookings by email (`GET /bookings?email=...`)
- Delete a booking (`DELETE /bookings/delete`)
- Admin: View all bookings (`GET /bookings/all`)
- Admin: Delete all bookings (`DELETE /bookings/all/delete`)
- SQLite database (file-based, lightweight)
- Logging for all actions
- Unit test support with Pytest

---

## Setup Instructions

### 1. Clone repo and create virtual environment
```bash
git clone https://github.com/sagarbandagar/fitness-booking-api.git
cd fitness-booking-api
python3 -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows



# curl commands 
# 1. Get all classes
curl -X GET "http://127.0.0.1:8000/classes?timezone=Asia/Kolkata" -H "accept: application/json"

# 2. Book a class
curl -X POST "http://127.0.0.1:8000/book" -H "Content-Type: application/json" -d '{"class_id": 1,"client_name": "Alice",
  "client_email": "alice@example.com"
}'

# 3. View bookings for a client (by email)
curl -X GET "http://127.0.0.1:8000/bookings?email=alice@example.com" -H "accept: application/json"

# 4. Delete a booking
curl -X DELETE "http://127.0.0.1:8000/bookings/delete" \
-H "Content-Type: application/json" \
-d '{
  "client_name": "Alice",
  "client_email": "alice@example.com"
}'

# 5. View all bookings 
curl -X GET "http://127.0.0.1:8000/bookings/all" -H "accept: application/json"

# 6. Delete all bookings + reset slots
curl -X DELETE "http://127.0.0.1:8000/bookings/all/delete" -H "accept: application/json"

