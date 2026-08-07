# ISD Media Service

Centralized Media Service for the ISD Platform ecosystem.

## Features

- **Image & Video Management** - Upload, organize, and serve media files
- **Dual Storage** - Local filesystem or Amazon S3 (extensible to MinIO, Cloudflare R2, Azure Blob, etc.)
- **REST API** - Public API for Portal, PhotoApp, Mobile App, and external systems
- **Category & Tag** - Organize media with categories and tags
- **Publish Scheduling** - Control when media is visible via publish from/to dates
- **Version API** - Cache optimization for client applications
- **Origin Control** - Restrict API access by domain

## Architecture

```
Controller → Service → Storage Provider → ORM/Filesystem
```

### Storage Provider Pattern

Extensible storage via abstract base class:

```
StorageProvider (abstract)
├── LocalStorageProvider
├── S3StorageProvider
└── (future: MinIO, R2, Azure, GCS...)
```

## REST API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/categories` | List active categories |
| GET | `/api/v1/media` | List active, published media (paginated) |
| GET | `/api/v1/version` | Get data version for cache check |

### Response Format

```json
{
    "success": true,
    "code": 200,
    "message": "",
    "meta": {"page": 1, "limit": 20, "total": 58},
    "data": [...]
}
```

## Menu Structure

```
Media
├── Upload Media
├── Categories
├── Tags
└── Configuration (Admin only)
```

## Security Groups

- **Media User** - Upload media, manage categories and tags
- **Media Administrator** - Full access including configuration

## Configuration

All settings stored in `ir.config_parameter`:

- Storage provider (Local/S3)
- S3 credentials and bucket config
- Upload size limits (Image/Video)
- Media count limits (warning only)
- API maximum return count
- Allowed origins for CORS

## Requirements

- Odoo 18 Community
- `boto3` (only if using S3 storage)
- `ffmpeg` (optional, for video thumbnail generation)

## Installation

1. Place `isd_media` in your Odoo addons path
2. Update apps list
3. Install "ISD Media Service"
4. Configure storage provider in Media > Configuration
