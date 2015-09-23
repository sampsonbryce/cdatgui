import shutil
import sqlalchemy


def migrate(old_path, new_path):
    # Copy the old path to the new path for now
    shutil.copyfile(old_path, new_path)
    return sqlalchemy.create_engine("sqlite:///%s" % new_path)
