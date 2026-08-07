import logging
import os

from odoo import http
from odoo.http import request
from odoo.tools import config

_logger = logging.getLogger(__name__)


class IsdMediaFileController(http.Controller):
    """Controller to serve locally stored media files."""

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

        return request.make_response(
            file_data,
            headers=[
                ('Content-Type', mime_type),
                ('Content-Length', str(len(file_data))),
                ('Cache-Control', 'public, max-age=31536000'),
            ],
        )
