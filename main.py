from fastapi import FastAPI, HTTPException # type: ignore
from models import BookingRequest, DeleteBookingRequest
from database import get_db_connection
from datetime import datetime
from zoneinfo import ZoneInfo
import logging

# ---------------- Logging ----------------
logging.basicConfig(level=logging.INFO,
                   format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("fitness_booking_api")

# ---------------- App ----------------
app = FastAPI(title="Fitness Studio Booking API")
# ---------------- Timezone ----------------
IST_ZONE = "Asia/Kolkata"
def _convert_from_ist(iso_dt_str: str, target_tz: str) -> str:
   try:
       dt = datetime.fromisoformat(iso_dt_str).replace(tzinfo=ZoneInfo(IST_ZONE))
       return dt.astimezone(ZoneInfo(target_tz)).isoformat()
   except Exception:
       raise HTTPException(status_code=400, detail="Invalid datetime or timezone")

# ---------------- API Endpoints ----------------
# Get all classes
@app.get("/classes")
def get_classes(timezone: str = "Asia/Kolkata"):
   conn = get_db_connection()
   cursor = conn.cursor()
   cursor.execute("SELECT * FROM classes ORDER BY datetime ASC")
   rows = cursor.fetchall()
   classes = []
   for row in rows:
       converted_iso = _convert_from_ist(row["datetime"], timezone)
       classes.append({
           "id": row["id"],
           "name": row["name"],
           "datetime": converted_iso,
           "instructor": row["instructor"],
           "available_slots": row["available_slots"]
       })
   logger.info(f"Returned {len(classes)} classes for timezone={timezone}")
   return classes

# Book a class
@app.post("/book")
def book_class(req: BookingRequest):
   conn = get_db_connection()
   cursor = conn.cursor()
   logger.info(f"Booking attempt by {req.client_name} ({req.client_email}) for class_id={req.class_id}")
   try:
       cursor.execute("SELECT * FROM classes WHERE id = ?", (req.class_id,))
       cls = cursor.fetchone()
       if not cls:
           raise HTTPException(status_code=404, detail="Class not found")
       if cls["available_slots"] <= 0:
           raise HTTPException(status_code=400, detail="No slots available")
       # Insert booking
       cursor.execute(
           "INSERT INTO bookings (class_id, client_name, client_email) VALUES (?, ?, ?)",
           (req.class_id, req.client_name, req.client_email)
       )
       # Reduce available slots
       cursor.execute(
           "UPDATE classes SET available_slots = available_slots - 1 WHERE id = ?",
           (req.class_id,)
       )
       conn.commit()
       logger.info(f"Booking successful: {req.client_email} -> class {req.class_id}")
       return {"message": "Booking successful"}
   except HTTPException as he:
       raise he
   except Exception as e:
       conn.rollback()
       logger.error(f"Booking failed: {e}")
       raise HTTPException(status_code=500, detail="Internal Server Error")

# Get bookings (optional email filter)
@app.get("/bookings")
def get_bookings(email: str = None):
   conn = get_db_connection()
   cursor = conn.cursor()
   if email:
       cursor.execute("SELECT * FROM bookings WHERE client_email = ? ORDER BY id DESC", (email,))
   else:
       cursor.execute("SELECT * FROM bookings ORDER BY id DESC")
   rows = cursor.fetchall()
   bookings = [dict(row) for row in rows]
   logger.info(f"Returned {len(bookings)} bookings{' for ' + email if email else ''}")
   return bookings

# Delete a single booking
@app.delete("/bookings/delete")
def delete_booking(req: DeleteBookingRequest):
   conn = get_db_connection()
   cursor = conn.cursor()
   cursor.execute(
       "SELECT class_id FROM bookings WHERE client_email = ? AND client_name = ?",
       (req.client_email, req.client_name)
   )
   booking = cursor.fetchone()
   if not booking:
       raise HTTPException(status_code=404, detail="Booking not found")
   cursor.execute(
       "DELETE FROM bookings WHERE client_email = ? AND client_name = ?",
       (req.client_email, req.client_name)
   )
   # Restore slot
   cursor.execute(
       "UPDATE classes SET available_slots = available_slots + 1 WHERE id = ?",
       (booking["class_id"],)
   )
   conn.commit()
   logger.info(f"Booking deleted: {req.client_name} ({req.client_email})")
   return {"message": f"Booking deleted: {req.client_name} ({req.client_email})"}

# Get all bookings
@app.get("/bookings/all")
def get_all_bookings():
   conn = get_db_connection()
   cursor = conn.cursor()
   cursor.execute("SELECT * FROM bookings ORDER BY id DESC")
   rows = cursor.fetchall()
   bookings = [dict(row) for row in rows]
   logger.info(f"Returned all {len(bookings)} bookings")
   return bookings

# Delete all bookings
@app.delete("/bookings/all/delete")
def delete_all_bookings():
   conn = get_db_connection()
   cursor = conn.cursor()
   cursor.execute("DELETE FROM bookings")
   deleted_count = cursor.rowcount
   # Reset all slots back (optional, assuming 10 slots default)
   cursor.execute("UPDATE classes SET available_slots = 10")
   conn.commit()
   logger.warning(f"All bookings deleted ({deleted_count} entries)")
   return {"message": f"Deleted all {deleted_count} bookings and reset slots"}