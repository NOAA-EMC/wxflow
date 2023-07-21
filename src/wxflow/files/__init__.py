from ..factory import Factory
from .file_file import FileFile

# In the future, one can have different file systems, e.g. S3, HDFS, etc.
# from .file_s3 import FileS3
# from .s3_file import S3File
# from .s3_s3 import S3S3
# from .s3 import S3
# from .file import File


file_factory = Factory('File')
file_factory.register('file_file', FileFile)  # local to local
# file_factory.register('file_s3', FileS3)  # local to s3
# file_factory.register('s3_file', S3File)  # s3 to local
# file_factory.register('s3_s3', S3S3)  # s3 to s3
# file_factory.register('s3', S3)  # S3FS
# file_factory.register('file', File)  # LocalFileSystem
# for non supported protocols we assume local to local.
file_factory.register_default(FileFile)
