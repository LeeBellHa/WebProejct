CREATE TABLE bookings (
  id INT AUTO_INCREMENT PRIMARY KEY,
  student_id VARCHAR(20),
  name VARCHAR(50),
  major VARCHAR(50),
  room VARCHAR(10),
  floor INT,
  date DATE,
  time_slot VARCHAR(10),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);