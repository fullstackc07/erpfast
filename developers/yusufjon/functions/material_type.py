import math
from sqlalchemy.orm import contains_eager, Session, aliased
from fastapi import HTTPException
from developers.yusufjon.models.component import Component
from developers.yusufjon.models.cycle import Cycle
from developers.yusufjon.models.material import Material
from developers.yusufjon.models.material_type import *
from developers.yusufjon.models.plant_cycle import Plant_Cycle


def get_all_material_types(for_plant_id, search, page, limit, usr, db, hidden: bool):
    if page == 1 or page < 1:
        offset = 0
    else:
        offset = (page-1) * limit

    m_t = aliased(Material)

    material_types = db.query(
        Material_Type,
        func.count(m_t.id.distinct()).label('material_count')
    )\
        .outerjoin(m_t, Material_Type.materials)\

    # if for_plant_id > 0:
    #     material_types = material_types\
    #         .join(Material_Type.components)\
    #         .join(Component.cycle)\
    #         .filter(Cycle.plant_cycles.has(Plant_Cycle.plant_id==for_plant_id))

    material_types = material_types.filter(
        Material_Type.hidden == hidden).group_by(Material_Type)

    if search:
        material_types = material_types.filter(
            Material_Type.name.like(f"%{search}%"),
        )

    all_data = material_types.order_by(
        Material_Type.id.desc()).offset(offset).limit(limit)
    count_data = material_types.count()

    return {
        "data": all_data.all(),
        "page_count": math.ceil(count_data / limit),
        "data_count": count_data,
        "current_page": page,
        "page_limit": limit,
    }


def update_material_type(id, form_data, usr, db):
    material_type = db.query(Material_Type).filter(Material_Type.id == id)
    this_material_type = material_type.first()
    if this_material_type:
        material_type.update({
            Material_Type.name: form_data.name,
            Material_Type.image: form_data.image,
            Material_Type.hidden: form_data.hidden,
        })
        db.commit()

        raise HTTPException(status_code=200, detail="O`zgarish saqlandi!")
    else:
        raise HTTPException(status_code=400, detail="So`rovda xatolik!")
