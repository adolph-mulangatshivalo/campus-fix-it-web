
-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    student_number VARCHAR(20) UNIQUE,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('student', 'admin', 'worker') DEFAULT 'student',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create categories table
CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description TEXT
);

-- Create reports table
CREATE TABLE IF NOT EXISTS reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    category_id INT NOT NULL,
    title VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    location VARCHAR(255) NOT NULL,
    image_path VARCHAR(255),
    status ENUM('Submitted', 'Under Review', 'Assigned', 'In Progress', 'Fixed', 'Rejected') DEFAULT 'Submitted',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    worker_id INT DEFAULT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT,
    FOREIGN KEY (worker_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Create report_updates table
CREATE TABLE IF NOT EXISTS report_updates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    report_id INT NOT NULL,
    admin_id INT NOT NULL,
    status ENUM('Submitted', 'Under Review', 'Assigned', 'In Progress', 'Fixed', 'Rejected') NOT NULL,
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE CASCADE,
    FOREIGN KEY (admin_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Insert some default categories
INSERT INTO categories (name, description) VALUES
('Plumbing', 'Leaks, blocked toilets, broken sinks, water issues'),
('Electrical', 'Power outages, broken outlets, exposed wires'),
('Furniture', 'Broken chairs, desks, or other furniture'),
('Buildings', 'Broken windows, structural issues, roof leaks'),
('Toilets', 'Restroom supplies, cleanliness, broken dispensers'),
('Lighting', 'Burnt out bulbs, broken light fixtures'),
('Doors/Locks', 'Broken locks, doors won\'t close or open'),
('Cleaning', 'Spills, trash overflow, general cleaning needed'),
('Grounds/Landscaping', 'Fallen branches, pathway issues'),
('Other', 'Any other physical maintenance issues');
