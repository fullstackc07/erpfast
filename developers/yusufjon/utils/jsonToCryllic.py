from .trlatin import tarjima

def dict_to_nested_class(data):
    
    res = {}
    
    for key, value in data.items():
        if isinstance(value, dict):
            res[key] = dict_to_nested_class(value)
        else:
            res[key] = tarjima(value, 'ru')
    
    return res