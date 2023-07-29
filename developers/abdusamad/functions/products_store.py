from ...yusufjon.models.product_store import Product_Store
from ...yusufjon.models.product import Product
from ...yusufjon.models.cycle_store import Cycle_Store
from ...yusufjon.models.product_type import Product_Type
from ...yusufjon.utils.trlatin import tarjima
import math
from sqlalchemy.orm import joinedload, Session, aliased
from sqlalchemy import func, and_, or_
from sqlalchemy.sql import label



def all_products_store(search, trade, pr_type_id, market_id, size1, size2, page, limit, db: Session):
    
    if search:
        search_formatted = "%{}%".format(search)
        search_filter = or_(
            Product.name.like(f"%{tarjima(search_formatted, 'ru')}%"),
            Product.name.like(f"%{tarjima(search_formatted, 'uz')}%"),
        )
    else:
        search_filter = Product_Store.id > 0
    
    if pr_type_id:
        pr_type_filter = Product.product_type_id == pr_type_id
    else:
        pr_type_filter = Product_Store.id > 0
        
    if market_id:
        market_filter = Product_Store.market_id == market_id
    else:
        market_filter = Product_Store.id > 0
    
    if size1 and size2:
        size_filter = and_(Product_Store.size1 == size1, Product_Store.size2 == size2)
    else:
        size_filter = Product_Store.id > 0
    products_sum_price = 0

    if trade:

        products = db.query(Product_Store, func.sum(Product_Store.value).label("sum_quantity"))\
            .join(Product)\
            .options(joinedload(Product_Store.product).options(
                joinedload(Product.olchov),
                joinedload(Product.product_type),
            ), joinedload(Product_Store.material))\
            .group_by(Product_Store.product_id, Product_Store.size1, Product_Store.size2, Product_Store.material_id)\
            .filter(search_filter, pr_type_filter, market_filter, size_filter).filter(Product_Store.trade_id == 0, Product_Store.plant_id == 0)

        products_sum_price = db.query(func.sum(Product_Store.trade_price*Product_Store.value)).filter(search_filter, pr_type_filter, market_filter, size_filter).filter(Product_Store.trade_id == 0, Product_Store.plant_id == 0).scalar()

    else:

        pr_store1 = aliased(Product_Store)
        pr_store2 = aliased(Product_Store)

        products = db.query(
            Product_Store,
            label(
                "sum_quantity",
                db.query(func.coalesce(func.sum(pr_store1.value), 0)).filter_by(
                    product_id=Product_Store.product_id,
                    trade_id=0, plant_id=0,
                    size1=Product_Store.size1,
                    size2=Product_Store.size2,
                    material_id=Product_Store.material_id,
                    market_id=0,
                ).subquery()),
            label(
                "sum_quantity_bron",
                db.query(func.coalesce(func.sum(pr_store2.value), 0)).filter(
                    pr_store2.product_id == Product_Store.product_id,
                    pr_store2.trade_id > 0,
                    pr_store2.plant_id == 0,
                    pr_store2.size1 == Product_Store.size1,
                    pr_store2.size2 == Product_Store.size2,
                    pr_store2.material_id==Product_Store.material_id,
                    pr_store2.market_id==0,
                ).subquery()),
            label("product_name", func.IF(
                and_(
                    Product_Store.size1 > 0,
                    Product_Store.size2 > 0,
                ),
                func.concat(Product.name, ' (', Product_Store.size1,
                            'x', Product_Store.size2, ') '),
                Product.name
            )),
            label("isReady", Product_Type.isReady),
        )\
            .join(Product_Store.product)\
            .join(Product_Type, Product_Type.id==Product.product_type_id)\
            .options(joinedload(Product_Store.product).subqueryload(Product.olchov), joinedload(Product_Store.material))\
            .filter(search_filter, pr_type_filter, market_filter, size_filter)\
            .filter(Product_Store.market_id==0)\
            .group_by(Product_Store.product_id, Product_Store.size1, Product_Store.size2, Product_Store.material_id)

    return {"current_page": page, "limit": limit, "pages": math.ceil(products.count() / limit), "data": products.offset((page - 1) * limit).limit(limit).all(), "products_sum_price": products_sum_price}


def one_product_store(id, db):
    return db.query(Product_Store, func.sum(Product_Store.value).label("sum_quantity")).options(joinedload(Product_Store.product)).group_by(Product_Store.product_id).filter(Product_Store.id == id, Product_Store.trade_id == 0, Product_Store.plant_id == 0).first()

