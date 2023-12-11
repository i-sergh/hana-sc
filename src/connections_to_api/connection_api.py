import requests
import json


class APIConnection():
    # TODO: different protocol connections
    # TODO: decorator path validator 
    # TODO: verify=False - var for requests 
    def __init__(self,HOST:str,  USER:str="", PASS:str="",  PORT:str = "",  *args, **kwargs):
        self.USER = USER
        self.PASS = PASS

        if HOST[-1] == '/':
            HOST = HOST[0:len(HOST)-1]

        self.HOST = HOST
        self.PORT = ':' + PORT +'/' if PORT else '/'
        
        self.ROOT = ""
        self.ROOT_PATH = ""

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
        print(self.API_MAPPING)

    def create_session(self):
        session = requests.Session()  
        if self.USER and self.PASS:  
            session.auth = (self.USER, self.PASS)
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
                    pass
                case "DELETE":
                    pass
                case _:
                    print(f"Unpredictable method - {method} in API {self.__str__()}")
                    return None
                 
            

    async def check_connection(self):
        pass


if __name__ == "__main__":
    import asyncio

    api = APIConnection(HOST='https://10.100.103.59/', USER="WebService", PASS="WebService1")

    api.change_root_path('TLERPS1/ru_RU/')
    print(api)

    api.add_request_path('hs/tl/ping')
    asyncio.run(
        api.exequte_query('hs/tl/ping', "GET")
    )

    print("\n\n DONE IT \n\n")
    var_json = {"code":"54321","description":"test type","type":"1","code_parent":"23","is_group":"0"}
    api.add_request_path("hs/tl/types_nomenclature/", "POST", body_variables=var_json )
    
    asyncio.run(
        api.exequte_query("hs/tl/types_nomenclature/", "POST")
    )


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
    
