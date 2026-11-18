# SonicWave Frontend

This frontend is connected to the SonicWave Django REST API. Start the backend first (see the root project README), then serve this folder using VS Code Live Server at `http://127.0.0.1:5500` or `http://localhost:5500`.

The API base URL is configured at the top of `app.js` as `http://127.0.0.1:8000/api`. The frontend loads tracks and artists from Django, streams uploaded track audio using `audio_url`, and uses JWT authentication for likes, playlists and recently played history.

Upload audio files and artwork through Django Admin. There are no longer hardcoded demo tracks in the frontend.
