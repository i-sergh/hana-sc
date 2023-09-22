class Tables:
    tables = None
    def __call__(self):
        return self.tables
    
    def find(self, word):
        result = []
        for name in self.tables:
            name = ''.join(name.rstrip())
            if word == name:
                result[0] = name
            elif word in name and len(result ) < 10:
                result.append(name)
            
        return result



def read_data(file = 'search_drv/data/tables_names.txt'):
    with open(file, 'r') as f:
        data = ''
        Lines = f.readlines()
    return Lines

Tables.tables = read_data()

TABLES = Tables()
