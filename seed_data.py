import sqlite3
DB = "fitness.db"

def seed():
   conn = sqlite3.connect(DB)
   cursor = conn.cursor()
   cursor.execute("DROP TABLE IF EXISTS classes")
   cursor.execute("DROP TABLE IF EXISTS bookings")
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
       client_email TEXT NOT NULL,
       FOREIGN KEY (class_id) REFERENCES classes(id)
   )
   """)
   classes = [
       ("Yoga", "2025-08-22T07:00:00", "Sagar", 4),
       ("Zumba", "2025-08-22T09:00:00", "Sachin", 1),
       ("HIIT", "2025-08-22T18:00:00", "Santosh", 4),
   ]
   cursor.executemany(
       "INSERT INTO classes (name, datetime, instructor, available_slots) VALUES (?, ?, ?, ?)",
       classes
   )
   conn.commit()
   conn.close()
   print("Database seeded ->", DB)
if __name__ == "__main__":
   seed()