import math
from sqlalchemy.orm import joinedload, Session, aliased
from fastapi import HTTPException
from databases.main import SessionLocal
from developers.yusufjon.utils.trlatin import tarjima
from ..models.material_store import Material_Store
from ..models.product_store import Product_Store
from ..models.production import *
from ..models.material import *
from ..models.product import *
from ..models.attandance import *
from ..models.material import *
from ..models.component import *
from ..models.cycle_store import *
from ..models.plant_cycle import *
from ..models.plan import *
from ..models.product_material import *
from ..models.user_kpi import *
from ..schemas.production import *
from ..schemas.notification import *
from ..models.product_cycle import *
from ..models.component_utilizing import *
from developers.abdusamad.models import *
from sqlalchemy.sql import label, func, or_
from ..utils.wsmanager import manager

dbb: Session = SessionLocal()


def get_all_productions(plant_id, search, page, limit, usr, db: Session):
    if page == 1 or page < 1:
        offset = 0
    else:
        offset = (page-1) * limit

    productions = db.query(Production).options(
        joinedload(Production.product).subqueryload(Product.olchov),
        joinedload(Production.material),
        joinedload(Production.cycle),
        joinedload(Production.user),
        joinedload(Production.trade).options(
            joinedload(Trades.order).subqueryload(Orders.customer)
        )
    )

    if plant_id > 0:
        productions = productions.filter(Production.plant_id == plant_id)

    if len(search) > 0:
        productions = productions.join(Production.product)\
            .join(Production.material)\
            .join(Production.cycle).filter(
                or_(
                    Product.name.like(f"%{tarjima(search, 'ru')}%"),
                    Product.name.like(f"%{tarjima(search, 'uz')}%"),
                    Material.name.like(f"%{tarjima(search, 'ru')}%"),
                    Material.name.like(f"%{tarjima(search, 'uz')}%"),
                    Cycle.name.like(f"%{tarjima(search, 'ru')}%"),
                    Cycle.name.like(f"%{tarjima(search, 'uz')}%"),
                )
        )

    all_data = productions.order_by(
        Production.created_at.desc()).offset(offset).limit(limit)
    count_data = productions.count()

    return {
        "data": all_data.all(),
        "page_count": math.ceil(count_data / limit),
        "data_count": count_data,
        "current_page": page,
        "page_limit": limit,
    }


def get_production_orders(search, plant_id, page, limit, usr, db: Session):

    if page == 1 or page < 1:
        offset = 0
    else:
        offset = (page-1) * limit

    cycle_store = db.query(
        func.coalesce(func.sum(Cycle_Store.value), 0)
    ).filter(
        Cycle_Store.trade_item_id == Plan.trade_item_id,
        Cycle_Store.size1 == Plan.size1,
        Cycle_Store.size2 == Plan.size2,
        Cycle_Store.material_id == Plan.material_id,
        Cycle_Store.ordinate >= Product_Cycle.ordinate,
        Cycle_Store.value > 0,
    )

    plans = db.query(
        label('plan_id', Plan.id),
        label('quantity', func.ceil(Plan.rest_value - cycle_store)),
        label('product_id', Plan.product_id),
        label('izoh', Plan.comment),
        label('trade_id', Plan.trade_id),
        label('trade_item_id', Plan.trade_item_id),
        label('size1', Plan.size1),
        label('size2', Plan.size2),
        label('customer_name', Customers.name),
        label('ready_value', Plan.bron_value + cycle_store),
        label('product_name', Product.name),
        label('product_image', Product.image),
        label('hasSize', Product_Type.hasSize),
        label('olchov_name', Olchov.name),
        label('cycle_name', Cycle.name),
        label('customer_id', Customers.name),
        label('product_cycle_id', Product_Cycle.id),
        label('material', func.coalesce(Material.name, '')),
        label('material_id', func.coalesce(Material.id, 0)),
        label('to_date', Plan.to_date),
    )\
        .join(Plan.product)\
        .join(Product.olchov)\
        .join(Product.product_type)\
        .join(Product_Cycle, Plan.product_id == Product_Cycle.product_id)\
        .join(Product_Cycle.cycle)\
        .join(Cycle.plant_cycles)\
        .join(Plan.order)\
        .join(Orders.customer)\
        .outerjoin(Plan.material)\
        .filter(
            Plant_Cycle.plant_id == plant_id,
            Plant_Cycle.disabled == False,
            Orders.status == 'pre_order'
    ).filter(Plan.rest_value - cycle_store > 0)\
        .group_by(Plan.id, Product_Cycle.id)\
        .order_by(Orders.delivery_date.desc())

    if len(search) > 0:
        plans = plans.filter(or_(
            Product.name.like(f"%{tarjima(search, 'uz')}%"),
            Product.name.like(f"%{tarjima(search, 'ru')}%"),
            Cycle.name.like(f"%{tarjima(search, 'uz')}%"),
            Cycle.name.like(f"%{tarjima(search, 'ru')}%"),
        ))

    all_data = plans.order_by(
        Orders.delivery_date.asc()).offset(offset).limit(limit)
    count_data = plans.count()

    return {
        "data": all_data.all(),
        "page_count": math.ceil(count_data / limit),
        "data_count": count_data,
        "current_page": page,
        "page_limit": limit,
    }


def get_production_order_details(plan_id: int, material_id: int, size1: float, size2: float, plant_id: int, product_cycle_id: int, value: float, trade_id: int, usr, db: Session):

    product_cycle = db.query(Product_Cycle).get(product_cycle_id)

    cycle = product_cycle.cycle
    if not cycle:
        raise HTTPException(status_code=400, detail=f"Jarayon topilmadi!")

    next_product_cycle = db.query(Product_Cycle).join(Product_Cycle.cycle)\
        .filter(
            Product_Cycle.product_id == product_cycle.product_id,
            Product_Cycle.disabled == False,
            Product_Cycle.ordinate > product_cycle.ordinate
    )

    if trade_id == 0:
        next_product_cycle = next_product_cycle.filter(Cycle.special == False)

    next_product_cycle = next_product_cycle.order_by(
        Product_Cycle.ordinate.asc()).first()

    if next_product_cycle:
        next_plants = db.query(Plant.id, Plant.name).select_from(Plant_Cycle)\
            .join(Plant_Cycle.plant).filter(
                Plant_Cycle.cycle_id == next_product_cycle.cycle_id,
                Plant_Cycle.disabled == False
        ).all()
    else:
        next_plants = []

    mtrlstr = aliased(Material_Store)
    material_store = db.query(func.sum(mtrlstr.value)).select_from(mtrlstr).filter(
        mtrlstr.material_id == Component_Item.material_id).subquery()

    prdctstr = aliased(Product_Store)


    product_store = db.query(func.sum(prdctstr.value)).select_from(prdctstr).filter(
        prdctstr.product_id == Component_Item.product_id,
        prdctstr.value > 0,
        prdctstr.market_id == 0,
        prdctstr.material_id == material_id,
        prdctstr.size1 == 0,
        prdctstr.size2 == 0,
    )

    try:
        material_type_id = db.query(Material).get(material_id).material_type_id
    except:
        material_type_id = 0

    components = db.query(
        Component_Item,
        label('needy_value', (Component_Item.value*value)),
        label('warehouse', func.coalesce(
            func.IF(Component_Item.material_id > 0, material_store, product_store.subquery()), 0))
    ).options(
        joinedload(Component_Item.material).options(
            joinedload(Material.olchov).load_only(Olchov.name)
        ).load_only(Material.name),
        joinedload(Component_Item.product).options(
            joinedload(Product.olchov).load_only(Olchov.name)
        ).load_only(Product.name)
    ).join(Component_Item.component).join(Component.cycle)\
        .filter(Component.cycle_id == product_cycle.cycle_id, Component_Item.disabled == False, Component.disabled == False)\
        .filter(func.IF(
            Component.material_type_id == material_type_id,
            Component_Item.material_id == material_id,
            Component_Item.main == True,
        ))

    before_cycle = db.query(Cycle).select_from(Product_Cycle).join(Product_Cycle.cycle)\
        .filter(
            Product_Cycle.ordinate < product_cycle.ordinate,
            Product_Cycle.product_id == product_cycle.product_id,
            Product_Cycle.disabled == False
    )

    # return next_plants

    if trade_id == 0:
        before_cycle = before_cycle.filter(Cycle.special == False)

    before_cycle = before_cycle.order_by(Product_Cycle.ordinate.desc()).first()

    if not before_cycle:
        before_cycle_one = None
    else:

        # before_cycle.hasPeriod = True

        if before_cycle.hasPeriod == True:

            warhs = db.query(func.coalesce(func.sum(Cycle_Store.value), 0).label('value'), Cycle_Store.period).filter_by(
                    cycle_id=before_cycle.id,
                    product_id=product_cycle.product_id,
                    plant_id=plant_id,
                    trade_id=trade_id,
                    size1=size1,
                    size2=size2,
                    material_id=material_id,
                ).order_by(Cycle_Store.period.desc()).group_by(Cycle_Store.period).all()

            before_cycle_one = {
                "Cycle": before_cycle,
                "warehouse": warhs,
                "warehouse_list": [ # warhs
                    {
                        "period": "2023-07-30",
                        "value": 12.5,
                    },
                    {
                        "period": "2023-08-22",
                        "value": 10.1,
                    },

                ],
                'warehouse_double': 0
            }
        else:

            warhs = db.query(func.sum(Cycle_Store.value)).filter_by(
                    cycle_id=before_cycle.id,
                    product_id=product_cycle.product_id,
                    plant_id=plant_id,
                    trade_id=trade_id,
                    size1=size1,
                    size2=size2,
                    material_id=material_id).scalar()

            before_cycle_one = {
                
                "Cycle": before_cycle,
                "warehouse": warhs,
                
                "warehouse_list": [],
                'warehouse_double': warhs
                
            }

    return {
        'this_cycle': product_cycle.cycle,
        'next_plants': next_plants,
        'before_cycle': before_cycle_one,
        'components': components.all(),
    }


async def create_production(form_data: NewProduction, usr, db: Session):

    utilizings = []

    cycle_store = db.query(func.sum(Cycle_Store.value)).filter_by(
        cycle_id=Cycle.id,
        product_id=Product_Cycle.product_id,
        plant_id=form_data.plant_id,
        trade_id=form_data.trade_id,
        size1=form_data.size1,
        size2=form_data.size2,
        material_id=form_data.material_id,
    ).subquery()

    product_cycle: Product_Cycle = db.query(
        Product_Cycle).get(form_data.product_cycle_id)

    cycle: Cycle = product_cycle.cycle

    before_cycle = db.query(Cycle, label('warehouse', func.coalesce(cycle_store, 0)))\
        .select_from(Product_Cycle).join(Product_Cycle.cycle)\
        .filter(
            Product_Cycle.ordinate < product_cycle.ordinate,
            Product_Cycle.product_id == product_cycle.product_id,
            Product_Cycle.disabled == False
    )

    if form_data.trade_id == 0:
        before_cycle = before_cycle.filter(Cycle.special == False)

    before_cycle = before_cycle.order_by(Product_Cycle.ordinate.desc()).first()

    if form_data.next_plant_id > 0:
        finished = False
    else:
        finished = True
        form_data.next_plant_id = form_data.plant_id

    plan: Plan = db.query(Plan).get(form_data.plan_id)
    plan = Plan(product_id=0, size1=0, size2=0,
                material_id=0) if not plan else plan
    # tannarni hisoblash boshlanishi
    total_cost = 0  # <--- noldan boshlanadi

    if form_data.material_id > 0:
        product_material = db.query(ProductMaterial).filter_by(
            product_id=product_cycle.product_id,
            material_id=form_data.material_id,
        ).first()

        if not product_material:
            raise HTTPException(
                status_code=400, detail='Material shaklga biriktirilmagan')

    # Bitta oldingi jarayondan chiqqan yarim tayyor mahsulot miqdorini tekshirish
    if before_cycle:

        needy_value_before = form_data.value
        cycle_stores = db.query(Cycle_Store).filter_by(
            product_id=product_cycle.product_id,
            material_id=form_data.material_id,
            plant_id=form_data.plant_id,
            cycle_id=before_cycle.Cycle.id,
            size1=form_data.size1,
            size2=form_data.size2,
            trade_id=form_data.trade_id
        ).filter(Cycle_Store.value > 0)

        for cycle_store in cycle_stores.all():
            if needy_value_before > 0:
                if cycle_store.value < needy_value_before:
                    total_cost = total_cost + cycle_store.price * cycle_store.value
                    needy_value_before = needy_value_before - cycle_store.value
                    minus_val = cycle_store.value
                    db.query(Cycle_Store).filter_by(
                        id=cycle_store.id).update({Cycle_Store.value: 0})

                else:
                    total_cost = total_cost + cycle_store.price * needy_value_before
                    minus_val = needy_value_before
                    db.query(Cycle_Store).filter_by(id=cycle_store.id).update(
                        {Cycle_Store.value: Cycle_Store.value - needy_value_before})

                    needy_value_before = 0

                utilizings.append(ComponentUtilizing(
                    value=minus_val,
                    cycle_store_id=cycle_store.id
                ))

            # kerakli mahsulotlar omborda yetarlimi tekshirish
        if needy_value_before > 0:
            raise HTTPException(
                status_code=400, detail='Yarim tayyor yetarli emas!')
        # ../ kerakli mahsulotlar omborda yetarlimi tekshirish ../
    try:
        material_type_id = db.query(Material).get(
            form_data.material_id).material_type_id
    except:
        material_type_id = 0
    # shu jarayonda ishlatiluvchi tarkiblarni select qilish
    main_component_items = db.query(Component_Item)\
        .join(Component_Item.component)\
        .filter(
            Component.cycle_id == cycle.id,
            Component.disabled == False,
            Component_Item.disabled == False,
    ) .filter(func.IF(
        Component.material_type_id == material_type_id,
        Component_Item.material_id == form_data.material_id,
        Component_Item.main == True,
    )).all()

    if plan.size1 > 0 and plan.size2 > 0:
        sizes = db.query(Trade_items_size).join(Trade_items_size.trade_item).filter(
            Trade_items.id == form_data.trade_item_id,
            Trade_items.trade_id == form_data.trade_id
        ).first()
        if sizes:
            form_data.size1 = sizes.size1
            form_data.size2 = sizes.size2

    # tarkib boyicha ombordan aylirish
    for component in main_component_items:

        surface = form_data.size1 * form_data.size2

        needy_value = component.value * form_data.value * \
            (surface if surface > 0 else 1)

        # agar tarkibida mahsulot bolsa
        if component.product:

            product_stores = db.query(Product_Store).filter(
                Product_Store.product_id == component.product_id,
                Product_Store.value > 0,
                Product_Store.market_id == 0,
                Product_Store.material_id == form_data.material_id,
                Product_Store.size1 == 0,
                Product_Store.size2 == 0,
            )

            # raise HTTPException(
            #     status_code=400, detail=f'{needy_value}Yarim tayyor yetarli emas!{product_stores}')


            for product_store in product_stores.all():
                if needy_value > 0:
                    if product_store.value <= needy_value:
                        minus_val = product_store.value
                        total_cost = total_cost + product_store.price * product_store.value
                        needy_value = needy_value - product_store.value
                        db.query(Product_Store).filter_by(id=product_store.id).update({Product_Store.value: 0})

                    else:
                        minus_val = needy_value
                        total_cost = total_cost + product_store.price * needy_value
                        db.query(Product_Store).filter_by(id=product_store.id).update(
                            {Product_Store.value: Product_Store.value - needy_value})

                        needy_value = 0

                    utilizings.append(ComponentUtilizing(
                        value=minus_val,
                        product_store_id=product_store.id
                    ))
                else:
                    break

             # kerakli mahsulotlar omborda yetarlimi tekshirish
            if needy_value > 0:
                raise HTTPException(
                    status_code=400, detail=component.product.name + f' yetarli emas!')
            # ../ kerakli mahsulotlar omborda yetarlimi tekshirish ../

        if component.material:
            needy_value = component.value * form_data.value

            material_stores = db.query(Material_Store).filter(
                # Material_Store.plant_id == plant.id,
                Material_Store.material_id == component.material_id,
                Material_Store.value > 0
            ).all()

            # raise HTTPException(status_code=400, detail=f"{len(material_stores)} bor")

            for material_store in material_stores:
                if needy_value > 0:
                    if material_store.value < needy_value:
                        total_cost = total_cost + material_store.price * material_store.value
                        minus_val = material_store.value
                        needy_value = needy_value - material_store.value
                        db.query(Material_Store).filter_by(
                            id=material_store.id).update({Material_Store.value: 0})

                    else:
                        minus_val = needy_value
                        total_cost = total_cost + material_store.price * needy_value
                        db.query(Material_Store).filter_by(id=material_store.id).update(
                            {Material_Store.value: Material_Store.value - needy_value})

                        needy_value = 0

                    utilizings.append(ComponentUtilizing(
                        value=minus_val,
                        material_store_id=material_store.id
                    ))
                else:
                    break

            # kerakli mahsulotlar omborda yetarlimi tekshirish
            if needy_value > 0:
                raise HTTPException(
                    status_code=400, detail=f"{component.material.name} dan {needy_value} {component.material.olchov.name} yetarli emas!")
            # ../ kerakli mahsulotlar omborda yetarlimi tekshirish ../

    # cost for one product
    cost = round(total_cost / form_data.value, 2) + cycle.kpi

    new_production = Production(
        material_id=form_data.material_id,
        cycle_id=cycle.id,
        product_id=product_cycle.product_id,
        product_type_id=product_cycle.product.product_type_id,
        plant_id=form_data.plant_id,
        value=form_data.value,
        norm=form_data.norm,
        user_id=usr.id,
        cost=cost,
        size1=form_data.size1,
        size2=form_data.size2,
        finished=finished,
        trade_id=form_data.trade_id,
        trade_item_id=form_data.trade_item_id,
    )

    db.add(new_production)
    db.flush()

    for com_uti in utilizings:
        com_uti.production_id = new_production.id
        db.add(com_uti)

    # agar jarayon yakunlamagan bolsa keyingi jarayon tsehiga borib tushadi
    db.commit()
    if finished == True:

        if form_data.plan_id == 0:
            plans = db.query(Plan).filter(
                Plan.product_id == product_cycle.product_id,
                Plan.rest_value > 0,
                Plan.material_id == form_data.material_id,
                Plan.size1 == form_data.size1,
                Plan.size2 == form_data.size2,
            ).order_by(Plan.to_date.asc()).all()

            minus_value = form_data.value
            for pl in plans:
                if minus_value > 0:
                    if pl.rest_value < minus_value:
                        minus_value -= pl.rest_value
                        db.query(Plan).filter_by(id=pl.id).update({
                            Plan.rest_value: 0,
                            Plan.bron_value: Plan.bron_value + pl.rest_value
                        })

                    else:
                        db.query(Plan).filter_by(id=pl.id).update({
                            Plan.rest_value: Plan.rest_value - minus_value,
                            Plan.bron_value: Plan.bron_value + minus_value
                        })
                        minus_value = 0
                else:
                    continue

        else:
            db.query(Plan).filter_by(id=plan.id).update({
                Plan.rest_value: Plan.rest_value - form_data.value,
                Plan.bron_value: Plan.bron_value + form_data.value
            })

        product_store = db.query(Product_Store).filter_by(
            product_id=product_cycle.product_id,
            price=cost,
            size1=form_data.size1,
            size2=form_data.size2,
            material_id=form_data.material_id,
            trade_id=form_data.trade_id,
            trade_item_id=form_data.trade_item_id,
        )

        product_store_one = product_store.first()

        if product_store_one:
            product_store.update(
                {Product_Store.value: Product_Store.value + form_data.value})
            db.query(Production).filter_by(id=new_production.id).update({
                Production.product_store_id: product_store_one.id
            })
        else:
            new_product_store = Product_Store(
                product_id=product_cycle.product_id,
                price=cost,
                size1=form_data.size1,
                size2=form_data.size2,
                material_id=form_data.material_id,
                trade_id=form_data.trade_id,
                trade_item_id=form_data.trade_item_id,
                value=form_data.value
            )
            db.add(new_product_store)
            db.flush()

            if not new_production.id:
                raise HTTPException(
                    status_code=400, detail=f'yetarli emas!')

            db.query(Production).filter_by(id=new_production.id).update({
                Production.product_store_id: new_product_store.id
            })
    else:
        new_cycle_store = Cycle_Store(
            cycle_id=cycle.id,
            product_id=product_cycle.product.id,
            plant_id=form_data.next_plant_id,
            value=form_data.value,
            ordinate=product_cycle.ordinate,
            olchov_id=product_cycle.product.olchov_id,
            trade_id=form_data.trade_id,
            trade_item_id=form_data.trade_item_id,
            finished=finished,
            price=cost,
            period=form_data.period,
            size1=form_data.size1,
            material_id=form_data.material_id,
            size2=form_data.size2,
        )

        db.add(new_cycle_store)
        db.flush()
        db.query(Production).filter_by(id=new_production.id).update({
            Production.cycle_store_id: new_cycle_store.id
        })

    message = MessageSchema(
        title="Тайёр махсулот",
        body=f"{product_cycle.product.name} дан {form_data.value} {product_cycle.product.olchov.name}",
        imgurl=f"https://api2.f9.crud.uz/images/products/{product_cycle.product.image}"
    )

    # user_kpis = db.query(User_Kpi).join(User_Kpi.user).join(User.last_attandance).filter(
    #     User_Kpi.cycle_id == cycle.id,
    #     User_Kpi.disabled == False,
    #     func.date(Attandance.datetime) == datetime.now().strftime('%Y-%m-%d'),
    #     Attandance.type == 'entry'
    # ).all()

    # if len(user_kpis) > 0:
    #     kpi_individual_cost = round(form_data.value*cycle.kpi / len(user_kpis))

    #     if kpi_individual_cost > 0:
    #         for user_kpi in user_kpis:
    #             db.query(User).filter_by(id=user_kpi.user_id).update({
    #                 User.salary: User.salary + kpi_individual_cost
    #             })

    db.commit()

    await manager.send_user(message, 'analyst', db)
    raise HTTPException(status_code=200, detail="Ma`lumotlar saqlandi!")


def update_production(id, form_data: UpdateProduction, usr, db: Session):

    production = db.query(Production).filter(Production.id == id)
    this_production = production.first()
    if this_production:
        production.update({
            Production.cycle_id: form_data.cycle_id,
            Production.product_id: form_data.product_id,
            Production.product_type_id: form_data.product_type_id,
            Production.plant_id: form_data.plant_id,
            Production.value: form_data.value,
            Production.user_id: form_data.user_id,
            Production.created_at: form_data.created_at,
            Production.cost: form_data.cost,
            Production.finished: form_data.finished,
        })
        db.commit()

        raise HTTPException(status_code=200, detail="O`zgarish saqlandi!")
    else:
        raise HTTPException(status_code=400, detail="So`rovda xatolik!")


def delete_production(id, db: Session):
    production = db.query(Production).filter(Production.id == id)
    this_production = production.first()

    if this_production:
        # utilizings = db.query(ComponentUtilizing).filter_by
        # raise HTTPException(status_code=400, detail=f"Kech qoldingiz! Omborga qo`shilgan mahsulot yetarli emas!{len(this_production.utilizings)}")
        # ishlatilgan homashyolarni joyiga qaytarish
        for utlz in this_production.utilizings:

            db.query(Cycle_Store).filter_by(id=utlz.cycle_store_id).update({
                Cycle_Store.value: Cycle_Store.value+utlz.value
            })
            db.query(Product_Store).filter_by(id=utlz.product_store_id).update({
                Product_Store.value: Product_Store.value+utlz.value
            })
            db.query(Material_Store).filter_by(id=utlz.material_store_id).update({
                Material_Store.value: Material_Store.value+utlz.value
            })

            db.delete(utlz)

        if this_production.product_store:

            if this_production.product_store.value < this_production.value:
                raise HTTPException(
                    status_code=400, detail="Kech qoldingiz! Omborga qo`shilgan mahsulot yetarli emas!")

            db.query(Product_Store).filter_by(id=this_production.product_store_id).update({
                Product_Store.value: Product_Store.value-this_production.value
            })

        if this_production.cycle_store:

            if this_production.cycle_store.value < this_production.value:
                raise HTTPException(
                    status_code=400, detail="Kech qoldingiz! Omborga qo`shilgan mahsulot yetarli emas!")

            db.query(Cycle_Store).filter_by(id=this_production.cycle_store_id).update({
                Cycle_Store.value: Cycle_Store.value-this_production.value
            })

        production.delete()
        db.commit()

        return "deleted"


def production_cycles(search, page, plant_id, limit, usr, db: Session):

    before_cycle_quantity = db.query(func.sum(Cycle_Store.value))\
        .filter(
            Cycle_Store.ordinate >= Product_Cycle.ordinate,
            Cycle_Store.product_id == Product_Cycle.product_id,
            Cycle_Store.plant_id == plant_id
    ).limit(1).subquery()

    plan_mod = aliased(Plan)

    plan_rest_val = db.query(func.sum(plan_mod.rest_value)).filter(
        plan_mod.product_id == Plan.product_id,
        plan_mod.material_id == Plan.material_id,
        plan_mod.size1 == Plan.size1,
        plan_mod.size2 == Plan.size2,
    ).subquery()

    quantity = func.coalesce(plan_rest_val, 0) - \
        func.coalesce(before_cycle_quantity, 0)

    cycles = db.query(
        label("quantity", quantity),
        label("cycle_name", Cycle.name),
        label("cycle_id", Cycle.id),
        label("product_name", Product.name),
        label("product_id", Product.id),
        label("product_image", Product.image),
        label("olchov_name", Olchov.name),
        label("hasSize", Product_Type.hasSize),
        label("izoh", ""),
        label("product_cycle_id", Product_Cycle.id),
        label("ordinate", Product_Cycle.ordinate),
        label("plan_id", 0),
        label("size1", Plan.size1),
        label("size2", Plan.size2),
        label('material', func.coalesce(Material.name, '')),
        label('material_id', func.coalesce(Material.id, 0)),
    )\
        .join(Plan.product)\
        .join(Plan.material)\
        .join(Product.product_cycles)\
        .join(Product_Cycle.cycle)\
        .join(Product.olchov)\
        .join(Product.product_type)\
        .join(Cycle.plant_cycles)\
        .filter(
            Plant_Cycle.plant_id == plant_id,
            Plant_Cycle.disabled == False,
            Product.disabled == False,
            Product_Cycle.disabled == False,
            Cycle.disabled == False,
            Cycle.special == False,
            quantity > 0
    ).group_by(Plan.product_id, Cycle.id, Plan.size1, Plan.size2, Plan.material_id)

    count_data = cycles.count()

    all_data = cycles.all()

    return {
        "data": all_data,
        "page_count": math.ceil(count_data / limit),
        "data_count": count_data,
        "current_page": page,
        "page_limit": limit,
    }

    return cycles.all()

    if search:
        cycles = cycles.filter(
            or_(
                Cycle.name.like(f"%{search}%"),
                Product.name.like(f"%{search}%"),
            )
        )

    # if page == 1 or page < 1:
    #     offset = 0
    # else:
    #     offset = (page-1) * limit

    # all_data = cycles.order_by(
    #     Cycle.id.desc()).offset(offset).limit(limit)
    count_data = cycles.count()

    all_data = cycles.all()

    # raise HTTPException(status_code=400,detail=f"{len(all_data)} ta")

    # cycle1 = aliased(Cycle)
    # before_cycle_id = db.query(Cycle.id)\
    #     .join(cycle1, Cycle_Store.cycle).filter(
    #         cycle1.ordinate < Cycle.ordinate,
    #         cycle1.product_id == Cycle.product_id,
    #         cycle1.special==False,
    # ).order_by(cycle1.ordinate.desc()).limit(1).subquery()

    # cyclestr = aliased(Cycle_Store)
    # cycle_store = db.query(
    #     label("quantity", func.coalesce(func.sum(cyclestr.value), 0)),
    #     label("cycle_name", func.IF(
    #         and_(
    #             cyclestr.size1 > 0,
    #             cyclestr.size2 > 0,
    #         ),
    #         func.concat(Cycle.name, ' (', cyclestr.size1,
    #                     'x', cyclestr.size2, ') '),
    #         Cycle.name
    #     )),
    #     label("cycle_id", Cycle.id),
    #     label("product_name", Product.name),
    #     label("product_id", Product.id),
    #     label("product_image", Product.image),
    #     label("olchov_name", Olchov.name),
    #     label("size1", cyclestr.size1),
    #     label("size2", cyclestr.size2),

    # )\
    #     .join(Cycle.product)\
    #     .join(Product.olchov)\
    #     .join(Cycle.plant_cycles)\
    #     .join(cyclestr, and_(
    #         cyclestr.cycle_id == before_cycle_id,
    #         cyclestr.value > 0
    #     ))\
    #     .filter(
    #         Plant_Cycle.plant_id == plant_id,
    #         Plant_Cycle.disabled == False,
    #         Product.disabled == False,
    #         Cycle.disabled == False,
    #         Cycle.special == False,
    #         Cycle.ordinate > 1,
    # ).group_by(cyclestr.cycle_id, cyclestr.size1, cyclestr.size2).all()

    # for one_data in cycle_store:
    #     all_data.append(one_data)

    secondary_cycles = db.query(Cycle).join(Cycle.plant_cycles).filter(
        Plant_Cycle.plant_id == plant_id, Plant_Cycle.disabled == False,
        Product_Cycle.ordinate > 1, Cycle.disabled == False).all()

    for one_cycle in secondary_cycles:
        before_cycle_one = db.query(Cycle).filter(
            Product_Cycle.ordinate < one_cycle.ordinate,
            Cycle.product_id == one_cycle.product_id,
            Cycle.special == False,
            Cycle.disabled == False,
        ).order_by(Product_Cycle.ordinate.desc()).first()

        if before_cycle_one:
            cycstrs = db.query(Cycle_Store, func.coalesce(func.sum(Cycle_Store.value), 0).label("sum_quantity"))\
                .filter(Cycle_Store.cycle_id == before_cycle_one.id, Cycle_Store.value > 0, Cycle_Store.plant_id == plant_id)\
                .group_by(Cycle_Store.cycle_id, Cycle_Store.size1, Cycle_Store.size2).all()

            for cystr in cycstrs:

                if cystr.Cycle_Store.size1 > 0 and cystr.Cycle_Store.size2 > 0:
                    name_text = f"({cystr.Cycle_Store.size1}{cystr.Cycle_Store.size2})"
                else:
                    name_text = ""

                all_data.append({
                    "quantity": cystr.sum_quantity,
                    "cycle_name": one_cycle.name,
                    "product_name": one_cycle.product.name + name_text,
                    "cycle_id": one_cycle.id,
                    "product_id": one_cycle.product_id,
                    "product_image": one_cycle.product.image,
                    "olchov_name": one_cycle.product.olchov.name,
                    "size1": cystr.Cycle_Store.size1,
                    "size2": cystr.Cycle_Store.size2,
                    "izoh": "",
                })

    return {
        "data": all_data,
        "page_count": math.ceil(count_data / limit),
        "data_count": count_data,
        "current_page": page,
        "page_limit": limit,
    }
