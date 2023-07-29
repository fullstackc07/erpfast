from fastapi import HTTPException, UploadFile


def looking_for(search, model):
    return model

def check_file_type(file: UploadFile, types: list, size: int):

    if file.content_type not in types:
        raise HTTPException(status_code=400, detail="Fayl tipi png, jpg yoki jpeg bo`lishi kerak!")
    else:
        return file.content_type