from copy import deepcopy
import math
from sqlalchemy.orm import joinedload, Session
from fastapi import HTTPException
from developers.yusufjon.models.product_cycle import *
from developers.yusufjon.schemas.cycle import UpdateCyclePosition
from developers.yusufjon.schemas.product_cycle import *
from developers.yusufjon.models.production_tree import *

def get_all_product_cycles(all_cycles, product_id, cycle_id, page, limit, db: Session):
    
    if page == 1 or page < 1:
        offset = 0
    else:
        offset = (page-1) * limit
    
    if all_cycles == False:
        product_cycles = db.query(Product_Cycle).filter_by(disabled=False)
        if product_id > 0:
            product_cycles = product_cycles.filter_by(product_id=product_id)
        
        if cycle_id > 0:
            product_cycles = product_cycles.filter_by(cycle_id=cycle_id)

        all_data = product_cycles.order_by(Product_Cycle.ordinate.asc()).offset(offset).limit(limit)
        count_data = product_cycles.count()
    else:
        product_cycles = db.query(Production_Tree).options(joinedload(Production_Tree.cycle)).filter_by(for_product_id=product_id).group_by(Production_Tree.cycle_id)
        
        all_data = product_cycles.order_by(Production_Tree.ordinate.desc()).offset(offset).limit(limit)
        count_data = product_cycles.count()

    

    return {
        "data": all_data.all(),
        "page_count": math.ceil(count_data / limit),
        "data_count": count_data,
        "current_page": page,
        "page_limit": limit,
    }

def create_product_cycle(form_data: NewProduct_Cycle, usr, db: Session):

    product = db.query(Product).filter_by(
        id=form_data.product_id, disabled=False).first()

    if not product:
        raise HTTPException(status_code=400, detail="Mahsulot topilmadi!")

    exist_pr_cycle = db.query(Product_Cycle).filter_by(cycle_id=form_data.cycle_id,
        product_id=form_data.product_id, disabled=False).first()

    if not exist_pr_cycle:

     # detecting after and before ids
        cycles = db.query(Product_Cycle).filter_by(product_id=product.id, disabled=False)

        if cycles.count() == 0:
            ordinate = 1
        else:
            last_cycle = cycles.order_by(Product_Cycle.ordinate.desc()).first()
            if last_cycle:
                ordinate = last_cycle.ordinate + 1
            else:
                raise HTTPException(
                    status_code=400, detail="Jarayonlar taribida xatolik bor!")

    
        new_product_cycle = Product_Cycle(
            cycle_id=form_data.cycle_id,
            product_id=form_data.product_id,
            ordinate=ordinate,
        )

        db.add(new_product_cycle)
        db.commit()


def update_product_cycle(id, form_data: UpdateProduct_Cycle, usr, db: Session):
    product_cycle = db.query(Product_Cycle).filter(Product_Cycle.id == id)
    this_product_cycle = product_cycle.first()
    if this_product_cycle:
        product_cycle.update({    
            Product_Cycle.cycle_id: form_data.cycle_id,
            Product_Cycle.disabled: form_data.disabled,
            Product_Cycle.product_id: form_data.product_id,
        })
        db.commit()

        raise HTTPException(status_code=200, detail="O`zgarish saqlandi!")
    else:
        raise HTTPException(status_code=400, detail="So`rovda xatolik!")
    
def update_cycle_posistion(form_data: UpdateCyclePosition, usr, db: Session):

    cycle = db.query(Product_Cycle).filter_by(id=form_data.id)
    this_cycle = cycle.first()

    error_req = HTTPException(status_code=400, detail="So`rovda xatolik!")

    if this_cycle:
        ordinate = deepcopy(this_cycle.ordinate)
        if form_data.direction == 'top':
            next_ordinate = ordinate - 1
        else:
            next_ordinate = ordinate + 1


        next_cycle = db.query(Product_Cycle).filter_by(product_id=this_cycle.product_id, ordinate=next_ordinate)
        this_next_cycle = next_cycle.first()

        if this_next_cycle:
            # return str(ordinate) + " " + str(next_ordinate)
            next_cycle.update({Product_Cycle.ordinate: deepcopy(ordinate)})
            cycle.update({Product_Cycle.ordinate: deepcopy(next_ordinate)})
            db.commit()

        else:
            raise error_req

        raise HTTPException(status_code=200, detail="O`zgarish saqlandi!")

    raise HTTPException(status_code=400, detail="So`rovda xatolik!")

