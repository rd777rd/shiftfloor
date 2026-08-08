from django.core.exceptions import ValidationError

ALLOWED_CERT_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}
MAX_CERT_FILE_SIZE_MB = 8


def validate_cert_document(file):
    ext = file.name.rsplit(".", 1)[-1].lower() if "." in file.name else ""
    if ext not in ALLOWED_CERT_EXTENSIONS:
        raise ValidationError(
            "Unsupported file type. Upload a PDF, JPG, or PNG of your certification."
        )
    if file.size > MAX_CERT_FILE_SIZE_MB * 1024 * 1024:
        raise ValidationError(
            f"File is too large. Certification documents must be under "
            f"{MAX_CERT_FILE_SIZE_MB}MB."
        )
