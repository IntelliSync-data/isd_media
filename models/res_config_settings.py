from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Dashboard (computed, not stored)
    isd_media_total_images = fields.Integer('Total Images', compute='_compute_media_stats')
    isd_media_total_videos = fields.Integer('Total Videos', compute='_compute_media_stats')
    isd_media_total_categories = fields.Integer('Total Categories', compute='_compute_media_stats')

    # Limits
    isd_media_max_image_count = fields.Integer('Maximum Image Count')
    isd_media_max_video_count = fields.Integer('Maximum Video Count')
    isd_media_max_image_upload_size = fields.Float('Maximum Image Upload Size (MB)', default=10.0)
    isd_media_max_video_upload_size = fields.Float('Maximum Video Upload Size (MB)', default=100.0)

    # API
    isd_media_api_max_return = fields.Integer('API Maximum Return', default=100)

    # Storage Provider
    isd_media_storage_provider = fields.Selection([
        ('local', 'Local Storage'),
        ('s3', 'Amazon S3'),
    ], string='Storage Provider', default='local')

    # S3 Settings
    isd_media_s3_bucket_name = fields.Char('Bucket Name')
    isd_media_s3_region = fields.Char('Region')
    isd_media_s3_access_key = fields.Char('Access Key')
    isd_media_s3_secret_key = fields.Char('Secret Key')
    isd_media_s3_endpoint_url = fields.Char('Endpoint URL')
    isd_media_s3_public_base_url = fields.Char('Public Base URL')
    isd_media_s3_use_ssl = fields.Boolean('Use SSL', default=True)

    # Allowed Origins (One2many via config)
    isd_media_allowed_origin_ids = fields.Many2many(
        'isd.media.allowed_origin', string='Allowed Origins',
        compute='_compute_allowed_origins', inverse='_inverse_allowed_origins')

    @api.depends_context('uid')
    def _compute_media_stats(self):
        Media = self.env['isd.media'].sudo()
        Category = self.env['isd.media.category'].sudo()
        total_images = Media.search_count([('media_type', '=', 'image'), ('active', '=', True)])
        total_videos = Media.search_count([('media_type', '=', 'video'), ('active', '=', True)])
        total_categories = Category.search_count([('active', '=', True)])
        for record in self:
            record.isd_media_total_images = total_images
            record.isd_media_total_videos = total_videos
            record.isd_media_total_categories = total_categories

    def _compute_allowed_origins(self):
        origins = self.env['isd.media.allowed_origin'].sudo().search([])
        for record in self:
            record.isd_media_allowed_origin_ids = origins

    def _inverse_allowed_origins(self):
        pass

    @api.model
    def get_values(self):
        res = super().get_values()
        ICP = self.env['ir.config_parameter'].sudo()
        res.update(
            isd_media_max_image_count=int(ICP.get_param('isd_media.max_image_count', '0')),
            isd_media_max_video_count=int(ICP.get_param('isd_media.max_video_count', '0')),
            isd_media_max_image_upload_size=float(ICP.get_param('isd_media.max_image_upload_size', '10')),
            isd_media_max_video_upload_size=float(ICP.get_param('isd_media.max_video_upload_size', '100')),
            isd_media_api_max_return=int(ICP.get_param('isd_media.api_max_return', '100')),
            isd_media_storage_provider=ICP.get_param('isd_media.storage_provider', 'local'),
            isd_media_s3_bucket_name=ICP.get_param('isd_media.s3_bucket_name', ''),
            isd_media_s3_region=ICP.get_param('isd_media.s3_region', ''),
            isd_media_s3_access_key=ICP.get_param('isd_media.s3_access_key', ''),
            isd_media_s3_secret_key=ICP.get_param('isd_media.s3_secret_key', ''),
            isd_media_s3_endpoint_url=ICP.get_param('isd_media.s3_endpoint_url', ''),
            isd_media_s3_public_base_url=ICP.get_param('isd_media.s3_public_base_url', ''),
            isd_media_s3_use_ssl=ICP.get_param('isd_media.s3_use_ssl', 'True') == 'True',
        )
        return res

    def set_values(self):
        super().set_values()
        ICP = self.env['ir.config_parameter'].sudo()
        ICP.set_param('isd_media.max_image_count', str(self.isd_media_max_image_count))
        ICP.set_param('isd_media.max_video_count', str(self.isd_media_max_video_count))
        ICP.set_param('isd_media.max_image_upload_size', str(self.isd_media_max_image_upload_size))
        ICP.set_param('isd_media.max_video_upload_size', str(self.isd_media_max_video_upload_size))
        ICP.set_param('isd_media.api_max_return', str(self.isd_media_api_max_return))
        ICP.set_param('isd_media.storage_provider', self.isd_media_storage_provider)
        ICP.set_param('isd_media.s3_bucket_name', self.isd_media_s3_bucket_name or '')
        ICP.set_param('isd_media.s3_region', self.isd_media_s3_region or '')
        ICP.set_param('isd_media.s3_access_key', self.isd_media_s3_access_key or '')
        ICP.set_param('isd_media.s3_secret_key', self.isd_media_s3_secret_key or '')
        ICP.set_param('isd_media.s3_endpoint_url', self.isd_media_s3_endpoint_url or '')
        ICP.set_param('isd_media.s3_public_base_url', self.isd_media_s3_public_base_url or '')
        ICP.set_param('isd_media.s3_use_ssl', str(self.isd_media_s3_use_ssl))

    def action_view_api_documentation(self):
        return {
            'name': 'API Documentation',
            'type': 'ir.actions.act_window',
            'res_model': 'isd.media.api.doc.wizard',
            'view_mode': 'form',
            'target': 'new',
        }
