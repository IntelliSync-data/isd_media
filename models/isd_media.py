import base64
import logging
import mimetypes
import os

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class IsdMedia(models.Model):
    _name = 'isd.media'
    _description = 'Media'
    _order = 'sort_order asc, id desc'

    name = fields.Char('Name')
    media_type = fields.Selection([
        ('image', 'Image'),
        ('video', 'Video'),
        ('facebook', 'Facebook'),
        ('youtube', 'YouTube'),
    ], string='Media Type', required=True)

    display_size = fields.Selection([
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large'),
    ], string='Size', default='medium')

    external_url = fields.Char('URL')

    category_ids = fields.Many2many(
        'isd.media.category', string='Categories', required=True,
        domain=[('active', '=', True)])
    tag_ids = fields.Many2many('isd.media.tag', string='Tags')

    sort_order = fields.Integer('Sort Order', default=10)

    # File data (Binary field for upload, required for image/video only)
    media_file = fields.Binary('Media File', attachment=True)
    file_name = fields.Char('File Name')
    mime_type = fields.Char('MIME Type', readonly=True)
    file_size = fields.Integer('File Size (bytes)', readonly=True)
    file_size_display = fields.Char('File Size', compute='_compute_file_size_display')

    # Storage
    storage_key = fields.Char('Storage Key', readonly=True)
    storage_provider = fields.Selection([
        ('local', 'Local'),
        ('s3', 'Amazon S3'),
    ], string='Storage Provider', readonly=True)

    # Public URL (computed, not stored)
    public_url = fields.Char('Public URL', compute='_compute_public_url')

    # Thumbnail
    thumbnail = fields.Image('Thumbnail', max_width=256, max_height=256)
    thumbnail_url = fields.Char('Thumbnail URL', compute='_compute_thumbnail_url')

    # Preview (image for images, thumbnail for videos)
    preview_image = fields.Image('Preview', compute='_compute_preview_image')

    # Publish scheduling
    publish_from = fields.Datetime('Publish From')
    publish_to = fields.Datetime('Publish To')
    is_published = fields.Boolean('Published', compute='_compute_is_published', search='_search_is_published')

    active = fields.Boolean('Active', default=True)

    @api.constrains('media_file', 'media_type', 'external_url')
    def _check_media_file(self):
        for record in self:
            if record.media_type in ('image', 'video') and not record.media_file:
                raise ValidationError(_("Media file is required for image and video types."))
            if record.media_type in ('facebook', 'youtube') and not record.external_url:
                raise ValidationError(_("URL is required for Facebook and YouTube types."))

    @api.constrains('media_file', 'media_type')
    def _check_file_size(self):
        ICP = self.env['ir.config_parameter'].sudo()
        max_image_size = float(ICP.get_param('isd_media.max_image_upload_size', '10'))
        max_video_size = float(ICP.get_param('isd_media.max_video_upload_size', '100'))

        for record in self:
            if not record.file_size or record.media_type in ('facebook', 'youtube'):
                continue
            size_mb = record.file_size / (1024 * 1024)
            if record.media_type == 'image' and size_mb > max_image_size:
                raise ValidationError(
                    _("Image file size (%.1f MB) exceeds maximum allowed (%.1f MB).") % (size_mb, max_image_size))
            if record.media_type == 'video' and size_mb > max_video_size:
                raise ValidationError(
                    _("Video file size (%.1f MB) exceeds maximum allowed (%.1f MB).") % (size_mb, max_video_size))

    @api.depends('file_size')
    def _compute_file_size_display(self):
        for record in self:
            if not record.file_size:
                record.file_size_display = '0 B'
            elif record.file_size < 1024:
                record.file_size_display = f'{record.file_size} B'
            elif record.file_size < 1024 * 1024:
                record.file_size_display = f'{record.file_size / 1024:.1f} KB'
            else:
                record.file_size_display = f'{record.file_size / (1024 * 1024):.2f} MB'

    @api.depends('storage_key', 'storage_provider', 'external_url', 'media_type')
    def _compute_public_url(self):
        from ..storage import get_storage_provider
        for record in self:
            if record.media_type in ('facebook', 'youtube'):
                record.public_url = record.external_url or False
                continue
            if not record.storage_key or not record.storage_provider:
                record.public_url = False
                continue
            provider = get_storage_provider(record.storage_provider, self.env)
            record.public_url = provider.get_url(record.storage_key)

    @api.depends('media_type', 'media_file', 'thumbnail')
    def _compute_preview_image(self):
        for record in self:
            if record.media_type in ('video', 'facebook', 'youtube'):
                record.preview_image = record.thumbnail
            else:
                record.preview_image = record.media_file

    @api.depends('thumbnail', 'storage_provider')
    def _compute_thumbnail_url(self):
        for record in self:
            if record.thumbnail:
                record.thumbnail_url = f'/web/image/isd.media/{record.id}/thumbnail'
            else:
                record.thumbnail_url = False

    @api.depends('publish_from', 'publish_to')
    def _compute_is_published(self):
        now = fields.Datetime.now()
        for record in self:
            if not record.publish_from and not record.publish_to:
                record.is_published = True
            elif record.publish_from and not record.publish_to:
                record.is_published = now >= record.publish_from
            elif not record.publish_from and record.publish_to:
                record.is_published = now <= record.publish_to
            else:
                record.is_published = record.publish_from <= now <= record.publish_to

    def _search_is_published(self, operator, value):
        now = fields.Datetime.now()
        if (operator == '=' and value) or (operator == '!=' and not value):
            return [
                '|', '&', ('publish_from', '=', False), ('publish_to', '=', False),
                '|', '&', ('publish_from', '<=', now), ('publish_to', '=', False),
                '|', '&', ('publish_from', '=', False), ('publish_to', '>=', now),
                '&', ('publish_from', '<=', now), ('publish_to', '>=', now),
            ]
        return [
            '|', '&', ('publish_from', '!=', False), ('publish_from', '>', now),
            '&', ('publish_to', '!=', False), ('publish_to', '<', now),
        ]

    @api.model_create_multi
    def create(self, vals_list):
        from ..storage import get_storage_provider

        ICP = self.env['ir.config_parameter'].sudo()
        provider_type = ICP.get_param('isd_media.storage_provider', 'local')
        provider = get_storage_provider(provider_type, self.env)

        for vals in vals_list:
            media_type = vals.get('media_type')

            # Facebook/YouTube: no file upload, just URL
            if media_type in ('facebook', 'youtube'):
                vals.pop('media_file', None)
                vals.pop('file_name', None)
                vals['file_size'] = 0
                vals['mime_type'] = False
                vals['storage_key'] = False
                vals['storage_provider'] = False
                continue

            if vals.get('media_file'):
                file_data = base64.b64decode(vals['media_file'])
                file_name = vals.get('file_name') or 'unnamed'
                mime = mimetypes.guess_type(file_name)[0] or 'application/octet-stream'

                # If no extension in file_name, add one from mime type
                if not os.path.splitext(file_name)[1]:
                    ext = mimetypes.guess_extension(mime) or ''
                    if ext:
                        file_name = file_name + ext

                vals['file_size'] = len(file_data)
                vals['mime_type'] = mime
                vals['file_name'] = file_name
                vals['storage_provider'] = provider_type

                # Upload to storage
                storage_key = provider.upload(file_data, file_name, mime)
                vals['storage_key'] = storage_key

                # Generate thumbnail for video
                if media_type == 'video' and not vals.get('thumbnail'):
                    vals['thumbnail'] = self._generate_video_thumbnail(file_data)

        records = super().create(vals_list)
        self._increment_version()
        self._check_media_count_warning(records)
        return records

    def write(self, vals):
        from ..storage import get_storage_provider

        media_type = vals.get('media_type') or (self[0].media_type if len(self) == 1 else None)

        # If switching to facebook/youtube, clean up old storage file
        if media_type in ('facebook', 'youtube'):
            for record in self:
                if record.storage_key and record.storage_provider:
                    old_provider = get_storage_provider(record.storage_provider, self.env)
                    old_provider.delete(record.storage_key)
            vals['media_file'] = False
            vals['file_name'] = False
            vals['file_size'] = 0
            vals['mime_type'] = False
            vals['storage_key'] = False
            vals['storage_provider'] = False
        elif vals.get('media_file'):
            ICP = self.env['ir.config_parameter'].sudo()
            provider_type = ICP.get_param('isd_media.storage_provider', 'local')
            provider = get_storage_provider(provider_type, self.env)

            file_data = base64.b64decode(vals['media_file'])
            file_name = vals.get('file_name') or self.file_name or 'unnamed'
            mime = mimetypes.guess_type(file_name)[0] or 'application/octet-stream'

            # If no extension in file_name, add one from mime type
            if not os.path.splitext(file_name)[1]:
                ext = mimetypes.guess_extension(mime) or ''
                if ext:
                    file_name = file_name + ext

            # Delete old file from storage
            for record in self:
                if record.storage_key and record.storage_provider:
                    old_provider = get_storage_provider(record.storage_provider, self.env)
                    old_provider.delete(record.storage_key)

            # Upload new file
            storage_key = provider.upload(file_data, file_name, mime)
            vals['file_size'] = len(file_data)
            vals['mime_type'] = mime
            vals['file_name'] = file_name
            vals['storage_key'] = storage_key
            vals['storage_provider'] = provider_type

            if media_type == 'video' and not vals.get('thumbnail'):
                vals['thumbnail'] = self._generate_video_thumbnail(file_data)

        res = super().write(vals)
        self._increment_version()
        return res

    def unlink(self):
        from ..storage import get_storage_provider
        for record in self:
            if record.storage_key and record.storage_provider:
                provider = get_storage_provider(record.storage_provider, self.env)
                provider.delete(record.storage_key)
        self._increment_version()
        return super().unlink()

    def _increment_version(self):
        ICP = self.env['ir.config_parameter'].sudo()
        current = int(ICP.get_param('isd_media.api_version', '0'))
        ICP.set_param('isd_media.api_version', str(current + 1))
        ICP.set_param('isd_media.api_last_updated', fields.Datetime.now())

    def _check_media_count_warning(self, records):
        ICP = self.env['ir.config_parameter'].sudo()
        max_images = int(ICP.get_param('isd_media.max_image_count', '0'))
        max_videos = int(ICP.get_param('isd_media.max_video_count', '0'))

        if not max_images and not max_videos:
            return

        warnings = []
        for record in records:
            if record.media_type == 'image' and max_images:
                total = self.search_count([('media_type', '=', 'image'), ('active', '=', True)])
                if total > max_images:
                    warnings.append(
                        _("You are adding Image #%(total)s/%(max)s allowed. "
                          "Please contact your administrator to upgrade.",
                          total=total, max=max_images))

            if record.media_type in ('video', 'facebook', 'youtube') and max_videos:
                total = self.search_count([
                    ('media_type', 'in', ('video', 'facebook', 'youtube')),
                    ('active', '=', True),
                ])
                if total > max_videos:
                    warnings.append(
                        _("You are adding Video/URL #%(total)s/%(max)s allowed. "
                          "Please contact your administrator to upgrade.",
                          total=total, max=max_videos))

        if warnings:
            # Send bus notification to current user
            self.env['bus.bus']._sendone(
                self.env.user.partner_id,
                'simple_notification',
                {
                    'title': _("Media Limit Warning"),
                    'message': '\n'.join(warnings),
                    'type': 'warning',
                    'sticky': True,
                },
            )

    @staticmethod
    def _generate_video_thumbnail(file_data):
        """Generate a thumbnail from video data. Returns base64 image or False."""
        try:
            import subprocess
            import tempfile
            import os

            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp_video:
                tmp_video.write(file_data)
                tmp_video_path = tmp_video.name

            tmp_thumb_path = tmp_video_path + '.jpg'
            subprocess.run([
                'ffmpeg', '-i', tmp_video_path,
                '-ss', '00:00:01', '-vframes', '1',
                '-y', tmp_thumb_path
            ], capture_output=True, timeout=30)

            if os.path.exists(tmp_thumb_path):
                with open(tmp_thumb_path, 'rb') as f:
                    thumb_data = base64.b64encode(f.read())
                os.unlink(tmp_thumb_path)
                os.unlink(tmp_video_path)
                return thumb_data

            os.unlink(tmp_video_path)
        except Exception as e:
            _logger.warning("Failed to generate video thumbnail: %s", e)
        return False
