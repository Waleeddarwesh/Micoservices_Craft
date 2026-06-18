import boto3
from botocore.exceptions import ClientError
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class VideoAccessService:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL
        )
        self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME

    def generate_playback_url(self, storage_key):
        """
        Generate a short-lived presigned URL for secure video playback.
        """
        if not storage_key:
            return None

        try:
            url = self.s3_client.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': storage_key
                },
                ExpiresIn=settings.VIDEO_PLAYBACK_EXPIRATION
            )
            return url
        except ClientError as e:
            logger.error(f"Error generating presigned playback URL: {e}")
            return None
