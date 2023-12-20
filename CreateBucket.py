import os
from dotenv import load_dotenv
from minio import Minio
from minio.error import S3Error

class MinioBucketManager:
    def __init__(self):
        load_dotenv()  # Load environment variables from .env file

        self.accessID = os.getenv('AWS_ACCESS_KEY_ID')
        self.accessSecret = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.bucketName = os.getenv('AWS_BUCKET_NAME')
        self.minioUrl = os.getenv('S3_ENDPOINT_URL')

        if not all([self.accessID, self.accessSecret, self.minioUrl, self.bucketName]):
            raise ValueError('One or more environment variables are missing.')

        minioUrlHostWithPort = self.minioUrl.split('//')[1]
        print('[*] Minio URL: ', minioUrlHostWithPort)

        self.s3Client = Minio(
            minioUrlHostWithPort,
            access_key=self.accessID,
            secret_key=self.accessSecret,
            secure=False
        )

    def create_bucket(self):
        try:
            if not self.s3Client.bucket_exists(self.bucketName):
                self.s3Client.make_bucket(self.bucketName)
                print(f'Bucket {self.bucketName} created successfully.')
            else:
                print(f'Bucket {self.bucketName} already exists.')
        except S3Error as e:
            print('Error in creating bucket:', e)


if __name__ == "__main__":
    try:
        minioManager = MinioBucketManager()
        minioManager.create_bucket()
    except ValueError as e:
        print(e)
