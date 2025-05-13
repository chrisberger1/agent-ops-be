-- Create ENUM type for designation
CREATE TYPE designation_enum AS ENUM (
    'Manager_Level1', 'Manager_Level2', 'Manager_Level3', 'Manager_Level4',
    'SeniorConsultant_Level1', 'SeniorConsultant_Level2', 'SeniorConsultant_Level3', 'SeniorConsultant_Level4'
);

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    designation designation_enum NOT NULL
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Insert sample data for testing
-- Note: Passwords are bcrypt hashed - all sample users have password "password123"
INSERT INTO users (first_name, last_name, email, password, designation)
VALUES 
    -- Managers
    ('John', 'Smith', 'john.smith@example.com', '$2b$12$1FpXLGBeDQcXLPJ7tWY8tuafosuuWNwG0M1bEw6AhGwp5.YNlMrQC', 'Manager_Level1'),
    ('Emily', 'Johnson', 'emily.johnson@example.com', '$2b$12$1FpXLGBeDQcXLPJ7tWY8tuafosuuWNwG0M1bEw6AhGwp5.YNlMrQC', 'Manager_Level2'),
    ('Michael', 'Williams', 'michael.williams@example.com', '$2b$12$1FpXLGBeDQcXLPJ7tWY8tuafosuuWNwG0M1bEw6AhGwp5.YNlMrQC', 'Manager_Level3'),
    ('Sarah', 'Brown', 'sarah.brown@example.com', '$2b$12$1FpXLGBeDQcXLPJ7tWY8tuafosuuWNwG0M1bEw6AhGwp5.YNlMrQC', 'Manager_Level4'),
    
    -- Senior Consultants
    ('David', 'Jones', 'david.jones@example.com', '$2b$12$1FpXLGBeDQcXLPJ7tWY8tuafosuuWNwG0M1bEw6AhGwp5.YNlMrQC', 'SeniorConsultant_Level1'),
    ('Jennifer', 'Garcia', 'jennifer.garcia@example.com', '$2b$12$1FpXLGBeDQcXLPJ7tWY8tuafosuuWNwG0M1bEw6AhGwp5.YNlMrQC', 'SeniorConsultant_Level2'),
    ('Robert', 'Miller', 'robert.miller@example.com', '$2b$12$1FpXLGBeDQcXLPJ7tWY8tuafosuuWNwG0M1bEw6AhGwp5.YNlMrQC', 'SeniorConsultant_Level3'),
    ('Lisa', 'Davis', 'lisa.davis@example.com', '$2b$12$1FpXLGBeDQcXLPJ7tWY8tuafosuuWNwG0M1bEw6AhGwp5.YNlMrQC', 'SeniorConsultant_Level4');

-- Output confirmation message
DO $$
BEGIN
    RAISE NOTICE 'Tables created and sample data loaded successfully.';
    RAISE NOTICE 'Sample users have been created with password "password123"';
END $$;