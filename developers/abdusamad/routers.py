from fastapi import APIRouter
from .routes.customers import customers_router
from .routes.expenses import expenses_router
from .routes.fixed_expenses import fixed_expenses_router
from .routes.incomes import incomes_router
from .routes.kassa import kassa_router
from .routes.loans import loans_router
from .routes.markets import markets_router
from .routes.orders import orders_router
from .routes.order_files import order_files_router
from .routes.products_store import product_store_router
from .routes.statistics import statistics_router
from .routes.trades import trades_router
from .routes.galery import galery_router
from .routes.products_control import products_control_router


abdusamad_routes = APIRouter()


abdusamad_routes.include_router(customers_router)
abdusamad_routes.include_router(expenses_router)
abdusamad_routes.include_router(fixed_expenses_router)
abdusamad_routes.include_router(incomes_router)
abdusamad_routes.include_router(kassa_router)
abdusamad_routes.include_router(loans_router)
abdusamad_routes.include_router(markets_router)
abdusamad_routes.include_router(orders_router)
abdusamad_routes.include_router(order_files_router)
abdusamad_routes.include_router(product_store_router)
abdusamad_routes.include_router(statistics_router)
abdusamad_routes.include_router(trades_router)
abdusamad_routes.include_router(galery_router)
abdusamad_routes.include_router(products_control_router)