"""Static document checks; photos may still be in the original tree before migration."""
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'public'
IDS = {'b', 'barn', 'cottage', 'cotton', 'd', 'e', 'firethorn', 'rocksprings-a', 'rocksprings-b', 'shankle'}


class Document(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.elements = []
        self.feed(path.read_text())

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))


class StaticSiteTests(unittest.TestCase):
    def test_required_pages(self):
        expected = ['index.html', 'apply/index.html', 'apply/app.html', 'apply/maintenance.html', 'admin/index.html']
        expected += [f'apply/p/{key}.html' for key in IDS]
        for path in expected:
            with self.subTest(path=path):
                self.assertTrue((PUBLIC / path).is_file(), path)

    def test_documents_and_local_links(self):
        pages = list(PUBLIC.rglob('*.html'))
        self.assertGreaterEqual(len(pages), 15)
        for page in pages:
            text = page.read_text()
            doc = Document(page)
            self.assertNotIn('<?php', text)
            self.assertNotRegex(text.lower(), r'bootstrap|jquery|cdn\.|autoplay|data-bs-')
            self.assertTrue(any(t == 'meta' and a.get('name') == 'robots' and 'noindex' in a.get('content', '') for t, a in doc.elements), page)
            for tag, attrs in doc.elements:
                if tag == 'img':
                    self.assertTrue(attrs.get('alt'), page)
                if tag in ('script', 'link'):
                    resource = attrs.get('src', attrs.get('href', ''))
                    self.assertFalse(urlsplit(resource).netloc, resource)
                for attr in ('src', 'href'):
                    value = attrs.get(attr, '')
                    url = urlsplit(value)
                    if not value or url.scheme or url.netloc:
                        continue
                    if not url.path:
                        if url.fragment:
                            self.assertTrue(any(a.get('id') == unquote(url.fragment) for _, a in doc.elements), f'{page}: {value}')
                        continue
                    target = (PUBLIC / unquote(url.path).lstrip('/')) if url.path.startswith('/') else page.parent / unquote(url.path)
                    if url.path.endswith('/'):
                        target /= 'index.html'
                    self.assertTrue(target.is_file(), f'{page}: {value}')

    def test_forms_preserve_destinations(self):
        for page, form in [('app', 'shrMUhRNEnnrSTwpN'), ('maintenance', 'shr26oqd6WR6mSa4C')]:
            doc = Document(PUBLIC / f'apply/{page}.html')
            frames = [a for t, a in doc.elements if t == 'iframe']
            self.assertEqual(len(frames), 1)
            self.assertEqual(frames[0]['src'], f'https://airtable.com/embed/{form}?backgroundColor=red')
            self.assertTrue(frames[0].get('title'))
            self.assertTrue(any(t == 'a' and a.get('href') == f'https://airtable.com/{form}' for t, a in doc.elements))

    def test_listing_fails_closed_and_admin_is_fixed(self):
        doc = Document(PUBLIC / 'apply/index.html')
        cards = [a for _, a in doc.elements if 'data-property' in a]
        self.assertEqual({a['data-property'] for a in cards}, IDS)
        self.assertTrue(all('hidden' in a for a in cards))
        self.assertTrue(any(t == 'noscript' for t, _ in doc.elements))
        admin = Document(PUBLIC / 'admin/index.html')
        self.assertEqual({a['data-property'] for t, a in admin.elements if t == 'button' and 'data-property' in a}, IDS)
        self.assertFalse(any(t == 'input' and a.get('type') == 'password' for t, a in admin.elements))

    def test_gallery_for_every_property(self):
        for key in IDS:
            doc = Document(PUBLIC / f'apply/p/{key}.html')
            self.assertTrue(any(t == 'dialog' for t, _ in doc.elements), key)
            self.assertTrue(any(t == 'a' and 'data-photo' in a for t, a in doc.elements), key)
            self.assertTrue(any(t == 'a' and a.get('href') == '/apply/app.html' for t, a in doc.elements), key)

    def test_assets_are_library_free(self):
        assets = list((PUBLIC / 'assets').glob('*'))
        self.assertTrue(assets)
        for asset in assets:
            text = asset.read_text()
            self.assertNotRegex(text.lower(), r'bootstrap|jquery|https?://|@import')
        visibility = (PUBLIC / 'assets/visibility.js').read_text()
        admin = (PUBLIC / 'assets/admin.js').read_text()
        gallery = (PUBLIC / 'assets/gallery.js').read_text()
        for token in ('/api/visibility', "credentials: 'same-origin'", 'validate', 'card.hidden = true'):
            self.assertIn(token, visibility)
        for token in ('/api/admin/visibility', "method: 'PUT'", "'X-Pops-Admin': '1'", 'response.status === 409', 'response.status === 429', 'revision: saved.revision'):
            self.assertIn(token, admin)
        self.assertNotRegex(admin, r'localStorage|sessionStorage|password')
        for token in ('showModal', 'ArrowLeft', 'ArrowRight', 'dialog.close()', "addEventListener('close'"):
            self.assertIn(token, gallery)

    def test_all_original_property_photos_accessible(self):
        source = ROOT / 'apply/pics'
        if not source.exists():
            source = PUBLIC / 'apply/pics'
        linked = set()
        for page in (PUBLIC / 'apply/p').glob('*.html'):
            for tag, attrs in Document(page).elements:
                if tag == 'a' and 'data-photo' in attrs:
                    linked.add(unquote(attrs['href']))
        for photo in source.rglob('*'):
            if photo.is_file() and photo.parent.name != 'icons':
                self.assertIn('/apply/pics/' + str(photo.relative_to(source)), linked)


if __name__ == '__main__':
    unittest.main()
