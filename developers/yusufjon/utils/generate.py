from sqlalchemy.orm import Session
from databases.main import ActiveSession, engine
from sqlalchemy import inspect
from fastapi import APIRouter

generate_router = APIRouter()

a_bracet = "{"
b_bracet = "}"

@generate_router.get("/generation", include_in_schema=False)
async def get_home(db: Session = ActiveSession):

    inspector = inspect(engine)

    # Beginning of Routes binding generation part
   
    # tables_names = ['production', 'product_store', 'cycle_store', 'material_use', 'product_use']
    tables_names = []

    for table_name in tables_names:

        model_content = schema_content = create_of_crud = update_of_crud = ""
        model_name = table_name.title()
        schema_name = "New" + model_name
        relationships = ""
        relationships_imports = ""

        for column in inspector.get_columns(table_name, schema="f9project"):

            colName = str(column['name'])
            colType = str(column['type'])


            if colName != 'id':

                col_type = 'Integer'

                if colType == 'INTEGER' or colType == 'SMALLINT':
                    col_type = "Integer"
                    prop_type = 'int'
                    default_val=0
                elif colType == 'TEXT':
                    col_type = "Text"
                    prop_type = 'dict'
                    default_val="''"
                elif colType == 'DOUBLE':
                    col_type = "Numeric"
                    prop_type = 'float'
                    default_val=0
                elif colType == 'DATETIME':
                    col_type = "DateTime"
                    prop_type = 'str'
                    default_val='func.now()'
                elif colType == 'DATE':
                    col_type = "Date"
                    prop_type = 'str'
                    default_val='func.now()'
                elif colType == 'TIME':
                    col_type = "Time"
                    prop_type = 'str'
                    default_val='func.now()'
                elif colType == 'TINYINT':
                    col_type = "Boolean"
                    prop_type = 'bool'
                    default_val='False'
                else: 
                    col_type = "String"
                    prop_type = 'str'
                    default_val="''"

                if column['nullable'] == False:
                    def_name = f"default={default_val}"
                else:
                    def_name="nullable=True"

                    

                foreign = ""
                if colName[-3:] == '_id':
                    foreign = f", ForeignKey('{colName[:-3]}.id')"
                    relationships += f"    {colName[:-3]} = relationship('{colName[:-3].title()}', backref='{table_name}s')\n"
                    relationships_imports += f"from developers.yusufjon.models.{colName[:-3]} import * \n"
                    
                model_content += f"    {column['name']} = Column({col_type}{foreign}, {def_name})\n"
                schema_content +=  f"    {colName.lower()}: {prop_type}\n"
                create_of_crud += f"        {colName}=form_data.{colName.lower()},\n"
                update_of_crud += f"\n            {model_name}.{colName}: form_data.{colName.lower()},"
        

        

#         with open(f'./developers/yusufjon/models/{table_name}.py', 'w') as f:
#             f.write(f'''from sqlalchemy import Column, Date, Integer, Numeric, DateTime, Time, String, Boolean, Text, ForeignKey, func
# from databases.main import Base
# from sqlalchemy.orm import relationship, backref
# {relationships_imports}

# class {model_name}(Base):
#     __tablename__ = "{table_name}"
#     id = Column(Integer, primary_key=True, index=True, autoincrement=True)
# {model_content}
# {relationships}
# ''')
            
#         with open(f'./developers/yusufjon/functions/{table_name}.py', 'w') as f:
#             f.write(f'''import math
# from sqlalchemy.orm import joinedload, Session
# from fastapi import HTTPException
# from developers.yusufjon.models.{table_name} import *
# from developers.yusufjon.schemas.{table_name} import *

# def get_all_{table_name}s(search, page, limit, usr, db: Session):
#     if page == 1 or page < 1:
#         offset = 0
#     else:
#         offset = (page-1) * limit
    
#     {table_name}s = db.query({model_name})

#     #if search:
#        #{table_name}s = {table_name}s.filter(
#            #{model_name}.id.like(f"%{a_bracet}search{b_bracet}%"),
#        #)

    
#     all_data = {table_name}s.order_by({model_name}.id.desc()).offset(offset).limit(limit)
#     count_data = {table_name}s.count()

#     return {a_bracet}
#         "data": all_data.all(),
#         "page_count": math.ceil(count_data / limit),
#         "data_count": count_data,
#         "current_page": page,
#         "page_limit": limit,
#     {b_bracet}

# def create_{table_name}(form_data: {schema_name}, usr, db: Session):
#     new_{table_name} = {model_name}(
# {create_of_crud}    )

#     db.add(new_{table_name})
#     db.commit()

#     raise HTTPException(status_code=200, detail="Ma`lumotlar saqlandi!")

# def update_{table_name}(id, form_data: Update{model_name}, usr, db: Session):
#     {table_name} = db.query({model_name}).filter({model_name}.id == id)
#     this_{table_name} = {table_name}.first()
#     if this_{table_name}:
#         {table_name}.update({a_bracet}    {update_of_crud}
#         {b_bracet})
#         db.commit()

#         raise HTTPException(status_code=200, detail="O`zgarish saqlandi!")
#     else:
#         raise HTTPException(status_code=400, detail=\"So`rovda xatolik!\")
    
# ''')
            
#         with open(f'./developers/yusufjon/schemas/{table_name}.py', 'w') as f:
#             f.write(f'''from enum import Enum
# from pydantic import BaseModel
# from developers.yusufjon.models.{table_name} import *

# class {schema_name}(BaseModel):
# {schema_content}

# class Update{model_name}(BaseModel):
# {schema_content}
        
# ''')
            
        with open(f'./developers/yusufjon/routers/{table_name}.py', 'w') as f:
            f.write(f'''from fastapi import HTTPException, APIRouter, Depends
from typing import Optional
from developers.yusufjon.schemas.user import NewUser
from security.auth import get_current_active_user
from databases.main import ActiveSession
from sqlalchemy.orm import joinedload, Session
from developers.yusufjon.models.{table_name} import *
from developers.yusufjon.functions.{table_name} import *
from developers.yusufjon.schemas.{table_name} import *
\n{table_name}_router = APIRouter(tags=['{model_name} Endpoint'])
\n@{table_name}_router.get("/{table_name}s", description="This router returns list of the {table_name}s using pagination")
async def get_{table_name}s_list(
    search: Optional[str] = "",
    page: int = 1,
    limit: int = 10,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)\n):   
    if not usr.role in ['any_role']:
        return get_all_{table_name}s(search, page, limit, usr, db)  
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")  

@{table_name}_router.post("/{table_name}/create", description="This router is able to add new {table_name}")
async def create_new_{table_name}(
    form_data: {schema_name},
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)\n):
    if not usr.role in ['any_role']:
        return create_{table_name}(form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")

@{table_name}_router.put("/{table_name}/{a_bracet + 'id' + b_bracet}/update", description="This router is able to update {table_name}")
async def update_one_{table_name}(
    id: int,
    form_data: Update{model_name},
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)\n):
    if not usr.role in ['any_role']:
        return update_{table_name}(id, form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")
''')
    return "success"
