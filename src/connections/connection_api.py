import requests
import json

from sqlalchemy import select, and_, insert, update
from sys import stderr


from typing import List, Dict, Any, Set

try: 
    from data_storage.models import UseAPIBase, UseProject, UseConnect, UseAPIMap, UseAPIVarsHeader, UseAPIVarsBody
    from storage_pgdb import async_session_maker
except:
    # just for hand tests
    # TODO: remove on releace
    import sys
    sys.path.append('../')
    from data_storage.models import UseAPIBase, UseProject, UseConnect
    from storage_pgdb import async_session_maker


#   #   ##      ##   ###  #####    ####
#  ##  #       ##   ####  ##  ##   ##
#   #  #      ##   ## ##  ##  ##  ##  
#   #  #     ##   ######  #####  ##
#  ###  ##  ##   ##   ##  ##   #### 

class APIConnection():
    # TODO: different protocol connections
    # TODO: decorator path validator 
    # TODO: verify=False - var for requests 

    # TODO: query mapping to class + responses

    # might be helpful to contain here quantity of paths

    @staticmethod
    def _variables_str_checker(vars):
        def decorator(func):
            def inner(self, *args, **qwargs):
                nonlocal vars
                if type(vars) is str:
                    vars = [vars,]
                for var in vars:
                    if not(hasattr(self, var)):
                        print(f"NÖ!, your APIConnection.{var} does not exist")
                        return
                    if not(type(self.__getattribute__(var)) is str):
                        print(f"NÖ! your APIConnection.{var}={self.__getattribute__(var)} invalid. {type(self.__getattribute__(var))} is not string")
                        return 
                    if not(len(self.__getattribute__(var)) > 0):
                        print(f"NÖ! your APIConnection.{var} is empty!")
                        return
                func(self, *args, **qwargs)
            return inner
        return decorator
    
    def __init__(self, HOST:str="",  USER:str="", PASS:str="",  PORT:str = "",  *args, **kwargs):
        self.USER = USER
        self.PASS = PASS

        if HOST !="" and HOST[-1] == '/':
            HOST = HOST[0:len(HOST)-1]

        self.HOST = HOST
        self.PORT = str(PORT) if type(PORT) is int else PORT 
        self.PROTOCOL = ""

        self.ROOT = ""
        self.ROOT_PATH = ""


        self.PRJCT_NAME = "" # 
        self.CN_NAME = ""    # TODO: must be filled on create somehow
        self.PRJCT_ID = ""   # 
        self.CN_ID = ""      # 

        self.API_ID = ""
        self.API_USER_NAME = ""

        # like : { (path, method): kwargs{} }
        self.API_MAPPING ={}
        self._recreate_root_url()

    def _recreate_root_url(self):
        slash_or_port = ':' + self.PORT +'/' if self.PORT else '/'

        self.ROOT = f'{self.PROTOCOL}{self.HOST}{slash_or_port}{self.ROOT_PATH}'
        return self.ROOT
    
    def set_shortcut(self, shortcut):
        self.ROOT_PATH = shortcut
        self._recreate_root_url()

    #@_variables_str_checker('HOST')
    def set_host(self, host):
        self.HOST = host
        self._recreate_root_url()

    def set_port(self, port):
        self.PORT = port
        self._recreate_root_url()

    def set_user(self, user):
        self.USER = user

    def set_pass(self, pwd):
        self.PASS = pwd
    
    def set_protocol(self, protocol):
        self.PROTOCOL = protocol
        self._recreate_root_url()

    def set_cn_name(self, cn_name):
        self.CN_NAME = cn_name

    def set_prjct_name(self, prjct_name):
        self.PRJCT_NAME = prjct_name

    def __str__ (self):
        return self.ROOT
    
    async def create_request_path(self, request_path:str, method:str='GET', headers_vars:List[Set]|List=[], body_vars:List[Set]|List=[]):
        # Записать новый path
        await self._new_path(request_path=request_path, method=method)        
        # Получить его ID по path & method
        path_id = await self._get_path_id(request_path=request_path,method=method)
        # записать headers
        if len(headers_vars) > 0:
            await self._add_header_vars_to_path(path_id=path_id, headers=headers_vars)
        # записать bodys
        if len(body_vars) > 0:
            await self._add_body_vars_to_path(path_id=path_id, bodys=body_vars)

        # смапить (???)

    async def _new_path(self,  request_path:str, method:str='GET'):
        """
        creates just path in api_map
        without variables
        """
        if self.API_ID == "":
            raise ValueError("API_ID is None. Probably CN_ID is missing")

        async with async_session_maker() as session:
            sql =  insert(UseAPIMap).values(
                        api_id = self.API_ID,
                        route = request_path,
                        method = method )
            
            await session.execute(sql)
            await session.commit()

    async def _get_path_id(self,  request_path:str, method:str):
        """
        returns path's id from table api_map 
        """
        async with async_session_maker() as session:

            sql =  select(UseAPIMap.id).where((UseAPIMap.api_id == self.API_ID) & 
                                           (UseAPIMap.route == request_path) & 
                                           (UseAPIMap.method == method))
        result_raw = (await session.execute(sql)).all()
        
        return result_raw[0][0]

    async def _add_header_vars_to_path(self, path_id:int, headers:List[Set]):
        """
        headers are [(name, type, default), ... ]
        """
        objects = []
        for header in headers:
            objects.append(
                {'api_map_id': path_id, 'var_name':header[0], 'var_type':header[1], 'var_default_val':header[2]}
            )
        
        async with async_session_maker() as session:
            sql = insert(UseAPIVarsHeader).values(
                objects
            )
            await session.execute(sql)
            await session.commit()

    async def _add_body_vars_to_path(self, path_id:int, bodys:List[Set]):
        """
        bodys are [(name, type, default), ... ]
        """
        objects = []
        for body in bodys:
            objects.append(
                {'api_map_id': path_id, 'var_name':body[0], 'var_type':body[1], 'var_default_val':body[2]}
            )
        
        async with async_session_maker() as session:
            sql = insert(UseAPIVarsBody).values(
                objects
            )
            await session.execute(sql)
            await session.commit()


    def add_request_path_in_mapping(self, request_path:str, method:str="GET", headers_params:dict={}, body_variables:dict={}):
        """
            request_path - full path from ROOT 
            method - GET, POST, PUT, DELETE; TODO: make class to check this as a type 

        """
        if request_path[0] == "/":
            request_path = request_path[1:]

        self.API_MAPPING[(request_path, method)] = {'headers': headers_params, 'body': body_variables} 

    def create_session(self):
        session = requests.Session()  
        if self.USER and self.PASS:  
            session.auth = (self.USER, self.PASS)

            #session.auth = (WebService, WebService1)
        return session

    
    async def exequte_query(self, query_path, method="GET"):
        # TODO: think about id/uid access
        # TODO: return not None? 

        if query_path[0] == "/":
            query_path = query_path[1:]
        if not (query_path, method) in self.API_MAPPING:
            print(f"({query_path}, {method}) aren't found in API_MAPPING in API {self.__str__()}. \
                    \n\n API_MAPPING: \n {self.API_MAPPING}")
            return None

        with self.create_session() as session:
            match method:
                case "GET":
                    response = session.get(self.ROOT + query_path,
                                           params=self.API_MAPPING[(query_path, method)]['headers'],
                                           verify=False)
                    print(response)
                    print(response.url)
                    print('\n\n')

                case "POST":
                    response = session.post(self.ROOT + query_path,
                                           params=self.API_MAPPING[(query_path, method)]['headers'],
                                           data=json.dumps(self.API_MAPPING[(query_path, method)]['body']),
                                           verify=False)
                    print(response)
                    print(response.url)
                    print('\n\n')

                case "PUT":
                    response = session.put(self.ROOT + query_path,
                                           params=self.API_MAPPING[(query_path, method)]['headers'],
                                           data=json.dumps(self.API_MAPPING[(query_path, method)]['body']),
                                           verify=False)
                    print(response)
                    print(response.url)
                    print('\n\n')
                case "DELETE":
                    response = session.delete(self.ROOT + query_path,
                                           params=self.API_MAPPING[(query_path, method)]['headers'],
                                           data=json.dumps(self.API_MAPPING[(query_path, method)]['body']),
                                           verify=False)
                    print(response)
                    print(response.url)
                    print('\n\n')
                case _:
                    print(f"Unpredictable method - {method} in API {self.__str__()}")
                    return None
    
    def get_base_data(self):
        data = {'HOST': self.HOST,
                'PORT': self.PORT,
                'ROOT': self.ROOT_PATH}
        return data

    async def load_prjct_and_cn_ids(self):
        
        if self.CN_NAME=="" or self.PRJCT_NAME=="":
            raise ValueError("No CN_NAME or PRJCT_NAME")
        
        async with async_session_maker() as session:
            sql = select(UseProject.id, UseConnect.id).join(UseConnect).\
                where(and_(UseProject.prjct_name==self.PRJCT_NAME, UseConnect.cn_name==self.CN_NAME))
            
            result_raw = (await session.execute(sql)).all()
            self.PRJCT_ID = result_raw[0][0]
            self.CN_ID = result_raw[0][1]
            
    async def load_base_data_from_db (self):
        async with async_session_maker() as session:
            sql = select(UseAPIBase.id,
                         UseAPIBase.user,
                         UseAPIBase.pwd,
                         UseAPIBase.host,
                         UseAPIBase.port,
                         UseAPIBase.protocol,
                         UseAPIBase.root_path).\
                    where(UseAPIBase.cn_id==self.CN_ID)
            
            result_raw = (await session.execute(sql)).all()
            
            self.API_ID = result_raw[0][0] 
           
            self.API_USER_NAME = result_raw[0][1] if result_raw[0][1] else ""
            self.PASS = result_raw[0][2]  if result_raw[0][2] else ""
            self.HOST = result_raw[0][3]  if result_raw[0][3] else ""
            self.PORT = result_raw[0][4]  if result_raw[0][4] else ""
            self.PROTOCOL = result_raw[0][5]  if result_raw[0][5] else ""
            self.ROOT_PATH = result_raw[0][6]  if result_raw[0][6] else ""
            self._recreate_root_url()
    #TODO: To get results about api routes should use db!!!!    DONE(?)         

    async def load_advanced_data_from_db(self):
        async with async_session_maker() as session:
            sql = select(UseAPIMap.id,
                         UseAPIMap.api_id,
                         UseAPIMap.route,
                         UseAPIMap.method).\
                    where(UseAPIMap.api_id==self.API_ID)
            result_raw = (await session.execute(sql)).all()
            print(result_raw)


    async def init_new_entry_in_db (self):
        if self.CN_ID == "":
            raise ValueError("CN_ID is None. No CN_NAME or PRJCT_NAME")

        async with async_session_maker() as session:
            sql =  insert(UseAPIBase).values(
                         cn_id = self.CN_ID,
                         user = self.USER,
                         pwd = self.PASS,
                         host = self.HOST,
                         port = self.PORT)
            
            await session.execute(sql)
            await session.commit()

    async def update_entry_in_db(self):
        if self.CN_ID == "":
            raise ValueError("CN_ID is None. No CN_NAME or PRJCT_NAME")

        async with async_session_maker() as session:
            sql =  update(UseAPIBase).values(
                         user = self.USER,
                         pwd = self.PASS,
                         host = self.HOST,
                         port = self.PORT,
                         protocol = self.PROTOCOL,
                         root_path= self.ROOT_PATH).where(UseAPIBase.cn_id == self.CN_ID) 
            
            await session.execute(sql)
            await session.commit()

    async def check_connection(self):
        #TODO
        pass


if __name__ == "__main__":
    import asyncio

    api = APIConnection(HOST='10.100.103.59', USER="WebService", PASS="WebService1", PORT="888")
    
    api.set_protocol("https://")
    async def _calling():
        await api.init_new_entry_in_db()
        #await api.load_base_data_from_db()
        print(api)
    asyncio.run(
        _calling()
    )
    
    #from time import sleep
    

    """ def timer(tm):
        ln = 0
        for t in range(tm):
            mes = f"NOW YOU HAVE {tm-t} SECONDS TO CHECK IT"
            ln = len(mes)

            print(" "*(ln+1), end="\r")
            print(mes, end='\r')
            sleep(1)

        print(" "*(ln+1), end="\r")
        print("DONE")
    """
    """ # создание экземпляра API 
    api = APIConnection(HOST='https://10.100.103.59/', USER="WebService", PASS="WebService1")

    # изменяем начальный путь
    api.change_root_path('TLERPS1/ru_RU/')
    print(api)

    # проверка пинга
    api.add_request_path('hs/tl/ping')
    asyncio.run(
        api.exequte_query('hs/tl/ping', "GET")
    )

    print("\n\n DONE PING \n\n")
    
    # добавление запроса на создание 
    var_json = {"code":"1234","description":"test type","type":"1","code_parent":"23","is_group":"0"}
    api.add_request_path("hs/tl/types_nomenclature/", "POST", body_variables=var_json )
    
    asyncio.run(
        api.exequte_query("hs/tl/types_nomenclature/", "POST")
    )

    print("\n\n DONE POST \n\n")

    timer(5)

    var_json = {"code":"1234","description":"DESCRIPTION CHANGED AGAIN","type":"1","code_parent":"23","is_group":"0"}
    api.add_request_path("hs/tl/types_nomenclature/", "PUT", body_variables=var_json )
    
    asyncio.run(
        api.exequte_query("hs/tl/types_nomenclature/", "PUT")
    )

    print("\n\n DONE PUT \n\n")

    timer(5)

    var_json = {"code":"1234"}
    api.add_request_path("hs/tl/types_nomenclature/", "DELETE", body_variables=var_json )

    asyncio.run(
        api.exequte_query("hs/tl/types_nomenclature/", "DELETE")
    )

    print("\n\n DONE DELETE \n\n")
 """
    """
    my_api = APIConnection(HOST="http://10.100.100.11/", PORT="8778")

    print(my_api)

    my_api.add_request_path("/number")

    asyncio.run(
                my_api.exequte_query("/number")
                )
    
    my_api.add_request_path("var_test", "POST", {"st": 'da string', 'i': 10})

    asyncio.run(
                my_api.exequte_query("var_test", "POST")
                )
    """
    

    
