import os
import tempfile
from unittest.mock import patch, MagicMock

from odoo.tests.common import TransactionCase


class TestLocalStorage(TransactionCase):

    def test_upload_and_get_url(self):
        from ..storage.local_storage import LocalStorageProvider
        provider = LocalStorageProvider(self.env)

        file_data = b'test file content'
        storage_key = provider.upload(file_data, 'test.txt', 'text/plain')

        self.assertTrue(storage_key)
        self.assertTrue(storage_key.startswith('media/'))
        self.assertTrue(provider.exists(storage_key))

        url = provider.get_url(storage_key)
        self.assertTrue(url.startswith('/isd_media/file/'))

        # Cleanup
        provider.delete(storage_key)
        self.assertFalse(provider.exists(storage_key))

    def test_delete_nonexistent(self):
        from ..storage.local_storage import LocalStorageProvider
        provider = LocalStorageProvider(self.env)
        # Should not raise
        provider.delete('media/nonexistent.txt')


class TestS3Storage(TransactionCase):

    def test_get_url_with_public_base(self):
        from ..storage.s3_storage import S3StorageProvider
        ICP = self.env['ir.config_parameter'].sudo()
        ICP.set_param('isd_media.s3_public_base_url', 'https://cdn.example.com')

        provider = S3StorageProvider(self.env)
        url = provider.get_url('media/test.jpg')
        self.assertEqual(url, 'https://cdn.example.com/media/test.jpg')

    def test_get_url_without_public_base(self):
        from ..storage.s3_storage import S3StorageProvider
        ICP = self.env['ir.config_parameter'].sudo()
        ICP.set_param('isd_media.s3_public_base_url', '')
        ICP.set_param('isd_media.s3_bucket_name', 'my-bucket')
        ICP.set_param('isd_media.s3_region', 'ap-southeast-1')
        ICP.set_param('isd_media.s3_endpoint_url', '')

        provider = S3StorageProvider(self.env)
        url = provider.get_url('media/test.jpg')
        self.assertEqual(url, 'https://my-bucket.s3.ap-southeast-1.amazonaws.com/media/test.jpg')
