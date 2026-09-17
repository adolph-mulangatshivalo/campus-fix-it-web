-- Migration to add worker role and report assignments
ALTER TABLE users MODIFY COLUMN role ENUM('student', 'admin', 'worker') DEFAULT 'student';
ALTER TABLE reports ADD COLUMN worker_id INT DEFAULT NULL;
ALTER TABLE reports ADD CONSTRAINT fk_reports_worker FOREIGN KEY (worker_id) REFERENCES users(id) ON DELETE SET NULL;
