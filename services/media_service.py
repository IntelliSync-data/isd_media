from odoo import fields


class MediaService:
    """Service layer for media business logic."""

    def __init__(self, env):
        self.env = env
        self.ICP = env['ir.config_parameter'].sudo()

    def get_media_list(self, page=1, limit=None, category_id=None):
        """Get paginated list of active, published media.

        Args:
            page: Page number (1-based)
            limit: Items per page
            category_id: Filter by category ID

        Returns:
            dict with items, page, limit, total
        """
        max_return = int(self.ICP.get_param('isd_media.api_max_return', '100'))

        if not limit or limit <= 0:
            limit = max_return
        if limit > max_return:
            limit = max_return
        if page < 1:
            page = 1

        domain = [('active', '=', True), ('is_published', '=', True)]

        # Only include media with at least one active category
        domain.append(('category_ids.active', '=', True))

        if category_id:
            domain.append(('category_ids', 'in', [category_id]))

        Media = self.env['isd.media'].sudo()
        total = Media.search_count(domain)
        offset = (page - 1) * limit
        records = Media.search(domain, limit=limit, offset=offset, order='sort_order asc, id desc')

        items = []
        for rec in records:
            items.append(self._serialize_media(rec))

        return {
            'items': items,
            'page': page,
            'limit': limit,
            'total': total,
        }

    def get_version(self):
        """Get current API version and last updated timestamp."""
        version = int(self.ICP.get_param('isd_media.api_version', '0'))
        last_updated = self.ICP.get_param('isd_media.api_last_updated', '')
        return {
            'version': version,
            'last_updated': last_updated or None,
        }

    def _serialize_media(self, record):
        """Serialize a media record to dict for API response."""
        categories = []
        for cat in record.category_ids.filtered('active'):
            categories.append({
                'id': cat.id,
                'name': cat.name,
            })

        tags = []
        for tag in record.tag_ids.filtered('active'):
            tags.append({
                'id': tag.id,
                'name': tag.name,
            })

        result = {
            'id': record.id,
            'name': record.name or '',
            'type': record.media_type,
            'display_size': record.display_size or 'medium',
            'categories': categories,
            'tags': tags,
            'url': record.public_url or '',
            'thumbnail_url': record.thumbnail_url or '',
            'mime_type': record.mime_type or '',
            'size': record.file_size,
            'created_at': record.create_date.isoformat() if record.create_date else None,
        }

        if record.media_type in ('facebook', 'youtube'):
            result['external_url'] = record.external_url or ''

        return result
