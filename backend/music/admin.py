from django.contrib import admin
from .models import Artist, Album, Track, Playlist, PlaylistTrack, Like, RecentlyPlayed

@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ["name", "created_at"]

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ["title", "artist", "release_date"]
    search_fields = ["title", "artist__name"]
    list_filter = ["release_date"]

@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ["title", "artist", "album", "genre", "play_count", "is_published"]
    search_fields = ["title", "artist__name", "album__title"]
    list_filter = ["genre", "is_published"]
    list_editable = ["is_published"]

class PlaylistTrackInline(admin.TabularInline):
    model = PlaylistTrack
    extra = 0

@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ["name", "owner", "is_public", "created_at"]
    inlines = [PlaylistTrackInline]

admin.site.register(Like)
admin.site.register(RecentlyPlayed)
