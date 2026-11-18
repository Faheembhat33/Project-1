from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Artist, Album, Track, Playlist, PlaylistTrack, Like, RecentlyPlayed


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    class Meta:
        model = User
        fields = ("id", "username", "email", "password")
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name")


class ArtistSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    banner_url = serializers.SerializerMethodField()
    class Meta:
        model = Artist
        fields = ("id", "name", "bio", "image", "image_url", "banner", "banner_url")
    def get_image_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.image.url) if request and obj.image else None
    def get_banner_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.banner.url) if request and obj.banner else None


class AlbumSerializer(serializers.ModelSerializer):
    artist_name = serializers.CharField(source="artist.name", read_only=True)
    cover_url = serializers.SerializerMethodField()
    class Meta:
        model = Album
        fields = ("id", "title", "artist", "artist_name", "cover", "cover_url", "release_date", "description")
    def get_cover_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.cover.url) if request and obj.cover else None


class TrackSerializer(serializers.ModelSerializer):
    artist_name = serializers.CharField(source="artist.name", read_only=True)
    album_title = serializers.CharField(source="album.title", read_only=True, allow_null=True)
    audio_url = serializers.SerializerMethodField()
    cover_url = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()

    class Meta:
        model = Track
        fields = (
            "id", "title", "artist", "artist_name", "album", "album_title", "genre",
            "audio_file", "audio_url", "cover", "cover_url", "duration_seconds",
            "play_count", "liked", "created_at",
        )
        read_only_fields = ("play_count", "created_at")

    def get_audio_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.audio_file.url) if request and obj.audio_file else None

    def get_cover_url(self, obj):
        request = self.context.get("request")
        if request and obj.cover:
            return request.build_absolute_uri(obj.cover.url)
        if request and obj.album and obj.album.cover:
            return request.build_absolute_uri(obj.album.cover.url)
        return None

    def get_liked(self, obj):
        user = self.context["request"].user
        return user.is_authenticated and Like.objects.filter(user=user, track=obj).exists()


class PlaylistTrackSerializer(serializers.ModelSerializer):
    track_detail = TrackSerializer(source="track", read_only=True)
    class Meta:
        model = PlaylistTrack
        fields = ("id", "track", "position", "added_at", "track_detail")
        read_only_fields = ("added_at",)


class PlaylistSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source="owner.username", read_only=True)
    track_count = serializers.IntegerField(source="tracks.count", read_only=True)
    tracks_detail = serializers.SerializerMethodField()
    cover_url = serializers.SerializerMethodField()

    class Meta:
        model = Playlist
        fields = ("id", "owner", "owner_name", "name", "description", "cover", "cover_url",
                  "is_public", "track_count", "tracks_detail", "created_at", "updated_at")
        read_only_fields = ("owner", "created_at", "updated_at")

    def get_tracks_detail(self, obj):
        request = self.context.get("request")
        items = PlaylistTrack.objects.filter(playlist=obj).select_related("track", "track__artist", "track__album")
        return PlaylistTrackSerializer(items, many=True, context={"request": request}).data

    def get_cover_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.cover.url) if request and obj.cover else None


class LikeSerializer(serializers.ModelSerializer):
    track_detail = TrackSerializer(source="track", read_only=True)
    class Meta:
        model = Like
        fields = ("id", "track", "track_detail", "created_at")


class RecentlyPlayedSerializer(serializers.ModelSerializer):
    track_detail = TrackSerializer(source="track", read_only=True)
    class Meta:
        model = RecentlyPlayed
        fields = ("id", "track", "track_detail", "played_at")
