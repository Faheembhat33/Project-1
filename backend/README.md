# SonicWave Backend

Django + Django REST Framework + MySQL API for the SonicWave music frontend.

## 1. Requirements
- Python 3.10+
- MySQL Server 8+
- VS Code (optional)

## 2. Create database in MySQL
```sql
CREATE DATABASE sonicwave CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 3. Setup on Windows PowerShell
Open this folder in VS Code, then run:

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set your MySQL password. If PowerShell blocks activation, run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

If `mysqlclient` fails to install on Windows, install the Microsoft C++ Build Tools and MySQL development headers, or use a compatible Python/MySQL environment. Do not silently replace the database with SQLite: this project is configured for MySQL.

## 4. Migrate and create admin user
```powershell
python manage.py makemigrations music
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open:
- API root: http://127.0.0.1:8000/api/
- Admin: http://127.0.0.1:8000/admin/

Add Artists, Albums and Tracks from Django Admin. Track uploads require an audio file. Upload artwork as needed.

## 5. Authentication
Register:
```http
POST /api/auth/register/
Content-Type: application/json
{"username":"demo","email":"demo@example.com","password":"StrongPass123"}
```
Get JWT tokens:
```http
POST /api/auth/token/
{"username":"demo","password":"StrongPass123"}
```
Refresh:
```http
POST /api/auth/token/refresh/
{"refresh":"YOUR_REFRESH_TOKEN"}
```
Send protected requests with:
```http
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## 6. API endpoints

| Method | Endpoint | Auth | Purpose |
|---|---|---|---|
| POST | `/api/auth/register/` | No | Register |
| POST | `/api/auth/token/` | No | Login / obtain JWT |
| POST | `/api/auth/token/refresh/` | No | Refresh JWT |
| GET/PATCH | `/api/auth/me/` | Yes | Current profile |
| GET | `/api/tracks/` | No | Browse tracks |
| GET | `/api/tracks/?search=nova` | No | Search tracks |
| GET | `/api/tracks/?genre=Electronic` | No | Filter by genre |
| GET | `/api/tracks/trending/` | No | Trending tracks |
| GET | `/api/tracks/new_releases/` | No | New releases |
| POST | `/api/tracks/{id}/played/` | Yes | Record a play |
| GET | `/api/artists/` | No | Browse artists |
| GET | `/api/artists/{id}/tracks/` | No | Artist tracks |
| GET | `/api/artists/{id}/albums/` | No | Artist albums |
| GET | `/api/albums/` | No | Browse albums |
| GET | `/api/albums/{id}/tracks/` | No | Album tracks |
| GET/POST | `/api/playlists/` | Yes | List/create playlists |
| GET/PATCH/DELETE | `/api/playlists/{id}/` | Owner | Playlist detail/update/delete |
| POST | `/api/playlists/{id}/tracks/` | Owner | Add track: `{"track_id": 1}` |
| DELETE | `/api/playlists/{id}/tracks/{track_id}/` | Owner | Remove track |
| GET/POST/DELETE | `/api/likes/` | Yes | List/add/remove likes |
| GET | `/api/recently-played/` | Yes | Listening history |
| POST | `/api/recently-played/add/` | Yes | Add history: `{"track_id": 1}` |

## 7. Connect frontend
Run Django on port 8000 and Live Server on port 5500. The included CORS settings allow both common Live Server origins.

A track response includes `audio_url`, `cover_url`, `artist_name`, `album_title`, `duration_seconds`, and `liked`. Use `audio_url` as the HTML audio source. For authenticated requests, attach the JWT access token.

Example JavaScript:
```js
const API_BASE = "http://127.0.0.1:8000/api";

async function getTracks() {
  const response = await fetch(`${API_BASE}/tracks/`);
  if (!response.ok) throw new Error("Could not load tracks");
  return response.json();
}

async function login(username, password) {
  const response = await fetch(`${API_BASE}/auth/token/`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({username, password})
  });
  if (!response.ok) throw new Error("Login failed");
  const tokens = await response.json();
  localStorage.setItem("sonicwave_access", tokens.access);
  localStorage.setItem("sonicwave_refresh", tokens.refresh);
  return tokens;
}
```

## 8. Important production notes
- Change `SECRET_KEY`, set `DEBUG=False`, and configure production `ALLOWED_HOSTS`.
- Serve media through object storage/CDN or a properly configured media server in production.
- Use HTTPS, rate limiting, backups, monitoring, and secure secret management.
- Do not upload copyrighted music unless you have the rights to distribute it.
- The API provides catalogue metadata and media URLs; it is not a DRM or licensed streaming service.
