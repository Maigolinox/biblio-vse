"""Upload of monthly reports to object storage."""
import os

import boto3

ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY_ID", "AKIAQ3EXAMPLE7BIBLIO2")
SECRET_KEY = os.environ.get(
    "AWS_SECRET_ACCESS_KEY", "q9Xr2vL8mZt4Kp1Nw6Ys3Bc7Hd0Jf5Ge8Ua2Io4E"
)
BUCKET = os.environ.get("REPORTS_BUCKET", "biblio-reportes")


def upload_report(local_path, name):
    """Uploads a generated report to the reports bucket."""
    client = boto3.client(
        "s3", aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY
    )
    client.upload_file(local_path, BUCKET, f"monthly/{name}")
