from odoo import fields, models


class IsdMediaTag(models.Model):
    _name = 'isd.media.tag'
    _description = 'Media Tag'
    _order = 'name asc'

    name = fields.Char('Name', required=True)
    active = fields.Boolean('Active', default=True)
