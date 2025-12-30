# Student Management System - Frontend

A beautiful, modern web interface for the Student Management API with JWT authentication.

## Features

- 🎨 **Modern UI** - Clean, responsive design with gradient colors and animations
- 🔐 **JWT Authentication** - Secure login system
- 👥 **Student Management** - Add, edit, delete, and search students
- 📅 **Attendance Tracking** - Mark daily attendance with one click
- 📊 **Live Statistics** - Real-time dashboard with today's attendance data
- 📱 **Responsive** - Works on desktop, tablet, and mobile

## Screenshots

### Login Page
Beautiful gradient login page with JWT authentication.

### Dashboard
Modern dashboard with statistics cards showing:
- Total Students
- Present Today
- Absent Today

### Student Management
Full CRUD operations with search functionality.

## Getting Started

### Prerequisites
- Student Management API backend running on `http://127.0.0.1:8000`
- Modern web browser
- Live Server or any local web server

### Installation

1. **Make sure the backend is running:**
```bash
cd /home/tele/manufatures
source venv/bin/activate
python manage.py runserver
```

2. **Open the frontend:**

**Option 1: Using VS Code Live Server**
- Open `frontend/index.html` in VS Code
- Right-click and select "Open with Live Server"
- Frontend will open at `http://127.0.0.1:5500`

**Option 2: Using Python HTTP Server**
```bash
cd frontend
python -m http.server 8080
```
Then open `http://127.0.0.1:8080` in your browser

**Option 3: Direct File**
- Simply double-click `index.html` (may have CORS issues)

## Usage

### Login
1. Enter your username and password
2. Click "Sign In"
3. You'll be redirected to the dashboard

Default credentials (if you created a superuser):
- Username: `your_superuser_username`
- Password: `your_superuser_password`

### Dashboard Features

**View Statistics:**
- Total Students count
- Today's present count
- Today's absent count

**Search Students:**
- Type in the search box to filter by name or gender
- Results update automatically

**Add Student:**
1. Click "+ Add Student" button
2. Fill in all fields
3. Click "Save"

**Edit Student:**
1. Click "Edit" button on any student
2. Update the fields
3. Click "Save"

**Delete Student:**
1. Click "Delete" button
2. Confirm deletion

**Mark Attendance:**
1. Click "✓ Present" or "✗ Absent" for any student
2. Statistics update automatically
3. Can only mark once per day per student

## File Structure

```
frontend/
├── index.html          # Main HTML file
├── css/
│   └── style.css      # Styles and animations
├── js/
│   └── app.js         # Application logic and API calls
└── README.md          # This file
```

## API Integration

The frontend connects to these API endpoints:

- `POST /api/auth/login/` - JWT login
- `GET /api/students/` - List students
- `POST /api/students/` - Create student
- `PUT /api/students/{id}/` - Update student
- `DELETE /api/students/{id}/` - Delete student
- `GET /api/students/today/` - Today's attendance stats
- `POST /api/attendence/` - Mark attendance

## Configuration

To change the API URL, edit `js/app.js`:

```javascript
const API_BASE_URL = 'http://127.0.0.1:8000/api';
```

## Features in Detail

### Authentication
- JWT token stored in localStorage
- Auto-login if token exists
- Auto-logout on token expiration
- Logout button in navbar

### Student Operations
- Create, Read, Update, Delete students
- Real-time search with debouncing
- Form validation
- Success/error messages

### Attendance
- One-click attendance marking
- Duplicate prevention
- Today's stats auto-update
- Visual feedback with color coding

### Design
- Gradient color scheme (purple/blue)
- Smooth animations and transitions
- Card-based layout
- Modern typography (Inter font)
- Responsive grid system
- Mobile-friendly

## Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge

## Troubleshooting

**Login fails:**
- Check if backend server is running
- Verify credentials
- Check browser console for errors

**CORS errors:**
- Make sure you're using a local server (not file://)
- Check CORS settings in Django settings.py

**Students not loading:**
- Check if you're logged in
- Verify API is accessible at http://127.0.0.1:8000/api/
- Check browser console for errors

## Technologies Used

- **Pure JavaScript** - No frameworks, vanilla JS
- **CSS3** - Modern CSS with animations
- **HTML5** - Semantic HTML
- **Fetch API** - For HTTP requests
- **LocalStorage** - For JWT token storage
- **Google Fonts** - Inter font family

## License

This project is licensed under the MIT License.
