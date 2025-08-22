import sqlite3
from fastapi.testclient import TestClient
from main import app
from database import DB
client = TestClient(app)
# ---------------- Setup function ----------------
def setup_function():
   """Reset DB before each test"""
   conn = sqlite3.connect(DB)
   cursor = conn.cursor()
   # Drop tables if they exist
   cursor.execute("DROP TABLE IF EXISTS classes")
   cursor.execute("DROP TABLE IF EXISTS bookings")
   # Recreate tables
   cursor.execute("""
   CREATE TABLE classes (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       name TEXT NOT NULL,
       datetime TEXT NOT NULL,
       instructor TEXT NOT NULL,
       available_slots INTEGER NOT NULL
   )
   """)
   cursor.execute("""
   CREATE TABLE bookings (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       class_id INTEGER NOT NULL,
       client_name TEXT NOT NULL,
       client_email TEXT NOT NULL
   )
   """)
   # Seed classes
   classes = [
       ("Yoga", "2025-08-21T07:00:00", "Sachin", 4),
       ("Zumba", "2025-08-21T09:00:00", "Sagar", 1),
       ("HIIT", "2025-08-21T18:00:00", "Santosh", 4),
   ]
   cursor.executemany(
       "INSERT INTO classes (name, datetime, instructor, available_slots) VALUES (?, ?, ?, ?)",
       classes
   )
   conn.commit()
   conn.close()

# ---------------- Tests ----------------
def test_get_classes():
   res = client.get("/classes")
   assert res.status_code == 200
   assert isinstance(res.json(), list)
   assert len(res.json()) == 3  # seeded classes
def test_book_class_success():
   res = client.post("/book", json={
       "class_id": 1,
       "client_name": "Test User",
       "client_email": "test@example.com"
   })
   assert res.status_code == 200
   assert res.json()["message"] == "Booking successful"
def test_book_class_overbook():
   # Book last slot for Zumba (1 slot)
   client.post("/book", json={
       "class_id": 2,
       "client_name": "U1",
       "client_email": "u1@example.com"
   })
   # Try booking again
   res2 = client.post("/book", json={
       "class_id": 2,
       "client_name": "U2",
       "client_email": "u2@example.com"
   })
   assert res2.status_code == 400
   assert res2.json()["detail"] == "No slots available"
def test_get_bookings_by_email():
   client.post("/book", json={
       "class_id": 1,
       "client_name": "Tester",
       "client_email": "tester@example.com"
   })
   res = client.get("/bookings", params={"email": "tester@example.com"})
   assert res.status_code == 200
   bookings = res.json()
   assert isinstance(bookings, list)
   assert any(b["client_name"] == "Tester" for b in bookings)
def test_get_all_bookings():
   # Book two classes
   client.post("/book", json={
       "class_id": 1,
       "client_name": "User1",
       "client_email": "user1@example.com"
   })
   client.post("/book", json={
       "class_id": 3,
       "client_name": "User2",
       "client_email": "user2@example.com"
   })
   res = client.get("/bookings/all")
   assert res.status_code == 200
   bookings = res.json()
   assert len(bookings) >= 2
def test_delete_booking():
   # Book a class first
   client.post("/book", json={
       "class_id": 1,
       "client_name": "Delete Me",
       "client_email": "deleteme@example.com"
   })
   # Delete the booking
   import json
   res = client.request(
       "DELETE", 
       "/bookings/delete", 
       content=json.dumps({
           "client_name": "Delete Me",
           "client_email": "deleteme@example.com"
       }),
       headers={"Content-Type": "application/json"}
   )
   assert res.status_code == 200
   assert "Booking deleted" in res.json()["message"]
   # Ensure booking is gone
   res2 = client.get("/bookings", params={"email": "deleteme@example.com"})
   assert all(b["client_name"] != "Delete Me" for b in res2.json())
def test_delete_all_bookings():
   # Book multiple classes
   client.post("/book", json={
       "class_id": 1,
       "client_name": "UserA",
       "client_email": "a@example.com"
   })
   client.post("/book", json={
       "class_id": 2,
       "client_name": "UserB",
       "client_email": "b@example.com"
   })
   # Delete all bookings
   res = client.delete("/bookings/all/delete")
   assert res.status_code == 200
   assert "Deleted all" in res.json()["message"]
   # Ensure bookings table empty
   res2 = client.get("/bookings/all")
   assert len(res2.json()) == 0
def test_booking_slot_restored_after_delete():
   # Book a class with 1 slot
   client.post("/book", json={
       "class_id": 2,
       "client_name": "RestoreTest",
       "client_email": "restore@example.com"
   })
   # Delete booking
   import json
   client.request(
       "DELETE", 
       "/bookings/delete", 
       content=json.dumps({
           "client_name": "RestoreTest",
           "client_email": "restore@example.com"
       }),
       headers={"Content-Type": "application/json"}
   )
   # Book again, should succeed
   res = client.post("/book", json={
       "class_id": 2,
       "client_name": "RestoreTest2",
       "client_email": "restore2@example.com"
   })
   assert res.status_code == 200
   assert res.json()["message"] == "Booking successful"