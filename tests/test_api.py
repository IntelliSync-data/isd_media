import base64
from odoo.tests.common import HttpCase


class TestMediaApi(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = cls.env['isd.media.category'].create({
            'name': 'API Test Category',
            'sort_order': 1,
        })
        # 1x1 transparent PNG
        test_image = base64.b64encode(
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
            b'\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89'
            b'\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01'
            b'\r\n\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        )
        cls.media = cls.env['isd.media'].create({
            'name': 'API Test Image',
            'media_type': 'image',
            'category_ids': [(4, cls.category.id)],
            'media_file': test_image,
            'file_name': 'api_test.png',
        })

    def test_get_categories(self):
        response = self.url_open('/api/v1/categories')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIsInstance(data['data'], list)
        names = [c['name'] for c in data['data']]
        self.assertIn('API Test Category', names)

    def test_get_media(self):
        response = self.url_open('/api/v1/media')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('page', data['meta'])
        self.assertIn('limit', data['meta'])
        self.assertIn('total', data['meta'])

    def test_get_media_with_category_filter(self):
        response = self.url_open(f'/api/v1/media?categoryId={self.category.id}')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])

    def test_get_media_pagination(self):
        response = self.url_open('/api/v1/media?page=1&limit=5')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['meta']['page'], 1)
        self.assertEqual(data['meta']['limit'], 5)

    def test_get_version(self):
        response = self.url_open('/api/v1/version')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('version', data['data'])
        self.assertIn('last_updated', data['data'])
