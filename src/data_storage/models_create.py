from sqlalchemy import Column, ForeignKey, Integer, String, TIMESTAMP, Boolean
from sqlalchemy.orm import relationship
try:
    from storage_pgdb import Base as StoragePgBase
except:
    ## TODO: remove on releace
    import sys
    sys.path.append('../')
    from storage_pgdb import Base as StoragePgBase


class ProjectCreate(StoragePgBase):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, autoincrement=True)
    prjct_name = Column(String, nullable=False, unique=True)
    prjct_description = Column(String)
    created_at = Column(TIMESTAMP, nullable=False)
    last_used_at = Column(TIMESTAMP, nullable=False)

class ConnectionCreate(StoragePgBase):
    __tablename__ = "connections"
    id = Column(Integer, primary_key=True, autoincrement=True)
    prjct_id = Column(Integer, ForeignKey('projects.id', ondelete="CASCADE"))
    cn_drv = Column(String, nullable=False) # TODO: make it choosable from list of variants
    cn_is_target = Column(Boolean, nullable=False, default=False)
    cn_requirements = Column(String) 
    cn_name = Column(String)
    cn_host = Column(String)
    cn_port = Column(String)
    cn_user = Column(String)
    cn_pwd = Column(String)
    cn_db = Column(String)
    cn_schema = Column(String)
    cn_apikey = Column(String) 
    prjcts = relationship(ProjectCreate)

class SessionCreate(StoragePgBase):
    __tablename__ = "sessions"
    id = Column( Integer, primary_key=True, autoincrement=True)
    prjct_id = Column(Integer, ForeignKey('projects.id', ondelete="CASCADE"))
    connection_id = Column(Integer, ForeignKey('connections.id', ondelete="CASCADE"))
    user_id = Column(String) # TODO: make users
    created_at = Column(TIMESTAMP, nullable=False)
    last_used_at = Column(TIMESTAMP, nullable=False)
    prjcts = relationship(ProjectCreate)
    prjcts = relationship(ConnectionCreate)
    

