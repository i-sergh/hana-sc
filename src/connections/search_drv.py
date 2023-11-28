import pandas as pd


def chek_file_existense(func):
    async def wraper(prjct_name:str, cn_name:str, prefix:str='tables', 
                     path:str|None=None,
                     *args, **kwargs):
        
        if not path:
            path = f"connections/connections_schemas/{prjct_name}__{cn_name}"
        
        try: 
            df = pd.read_csv(f'{path}/{prefix}_{prjct_name}__{cn_name}.csv')
        except FileNotFoundError:
            print("can't open df file. PATH: " + f'{path}/{prefix}_{prjct_name}__{cn_name}.csv')
            return {"message": "File Not Found",
                "data": None}
        
       
        return await func(df, *args, **kwargs)
    return wraper

@chek_file_existense
async def find_in_df(df, key_word:str, key_col:str='TABLE_NAME'):
    # TODO: no index table        
    result = []
    vals = 5
    if not df[df[key_col] == key_word].empty:
        exact_word = df[df[key_col] == key_word].to_dict('records')
        
        result = result + exact_word
        vals -= 1
    
    approximate_match = df[(df[key_col].str.contains(key_word)) & (df[key_col]!= key_word)].iloc[0:vals].to_dict('records')
    result = result + approximate_match 

    return result

@chek_file_existense
async def find_exact_in_df(df, key_word:str, key_col:str='TABLE_NAME'):
    
    exact_words = df[df[key_col] == key_word].to_dict('records')
        
    return exact_words



def pick_just_column(lst, column_name):
    result = []
    for dct in lst:
        result.append(dct[column_name])
    return result

async def find_table_columns_by_part_name(prjct_name:str, cn_name:str, key_col:str, word:str):
    
    """ just columns names"""
    result = await find_in_df(prjct_name=prjct_name, cn_name=cn_name, key_col=key_col, key_word=word)
    result = pick_just_column(result, key_col)
    return result

@chek_file_existense
async def headers_from_df(df):    
    return df.columns.values.tolist()

from time import sleep

@chek_file_existense
async def content_from_df(df, headers, key_col, key_word):
    
    #TODO: if df is empty !!!
    df = df[df[key_col]==key_word ]
    df.fillna('NaN', inplace=True)
    result = {}
    
    for header in headers:
        result[header] = df[header].to_list()
    return result


if __name__ == '__main__':

    import asyncio 
    
    #res = asyncio.run(find_in_df(prjct_name='Prjct', cn_name='Hana', prefix='tables',
    #                    key_word='MARA', key_col='TABLE_NAME', path='connections_schemas/Prjct__Hana'))


    #res = asyncio.run(find_exact_in_df(prjct_name='Prjct', cn_name='Hana', prefix='columns',
    #                    key_word='MARA', path='connections_schemas/Prjct__Hana'))


    headers = asyncio.run(headers_from_df(prjct_name='Prjct', cn_name='Hana', prefix='columns', path='connections_schemas/Prjct__Hana'))
    print(headers)
    
    #res = asyncio.run(content_from_df(prjct_name='Prjct', cn_name='Hana', headers=headers, key_col='TABLE_NAME', key_word='MARA', prefix='columns', path='connections_schemas/Prjct__Hana'))
    #print(res)