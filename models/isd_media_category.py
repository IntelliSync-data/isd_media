from odoo import fields, models, api


class IsdMediaCategory(models.Model):
    _name = 'isd.media.category'
    _description = 'Media Category'
    _order = 'sort_order asc, id desc'

    name = fields.Char('Name', required=True)
    description = fields.Text('Description')
    avatar = fields.Image('Avatar', max_width=256, max_height=256)
    sort_order = fields.Integer('Sort Order', default=10)
    active = fields.Boolean('Active', default=True)

    media_ids = fields.Many2many('isd.media', string='Media')
    media_count = fields.Integer('Media Count', compute='_compute_media_count')

    @api.depends('media_ids')
    def _compute_media_count(self):
        for record in self:
            record.media_count = len(record.media_ids)

    def write(self, vals):
        res = super().write(vals)
        self._increment_version()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        self._increment_version()
        return records

    def _increment_version(self):
        ICP = self.env['ir.config_parameter'].sudo()
        current = int(ICP.get_param('isd_media.api_version', '0'))
        ICP.set_param('isd_media.api_version', str(current + 1))
        ICP.set_param('isd_media.api_last_updated', fields.Datetime.now())
