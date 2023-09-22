

class Tables:
    tables = None
    def __call__(self):
        return self.tables

def read_data(file = 'data/columns_names.txt'):
    with open(file, 'r') as f:
        data = ''
        Lines = f.readlines()
    return Lines

Tables.tables = read_data()
#print(TABLES.tables)
TABLES = Tables()


