CREATE DATABASE student_activity;
USE student_activity;

CREATE TABLE students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    birth_date DATE NOT NULL,
    group_name VARCHAR(50) NOT NULL,
    enrollment_date timestamp DEFAULT current_timestamp
);
CREATE TABLE attendance (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    date DATE NOT NULL,
    status ENUM('present', 'absent', 'late') NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);
CREATE TABLE test_results (
    result_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    test_type ENUM('running', 'jumping', 'flexibility') NOT NULL,
    result_value DECIMAL(5,2) NOT NULL,
    test_date DATE NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);
CREATE TABLE test_standards (
    standard_id INT AUTO_INCREMENT PRIMARY KEY,
    test_type ENUM('running', 'jumping', 'flexibility') NOT NULL,
    age_group VARCHAR(20) NOT NULL,
    min_value DECIMAL(5,2) NOT NULL,
    max_value DECIMAL(5,2) NOT NULL
);
-- Добавляем студентов
INSERT INTO students (full_name, birth_date, group_name) VALUES
('Иван Петров', '2003-04-12', 'Группа 1'),
('Мария Иванова', '2004-08-20', 'Группа 2'),
('Алексей Смирнов', '2002-12-05', 'Группа 1');

-- Добавляем посещаемость
INSERT INTO attendance (student_id, date, status) VALUES
(1, '2025-03-10', 'present'),
(2, '2025-03-10', 'absent'),
(3, '2025-03-10', 'late');

-- Добавляем результаты тестов
INSERT INTO test_results (student_id, test_type, result_value, test_date) VALUES
(1, 'running', 12.5, '2025-03-15'),
(2, 'jumping', 2.1, '2025-03-15'),
(3, 'flexibility', 15.3, '2025-03-15');

-- Добавляем нормативы тестов
INSERT INTO test_standards (test_type, age_group, min_value, max_value) VALUES
('running', '18-20', 10.0, 14.0),
('jumping', '18-20', 2.0, 3.5),
('flexibility', '18-20', 12.0, 20.0);

