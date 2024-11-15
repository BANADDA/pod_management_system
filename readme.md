# Pod Management System

A FastAPI-based pod management system with Docker container orchestration. This system allows users to create, manage, and schedule the termination of Docker containers ("pods") via API requests.

## Features

- User Registration: Users can register and generate tokens for authentication
- Pod Management: Create, view, and delete Docker containers via API
- Scheduler: Automatically terminate and remove expired pods
- Authentication: Secure endpoints with JWT-based authentication

## Requirements

- Python: 3.8 or higher
- Docker: Ensure Docker is installed and running
- Database: SQLite (for development)  
- Others: pip, virtualenv

## Installation

1. Clone the Repository:
```bash
git clone https://github.com/BANADDA/pod_management_system.git
cd pod_management_system
```

2. Create a Virtual Environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install Dependencies:
```bash
pip install -r requirements.txt
```

## Environment Setup

Create an `.env` file in the project root:

```env
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./pod_management.db
```

Replace `your_secret_key` with a secure, random string.

## Database Setup

1. Initialize Database Migrations:
```bash
alembic revision --autogenerate -m "Initial migration"
```

2. Apply Migrations:
```bash
alembic upgrade head
```

## Running the Application

1. Start the Application:
```bash
uvicorn main:app --reload
```
The application will run on `http://127.0.0.1:8000`

2. Ensure Docker is running and accessible to manage containers.

## API Endpoints

### Authentication

- **Register**: `POST /register`
  ```json
  { "username": "newuser", "password": "newpassword" }
  ```

- **Login**: `POST /token`
  ```json
  { "username": "newuser", "password": "newpassword" }
  ```

### Pod Management

- **Create Pod**: `POST /pods`
  - Headers: `Authorization: Bearer <access_token>`
  - Body: `{ "duration_minutes": 5 }`

- **Get Pod Details**: `GET /pods/{pod_id}`
  - Headers: `Authorization: Bearer <access_token>`

- **Delete Pod**: `DELETE /pods/{pod_id}`
  - Headers: `Authorization: Bearer <access_token>`

## Example Usage

```bash
# Register User
curl -X POST "http://127.0.0.1:8000/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "newuser", "password": "newpassword"}'

# Get Token
curl -X POST "http://127.0.0.1:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=newuser&password=newpassword"

# Create Pod
curl -X POST "http://127.0.0.1:8000/pods" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"duration_minutes": 5}'
```

## Scheduler

The scheduler runs every 2 seconds to check for and terminate expired pods. It automatically starts with the application and handles:
- Checking for expired pods
- Stopping and removing containers
- Updating database entries

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature-branch`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature-branch`)
5. Open a pull request

## License

This project is licensed under the MIT License. See LICENSE for more information.