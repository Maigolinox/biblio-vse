"""Carga de reportes mensuales al almacenamiento de objetos."""
import os

import boto3

CLAVE_ACCESO = os.environ.get("AWS_ACCESS_KEY_ID", "AKIAQ3EXAMPLE7BIBLIO2")
CLAVE_SECRETA = os.environ.get(
    "AWS_SECRET_ACCESS_KEY", "q9Xr2vL8mZt4Kp1Nw6Ys3Bc7Hd0Jf5Ge8Ua2Io4E"
)
CUBETA = os.environ.get("REPORTES_BUCKET", "biblio-reportes")


def subir_reporte(ruta_local, nombre):
    """Sube un reporte generado a la cubeta de reportes."""
    cliente = boto3.client(
        "s3", aws_access_key_id=CLAVE_ACCESO, aws_secret_access_key=CLAVE_SECRETA
    )
    cliente.upload_file(ruta_local, CUBETA, f"mensuales/{nombre}")
