# Train Station API

A RESTful API service for managing train routes, trips, and ticket bookings, built with Django REST Framework.

## Project Overview

Train Station API is a backend platform for railway transportation management. It provides a structured system for handling trains, routes, stations, crew assignments, and passenger orders with full ticket validation logic.

The application supports JWT-based authentication, allowing users to register, browse available trips, and place ticket orders through a secure and documented API.

## Main Features

### Authentication and User Management
- JWT-based authentication with access and refresh tokens.
- Public registration endpoint for new passengers.
- Crew profiles linked to user accounts via a one-to-one relationship.

### Train and Route Management
- Train types, individual trains with cargo and seat configuration.
- Stations with geographic coordinates (latitude/longitude).
- Routes defined between source and destination stations with distance tracking.

### Trip Scheduling
- Trips assigned to a specific route and train with departure and arrival times.
- Many-to-many crew assignments per trip.

### Orders and Tickets
- Passengers can place orders containing one or more tickets.
- Ticket validation enforces cargo and seat ranges based on the assigned train's configuration.
- Unique constraint prevents duplicate seat assignments per trip.

### API Documentation
- Swagger UI available at `/api/doc/swagger/`.
- ReDoc available at `/api/doc/redoc/`.

## Prerequisites

Before getting started, ensure you have the following installed:

- Python 3.10 or higher
- PostgreSQL (running locally or via Docker)
- Docker and Docker Compose (for containerized setup)

## Installation and Local Setup

Clone the repository:

```bash
git clone https://github.com/artradkevych/train-station.git
cd train-station-api
```

Create and activate a virtual environment:

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Copy `.env.sample` to `.env` and fill in your values:

```bash
cp .env.sample .env
```

```env
POSTGRES_PASSWORD=your_db_password
POSTGRES_USER=your_db_user
POSTGRES_DB=your_db_name
POSTGRES_HOST=localhost
PGDATA=/var/lib/postgresql/data
```

> When running locally, set `POSTGRES_HOST=localhost`.

Apply migrations and seed the database:

```bash
python manage.py migrate
python manage.py loaddata fixtures.json
```

Start the development server:

```bash
python manage.py runserver
```

## Docker Setup

Copy `.env.sample` to `.env` and fill in your values:

```bash
cp .env.sample .env
```

```env
POSTGRES_PASSWORD=your_db_password
POSTGRES_USER=your_db_user
POSTGRES_DB=your_db_name
POSTGRES_HOST=db
PGDATA=/var/lib/postgresql/data
```

> When running via Docker, set `POSTGRES_HOST=db` to match the database service name in `docker-compose.yml`.

Build and start the containers:

```bash
docker-compose up --build
```

The fixture data is loaded automatically on startup. No additional steps are required to seed the database.

## API Documentation

The project includes an interactive OpenAPI 3.0 schema generated via drf-spectacular. Once the server is running, you can use the following endpoints:

* **Swagger UI:** http://localhost:8000/api/doc/swagger/
* **Redoc UI:** http://localhost:8000/api/doc/redoc/
* **Schema (YAML):** http://localhost:8000/api/doc/

## Credentials

The following accounts are available after loading the fixture. All accounts share the same password:

- **Email:** `admin@admin.com`
- **Password:** `RpfpQ87$`

## Authentication

The API uses JWT for authentication.

Obtain tokens:

```
POST /api/user/token/
```

Request body:

```json
{
  "email": "admin@admin.com",
  "password": "RpfpQ87$"
}
```

Use the access token in subsequent requests:

```
Authorization: Bearer <your_access_token>
```

Refresh the access token:

```
POST /api/user/token/refresh/
```

## Tech Stack

- **Language:** Python 3.14
- **Framework:** Django + Django REST Framework
- **Database:** PostgreSQL
- **Authentication:** JWT via `djangorestframework-simplejwt`
- **Containerization:** Docker, Docker Compose
- **Documentation:** drf-spectacular (Swagger / ReDoc)

## Author

**Artem Radkevych**
