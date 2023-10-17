from sqlalchemy import Column, String, Integer, TIMESTAMP, ForeignKey

from storage_pgdb import Base as StoragePgBase


class UseProject(StoragePgBase):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, autoincrement=True)
    prjct_name = Column(String, nullable=False, unique=True)
    prjct_description = Column(String)
    created_at = Column(TIMESTAMP, nullable=False)

class UseConnect(StoragePgBase):
    __tablename__ = "connections"
    id = Column(Integer, primary_key=True, autoincrement=True)
    prjct_id = Column(Integer,  ForeignKey('projects.id'))
    cn_requirements = Column(String) 
    cn_name = Column(String)
    cn_host = Column(String)
    cn_port = Column(Integer)
    cn_user = Column(String)
    cn_pwd = Column(String)
    cn_db = Column(String)
    cn_schema = Column(String)
    cn_apikey = Column(String) 