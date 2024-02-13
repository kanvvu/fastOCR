import json

def check_and_return_config(path):
    with open(path) as file:
        data = json.load(file)

        if 'screen-scale' not in data:
            raise Exception('"screen-scale" not in CONFIG!')
        if 'alpha-value' not in data:
            raise Exception('"alpha-value" not in CONFIG!')
        if 'shortcut' not in data:
            raise Exception('"shortcut" not in CONFIG!')
        if 'languages' not in data:
            raise Exception('"languages" not in CONFIG!')
        
        if type(data['screen-scale']) != float:
            raise Exception("'screen-scale' should be type of FLOAT")
        if type(data['alpha-value']) != float:
            raise Exception("'alpha-value' should be type of FLOAT")
        if type(data['shortcut']) != str:
            raise Exception("'shortcut' should be type of STR")
        if type(data['languages']) != list:
            raise Exception("'languages' should be type of list")
        
        if len(data['languages']) == 0:
            raise Exception("no language in languages!")
        
        for lang in data['languages']:
            if type(lang) != str:
                raise Exception("language should be type of STR")
            
        return data
