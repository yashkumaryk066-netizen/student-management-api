# Student Management API

A Django REST API for managing students and their attendance records with JWT authentication.

## Features

- 🎓 **Student Management** - CRUD operations for student records
- 📅 **Attendance Tracking** - Mark and manage daily attendance
- 🔐 **JWT Authentication** - Secure token-based authentication
- 📚 **Swagger Documentation** - Interactive API documentation
- ✅ **RESTful Design** - Proper HTTP status codes and REST principles

## Tech Stack

- Django 5.2.8
- Django REST Framework 3.16.1
- djangorestframework-simplejwt 5.5.1
- drf-spectacular (Swagger/OpenAPI)
- PostgreSQL

## API Endpoints

### Student APIs
- `GET /api/students/` - List all students (with search)
- `POST /api/students/` - Create a new student
- `GET /api/students/{id}/` - Get student details
- `PUT /api/students/{id}/` - Update student
- `DELETE /api/students/{id}/` - Delete student
- `GET /api/students/today/` - Get today's attendance summary

### Attendance APIs
- `GET /api/attendence/` - List all attendance records
- `POST /api/attendence/` - Mark attendance
- `GET /api/attendence/{id}/` - Get attendance details
- `PUT /api/attendence/{id}/` - Update attendance
- `DELETE /api/attendence/{id}/` - Delete attendance

### Authentication APIs
- `POST /api/auth/login/` - JWT login
- `POST /api/auth/token/refresh/` - Refresh JWT token

### Profile APIs
- `GET /api/profile/` - Get user profile

## Setup Instructions

### 1. Clone the repository
```bash
git clone <repository-url>
cd manufatures
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure database
Create a PostgreSQL database and update settings in `.env` file (see `.env.example`):
```bash
cp .env.example .env
# Edit .env with your database credentials
```

### 5. Run migrations
```bash
python manage.py migrate
```

### 6. Create superuser
```bash
python manage.py createsuperuser
```

### 7. Run the server
```bash
python manage.py runserver
```

## API Documentation

Access the interactive Swagger documentation at:
- **Swagger UI**: http://127.0.0.1:8000/swagger/
- **OpenAPI Schema**: http://127.0.0.1:8000/schema/

## Authentication

This API uses JWT (JSON Web Tokens) for authentication.

### Login
```bash
POST /api/auth/login/
{
  "username": "your_username",
  "password": "your_password"
}
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Using the token
```bash
GET /api/students/
Authorization: Bearer <access_token>
```

## Project Structure

```
manufatures/
├── manage.py
├── requirements.txt
├── .env.example
├── manufatures/          # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── student/              # Student app
│   ├── models.py         # Student and Attendance models
│   ├── views.py          # API views
│   ├── Serializer.py     # DRF serializers
│   ├── urls.py           # App URLs
│   └── admin.py          # Admin configuration
├── cars/                 # Cars app
└── library/              # Library app
```

## Environment Variables

Create a `.env` file based on `.env.example`:

```env
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=mydb
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Contact

For any queries or support, please open an issue in the repository.
