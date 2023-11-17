import pandas as pd


# df[df["TABLE_NAME"].str.contains("MARA")].iloc[0:5]
# df[(df["TABLE_NAME"].str.contains("MARA")) & (df["TABLE_NAME"]!= "MARA_STXL")].iloc[0:5]
# df[df["TABLE_NAME"] == "MARA"]
def find_in_df(prjct_name:str, cn_name:str, word:str):
    # TODO: no index table
    path = "connections/connections_schemas/"
    try: 
        df = pd.read_csv(f'{path}{prjct_name}__{cn_name}.csv')
    except FileNotFoundError:
        return {"message": "File Not Found",
                "data": None}
    
    result = []
    vals = 5
    if not df[df["TABLE_NAME"] == word].empty:
        exact_word = df[df["TABLE_NAME"] == word].to_dict('records')
        
        result = result + exact_word
        vals -= 1
    
    approximate_match = df[(df["TABLE_NAME"].str.contains(word)) & (df["TABLE_NAME"]!= word)].iloc[0:vals].to_dict('records')
    result = result + approximate_match 

    return result


def pick_just_column(lst, column_name):
    result = []
    for dct in lst:
        result.append(dct[column_name])
    return result

def get_columns(prjct_name:str, cn_name:str, word:str):
    result = find_in_df(prjct_name, cn_name, word)
    result = pick_just_column(result, "TABLE_NAME")
    return result