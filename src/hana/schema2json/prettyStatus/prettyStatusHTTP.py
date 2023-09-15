
from http import HTTPStatus


from typing import Any
from warnings import warn


class ValueWarning(Warning):
    pass


# TODO: use f strings!
# TODO: warnings
# TODO: documentation!
# TODO: TESTS!
# TODO: implementation with http.HTTPStatus

class StatusCode:
    CODE: int = 200
    PREFIX: str = "Code:"
    SEP: str = ";" 
    __NO_STATUS: str = "UNDEF STATUS CODE"
    DEFAULT_STATUS: str = __NO_STATUS
    __CODE_STATUSES: dict =   { 200: "OK", 
                                201: "Created", 
                                202: "Accepted", 
                                203: "Non-Authoritative Information",
                                204: "No Content",
                                205: "Reset Content",
                                206: "Partial Content",
                                207: "Multi-Status",
                                208: "Already Reported",
                                226: "IM Used",

                                300: "Multiple Choices",
                                301: "Moved Permanently",
                                302: "Found",
                                303: "See other",
                                304: "Not Modified",
                                307: "Temporary Redirect",
                                308: "Permanent Redirect",
                                
                                400: "Bad Request",
                                401: "Unauthorized",
                                403: "Forbidden",
                                404: "Not Found",
                                405: "Method Not Allowed",
                                406: "Not Acceptable",
                                407: "Proxy Authentication Required",
                                408: "Request Timeout",
                                409: "Conflict",
                                410: "Gone",
                                411: "Length Required",
                                412: "Precondition Failed",
                                413: "Payload Too Large",
                                414: "URI Too Long",
                                415: "Unsupported Media Type",
                                416: "Range Not Satisfiable",
                                417: "Expectation Failed",
                                418: "I'm a teapot",
                                421: "Misdirected Request",
                                422: "Unprocessable Content",
                                423: "Locked",
                                424: "Failed Dependency",
                                425: "Too Early",
                                426: "Upgrade Required",
                                428: "Precondition Required",
                                429: "Too Many Requests",
                                431: "Request Header Fields Too Large",
                                451: "Unavailable For Legal Reasons",

                                500: "Internal Server Error",
                                501: "Not Implemented",
                                502: "Bad Gateway",
                                503: "Service Unavailable",
                                504: "Gateway Timeout",
                                505: "HTTP Version Not Supported",
                                506: "Variant Also Negotiates",
                                507: "Insufficient Storage",
                                508: "Loop Detected",
                                510: "Not Extended",
                                511: "Network Authentication Required"
                            }

    CUSTOM_CODE_STATUSES: dict = {}

    def __init__ (self, current_status_code:int = CODE, 
                  custom_code_statuses:dict = CUSTOM_CODE_STATUSES):
        
        self.CODE = current_status_code
        self.CUSTOM_CODE_STATUSES = custom_code_statuses

    def set_code_status(self, code: int, status:str):
        self.CUSTOM_CODE_STATUSES[code] =  status
        
    def set_code(self, code: int=200):
        self.CODE = code
        if not self.CODE in self.CUSTOM_CODE_STATUSES and self.CODE in self.__CODE_STATUSES:
            self.set_status(code, self.DEFAULT_STATUS)

    def set_status(self, code, status):
        self.CUSTOM_CODE_STATUSES[code] = status
    
    def set_default_status(self, default_status:str):
        self.DEFAULT_STATUS = default_status
    
    def set_undef_status(self, undef_status:str):
        self.__NO_STATUS = undef_status

    def code(self) -> int:
        return self.CODE

    def status(self) -> str:
        if self.CODE in self.CUSTOM_CODE_STATUSES:
            return self.CUSTOM_CODE_STATUSES[self.CODE]
        if self.CODE in self.__CODE_STATUSES:
            return self.__CODE_STATUSES[self.CODE]
        else:
            return f'{self.__NO_STATUS}'

    def full_code_status_message(self) -> str:
        if self.CODE in self.CUSTOM_CODE_STATUSES:
            return self.PREFIX + str(self.CODE) + self.SEP + self.CUSTOM_CODE_STATUSES[self.CODE]
        if self.CODE in self.__CODE_STATUSES:
            return self.PREFIX + str(self.CODE) + self.SEP + self.__CODE_STATUSES[self.CODE]
        else:
            return f'{self.PREFIX} {self.CODE}{self.SEP} {self.__NO_STATUS}'
        
    def __str__(self) -> str:
        
        return self.full_code_status_message()

    def __call__(self, code:int, status:str|None=None, *args: Any, **kwds: Any) -> Any:
        self.set_code(code)


    def __eq__(self, __value: object) -> bool:
        return __value == self.CODE
    
    def __repr__(self) -> str:
        if self.CODE in self.CUSTOM_CODE_STATUSES:
            return f'Status(\'{self.CODE}\', {self.CUSTOM_CODE_STATUSES[self.CODE]})'
        if self.CODE in self.__CODE_STATUSES:
            return f'Status(\'{self.CODE}\', {self.__CODE_STATUSES[self.CODE]})'     
        else:
            return f'Status(\'{self.CODE}\', {self.__NO_STATUS})'
    
    def __dict__(self):
        """
        returns json like format
        """
        if self.CODE in self.CUSTOM_CODE_STATUSES:
            return{"Code": self.CODE, "Status": self.CUSTOM_CODE_STATUSES[self.CODE]}
        if self.CODE in self.__CODE_STATUSES:
            return{"Code": self.CODE, "Status": self.__CODE_STATUSES[self.CODE]}
        else:
            return{"Code": self.CODE, "Status": self.__NO_STATUS}



if __name__ == "__main__":
    status = StatusCode()
    status(123)

    print(status)