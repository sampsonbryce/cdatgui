from sqlalchemy import Column, Integer, String, Date, Sequence
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class DataSource(Base):
    __tablename__ = "data_sources"

    id = Column(Integer, Sequence("datasource_seq"), primary_key=True)
    uri = Column(String)
    last_accessed = Column(Date)
    times_used = Column(Integer)

    def __repr__(self):
        return "<DataSource(uri='%s', last_accessed='%s', times_used='%d'>" % (self.uri, self.last_accessed.isoformat(), self.times_used)  # noqa
