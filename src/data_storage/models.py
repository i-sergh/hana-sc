from sqlalchemy import Column, String, Integer, TIMESTAMP, ForeignKey, Boolean

from storage_pgdb import Base as StoragePgBase


# No session megamind.jpg

class UseProject(StoragePgBase):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, autoincrement=True)
    prjct_name = Column(String, nullable=False, unique=True)
    prjct_description = Column(String)
    created_at = Column(TIMESTAMP, nullable=False)
    last_used_at = Column(TIMESTAMP, nullable=False)

class UseConnect(StoragePgBase):
    __tablename__ = "connections"
    id = Column(Integer, primary_key=True, autoincrement=True)
    prjct_id = Column(Integer,  ForeignKey('projects.id'))
    cn_drv = Column(String) 
    cn_is_target = Column(Boolean)
    cn_requirements = Column(String)
    cn_name = Column(String)
    cn_host = Column(String)
    cn_port = Column(String)
    cn_user = Column(String)
    cn_pwd = Column(String)
    cn_db = Column(String)
    cn_schema = Column(String)
    cn_apikey = Column(String) 

class UseSession(StoragePgBase):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    prjct_id = Column(Integer, ForeignKey('projects.id'))
    connection_id = Column(Integer, ForeignKey('connections.id'))
    user_id = Column(String) # TODO: make users
    created_at = Column(TIMESTAMP, nullable=False)
    last_used_at = Column(TIMESTAMP, nullable=False)


class UseAPIBase(StoragePgBase):
    __tablename__ = "api"
    id = Column(Integer, primary_key=True, autoincrement=True)
    cn_id = Column(Integer, ForeignKey('connections.id'))
    user = Column(String)
    pwd = Column(String)
    host = Column(String)
    port = Column(String)
    protocol = Column(String)
    root_path = Column(String) # Must content path without host


class UseAPIMap(StoragePgBase):
    __tablename__ = "api_map"
    id = Column(Integer, primary_key=True, autoincrement=True)
    apt_id = Column(Integer, ForeignKey('API.id'))
    route = Column(String)
    method = Column(String)

class UseAPIVarsHeader(StoragePgBase):
    __tablename__ = "api_map_header"
    id = Column(Integer, primary_key=True, autoincrement=True)
    api_map_id = Column(Integer, ForeignKey("API_map.id")) 
    var_type = Column(String) 
    var_val = Column(String)


class UseAPIVarsBody(StoragePgBase):
    __tablename__ = "api_map_body"
    id = Column(Integer, primary_key=True, autoincrement=True)
    api_map_id = Column(Integer, ForeignKey("API_map.id")) 
    var_type = Column(String) 
    var_val = Column(String)