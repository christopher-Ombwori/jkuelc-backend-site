# JKUELC Connect Hub Backend

A comprehensive backend API service for the JKUELC Connect Hub platform, built with Django REST Framework.

## Overview

The JKUELC Connect Hub Backend provides all necessary APIs for the JKUELC (Jaramogi Kenyatta University of Engineering and Law Club) platform. This API supports membership management, blog posts, events, gallery, merchandise sales, and payment processing.

## Features

- **User Management**: Registration, authentication, profile management, and role-based access
- **Membership**: Membership application, approval, and subscription management
- **Blog**: Content creation, publishing workflow with draft/pending/published states
- **Events**: Event creation, registration, and management
- **Gallery**: Photo and media management
- **Merchandise**: Product catalog and ordering system
- **Payment**: Payment processing and transaction tracking

## Tech Stack

- **Framework**: Django 5.0.6
- **API**: Django REST Framework
- **Authentication**: Token-based authentication
- **Database**: SQLite (development), can be configured for PostgreSQL in production
- **CORS**: Cross-Origin Resource Sharing enabled for frontend integration

## Project Structure

```
jkuelc-backend/
├── blog/                  # Blog post management
├── events/                # Event management
├── gallery/               # Media gallery management
├── jkuelc_backend/        # Core project settings
├── membership/            # Membership management
├── merchandise/           # Merchandise shop management
├── payment/               # Payment processing
├── static/                # Static files
├── users/                 # User authentication and profiles
├── manage.py              # Django management script
└── db.sqlite3             # Development database
```

## Installation

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd jkuelc-backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install django==5.0.6 djangorestframework django-cors-headers pillow
   ```

4. Apply migrations:
   ```
   python manage.py migrate
   ```

5. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```
   python manage.py runserver
   ```

The API will be available at `http://127.0.0.1:8000/`.

## API Endpoints

### Authentication

- `POST /api/token/`: Obtain authentication token
- `GET /api/auth/`: DRF browsable API authentication

### Users

- `GET /api/users/`: List users
- `POST /api/users/`: Register new user
- `GET /api/users/profile/`: Get current user profile
- `PUT /api/users/profile/`: Update current user profile

### Membership

- `GET /api/membership/`: List membership information
- `POST /api/membership/`: Apply for membership

### Blog

- `GET /api/blog/`: List blog posts
- `POST /api/blog/`: Create blog post
- `GET /api/blog/{id}/`: Get blog post details
- `PUT /api/blog/{id}/`: Update blog post
- `DELETE /api/blog/{id}/`: Delete blog post

### Events

- `GET /api/events/`: List events
- `POST /api/events/`: Create event
- `GET /api/events/{id}/`: Get event details
- `PUT /api/events/{id}/`: Update event
- `DELETE /api/events/{id}/`: Delete event

### Gallery

- `GET /api/gallery/`: List gallery items
- `POST /api/gallery/`: Upload new media

### Merchandise

- `GET /api/merchandise/`: List merchandise
- `POST /api/merchandise/`: Add new merchandise
- `GET /api/merchandise/{id}/`: Get merchandise details

### Payment

- `POST /api/payment/`: Process payment
- `GET /api/payment/history/`: Get payment history

## Authentication

The API uses token-based authentication. To authenticate:

1. Obtain a token by sending a POST request to `/api/token/` with credentials:
   ```json
   {
     "email": "user@example.com",
     "password": "yourpassword"
   }
   ```

2. Include the token in subsequent requests:
   ```
   Authorization: Token <your-token>
   ```

## Permissions

The system implements role-based access control with three main roles:
- **Admin**: Full system access
- **Manager**: Can manage content and approve member submissions
- **Member**: Standard user access

## Development

### Running Tests

```
python manage.py test
```

### API Documentation

Interactive API documentation is available at `/api/docs/` when the server is running.

## Deployment

For production deployment:

1. Set `DEBUG = False` in settings.py
2. Configure a production database (PostgreSQL recommended)
3. Set up proper static and media file hosting
4. Use a production-ready web server like Gunicorn
5. Set up HTTPS with proper SSL certificates

## License

[Specify License Information]

## Contact

[Specify Contact Information]
