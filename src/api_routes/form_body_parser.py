import re
from typing import List


class ConsistencyError(Exception):
    pass


def get_vars(string:str):
    return re.findall("(?<=name=\")(.*?)(?=\")", string)

def get_value(var:str, string:str): 
    
    value = re.search(r"(?<=name\=\"" +var + r"\"\\r\\n\\r\\n)(.*?)(?=\\)", string)
    value = value.group() if value else ""
    return value

def divider_head_body_vars(vars:List):
    mains = []
    heads = []
    bodys = []
    for var in vars:
        if var[0:5] == "head_":
            heads.append(var)
        elif var[0:5] == "body_":
            bodys.append(var)
        else:
            mains.append(var)
    return (mains, heads, bodys)

def suffix_devider_names_only( vars):
    """
        returns only names vars.
        checks consistency for all
    """

    names = []
    #dtypes = []
    #defaults = []
    for var in vars:

        if var.endswith('_name'):
            names.append(var)
            continue

        if var.endswith('_dtype'):
            #dtypes.append(var)
            continue

        if var.endswith('_defval'):
            #defaults.append(var)
            continue
        else: 
            raise ConsistencyError('Unpredictable variant name ' + var )
    return names


def packer_vars(string, prefix, vars):
    """
        must return:
        [   (name, type, default),
            (name, type, default),
            ...
            (name, type, default) ]
    """
    # разделить на 3 группы
    # сортировать относительно одной из групп

    names = suffix_devider_names_only(vars=vars)
    result = [] 
    for var in names:
        name = get_value(var, string=string)
        dtype = get_value(prefix + name + "_dtype", string=string)
        default = get_value(prefix + name + "_defval", string=string)

        result.append((name, dtype, default)) 
    return result       
        

def body_parser(string):
    """
    must return:

        {
            'api_path': 'path/part',
            'prjct_name': 'your prj name',
            'cn_name': 'your api name',
            'bodys': [(name, type, default),
                      (name, type, default),
                      ...
                      (name, type, default) ],
            'heads': [(name, type, default),
                      (name, type, default),
                      ...
                      (name, type, default) ],
        }
    """
    print(string)
    vars = get_vars(string=string)
    
    mains, heads, bodys = divider_head_body_vars(vars)

    dada_heads = packer_vars(string, 'head_', heads)
    dada_bodys = packer_vars(string, 'body_', bodys)
    result = {"heads":dada_heads, "bodys":dada_bodys}
    for var in mains:
        result[var] = get_value(var, string=string)

    return result

