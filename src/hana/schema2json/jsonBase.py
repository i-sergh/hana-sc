from hana.schema2json.prettyStatus.prettyStatusHTTP import StatusCode


from copy import deepcopy, copy

# interfaces :p

class TableName:
    _table_name = ''

    def __init__(self, name):
        self._table_name = name

    def set_table_name(self, name):
        self._table_name = name

    def __str__(self) -> str:
        return self._table_name
    
    def __repr__(self) -> str:
        return self._table_name



class JSONStruct:
    _table_name:TableName
    cols: dict
    _cols_counter: int
    _col_temp: dict 
    _cols_names: set
    _comparison_name_col:dict
    _cols_sequense: list
    statuscode: StatusCode
    data: dict 


    def __init__(self):
        self._table_name = TableName('')
        self.cols: dict = {}
        self._cols_counter: int  = 0
        self._col_temp: dict  = {    
                                    "name": None,
                                    "dtype": None,
                                    "primary_key": False,
                                }
        self._cols_names: set = set()
        self._comparison_name_col:dict  = {}
        self._cols_sequense: list  = []
        self.statuscode: StatusCode = StatusCode(200)
        self.data: dict = {
                            "status": self.statuscode.status(),
                            "code": self.statuscode.code(),
                            'table_name': self._table_name,
                            "cols": self.cols,
                        }

    def get_model(self):
        attrs = {}
        for key in self.__annotations__.keys():
            try:
                
                if key == 'statuscode':
                    attrs[key] = StatusCode(self.statuscode.CODE)
                else:
                    attrs[key] = copy(self.__getattribute__(key))
                
            except AttributeError:
                raise AttributeError(f' -> {key}: {self.__getattribute__(key)}')

        return attrs

    def copy(self, obj:object|None=None):
        attrs = self.get_model()
        if not obj:
            obj = JSONStruct()
        obj._copy_from(**attrs)
        obj._copy_data()
        return obj

    def set_table_name(self, name):
        self._table_name.set_table_name(name)

    def _copy_from (self, **kwargs):
        for key in kwargs.keys():
            if key != 'data':
                self.__setattr__(key, kwargs[key])     
            
    def _copy_data(self):
        self.data = {
                        "status": self.statuscode.status(),
                        "code": self.statuscode.code(),
                        'table_name': self._table_name,
                        "cols": self.cols,
                    }

    def _set_status(self, code):
        self.statuscode.set_code(code)

    def add_cols(self, cols:list|tuple, dtypes:list|tuple, pkeys:[int]):
        
        for ind, col_dtype in enumerate (zip(cols, dtypes)): 
            col, dtype = col_dtype
            if col in self._cols_names:
                print("Col", col, "already exists" )
                print(f'use alter_col to change col\'s values')
            else:
                #create new col
                self.cols['col'+ str(self._cols_counter)] = self._col_temp.copy()
                self.cols['col'+str(self._cols_counter)]["name"] = col
                self.cols['col'+str(self._cols_counter)]["dtype"] = dtype
                if ind in pkeys:
                    self.cols['col'+str(self._cols_counter)]["primary_key"] = True
                #  
                self._cols_names.add(col)
                self._comparison_name_col[col] = 'col'+str(self._cols_counter)
                self._cols_sequense.append(col)

                print("Col", col, "created as", 'col'+ str(self._cols_counter))
                
                self._cols_counter += 1

    def get_data(self):
        return self.data
        

    """
    def alter_col(self, col_name:str, dtype:str, pkey:bool):
        if not col_name in self._cols_names:
            print('There is no col ', col_name)
            return
        
        colid = self._comparison_name_col[col_name]

        self.cols[colid]["name"] = col_name
        self.cols[colid]["dtype"] = dtype
        self.cols[colid]["primary_key"] = pkey
        #del self._comparison_name_col[col_name]
        print('Col', col_name, 'changed:')
        print('name ' , col_name)
        print('dtype ', dtype)
        print('primart_key', pkey)

    """

class JSONData( JSONStruct):
    table_name:str
    cols: dict
    _cols_counter: int
    _col_temp: dict 
    _cols_names: set
    _comparison_name_col:dict
    _cols_sequense: list
    statuscode: StatusCode
    data: dict 
    rows: dict
    _rows_counter: int 
    _row_temp: dict 

    def __init__(self):
        super().__init__()
        
        self.rows: dict = {}

        self._rows_counter: int = 0 # счетчик количества строк - нужен для создания нового имени строки
        self._row_temp: dict = {} # Заполняется в процессе появления информации о колонках
        self.data['rows'] = self.rows

    def add_one_row(self, row:list|tuple):
        if len(row) != len(self._cols_sequense):
            # TODO:ERROR
            print("data len not match")
        
        rowid = 'row' + str(self._rows_counter)

        self.rows[rowid] = self._row_temp.copy()

        for col, cell in zip(self._cols_sequense, row):
            colid = self._comparison_name_col[col]        # gets colID
            self.rows[rowid][colid] = cell

        self._rows_counter += 1

    def copy(self, obj:object|None=None):
        attrs = self.get_model()
        if not obj:
            obj = JSONData()
        obj._copy_from(**attrs)
        obj._copy_data()
        return obj
    
    def _copy_data(self):
        self.data = {
                        "status": self.statuscode.status(),
                        "code": self.statuscode.code(),
                        'table_name': self._table_name,
                        "cols": self.cols,
                        "rows": self.rows,
                    }
    
    def set_Struct(self, model):
        self._copy_from(**model)
        self._copy_data()



'''
class JSONBase:
    def __init__(self,):
        self.cols: dict = {}

        self._cols_counter: int = 0 # счетчик количества колонок - нужен для создания нового имени колонки
        self._col_temp: dict = {    
                            "name": None,
                            "dtype": None,
                            "primary_key": False,
                        }
        self._cols_names: set = set() # список уникальных имен
        self._comparison_name_col:dict = {} # сопоставление для нахождения колонки апо имени
        self._cols_sequense = [] # порядок следования колонок. Используется в наследуемом классе

        self.statuscode = StatusCode() 
        self.data: dict = {
            "status": self.statuscode.status(),
            "code": self.statuscode.code(),
            "cols": self.cols,
        }

    #
    def set_status(self, code):
        self.statuscode.set_code(code)
    
    #
    def add_cols(self, cols:list|tuple, dtypes:list|tuple, pkeys:[int]):
        
        for ind, col_dtype in enumerate (zip(cols, dtypes)): 
            col, dtype = col_dtype
            if col in self._cols_names:
                print("Col", col, "already exists" )
                print(f'use alter_col to change col\'s values')
            else:
                #create new col
                self.cols['col'+ str(self._cols_counter)] = self._col_temp.copy()
                self.cols['col'+str(self._cols_counter)]["name"] = col
                self.cols['col'+str(self._cols_counter)]["dtype"] = dtype
                if ind in pkeys:
                    self.cols['col'+str(self._cols_counter)]["primary_key"] = True
                #  
                self._cols_names.add(col)
                self._comparison_name_col[col] = 'col'+str(self._cols_counter)
                self._cols_sequense.append(col)

                print("Col", col, "created as", 'col'+ str(self._cols_counter))
                
                self._cols_counter += 1

        #self._generate_rows_temp()

    #
    def alter_col(self, col_name:str, dtype:str, pkey:bool):
        if not col_name in self._cols_names:
            print('There is no col ', col_name)
            return
        
        colid = self._comparison_name_col[col_name]

        self.cols[colid]["name"] = col_name
        self.cols[colid]["dtype"] = dtype
        self.cols[colid]["primary_key"] = pkey
        #del self._comparison_name_col[col_name]
        print('Col', col_name, 'changed:')
        print('name ' , col_name)
        print('dtype ', dtype)
        print('primart_key', pkey)

    def remove_col(self,  col_name:str=None, col_idx:str=None):
        if col_name:
            self._remove_col_by_name(col_name)
            return None
        
        if col_idx:
            print('not ready :p')
            return None
        
    def _remove_col_by_name(self, col_name):
        colid = self._comparison_name_col[col_name]
        del self.cols[colid]
        del self._comparison_name_col[col_name]
        self._cols_names.remove(col_name)
        self._cols_sequense.remove(col_name)
        self._cols_counter -= 1

    def get_data(self):
        return self.data
    
    def get_copy_from(self, struct:JSONBase):
        self.cols = struct.cols.copy()
        self._cols_counter = struct._cols_counter
        self._col_temp = struct._col_temp.copy()
        self._cols_names = struct._cols_names.copy()
        self._comparison_name_col = struct._comparison_name_col.copy()
        self._cols_sequense = struct._cols_sequense.copy()
        self.statuscode.CODE = struct.statuscode.CODE
        self.data = struct.data.copy()

    def _copy_to(self):
        obj_params = []
        
        obj_params.append(self.cols.copy())
        obj_params.append(self._cols_counter)
        obj_params.append(self._col_temp.copy())
        obj_params.append(self._cols_names.copy())
        obj_params.append(self._comparison_name_col.copy())
        obj_params.append(self._cols_sequense.copy())
        obj_params.append(self.statuscode.CODE)
        obj_params.append(self.data.copy())

        return obj_params
    
    def copy(self):
        obj_params = self._copy_to()
        return 

'''


# TODO: Make real copy
'''
class JSONData(JSONBase):

    rows: dict = {}
    
    _rows_counter: int = 0 # счетчик количества строк - нужен для создания нового имени строки
    _row_temp: dict = {} # Заполняется в процессе появления информации о колонках
    
    statuscode = StatusCode() 
    
    data = JSONBase.data.copy() # super without init :p 
    data['rows'] = rows

    def add_one_row(self, row:list|tuple):
        if len(row) != len(self._cols_sequense):
            # TODO:ERROR
            print("data len not match")
        
        rowid = 'row' + str(self._rows_counter)

        self.rows[rowid] = self._row_temp.copy()

        for col, cell in zip(self._cols_sequense, row):
            colid = self._comparison_name_col[col]        # gets colID
            self.rows[rowid][colid] = cell

        self._rows_counter += 1

    def alter_col(self, col_name:str, dtype:str, pkey:bool):
        
        for key in self.data['rows']:
            pass    
        super().alter_col(col_name, dtype, pkey)

    def add_cols(self, cols:list|tuple, dtypes:list|tuple, pkeys:[int]):
        super().add_cols(cols, dtypes, pkeys)
        self._generate_rows_temp()

    def _generate_rows_temp(self):
          for col in self.cols.keys():
              if not col in self._row_temp:
                  self._row_temp[col] = None 

    def copy(self):
        """

        """
        self._copy_to(self)

    def fromStructure(self, struct:JSONBase):
        """
        Выполняет копирование структуры JSONBase
        """
        super()._copy_to(struct)
        self._generate_rows_temp()

    def _copy_to(self, struct:JSONData):
        """
        Вфыполняет копирование в этот экземпляр по введённой структуре
        """
        obj = super()._copy_to(struct)
        self.rows = struct.rows.copy()
        self._rows_counter = struct._rows_counter
        self._row_temp = struct._row_temp.copy()
        self.data = struct.data.copy()

'''
