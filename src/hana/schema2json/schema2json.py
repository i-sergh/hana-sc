
from hana.models import HanaBase

cols = {}
rows = {}
data = {"status": "success",
        "code": 200,
        "cols": cols,
        "rows": rows
}



def get_test_json():
    data2 = {"status": "success",
            "code": 200,
            "cols": {
                    "col1":{
                            "name": "eins",
                            "dtype": "str",
                            "other_data": "data",
                            "primary_key": True    
                        },
                    "col2":{
                            "name": "zwei",
                            "dtype": "str",
                            "other_data": "data",   
                            "primary_key": False 
                        },
                    "col3":{
                            "name": "drei",
                            "dtype": "str",
                            "other_data": "data",  
                            "primary_key": False  
                        },
                    },
            "rows": {
                    "row1": {
                            
                            "col1": "one",
                            "col2": "two",
                            "col3": "three"
                        },
                    "row2": {
                            
                            "col1": "один",
                            "col2": "два",
                            "col3": "три"
                        },

            }

    }
    return data2

def test_get_empty_json():
    return data

def _fill_by_schema():
    print(HanaBase.metadata.tables.values())
    return {'ha': 'ha'}