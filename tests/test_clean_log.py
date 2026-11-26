"""
What the uploader hides before a log leaves the device: the tokens and identifiers Plex Uno, SiloMod (SM4K),
JellyMod (JM4K) and CoreTube runs leave in kodi.log, mostly through Kodi's own lines (the URL it plays, its network
requests). Each sample line has the shape those add-ons hand to Kodi.
"""

import unittest

from lib.loguploader import Main


def clean(text):
    return Main.cleanLog(None, text)


class PlexUnoTest(unittest.TestCase):
    """The masks the uploader had for Plex, kept."""

    def test_plex_token_in_a_played_url(self):
        line = 'VideoPlayer::OpenFile: http://192.168.1.250:32400/library/parts/12/file.mkv?X-Plex-Token=PLEXSECRET123'

        cleaned = clean(line)

        self.assertNotIn('PLEXSECRET123', cleaned)
        self.assertNotIn('192.168.1.250', cleaned)
        self.assertIn('/library/parts/12/file.mkv', cleaned)

    def test_user_and_password_in_a_source_url(self):
        self.assertEqual(clean('smb://someone:hunter2@nas/films'), 'smb://USER:PASSWORD@nas/films')

    def test_client_identifier(self):
        self.assertNotIn('abcdef0123456789xyz', clean('clientIdentifier:abcdef0123456789xyz'))


class JellyModTest(unittest.TestCase):
    TOKEN = 'JFSECRET0123456789abcdef'
    DEVICE = 'a1b2c3d4e5f60718293a4b5c'

    def test_token_in_the_played_urls_authorization_header(self):
        # jellynet.playback: url|Authorization=<the MediaBrowser header, URL-encoded>
        line = (
            'VideoPlayer::OpenFile: http://192.168.1.250:8096/Videos/0f1e2d3c/stream?static=true'
            f'|Authorization=MediaBrowser%20Token%3D%22{self.TOKEN}%22%2C%20Client%3D%22JellyMod%22%2C%20'
            f'Version%3D%220.1.0%22%2C%20DeviceId%3D%22{self.DEVICE}%22%2C%20Device%3D%22Kodi6%22'
        )

        cleaned = clean(line)

        self.assertNotIn(self.TOKEN, cleaned)
        self.assertNotIn(self.DEVICE, cleaned)
        self.assertIn('/Videos/0f1e2d3c/stream?static=true', cleaned)
        self.assertIn('Client%3D%22JellyMod%22', cleaned)

    def test_token_in_a_plain_header(self):
        line = f'Authorization: MediaBrowser Token="{self.TOKEN}", Client="JellyMod", DeviceId="{self.DEVICE}"'

        cleaned = clean(line)

        self.assertNotIn(self.TOKEN, cleaned)
        self.assertNotIn(self.DEVICE, cleaned)
        self.assertIn('Client="JellyMod"', cleaned)

    def test_api_key_and_emby_token(self):
        cleaned = clean(
            'CTextureCache: http://jf.lan:8096/Items/9a/Images/Primary?maxWidth=400&api_key=JFAPIKEY0123\n'
            "headers {'X-Emby-Token': 'JFEMBYTOKEN0123'}"
        )

        self.assertNotIn('JFAPIKEY0123', cleaned)
        self.assertNotIn('JFEMBYTOKEN0123', cleaned)
        self.assertIn('maxWidth=400', cleaned)


class SiloModTest(unittest.TestCase):
    def test_stream_token_in_a_played_url(self):
        # silonet.playback: Silo's signed stream URLs carry their token in st
        cleaned = clean(
            'VideoPlayer::OpenFile: http://silo.lan:8090/api/v2/stream/77/index.m3u8?st=SILOSTREAM0123&start=0'
        )

        self.assertNotIn('SILOSTREAM0123', cleaned)
        self.assertIn('/api/v2/stream/77/index.m3u8', cleaned)
        self.assertIn('start=0', cleaned)

    def test_bearer_and_session_tokens(self):
        cleaned = clean(
            'Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0.SIGNATURE0123\n'
            "{'access_token': 'SILOACCESS0123', 'refresh_token': 'SILOREFRESH0123', 'profile_token': 'SILOPROFILE0123'}"
        )

        for secret in ('eyJhbGciOiJIUzI1NiJ9', 'SIGNATURE0123', 'SILOACCESS0123', 'SILOREFRESH0123', 'SILOPROFILE0123'):
            self.assertNotIn(secret, cleaned)

    def test_device_id_header(self):
        self.assertNotIn('silodevice0123456789', clean("'X-Silo-Device-Id': 'silodevice0123456789'"))


class CoreTubeTest(unittest.TestCase):
    def test_its_error_line_reads_as_written(self):
        line = '## TizenTube Addon Error: systemd-run failed: Unit coretube.service already exists.'

        self.assertEqual(clean(line), line)


class OrdinaryLinesTest(unittest.TestCase):
    def test_parameters_that_only_end_like_secret_ones_stay(self):
        line = 'GET /Items?first=10&start=0&SortBy=SortName'

        self.assertEqual(clean(line), line)
