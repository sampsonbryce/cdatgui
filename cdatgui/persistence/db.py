import os
import cdatgui.info
import migrations
import re
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from models import Base, DataSource
import datetime


__dbconn__ = None


def db_version_greater(left, right):
    greater = right

    major, minor, letter = left

    if major > right[0]:
        greater = left
    elif major == right[0]:
        if minor > right[1]:
            greater = left
        elif minor == right[1]:
            if (letter == '' and right[2] != '') or letter > right[2]:
                greater = left

    return greater


def db_version(filename):
    v = re.match("cdatgui_(\d+)\.(\d+)([abAB]?).db", filename)
    if v is None:
        return (0, 0, '')
    else:
        return (int(v.group(1)), int(v.group(2)), v.group(3))


def connect():
    global __dbconn__
    if __dbconn__ is None:
        # TODO: Use vcs.getdotdir() or whatever it is
        dotdir = os.path.expanduser("~/.uvcdat")
        path = os.path.expanduser(os.path.join(dotdir, "cdatgui_%s.db" %
                                  cdatgui.info.version))
        if os.path.exists(path):
            engine = create_engine("sqlite:///%s" % path)
        else:
            # Find highest version
            version = (0, 0, '')
            for f in os.listdir(dotdir):
                v = db_version(f)
                version = db_version_greater(v, version)

            if version == (0, 0, ''):
                # Clean .uvcdat directory
                engine = create_db(path)
            else:
                # Found an older DB
                old_path = os.path.join(dotdir, "cdatgui_%d.%d%s.db" % version)
                # Do custom migrations
                engine = migrations.migrate(old_path, path)

        __dbconn__ = sessionmaker(bind=engine)
    return __dbconn__()


def create_db(path):
    db = create_engine("sqlite:///%s" % path)
    Base.metadata.create_all(db)
    return db


def get_data_sources():
    db = connect()
    sources = db.query(DataSource).order_by(desc(DataSource.last_accessed))
    return [o.uri for o in sources.all()]


def add_data_source(uri):
    db = connect()

    matching = db.query(DataSource).filter_by(uri=uri).first()
    if matching is None:
        source = DataSource(uri=uri,
                            last_accessed=datetime.date.today(),
                            times_used=1)
        db.add(source)
    else:
        matching.last_accessed = datetime.date.today()
        matching.times_used += 1
    db.commit()

def remove_data_source(uri):
    db = connect()

    matching = db.query(DataSource).filter_by(uri=uri).first()
    if matching is not None:
        db.delete(matching)
        db.commit()
