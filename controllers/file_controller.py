import base64
import logging
import os

from odoo import http
from odoo.http import request
from odoo.tools import config

_logger = logging.getLogger(__name__)


class IsdMediaFileController(http.Controller):
    """Controller to serve locally stored media files."""

    @http.route('/isd_media/thumbnail/<int:media_id>', type='http', auth='public', csrf=False)
    def serve_thumbnail(self, media_id, **kwargs):
        """Serve media thumbnail publicly."""
        media = request.env['isd.media'].sudo().browse(media_id)
        if not media.exists() or not media.thumbnail:
            return request.not_found()

        image_data = base64.b64decode(media.thumbnail)
        headers = [
            ('Content-Type', 'image/jpeg'),
            ('Content-Length', str(len(image_data))),
            ('Cache-Control', 'public, max-age=31536000'),
        ]
        return request.make_response(image_data, headers=headers)

    @http.route('/isd_media/file/<path:storage_key>', type='http', auth='public', csrf=False)
    def serve_file(self, storage_key, **kwargs):
        """Serve a file from local storage."""
        data_dir = config.get('data_dir', '/var/lib/odoo')
        db_name = request.env.cr.dbname
        media_dir = os.path.join(data_dir, 'filestore', db_name, 'isd_media')
        file_path = os.path.join(media_dir, storage_key)

        # Security: prevent directory traversal
        real_media_dir = os.path.realpath(media_dir)
        real_file_path = os.path.realpath(file_path)
        if not real_file_path.startswith(real_media_dir):
            return request.not_found()

        if not os.path.exists(file_path):
            return request.not_found()

        import mimetypes
        mime_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'

        with open(file_path, 'rb') as f:
            file_data = f.read()

        headers = [
            ('Content-Type', mime_type),
            ('Content-Length', str(len(file_data))),
            ('Cache-Control', 'public, max-age=31536000'),
        ]

        if kwargs.get('download'):
            filename = os.path.basename(file_path)
            headers.append(('Content-Disposition', f'attachment; filename="{filename}"'))

        return request.make_response(file_data, headers=headers)
