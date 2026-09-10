# SportPath Backend

## Requirements

- Python 3.10 or newer
- XAMPP with MySQL running (Apache is not required)

## Setup

1. Start XAMPP and start MySQL.
2. Open phpMyAdmin or the MySQL client and run `backend/database.sql`.
3. From the project root, create and activate a virtual environment:

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env
```

4. Edit `.env` if the MySQL username, password, host, or port differs.
5. Start Flask:

```powershell
python app.py
```

6. Open `new copy/login.html` in a browser, or serve that folder with a static web server.
7. Test `http://127.0.0.1:5000/api/test` and `http://127.0.0.1:5000/api/db-test`.
8. Register, log in, and edit the profile through the existing SportPath pages.

The login page also supports password reset through `POST /api/forgot-password`.
It verifies the registered email and phone number before storing the new password hash.

The frontend uses `http://127.0.0.1:5000/api` by default. Set a different API origin before loading the page with `window.SPORTPATH_API_URL` if needed.
