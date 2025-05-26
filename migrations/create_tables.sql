
DROP SCHEMA IF EXISTS bench_management CASCADE;

-- Create the schema
CREATE SCHEMA IF NOT EXISTS bench_management;

-- Drop 'users' table if it exists
DROP TABLE IF EXISTS users;

-- Drop 'message' table if it exists
DROP TABLE IF EXISTS message;

-- Drop 'conversation' table if it exists
DROP TABLE IF EXISTS conversation;

-- Drop 'opportunity' table if it exists
DROP TABLE IF EXISTS opportunity;

-- Drop 'department' table if it exists
DROP TABLE IF EXISTS department;

-- Drop 'designation' table if it exists
DROP TABLE IF EXISTS designation;

-- Drop 'query' table if it exists
DROP TABLE IF EXISTS query;

-- Drop 'option' table if it exists
DROP TABLE IF EXISTS option;

CREATE EXTENSION vector;


-- Create the department table within the schema
CREATE TABLE IF NOT EXISTS department (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- Create the designation table within the schema
CREATE TABLE IF NOT EXISTS designation (
    id SERIAL PRIMARY KEY,
    department_id INT REFERENCES department(id),
    title VARCHAR(100) NOT NULL
);


-- Create the users table within the schema
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    department_id INT REFERENCES department(id),
    designation_id INT REFERENCES designation(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



-- Create the conversation table within the schema
CREATE TABLE IF NOT EXISTS conversation (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES department(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



-- Create the message table within the schema
CREATE TABLE IF NOT EXISTS message (
     id SERIAL PRIMARY KEY,
     conversation_id INT REFERENCES conversation(id),
     content TEXT NOT NULL,
     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



-- Create the opportunity table within the schema
CREATE TABLE IF NOT EXISTS opportunity (
    id SERIAL PRIMARY KEY,
    details TEXT NOT NULL,
    department_id INT REFERENCES department(id),
    user_id INT references users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



-- Create the option table within the schema
CREATE TABLE IF NOT EXISTS option (
    id SERIAL PRIMARY KEY,
    initial_option VARCHAR(255) NOT NULL
);

-- Create the query table within the schema
CREATE TABLE IF NOT EXISTS query (
    id SERIAL PRIMARY KEY,
    option_id INT REFERENCES option(id),
    ask TEXT NOT NULL,
    order_num INT NOT NULL
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Insert sample data for testing

INSERT INTO option (initial_option)
VALUES
    ('I have an opportunity to upload'),
    ('I am looking for an opportunity');

INSERT INTO query (option_id, ask, order_num)
VALUES
    (1, 'May I know the opportunity name?', 1),
    (1, 'Opportunity Type - BD Work/Client engagement/Internal Asset Building?', 2),
    (1, 'Duration in weeks?', 3),
    (1, 'Start Date (mm/dd/yyyy)?', 4),
    (1, 'Number of Resources with level(for ex - 3 Staff/2 Senior/1 Manager)', 5),
    (1, 'Skills required?', 6),
    (2, 'Opportunity Type - BD Work/Client engagement/Internal Asset Building?', 1),
    (2, 'Start Date (mm/dd/yyyy)?', 2),
    (2, 'Techstack (Java/SAP/Salesforce/AI)?', 3);

INSERT INTO department (name)
VALUES
    ('Digital Engineering'),
    ('AI & Data');

INSERT INTO designation (title, department_id)
VALUES
    ('Staff', 1),
    ('SeniorConsultant', 1),
    ('Manager', 1),
    ('Senior Manager', 1);

-- Note: Passwords are bcrypt hashed - all sample users have password "password123"
INSERT INTO users (first_name, last_name, email, password, department_id, designation_id)
VALUES
    -- Staff
    ('John', 'Smith', 'john.smith@example.com', '$2b$12$1FpXLGBeDQcXLPJ7tWY8tuafosuuWNwG0M1bEw6AhGwp5.YNlMrQC', 1, 1),
    ('Emily', 'Johnson', 'emily.johnson@example.com', '$2b$12$1FpXLGBeDQcXLPJ7tWY8tuafosuuWNwG0M1bEw6AhGwp5.YNlMrQC',  1, 1),
    -- Senior Consultants
    ('Michael', 'Williams', 'michael.williams@example.com', '$2b$12$1FpXLGBeDQcXLPJ7tWY8tuafosuuWNwG0M1bEw6AhGwp5.YNlMrQC', 1, 2),
    ('Sarah', 'Brown', 'sarah.brown@example.com', '$2b$12$1FpXLGBeDQcXLPJ7tWY8tuafosuuWNwG0M1bEw6AhGwp5.YNlMrQC', 1, 2),
    -- Manager
    ('David', 'Jones', 'david.jones@example.com', '$2b$12$1FpXLGBeDQcXLPJ7tWY8tuafosuuWNwG0M1bEw6AhGwp5.YNlMrQC', 1, 3),
    ('Jennifer', 'Garcia', 'jennifer.garcia@example.com', '$2b$12$1FpXLGBeDQcXLPJ7tWY8tuafosuuWNwG0M1bEw6AhGwp5.YNlMrQC', 1, 3),
    --Senior Manager
    ('Robert', 'Miller', 'robert.miller@example.com', '$2b$12$1FpXLGBeDQcXLPJ7tWY8tuafosuuWNwG0M1bEw6AhGwp5.YNlMrQC', 1, 4),
    ('Lisa', 'Davis', 'lisa.davis@example.com', '$2b$12$1FpXLGBeDQcXLPJ7tWY8tuafosuuWNwG0M1bEw6AhGwp5.YNlMrQC', 1, 4);

commit;
-- Output confirmation message
DO $$
BEGIN
    RAISE NOTICE 'Tables created and sample data loaded successfully.';
    RAISE NOTICE 'Sample users have been created with password "password123"';
END $$;