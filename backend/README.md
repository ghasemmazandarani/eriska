# Eriska Backend

This directory contains the backend code, built with **Django** and **Django REST Framework**.

## Prerequisites

- Python 3.8+
- pip

## Installation & Usage

1. Create a Virtual Environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Apply migrations:
```bash
python manage.py migrate
```

4. Run the server:
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`.
