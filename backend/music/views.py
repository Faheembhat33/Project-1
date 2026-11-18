from django.contrib.auth.models import User
from django.db.models import Q, F
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Artist, Album, Track, Playlist, PlaylistTrack, Like, RecentlyPlayed
from .serializers import (
    RegisterSerializer, UserSerializer, ArtistSerializer, AlbumSerializer,
    TrackSerializer, PlaylistSerializer, LikeSerializer, RecentlyPlayedSerializer,
)
from .permissions import IsOwnerOrPublicReadOnly


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        return self.request.user


class ArtistViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Artist.objects.prefetch_related("albums", "tracks").all()
    serializer_class = ArtistSerializer
    search_fields = ["name", "bio"]
    ordering_fields = ["name", "created_at"]

    @action(detail=True, methods=["get"])
    def tracks(self, request, pk=None):
        artist = self.get_object()
        qs = Track.objects.filter(artist=artist, is_published=True).select_related("artist", "album")
        return Response(TrackSerializer(qs, many=True, context={"request": request}).data)

    @action(detail=True, methods=["get"])
    def albums(self, request, pk=None):
        artist = self.get_object()
        qs = Album.objects.filter(artist=artist)
        return Response(AlbumSerializer(qs, many=True, context={"request": request}).data)


class AlbumViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Album.objects.select_related("artist").prefetch_related("tracks").all()
    serializer_class = AlbumSerializer
    search_fields = ["title", "artist__name"]
    ordering_fields = ["release_date", "title"]

    @action(detail=True, methods=["get"])
    def tracks(self, request, pk=None):
        album = self.get_object()
        qs = Track.objects.filter(album=album, is_published=True).select_related("artist", "album")
        return Response(TrackSerializer(qs, many=True, context={"request": request}).data)


class TrackViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Track.objects.filter(is_published=True).select_related("artist", "album")
    serializer_class = TrackSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    search_fields = ["title", "artist__name", "album__title", "genre"]
    filterset_fields = ["genre", "artist", "album"]
    ordering_fields = ["created_at", "play_count", "title", "duration_seconds"]

    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def trending(self, request):
        qs = self.get_queryset().order_by("-play_count", "-created_at")[:20]
        return Response(self.get_serializer(qs, many=True).data)

    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def new_releases(self, request):
        qs = self.get_queryset().order_by("-created_at")[:20]
        return Response(self.get_serializer(qs, many=True).data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def played(self, request, pk=None):
        track = self.get_object()
        Track.objects.filter(pk=track.pk).update(play_count=F("play_count") + 1)
        recent, _ = RecentlyPlayed.objects.update_or_create(
            user=request.user, track=track
        )
        recent.refresh_from_db()
        return Response({"message": "Play recorded"}, status=status.HTTP_200_OK)


class PlaylistViewSet(viewsets.ModelViewSet):
    serializer_class = PlaylistSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrPublicReadOnly]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Playlist.objects.filter(is_public=True)
        return Playlist.objects.filter(Q(owner=user) | Q(is_public=True)).distinct().select_related("owner")

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["post"], url_path="tracks")
    def add_track(self, request, pk=None):
        playlist = self.get_object()
        track_id = request.data.get("track_id")
        track = get_object_or_404(Track, pk=track_id, is_published=True)
        item, created = PlaylistTrack.objects.get_or_create(
            playlist=playlist, track=track,
            defaults={"position": playlist.playlisttrack_set.count()}
        )
        return Response(
            {"message": "Track added" if created else "Track already in playlist"},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

    @action(detail=True, methods=["delete"], url_path=r"tracks/(?P<track_id>[^/.]+)")
    def remove_track(self, request, pk=None, track_id=None):
        playlist = self.get_object()
        deleted, _ = PlaylistTrack.objects.filter(playlist=playlist, track_id=track_id).delete()
        if not deleted:
            return Response({"detail": "Track not found in playlist"}, status=404)
        return Response(status=status.HTTP_204_NO_CONTENT)


class LikeListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        likes = Like.objects.filter(user=request.user).select_related("track", "track__artist", "track__album")
        return Response(LikeSerializer(likes, many=True, context={"request": request}).data)
    def post(self, request):
        track = get_object_or_404(Track, pk=request.data.get("track_id"), is_published=True)
        like, created = Like.objects.get_or_create(user=request.user, track=track)
        return Response({"liked": True, "track_id": track.id}, status=201 if created else 200)
    def delete(self, request):
        track_id = request.data.get("track_id")
        Like.objects.filter(user=request.user, track_id=track_id).delete()
        return Response(status=204)


class RecentListView(generics.ListAPIView):
    serializer_class = RecentlyPlayedSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return RecentlyPlayed.objects.filter(user=self.request.user).select_related(
            "track", "track__artist", "track__album"
        )[:50]


class RecentCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        track = get_object_or_404(Track, pk=request.data.get("track_id"), is_published=True)
        RecentlyPlayed.objects.update_or_create(user=request.user, track=track)
        Track.objects.filter(pk=track.pk).update(play_count=F("play_count") + 1)
        return Response({"message": "Recently played updated"}, status=200)
