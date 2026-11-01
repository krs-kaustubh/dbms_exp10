-- Sample data for the SAMs demo (same records as Experiment 4, plus a few
-- pending items so the approval workflow can be shown straight away).

INSERT INTO resident (resident_id, name, apartment_no, contact_no, email, status) VALUES
(101, 'Aarav Raj Mehta',  'A-101', '9876543210', 'aarav.mehta@email.com', 'Approved'),
(102, 'Sara Khan',        'B-204', '9988776655', 'sara.khan@email.com',   'Approved'),
(103, 'Rohan Vijay Shah', 'C-305', '9876501234', 'rohan.shah@email.com',  'Approved'),
(104, 'Anaya Patel',      'A-302', '9898989898', 'anaya.patel@email.com', 'Approved'),
(105, 'Kabir Amit Joshi', 'B-110', '9000011111', 'kabir.joshi@email.com', 'Approved'),
(106, 'Ishaan Raj Kapoor','C-210', '9888877777', 'ishaan.kapoor@email.com','Pending');

INSERT INTO amenity (amenity_id, name, location, operating_hours, capacity, amenity_type) VALUES
(201, 'Gym',             'Block A Ground Floor',   '06:00-22:00', 40,  'Gym'),
(202, 'Community Hall',  'Clubhouse First Floor',  '09:00-23:00', 150, 'Community_Hall'),
(203, 'Swimming Pool',   'Clubhouse Ground Floor', '07:00-21:00', 60,  'Pool'),
(204, 'Badminton Court', 'Sports Complex',         '06:00-22:00', 20,  'Sports_Court'),
(205, 'Yoga Studio',     'Clubhouse Second Floor', '06:00-21:00', 30,  'Gym');

INSERT INTO pool (amenity_id, depth_ft) VALUES (203, 5.00);
INSERT INTO sports_court (amenity_id, sport_type) VALUES (204, 'Badminton');

INSERT INTO equipment (amenity_id, equipment_no, equipment_name, equipment_condition) VALUES
(201, 1, 'Treadmill',    'Good'),
(201, 2, 'Bench Press',  'Good'),
(201, 3, 'Dumbbell Set', 'New');

INSERT INTO staff (staff_id, name, contact_no, salary, shift_timing, staff_type, amenity_id) VALUES
(301, 'Vikram Singh', '9811111111', 32000.00, '06:00-14:00', 'Trainer',       201),
(302, 'Neha Verma',   '9822222222', 45000.00, '09:00-18:00', 'Support_Staff', 202),
(303, 'Imran Ali',    '9833333333', 28000.00, '07:00-15:00', 'Support_Staff', 203),
(304, 'Pooja Nair',   '9844444444', 30000.00, '14:00-22:00', 'Support_Staff', 204),
(305, 'Rahul Das',    '9855555555', 29000.00, '06:00-14:00', 'Trainer',       205);

INSERT INTO support_staff (staff_id, designation) VALUES
(302, 'Facility Manager'),
(303, 'Pool Attendant'),
(304, 'Sports Assistant');

INSERT INTO trainer (staff_id, specialization_area) VALUES
(301, 'Strength Training'),
(305, 'Yoga');

INSERT INTO training_session (session_id, session_date, time_slot, topic, trainer_id, amenity_id) VALUES
(601, '2026-09-15', '07:00-08:00', 'Strength Training', 301, 201),
(602, '2026-09-16', '07:30-08:30', 'Yoga Basics',       305, 205),
(603, '2026-09-17', '18:00-19:00', 'Sports Fitness',    301, 204);

INSERT INTO session_enrollment (resident_id, session_id) VALUES
(101, 601), (103, 601), (102, 602), (104, 602), (105, 603);

INSERT INTO booking (booking_id, booking_date, time_slot, status, resident_id, amenity_id) VALUES
(501, '2026-09-10', '18:00-20:00', 'Confirmed', 101, 202),
(502, '2026-09-11', '07:00-08:00', 'Confirmed', 102, 201),
(503, '2026-09-12', '17:00-18:00', 'Pending',   103, 204),
(504, '2026-09-13', '10:00-11:00', 'Confirmed', 104, 203),
(505, '2026-09-14', '07:00-08:00', 'Cancelled', 105, 205);

INSERT INTO entry_log (resident_id, amenity_id, entry_time, exit_time, recorded_by) VALUES
(102, 205, '2026-09-07 07:30:00', '2026-09-07 08:25:00', 305),
(104, 203, '2026-09-07 10:15:00', '2026-09-07 11:00:00', 303),
(101, 201, NOW(), NULL, 301);

INSERT INTO amenity_proposal (resident_id, amenity_name, suggested_type, reason, status) VALUES
(104, 'Squash Court', 'Sports_Court', 'Many residents play squash and have to travel outside the society.', 'Pending');
