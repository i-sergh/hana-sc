import requests
import json

from sqlalchemy import select, and_

try: 
    from data_storage.models import UseAPIBase, UseProject, UseConnect
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
    def __init__(self,HOST:str,  USER:str="", PASS:str="",  PORT:str = "",  *args, **kwargs):
        self.USER = USER
        self.PASS = PASS

        if HOST[-1] == '/':
            HOST = HOST[0:len(HOST)-1]

        self.HOST = HOST
        self.PORT = ':' + PORT +'/' if PORT else '/'
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
        self.ROOT = f'{self.HOST}{self.PORT}{self.ROOT_PATH}'
        return self.ROOT
    
    def change_root_path(self, root_path):
        self.ROOT_PATH = root_path
        self._recreate_root_url()

    def change_host(self, host):
        self.HOST = host
        self._recreate_root_url()

    def change_port(self, port):
        self.PORT = port
        self._recreate_root_url()

    def change_user(self, user):
        self.USER = user
        
    def change_pass(self, pwd):
        self.PASS = pwd

    def __str__ (self):
        return self.ROOT

    def add_request_path(self, request_path:str, method:str="GET", headers_params:dict={}, body_variables:dict={}):
        """
            request_path - full path from ROOT 
            method - GET, POST, PUT, DELETE; TODO: make class to check this as a type 
            
            TODO  THIS IS WRONG kwargs - variables of query, look like:
                    { 
                        var1: (type), 
                        var2: (type|type2)
                    }
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

    async def load_prjct_and_cn_ids(self,prjct_name="", cn_name=""):
        async with async_session_maker() as session:
            sql = select(UseProject.id, UseConnect.id).join(UseConnect).\
                where(and_(UseProject.prjct_name==prjct_name, UseConnect.cn_name==cn_name))
            result_raw = (await session.execute(sql)).all()
            self.PRJCT_ID = result_raw[0][0]
            self.CN_ID = result_raw[0][1]
            self.PRJCT_NAME = prjct_name
            self.CN_NAME = cn_name

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
            self.API_USER_NAME = result_raw[0][1]
            self.PASS = result_raw[0][2]
            self.HOST = result_raw[0][3]
            self.PORT = result_raw[0][4]
            self.PROTOCOL = result_raw[0][5]
            self.ROOT_PATH = result_raw[0][6]
    # TODO: To get results about api routes should use db!!!!   DONE(?)         

    async def check_connection(self):
        #TODO
        pass


if __name__ == "__main__":
    import asyncio

    api = APIConnection(HOST='https://10.100.103.59/', USER="WebService", PASS="WebService1")
    async def sequentially_calling():
        await api.load_prjct_and_cn_ids('p2', 'cn')
        await api.load_base_data_from_db()
    
    asyncio.run(
        sequentially_calling()
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
    

    
