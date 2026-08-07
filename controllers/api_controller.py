import json
import logging

from odoo import http
from odoo.http import request

from ..services.media_service import MediaService
from ..services.category_service import CategoryService

_logger = logging.getLogger(__name__)


class IsdMediaApiController(http.Controller):
    """REST API controller for ISD Media Service."""

    def _check_origin(self):
        """Check if request origin is allowed. Returns error response or None."""
        origin = request.httprequest.headers.get('Origin', '')
        if not origin:
            return None

        allowed = request.env['isd.media.allowed_origin'].sudo().search([
            ('active', '=', True),
        ])
        if not allowed:
            # No origins configured = allow all
            return None

        allowed_urls = [o.name.rstrip('/') for o in allowed]
        if origin.rstrip('/') not in allowed_urls:
            return self._error_response(403, 'Origin not allowed')
        return None

    def _success_response(self, data=None, meta=None, code=200, message=''):
        """Build standard success response."""
        body = {
            'success': True,
            'code': code,
            'message': message,
            'meta': meta or {},
            'data': data if data is not None else [],
        }
        headers = self._cors_headers()
        return request.make_response(
            json.dumps(body, default=str),
            headers=[('Content-Type', 'application/json')] + headers,
            status=code,
        )

    def _error_response(self, code, message):
        """Build standard error response."""
        body = {
            'success': False,
            'code': code,
            'message': message,
            'meta': {},
            'data': [],
        }
        headers = self._cors_headers()
        return request.make_response(
            json.dumps(body, default=str),
            headers=[('Content-Type', 'application/json')] + headers,
            status=code,
        )

    def _cors_headers(self):
        """Build CORS headers from allowed origins."""
        origin = request.httprequest.headers.get('Origin', '')
        headers = [
            ('Access-Control-Allow-Methods', 'GET, OPTIONS'),
            ('Access-Control-Allow-Headers', 'Content-Type, Authorization'),
            ('Access-Control-Max-Age', '3600'),
        ]
        if origin:
            headers.append(('Access-Control-Allow-Origin', origin))
        return headers

    # --- CORS Preflight ---
    @http.route([
        '/api/v1/categories',
        '/api/v1/media',
        '/api/v1/version',
    ], type='http', auth='public', methods=['OPTIONS'], csrf=False)
    def options_handler(self, **kwargs):
        headers = self._cors_headers()
        return request.make_response('', headers=headers, status=204)

    # --- GET /api/v1/categories ---
    @http.route('/api/v1/categories', type='http', auth='public', methods=['GET'], csrf=False)
    def get_categories(self, **kwargs):
        origin_error = self._check_origin()
        if origin_error:
            return origin_error

        try:
            service = CategoryService(request.env)
            items = service.get_categories()
            return self._success_response(data=items)
        except Exception as e:
            _logger.exception("Error in GET /api/v1/categories")
            return self._error_response(500, str(e))

    # --- GET /api/v1/media ---
    @http.route('/api/v1/media', type='http', auth='public', methods=['GET'], csrf=False)
    def get_media(self, **kwargs):
        origin_error = self._check_origin()
        if origin_error:
            return origin_error

        try:
            page = int(kwargs.get('page', 1))
            limit = int(kwargs.get('limit', 0)) or None
            category_id = int(kwargs.get('categoryId', 0)) or None

            service = MediaService(request.env)
            result = service.get_media_list(page=page, limit=limit, category_id=category_id)

            meta = {
                'page': result['page'],
                'limit': result['limit'],
                'total': result['total'],
            }
            return self._success_response(data=result['items'], meta=meta)
        except Exception as e:
            _logger.exception("Error in GET /api/v1/media")
            return self._error_response(500, str(e))

    # --- GET /api/v1/version ---
    @http.route('/api/v1/version', type='http', auth='public', methods=['GET'], csrf=False)
    def get_version(self, **kwargs):
        origin_error = self._check_origin()
        if origin_error:
            return origin_error

        try:
            service = MediaService(request.env)
            result = service.get_version()
            return self._success_response(data=result)
        except Exception as e:
            _logger.exception("Error in GET /api/v1/version")
            return self._error_response(500, str(e))
