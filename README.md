# SonicWave Full-Stack Project

SonicWave's existing music-player frontend is now wired to its Django REST Framework backend.

## Project layout

- `frontend/` — HTML, CSS and JavaScript UI. `app.js` calls the Django API at `http://127.0.0.1:8000/api`.
- `backend/` — Django REST Framework API, JWT authentication and MySQL models.

## Run it on Windows

### 1. Start MySQL

Create the database in MySQL Workbench or the MySQL shell:

```sql
CREATE DATABASE sonicwave CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. Configure and start Django

Open PowerShell in `backend`:

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set `DB_PASSWORD` to your MySQL password. Then run:

```powershell
python manage.py makemigrations music
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Keep this terminal running. Django should be available at `http://127.0.0.1:8000/` and admin at `http://127.0.0.1:8000/admin/`.

### 3. Add music to the database

Open `http://127.0.0.1:8000/admin/`, sign in with your superuser, and add:

1. Artists
2. Albums (optional)
3. Tracks — upload an audio file; add cover art if available; keep `is_published` enabled

The frontend now loads its catalogue from `GET /api/tracks/`. The sample demo tracks are no longer hardcoded in the browser. If there are no published tracks, the catalogue will be empty until you upload tracks.

### 4. Start the frontend

Open `frontend/index.html` in VS Code and use the Live Server extension. Use either:

- `http://127.0.0.1:5500`
- `http://localhost:5500`

Do not open the HTML as a `file://` URL. The Django CORS configuration already allows the two Live Server origins above.

## What is connected

- Catalogue and artist cards load from Django APIs.
- Search uses the backend track search endpoint.
- Audio player uses each track's `audio_url` served by Django media storage.
- Login, registration, JWT refresh and logout are wired to the authentication endpoints.
- Liked songs, recently played and playlists are stored per logged-in user in MySQL.
- Playlist creation and adding tracks use the playlist API.

Protected features require the user to log in. JWT access and refresh tokens are stored in browser local storage for this development project. For production, use HTTPS, review token storage and configure production CORS/hosts/media delivery.

## API configuration

The frontend API base URL is at the top of `frontend/app.js`:

```js
const API_BASE = "http://127.0.0.1:8000/api";
```

Change this value when deploying the backend to a server. Keep the backend's `CORS_ALLOWED_ORIGINS` in `.env` aligned with the frontend's deployed origin.

## Important

The project files are connected, but the application still needs to be configured and run on your computer: install Python packages, configure MySQL, migrate, create an admin user, upload real audio files, then run both servers. This archive has not been run against your local MySQL instance.
