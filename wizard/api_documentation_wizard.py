from odoo import fields, models, api


class IsdMediaApiDocWizard(models.TransientModel):
    _name = 'isd.media.api.doc.wizard'
    _description = 'Media API Documentation'

    documentation_html = fields.Html('Documentation', compute='_compute_documentation',
                                     sanitize=False, sanitize_form=False, sanitize_tags=False)

    @api.depends_context('uid')
    def _compute_documentation(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', '')
        for record in self:
            record.documentation_html = self._generate_docs(base_url)

    def _generate_docs(self, base_url):
        return f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 900px; margin: 0 auto; padding: 20px;">
            <h1 style="color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px;">
                ISD Media Service - REST API Documentation
            </h1>
            <p style="color: #7f8c8d;">Base URL: <code style="background: #ecf0f1; padding: 2px 6px; border-radius: 3px;">{base_url}</code></p>

            <h2 style="color: #2c3e50; margin-top: 30px;">Response Format</h2>
            <pre style="background: #2d3436; color: #dfe6e9; padding: 15px; border-radius: 6px; overflow-x: auto;">{{
    "success": true,
    "code": 200,
    "message": "",
    "meta": {{}},
    "data": []
}}</pre>

            <hr style="margin: 30px 0; border: 1px solid #ecf0f1;"/>

            <!-- GET /api/v1/categories -->
            <h2 style="color: #2c3e50;">
                <span style="background: #27ae60; color: white; padding: 3px 10px; border-radius: 4px; font-size: 14px; margin-right: 10px;">GET</span>
                /api/v1/categories
            </h2>
            <p>Get all active categories sorted by sort_order.</p>

            <h4>Response</h4>
            <pre style="background: #2d3436; color: #dfe6e9; padding: 15px; border-radius: 6px; overflow-x: auto;">{{
    "success": true,
    "code": 200,
    "message": "",
    "meta": {{}},
    "data": [
        {{
            "id": 1,
            "name": "Banner",
            "avatar": "/web/image/isd.media.category/1/avatar",
            "sort_order": 10
        }}
    ]
}}</pre>

            <h4>cURL Example</h4>
            <pre style="background: #2d3436; color: #dfe6e9; padding: 15px; border-radius: 6px; overflow-x: auto;">curl -X GET {base_url}/api/v1/categories</pre>

            <hr style="margin: 30px 0; border: 1px solid #ecf0f1;"/>

            <!-- GET /api/v1/media -->
            <h2 style="color: #2c3e50;">
                <span style="background: #27ae60; color: white; padding: 3px 10px; border-radius: 4px; font-size: 14px; margin-right: 10px;">GET</span>
                /api/v1/media
            </h2>
            <p>Get paginated list of active, published media.</p>

            <h4>Query Parameters</h4>
            <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
                <thead>
                    <tr style="background: #ecf0f1;">
                        <th style="padding: 8px 12px; text-align: left; border: 1px solid #ddd;">Parameter</th>
                        <th style="padding: 8px 12px; text-align: left; border: 1px solid #ddd;">Type</th>
                        <th style="padding: 8px 12px; text-align: left; border: 1px solid #ddd;">Description</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="padding: 8px 12px; border: 1px solid #ddd;"><code>page</code></td>
                        <td style="padding: 8px 12px; border: 1px solid #ddd;">Integer</td>
                        <td style="padding: 8px 12px; border: 1px solid #ddd;">Page number (default: 1)</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 12px; border: 1px solid #ddd;"><code>limit</code></td>
                        <td style="padding: 8px 12px; border: 1px solid #ddd;">Integer</td>
                        <td style="padding: 8px 12px; border: 1px solid #ddd;">Items per page (default/max: API Maximum Return setting)</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 12px; border: 1px solid #ddd;"><code>categoryId</code></td>
                        <td style="padding: 8px 12px; border: 1px solid #ddd;">Integer</td>
                        <td style="padding: 8px 12px; border: 1px solid #ddd;">Filter by category ID</td>
                    </tr>
                </tbody>
            </table>

            <h4>Response</h4>
            <pre style="background: #2d3436; color: #dfe6e9; padding: 15px; border-radius: 6px; overflow-x: auto;">{{
    "success": true,
    "code": 200,
    "message": "",
    "meta": {{
        "page": 1,
        "limit": 20,
        "total": 58
    }},
    "data": [
        {{
            "id": 1,
            "name": "Home Banner",
            "type": "image",
            "categories": [{{"id": 1, "name": "Banner"}}],
            "tags": [{{"id": 1, "name": "featured"}}],
            "url": "/isd_media/file/media/abc123.jpg",
            "thumbnail_url": "/web/image/isd.media/1/thumbnail",
            "mime_type": "image/jpeg",
            "size": 245760,
            "created_at": "2026-08-06T10:30:00"
        }}
    ]
}}</pre>

            <h4>cURL Examples</h4>
            <pre style="background: #2d3436; color: #dfe6e9; padding: 15px; border-radius: 6px; overflow-x: auto;"># Get all media (default pagination)
curl -X GET {base_url}/api/v1/media

# Get page 2 with 10 items per page
curl -X GET "{base_url}/api/v1/media?page=2&amp;limit=10"

# Filter by category
curl -X GET "{base_url}/api/v1/media?categoryId=1"</pre>

            <hr style="margin: 30px 0; border: 1px solid #ecf0f1;"/>

            <!-- GET /api/v1/version -->
            <h2 style="color: #2c3e50;">
                <span style="background: #27ae60; color: white; padding: 3px 10px; border-radius: 4px; font-size: 14px; margin-right: 10px;">GET</span>
                /api/v1/version
            </h2>
            <p>Get current data version for cache optimization. Version increments on any media or category change.</p>

            <h4>Response</h4>
            <pre style="background: #2d3436; color: #dfe6e9; padding: 15px; border-radius: 6px; overflow-x: auto;">{{
    "success": true,
    "code": 200,
    "message": "",
    "meta": {{}},
    "data": {{
        "version": 15,
        "last_updated": "2026-08-06T22:30:00"
    }}
}}</pre>

            <h4>Usage Flow</h4>
            <pre style="background: #f8f9fa; color: #2d3436; padding: 15px; border-radius: 6px; border: 1px solid #dee2e6;">
App Start
    |
    v
GET /api/v1/version
    |
    v
Version Changed?
    |         |
   YES        NO
    |         |
    v         v
GET /api/v1/media   Use Local Cache
    |
    v
Update Local Cache</pre>

            <h4>cURL Example</h4>
            <pre style="background: #2d3436; color: #dfe6e9; padding: 15px; border-radius: 6px; overflow-x: auto;">curl -X GET {base_url}/api/v1/version</pre>

            <hr style="margin: 30px 0; border: 1px solid #ecf0f1;"/>

            <h2 style="color: #2c3e50;">Business Rules</h2>
            <ul style="line-height: 2;">
                <li>API only returns <strong>active</strong> media and categories</li>
                <li>Media must be within its <strong>publish schedule</strong> to be returned</li>
                <li>Archived data is never returned via API</li>
                <li>If <code>limit</code> exceeds API Maximum Return, it is clamped to the maximum</li>
                <li>If no <code>page</code>/<code>limit</code> is provided, defaults are used</li>
                <li>Origin checking is enforced when Allowed Origins are configured</li>
            </ul>
        </div>
        """
