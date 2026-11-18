from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from music.views import ArtistViewSet, AlbumViewSet, TrackViewSet, PlaylistViewSet
from music.views import RegisterView, MeView, LikeListView, RecentListView, RecentCreateView

router = DefaultRouter()
router.register("artists", ArtistViewSet, basename="artist")
router.register("albums", AlbumViewSet, basename="album")
router.register("tracks", TrackViewSet, basename="track")
router.register("playlists", PlaylistViewSet, basename="playlist")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/register/", RegisterView.as_view(), name="register"),
    path("api/auth/me/", MeView.as_view(), name="me"),
    path("api/auth/", include("rest_framework_simplejwt.urls")),
    path("api/likes/", LikeListView.as_view(), name="likes"),
    path("api/recently-played/", RecentListView.as_view(), name="recent-list"),
    path("api/recently-played/add/", RecentCreateView.as_view(), name="recent-add"),
    path("api/", include(router.urls)),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
