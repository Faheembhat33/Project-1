from django.core.management.base import BaseCommand
from music.models import Artist, Album, Track

class Command(BaseCommand):
    help = "Create starter SonicWave catalogue records (no audio files are added)."

    def handle(self, *args, **options):
        starter = [
            ("Nova Bloom", "Electronic", "After Hours", "Midnight City Lights"),
            ("Mila June", "Indie", "Golden Hour", "Golden"),
            ("The Coastline", "Chill", "Blue State", "Ocean Drive"),
            ("Arlo West", "R&B", "Soft Focus", "Velvet Skies"),
        ]
        for artist_name, genre, album_title, track_title in starter:
            artist, _ = Artist.objects.get_or_create(name=artist_name)
            album, _ = Album.objects.get_or_create(title=album_title, artist=artist)
            # Tracks require an uploaded audio file; catalogue records are created in admin.
            self.stdout.write(f"Ready: {artist.name} / {album.title} / {track_title} ({genre})")
        self.stdout.write(self.style.SUCCESS(
            "Demo artists and albums created. Add tracks and audio files in /admin/."
        ))
