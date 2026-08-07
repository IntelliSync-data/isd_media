import base64
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestIsdMedia(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = cls.env['isd.media.category'].create({
            'name': 'Test Category',
            'sort_order': 1,
        })
        cls.tag = cls.env['isd.media.tag'].create({
            'name': 'test-tag',
        })
        # 1x1 transparent PNG
        cls.test_image_data = base64.b64encode(
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
            b'\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89'
            b'\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01'
            b'\r\n\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        )

    def test_create_media(self):
        media = self.env['isd.media'].create({
            'name': 'Test Image',
            'media_type': 'image',
            'category_ids': [(4, self.category.id)],
            'media_file': self.test_image_data,
            'file_name': 'test.png',
        })
        self.assertTrue(media.id)
        self.assertEqual(media.media_type, 'image')
        self.assertTrue(media.storage_key)
        self.assertEqual(media.storage_provider, 'local')
        self.assertTrue(media.file_size > 0)
        self.assertEqual(media.mime_type, 'image/png')

    def test_create_media_without_file_fails(self):
        with self.assertRaises(ValidationError):
            self.env['isd.media'].create({
                'name': 'No File',
                'media_type': 'image',
                'category_ids': [(4, self.category.id)],
            })

    def test_file_size_limit(self):
        self.env['ir.config_parameter'].sudo().set_param('isd_media.max_image_upload_size', '0.00001')
        with self.assertRaises(ValidationError):
            self.env['isd.media'].create({
                'name': 'Too Large',
                'media_type': 'image',
                'category_ids': [(4, self.category.id)],
                'media_file': self.test_image_data,
                'file_name': 'big.png',
            })

    def test_publish_schedule_always(self):
        media = self.env['isd.media'].create({
            'name': 'Always Published',
            'media_type': 'image',
            'category_ids': [(4, self.category.id)],
            'media_file': self.test_image_data,
            'file_name': 'test.png',
        })
        self.assertTrue(media.is_published)

    def test_publish_schedule_future(self):
        from datetime import datetime, timedelta
        media = self.env['isd.media'].create({
            'name': 'Future',
            'media_type': 'image',
            'category_ids': [(4, self.category.id)],
            'media_file': self.test_image_data,
            'file_name': 'test.png',
            'publish_from': datetime.now() + timedelta(days=1),
        })
        self.assertFalse(media.is_published)

    def test_publish_schedule_past(self):
        from datetime import datetime, timedelta
        media = self.env['isd.media'].create({
            'name': 'Past',
            'media_type': 'image',
            'category_ids': [(4, self.category.id)],
            'media_file': self.test_image_data,
            'file_name': 'test.png',
            'publish_to': datetime.now() - timedelta(days=1),
        })
        self.assertFalse(media.is_published)

    def test_category_version_increment(self):
        ICP = self.env['ir.config_parameter'].sudo()
        ICP.set_param('isd_media.api_version', '0')
        self.env['isd.media.category'].create({'name': 'V Test'})
        version = int(ICP.get_param('isd_media.api_version', '0'))
        self.assertGreater(version, 0)

    def test_media_version_increment(self):
        ICP = self.env['ir.config_parameter'].sudo()
        ICP.set_param('isd_media.api_version', '0')
        self.env['isd.media'].create({
            'name': 'V Test',
            'media_type': 'image',
            'category_ids': [(4, self.category.id)],
            'media_file': self.test_image_data,
            'file_name': 'test.png',
        })
        version = int(ICP.get_param('isd_media.api_version', '0'))
        self.assertGreater(version, 0)

    def test_file_size_display(self):
        media = self.env['isd.media'].create({
            'name': 'Size Test',
            'media_type': 'image',
            'category_ids': [(4, self.category.id)],
            'media_file': self.test_image_data,
            'file_name': 'test.png',
        })
        self.assertTrue(media.file_size_display)
