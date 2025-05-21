# Opportunity Collector App

A FastAPI application for user registration and authentication of managers and senior consultants.

## Features

- User registration with secure password encryption
- User authentication with JWT tokens
- Role-based access control (Manager and Senior Consultant with levels 1-4)
- PostgreSQL database integration with SQLAlchemy ORM
- Docker and Docker Compose setup for easy deployment
- Jenkins CI/CD pipeline integration

## Project Structure

```
bench_management_app/
├── app/
│   ├── __init__.py
│   ├── controller.py   # FastAPI endpoints
│   ├── service.py      # Business logic
│   ├── dao.py          # Database operations
│   ├── models.py       # SQLAlchemy models
│   ├── database.py     # Database connection
│   └── auth.py         # Authentication utilities
├── migrations/
│   └── create_tables.sql  # SQL scripts for PostgreSQL
├── tests/
│   ├── __init__.py
│   ├── test_controller.py
│   └── test_service.py
├── docker-compose.yml
├── Dockerfile
├── Jenkinsfile
├── requirements.txt
└── main.py
```

## API Endpoints

### User Registration

```
POST /register
```

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "password": "securepassword",
  "designation": "Manager_Level1"
}
```

**Valid Designations:**
- Manager_Level1, Manager_Level2, Manager_Level3, Manager_Level4
- SeniorConsultant_Level1, SeniorConsultant_Level2, SeniorConsultant_Level3, SeniorConsultant_Level4

**Response (201 Created):**
```json
{
  "id": 1,
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "designation": "Manager_Level1"
}
```

### User Login

```
POST /login
```

**Request Body (form-data):**
```
username: john.doe@example.com
password: securepassword
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "designation": "Manager_Level1"
  }
}
```

## Installation and Setup

### Prerequisites

- Docker and Docker Compose
- Python 3.9 or higher (if running locally)
- PostgreSQL (if running locally without Docker)

### Using Docker with Make (Recommended)

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd bench-management-app
   ```

2. Run the application using Make:
   ```bash
   # Start the application
   make start

   # View logs
   make logs

   # Stop the application
   make stop
   ```

   Or with Docker Compose directly:
   ```bash
   docker-compose up -d
   ```

3. The API will be available at http://localhost:8000

### Running Locally

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd bench-management-app
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up PostgreSQL and create the database:
   ```bash
   # Create a database named 'bench_management'
   # Run the SQL script in migrations/create_tables.sql
   ```

5. Update the database URL in `app/database.py` if needed.

6. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

7. The API will be available at http://localhost:8000

## Testing

To run the tests, you can use the Makefile:

```bash
# Run tests
make test

# Run tests with coverage report
make test-cov
```

Or run pytest directly:

```bash
pytest
```

## Sample Data

The application comes with preloaded sample data for testing purposes. When you start the application using Docker Compose, the following users are automatically created in the database:

### Managers
| Name | Email | Password | Designation |
|------|-------|----------|-------------|
| John Smith | john.smith@example.com | password123 | Manager_Level1 |
| Emily Johnson | emily.johnson@example.com | password123 | Manager_Level2 |
| Michael Williams | michael.williams@example.com | password123 | Manager_Level3 |
| Sarah Brown | sarah.brown@example.com | password123 | Manager_Level4 |

### Senior Consultants
| Name | Email | Password | Designation |
|------|-------|----------|-------------|
| David Jones | david.jones@example.com | password123 | SeniorConsultant_Level1 |
| Jennifer Garcia | jennifer.garcia@example.com | password123 | SeniorConsultant_Level2 |
| Robert Miller | robert.miller@example.com | password123 | SeniorConsultant_Level3 |
| Lisa Davis | lisa.davis@example.com | password123 | SeniorConsultant_Level4 |

You can use these accounts to test the login functionality without having to register new users. For example:

```bash
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john.smith@example.com&password=password123"
```

Or use the Swagger UI at http://localhost:8000/docs to test the API with these credentials.

## Makefile Commands

The project includes a Makefile to simplify common development tasks:

```bash
# Show all available commands
make help

# Install dependencies
make setup

# Start the application
make start

# View application logs
make logs

# Stop the application
make stop

# Run tests
make test

# Run tests with coverage
make test-cov

# Lint code with flake8
make lint

# Format code with black
make format

# Access PostgreSQL shell
make db-shell

# Apply database migrations
make db-migrate

# Start local development server (not in Docker)
make dev
```

## CI/CD with Jenkins

The project includes a Jenkinsfile for setting up a CI/CD pipeline:

1. **Checkout:** Fetches the latest code from the repository
2. **Setup Python Environment:** Sets up a Python virtual environment and installs dependencies
3. **Lint:** Runs code quality checks with Flake8
4. **Test:** Runs unit tests with Pytest
5. **Build Docker Image:** Builds the Docker image
6. **Deploy:** Deploys the application to the appropriate environment based on the branch

## Security Considerations

- Passwords are hashed using bcrypt before storage
- Authentication is handled via JWT tokens
- Database connection is secured
- Input validation is performed on all endpoints

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request