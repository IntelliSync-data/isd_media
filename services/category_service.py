class CategoryService:
    """Service layer for category business logic."""

    def __init__(self, env):
        self.env = env

    def get_categories(self):
        """Get all active categories sorted by sort_order.

        Returns:
            list of category dicts
        """
        Category = self.env['isd.media.category'].sudo()
        records = Category.search(
            [('active', '=', True)],
            order='sort_order asc',
        )

        items = []
        for rec in records:
            avatar_url = f'/web/image/isd.media.category/{rec.id}/avatar' if rec.avatar else ''
            items.append({
                'id': rec.id,
                'name': rec.name,
                'avatar': avatar_url,
                'sort_order': rec.sort_order,
            })

        return items
