from developers.abdusamad.models import *
from ..models.plant import *
from sqlalchemy.orm import Session
# def calculate_order_percent(plant_id, order_id, db: Session):
#     # total_belonging_data = order_in_plant_checker(order_id, db)
#     # return total_belonging_data
#     percents = []
#     for product in total_belonging_data:
        
#         plant_cycles = db.query(Plant_Cycle)\
#             .filter(
#                 Plant_Cycle.cycle.has(Cycle.product_id==product['product_id']),
#                 Plant_Cycle.disabled == False, Plant_Cycle.plant_id==plant_id
#             ).all()

#         for pl_cyc in plant_cycles:
#             if product['requiring_value'] == 0:
#                 percents.append(-1)
#             else:
#                 percent = (product['requiring_value']-product['rest_value'])/product['requiring_value']*100
#                 percents.append(percent)

#     # return percents
#     if len(percents) > 0:
#         return min(percents) 
#     else:
#         return -1

def get_orders_status_table2(plant_ids: str, usr, db: Session):
    
    ids = plant_ids.split(";")
    plant_id_all = []
    for x in ids:
        try:
            plant_id_all.append(int(x))
        except Exception as e:
            pass

    orders = db.query(Orders).join(Orders.trades)\
        .join(Trades.trade_items)\
        .filter(Orders.status == 'pre_order', Trade_items.id > 0).order_by(
        Orders.delivery_date.asc()).all()

    res = []

    for ord in orders:
        orders_by_plants = []
        for plant_id in plant_id_all:
            plant = db.query(Plant).get(plant_id)
            if plant:
                orders_by_plants.append({
                    'order_id': ord.id,
                    'delivery_date': ord.delivery_date,
                    'plant': plant.name,
                    'percentage': 100,
                })
        res.append({"row": orders_by_plants})

    return res


#     # loop = asyncio.get_running_loop()
#     # with ThreadPoolExecutor() as executor:
#     #     # Submit multiple tasks to the thread pool
#     #     tasks = [loop.run_in_executor(executor, calculate_order_percent, plant_id, ord.id, db) for ord in orders for plant_id in plant_id_all]
#     #     # Wait for all tasks to complete and get the results using asyncio.gather()
#     #     results = await asyncio.gather(*tasks)

#     #     res = results

#         # Reshape the results into a list of dicts
#     results = [results[i:i+len(plant_id_all)] for i in range(0, len(results), len(plant_id_all))]
#     for i, ord in enumerate(orders):
#         orders_by_plants = []
#         