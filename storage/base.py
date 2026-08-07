import abc


class StorageProvider(abc.ABC):
    """Abstract base class for storage providers."""

    def __init__(self, env):
        self.env = env
        self.ICP = env['ir.config_parameter'].sudo()

    @abc.abstractmethod
    def upload(self, file_data, file_name, mime_type):
        """Upload file and return storage key.

        Args:
            file_data: Raw file bytes
            file_name: Original file name
            mime_type: MIME type string

        Returns:
            str: Storage key for the uploaded file
        """

    @abc.abstractmethod
    def delete(self, storage_key):
        """Delete file by storage key.

        Args:
            storage_key: The key returned by upload()
        """

    @abc.abstractmethod
    def exists(self, storage_key):
        """Check if file exists.

        Args:
            storage_key: The key returned by upload()

        Returns:
            bool: True if file exists
        """

    @abc.abstractmethod
    def get_url(self, storage_key):
        """Get public URL for file.

        Args:
            storage_key: The key returned by upload()

        Returns:
            str: Public URL to access the file
        """
