-- Donors across every group, with a deliberate spread of eligibility:
-- some donated recently (ineligible), some long ago, some never.
INSERT INTO donors (name, blood_group, distance_km, age, last_donation) VALUES
    ('Asha Rao',      'O-',  2.1, 28, CURRENT_DATE - 200),
    ('Vikram Nair',   'O-',  8.4, 34, CURRENT_DATE - 10),   -- too recent
    ('Priya Menon',   'O+',  1.2, 22, NULL),                -- never donated
    ('Rahul Shetty',  'A+',  3.7, 45, CURRENT_DATE - 120),
    ('Fatima Khan',   'A-',  5.0, 31, CURRENT_DATE - 95),
    ('Joseph Dsouza', 'B+',  9.9, 52, NULL),
    ('Meera Iyer',    'B-',  4.4, 27, CURRENT_DATE - 30),   -- too recent
    ('Arjun Pillai',  'AB+', 6.8, 19, CURRENT_DATE - 365),
    ('Sneha Gupta',   'AB-', 7.2, 40, NULL),
    ('Imran Sheikh',  'A+', 12.5, 70, NULL)                 -- too old
ON CONFLICT DO NOTHING;

INSERT INTO requests (hospital, blood_group, units) VALUES
    ('City General', 'A+', 3),
    ('St Johns',     'O-', 2)
ON CONFLICT DO NOTHING;
