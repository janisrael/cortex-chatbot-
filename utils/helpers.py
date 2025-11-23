"""General helper utilities"""
from config.constants import ALLOWED_EXTENSIONS


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def format_file_size(bytes):
    """Format file size in human-readable format"""
    if bytes == 0:
        return '0 Bytes'
    k = 1024
    sizes = ['Bytes', 'KB', 'MB', 'GB']
    i = int(__import__('math').floor(__import__('math').log(bytes) / __import__('math').log(k)))
    return f"{round(bytes / (k ** i), 2)} {sizes[i]}"

