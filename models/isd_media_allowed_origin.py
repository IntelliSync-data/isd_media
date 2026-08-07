from odoo import fields, models


class IsdMediaAllowedOrigin(models.Model):
    _name = 'isd.media.allowed_origin'
    _description = 'Media Allowed Origin'
    _order = 'id asc'

    name = fields.Char('Origin URL', required=True, help='e.g. https://portal.company.com')
    active = fields.Boolean('Active', default=True)
