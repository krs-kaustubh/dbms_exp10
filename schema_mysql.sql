-- =========================================================
-- SAMs - Society Amenities Management System
-- MySQL DDL Schema for Experiment 10
-- =========================================================

DROP DATABASE IF EXISTS societydb;
CREATE DATABASE societydb;
USE societydb;

-- 1. RESIDENT
CREATE TABLE IF NOT EXISTS resident (
    resident_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    apartment_no VARCHAR(20) NOT NULL,
    contact_no VARCHAR(15) NOT NULL,
    email VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'Approved',
    CONSTRAINT pk_resident PRIMARY KEY (resident_id),
    CONSTRAINT uq_resident_email UNIQUE (email),
    CONSTRAINT chk_resident_contact CHECK (CHAR_LENGTH(contact_no) >= 10)
);

-- 2. AMENITY
CREATE TABLE IF NOT EXISTS amenity (
    amenity_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(100) NOT NULL,
    operating_hours VARCHAR(50) NOT NULL,
    capacity INT NOT NULL,
    amenity_type VARCHAR(20) NOT NULL,
    CONSTRAINT pk_amenity PRIMARY KEY (amenity_id),
    CONSTRAINT uq_amenity_name UNIQUE (name),
    CONSTRAINT chk_amenity_capacity CHECK (capacity > 0),
    CONSTRAINT chk_amenity_type CHECK (amenity_type IN ('Gym', 'Community_Hall', 'Pool', 'Sports_Court'))
);

-- 3. POOL (Specialization)
CREATE TABLE IF NOT EXISTS pool (
    amenity_id INT NOT NULL,
    depth_ft DECIMAL(4,2) NOT NULL,
    CONSTRAINT pk_pool PRIMARY KEY (amenity_id),
    CONSTRAINT fk_pool_amenity FOREIGN KEY (amenity_id)
        REFERENCES amenity(amenity_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_pool_depth CHECK (depth_ft > 0)
);

-- 4. SPORTS COURT (Specialization)
CREATE TABLE IF NOT EXISTS sports_court (
    amenity_id INT NOT NULL,
    sport_type VARCHAR(50) NOT NULL,
    CONSTRAINT pk_sportsCourt PRIMARY KEY (amenity_id),
    CONSTRAINT fk_sportsCourt_amenity FOREIGN KEY (amenity_id)
        REFERENCES amenity(amenity_id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 5. EQUIPMENT (Weak Entity)
CREATE TABLE IF NOT EXISTS equipment (
    amenity_id INT NOT NULL,
    equipment_no INT NOT NULL,
    equipment_name VARCHAR(100) NOT NULL,
    equipment_condition VARCHAR(20) NOT NULL,
    CONSTRAINT pk_equipment PRIMARY KEY (amenity_id, equipment_no),
    CONSTRAINT fk_equipment_amenity FOREIGN KEY (amenity_id)
        REFERENCES amenity(amenity_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_equipment_no CHECK (equipment_no > 0),
    CONSTRAINT chk_equipment_condition CHECK (equipment_condition IN ('New', 'Good', 'Fair', 'Damaged'))
);

-- 6. STAFF
CREATE TABLE IF NOT EXISTS staff (
    staff_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    contact_no VARCHAR(15) NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    shift_timing VARCHAR(50) NOT NULL,
    staff_type VARCHAR(20) NOT NULL,
    amenity_id INT NOT NULL,
    CONSTRAINT pk_staff PRIMARY KEY (staff_id),
    CONSTRAINT uq_staff_contact UNIQUE (contact_no),
    CONSTRAINT chk_staff_contact CHECK (CHAR_LENGTH(contact_no) >= 10),
    CONSTRAINT chk_staff_salary CHECK (salary >= 0),
    CONSTRAINT chk_staff_type CHECK (staff_type IN ('Trainer', 'Support_Staff')),
    CONSTRAINT fk_staff_amenity FOREIGN KEY (amenity_id)
        REFERENCES amenity(amenity_id) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- 7. TRAINER (Specialization)
CREATE TABLE IF NOT EXISTS trainer (
    staff_id INT NOT NULL,
    specialization_area VARCHAR(100) NOT NULL,
    CONSTRAINT pk_trainer PRIMARY KEY (staff_id),
    CONSTRAINT fk_trainer_staff FOREIGN KEY (staff_id)
        REFERENCES staff(staff_id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 8. SUPPORT STAFF (Specialization)
CREATE TABLE IF NOT EXISTS support_staff (
    staff_id INT NOT NULL,
    designation VARCHAR(50) NOT NULL,
    CONSTRAINT pk_supportStaff PRIMARY KEY (staff_id),
    CONSTRAINT fk_supportStaff_staff FOREIGN KEY (staff_id)
        REFERENCES staff(staff_id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 9. TRAINING SESSION
CREATE TABLE IF NOT EXISTS training_session (
    session_id INT NOT NULL,
    session_date DATE NOT NULL,
    time_slot VARCHAR(30) NOT NULL,
    topic VARCHAR(100) NOT NULL,
    trainer_id INT NOT NULL,
    amenity_id INT NOT NULL,
    CONSTRAINT pk_trainingSession PRIMARY KEY (session_id),
    CONSTRAINT fk_trainingSession_trainer FOREIGN KEY (trainer_id)
        REFERENCES trainer(staff_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_trainingSession_amenity FOREIGN KEY (amenity_id)
        REFERENCES amenity(amenity_id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 10. SESSION ENROLLMENT
CREATE TABLE IF NOT EXISTS session_enrollment (
    resident_id INT NOT NULL,
    session_id INT NOT NULL,
    CONSTRAINT pk_sessionEnrollment PRIMARY KEY (resident_id, session_id),
    CONSTRAINT fk_sessionEnrollment_resident FOREIGN KEY (resident_id)
        REFERENCES resident(resident_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_sessionEnrollment_session FOREIGN KEY (session_id)
        REFERENCES training_session(session_id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 11. BOOKING
CREATE TABLE IF NOT EXISTS booking (
    booking_id INT NOT NULL,
    booking_date DATE NOT NULL,
    time_slot VARCHAR(30) NOT NULL,
    status VARCHAR(20) NOT NULL,
    resident_id INT NOT NULL,
    amenity_id INT NOT NULL,
    CONSTRAINT pk_booking PRIMARY KEY (booking_id),
    CONSTRAINT fk_booking_resident FOREIGN KEY (resident_id)
        REFERENCES resident(resident_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_booking_amenity FOREIGN KEY (amenity_id)
        REFERENCES amenity(amenity_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_booking_status CHECK (status IN ('Pending', 'Confirmed', 'Cancelled', 'Completed')),
    CONSTRAINT uq_booking_slot UNIQUE (amenity_id, booking_date, time_slot)
);

-- 12. ENTRY LOG
CREATE TABLE IF NOT EXISTS entry_log (
    resident_id INT NOT NULL,
    amenity_id INT NOT NULL,
    entry_time DATETIME NOT NULL,
    exit_time DATETIME,
    recorded_by INT,
    CONSTRAINT pk_entryLog PRIMARY KEY (resident_id, entry_time),
    CONSTRAINT fk_entryLog_resident FOREIGN KEY (resident_id)
        REFERENCES resident(resident_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_entryLog_amenity FOREIGN KEY (amenity_id)
        REFERENCES amenity(amenity_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_entryLog_staff FOREIGN KEY (recorded_by)
        REFERENCES staff(staff_id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT chk_entryLog_exitTime CHECK (exit_time IS NULL OR exit_time >= entry_time)
);

-- 13. AMENITY PROPOSAL
CREATE TABLE IF NOT EXISTS amenity_proposal (
    proposal_id INT AUTO_INCREMENT PRIMARY KEY,
    resident_id INT NOT NULL,
    amenity_name VARCHAR(100) NOT NULL,
    suggested_type VARCHAR(50) NOT NULL,
    reason TEXT,
    status VARCHAR(20) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_prop_resident FOREIGN KEY (resident_id)
        REFERENCES resident(resident_id) ON DELETE CASCADE ON UPDATE CASCADE
);
