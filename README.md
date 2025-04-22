# Attendance Management Desktop Application

A desktop application for managing attendance in examination sessions, built with Python and PyQt5.

## Features

- User authentication (ADMIN and CANDIDATE roles)
- User management
- Exam management
- Attendance tracking
- Monitoring system

## System Requirements

- Python 3.7+
- PyQt5
- Requests library

## Installation

1. Clone the repository
2. Create and activate a virtual environment (optional but recommended)
3. Install dependencies using pip:

```
pip install -r requirements.txt
```

## Running the Application

Run the application using Python:

```
python main.py
```

## User Roles

The application supports two user roles:

1. **ADMIN**: Can manage users, exams, and track attendance
   - Access to user management
   - Exam creation and management
   - Attendance tracking and reporting
   - Monitoring system

2. **CANDIDATE**: Regular users who participate in exams
   - View own profile
   - View assigned exams
   - View attendance status

## Configuration

The application connects to a backend API for data storage and retrieval. The API endpoints can be configured in `config/config.py`.

By default, the application connects to `http://localhost:8080/api` for all API operations.

## Development

### Project Structure

```
attendance-desktop/
├── app/
│   ├── assets/       # Application assets (images, icons)
│   ├── controllers/  # Business logic controllers
│   ├── models/       # Data models
│   ├── utils/        # Utility functions
│   └── views/        # UI components
├── config/           # Configuration files
├── main.py           # Application entry point
└── requirements.txt  # Dependencies
```

## License

This project is licensed under the MIT License.