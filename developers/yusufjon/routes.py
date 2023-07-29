from fastapi import APIRouter
from . utils.generate import generate_router
from . routers.user import user_router
from . routers.phone import phone_router
from . routers.component import component_router
from . routers.component_item import component_item_router
from . routers.cycle import cycle_router
from . routers.material import material_router
from . routers.material_type import material_type_router
from . routers.plant import plant_router
from . routers.plant_cycle import plant_cycle_router
from . routers.plant_user import plant_user_router
from . routers.product import product_router
from . routers.product_type import product_type_router
from . routers.shift import shift_router
from . routers.user_kpi import user_kpi_router
from . routers.olchov import olchov_router
from . routers.supplier import supplier_router
from . routers.supply import supply_router
from . routers.olchov_proportion import olchov_proportion_router
from . routers.material_store import material_store_router
from . routers.material_transfer import material_transfer_router
from . routers.production import production_router
from . routers.attandance import attandance_router
from . routers.warehouse import warehouse_router
from . routers.building import building_router
from . routers.notification import notification_router
from . routers.spare_part import spare_part_router
from . routers.plan import plan_router
from . routers.norm import norm_router
from . routers.work import work_router
from . routers.indicator import indicator_router
from . routers.product_transfer import product_transfer_router
from . routers.utilization import utilization_router
from . routers.product_cycle import product_cycle_router
from . routers.expense import expense_router
from . routers.product_material import product_material_router
from . routers.salary import salary_router

yusufjon_routers = APIRouter()

yusufjon_routers.include_router(notification_router, prefix="/ws")
yusufjon_routers.include_router(salary_router)
yusufjon_routers.include_router(product_cycle_router)
yusufjon_routers.include_router(building_router)
yusufjon_routers.include_router(attandance_router)
yusufjon_routers.include_router(production_router)
yusufjon_routers.include_router(warehouse_router)
yusufjon_routers.include_router(production_router)
yusufjon_routers.include_router(generate_router)
yusufjon_routers.include_router(material_transfer_router)
yusufjon_routers.include_router(material_store_router)
yusufjon_routers.include_router(supply_router)
yusufjon_routers.include_router(supplier_router)
yusufjon_routers.include_router(user_router)
yusufjon_routers.include_router(component_router)
yusufjon_routers.include_router(component_item_router)
yusufjon_routers.include_router(cycle_router)
yusufjon_routers.include_router(material_router)
yusufjon_routers.include_router(material_type_router)
yusufjon_routers.include_router(plan_router)
yusufjon_routers.include_router(plant_router)
yusufjon_routers.include_router(plant_cycle_router)
yusufjon_routers.include_router(plant_user_router)
yusufjon_routers.include_router(product_router)
yusufjon_routers.include_router(product_type_router)
yusufjon_routers.include_router(shift_router)
yusufjon_routers.include_router(user_kpi_router)
yusufjon_routers.include_router(olchov_router)
yusufjon_routers.include_router(olchov_proportion_router)
yusufjon_routers.include_router(phone_router)
yusufjon_routers.include_router(spare_part_router)
yusufjon_routers.include_router(norm_router)
yusufjon_routers.include_router(work_router)
yusufjon_routers.include_router(indicator_router)
yusufjon_routers.include_router(product_transfer_router)
yusufjon_routers.include_router(utilization_router)
yusufjon_routers.include_router(expense_router)
yusufjon_routers.include_router(product_material_router)
