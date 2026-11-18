from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Artist(models.Model):
    name = models.CharField(max_length=120, unique=True)
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to="artists/", blank=True, null=True)
    banner = models.ImageField(upload_to="artist_banners/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Album(models.Model):
    title = models.CharField(max_length=160)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name="albums")
    cover = models.ImageField(upload_to="album_covers/", blank=True, null=True)
    release_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-release_date", "-created_at"]

    def __str__(self):
        return f"{self.title} — {self.artist.name}"


class Track(models.Model):
    title = models.CharField(max_length=160)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name="tracks")
    album = models.ForeignKey(Album, on_delete=models.SET_NULL, null=True, blank=True, related_name="tracks")
    genre = models.CharField(max_length=60, blank=True, db_index=True)
    audio_file = models.FileField(upload_to="tracks/")
    cover = models.ImageField(upload_to="track_covers/", blank=True, null=True)
    duration_seconds = models.PositiveIntegerField(default=0)
    play_count = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["genre"]),
            models.Index(fields=["-play_count"]),
        ]

    def __str__(self):
        return f"{self.title} — {self.artist.name}"


class Playlist(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="playlists")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    cover = models.ImageField(upload_to="playlist_covers/", blank=True, null=True)
    tracks = models.ManyToManyField(Track, through="PlaylistTrack", related_name="playlists")
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        unique_together = [("owner", "name")]

    def __str__(self):
        return f"{self.name} — {self.owner}"


class PlaylistTrack(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    position = models.PositiveIntegerField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["position", "added_at"]
        constraints = [
            models.UniqueConstraint(fields=["playlist", "track"], name="unique_track_per_playlist")
        ]


class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="music_likes")
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [models.UniqueConstraint(fields=["user", "track"], name="unique_user_track_like")]


class RecentlyPlayed(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recent_tracks")
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    played_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-played_at"]
        constraints = [models.UniqueConstraint(fields=["user", "track"], name="unique_user_recent_track")]
