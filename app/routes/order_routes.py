from fastapi import APIRouter,Depends,HTTPException
from fastapi_jwt_auth import AuthJWT
from app.db.models import User,Order
from app.schemas.schema import OrderModel,OrderStatusModel
from fastapi_jwt_auth import AuthJWT
from app.dependencies.dependency import get_db
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

order_router=APIRouter()

@order_router.get("/")
def hello(Authroize :AuthJWT=Depends()):
    """
        ## Sample hello world route
    
    """
    try:
        Authroize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=404,detail="token invalid or expired")
    return {"message: hello"}

@order_router.post("/order")
async def order(order:OrderModel,Authroize :AuthJWT=Depends(),db:Session=Depends(get_db)):
    
    
    """
        ## Placing an Order
        This requires the following
        - quantity : integer
        - pizza_size: str
    
    """

    try:
        Authroize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=404,detail="token invalid or expired")
    current_user=Authroize.get_jwt_subject()
    user=db.query(User).filter(User.username==current_user).first()
    
    new_order=Order(
        pizza_size=order.pizza_size,
        quantity=order.quantity
    )
    
    new_order.user=user#SQLAlchemy internally sets new_order.user_id = user.id.
    db.add(new_order)
    db.commit()
    
    res={
        "pizza-size":new_order.pizza_size,
        "quantity":new_order.quantity,
        "order_id":str(new_order.id)
    }
    return JSONResponse(status_code=200,content=res)

@order_router.post("/orders")
async def orders(Authroize :AuthJWT=Depends(),db:Session=Depends(get_db)):
    """
        ## List all orders
        This lists all  orders made. It can be accessed by superusers
        
    
    """

    try:
        Authroize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=404,detail="token invalid or expired")
    current_user=Authroize.get_jwt_subject()
    user=db.query(User).filter(User.username==current_user).first()
    if getattr(user, "is_staff",False):
        orders = db.query(Order).all()
        orders_data = [
            {
                "id": str(o.id),
                "pizza_size": o.pizza_size,
                "quantity": o.quantity,
                "user_id": o.user_id
            }
            for o in orders
        ]
        return JSONResponse(status_code=200, content=orders_data)
    raise HTTPException(status_code=404,detail="you are not a superuser")
    

@order_router.post("/order/{order_id}")
async def order_using_id(order_id:str,Authorize :AuthJWT=Depends(),db:Session=Depends(get_db)):
    """
        ## Get an order by its ID
        This gets an order by its ID and is only accessed by a superuser
        

    """
    try:
        Authorize.jwt_required()
    except Exception as e :
        raise HTTPException(status_code=404,detail="invalid token or expired")
    user=Authorize.get_jwt_subject()
    current_user=db.query(User).filter(User.username==user).first()
    
    if getattr(current_user,"is_staff",False):
        orders=db.query(Order).filter(Order.id==order_id)
        order_data = [{
            "id": order.id,
            "pizza_size": order.pizza_size,
            "user_id": order.user_id} for order in orders
        ]
        return jsonable_encoder(order_data)
    raise HTTPException(status_code=404,detail="Id invalid")


@order_router.post("/user/orders/")
async def user_orders(Authorize :AuthJWT=Depends(),db:Session=Depends(get_db)):
    """
        ## Get a current user's orders
        This lists the orders made by the currently logged in users
    
    """
    try:
        Authorize.jwt_required()
    except Exception as e :
        raise HTTPException(status_code=404,detail="invalid token or expired")
    user=Authorize.get_jwt_subject()
    current_user=db.query(User).filter(User.username==user).first()
    
    return jsonable_encoder(current_user.orders)

@order_router.get("/user/order/{order_id}")
async def user_order_using_id(order_id:str,Authorize:AuthJWT=Depends(),db:Session=Depends(get_db)):
    """
        ## Get a specific order by the currently logged in user
        This returns an order by ID for the currently logged in user
    
    """
    
    try:
        Authorize.jwt_required()
    except Exception as e :
        raise HTTPException(status_code=404,detail="invalid token or expired")
    subject=Authorize.get_jwt_subject()
    current_user=db.query(User).filter(User.username==subject).first()
    orders=current_user.orders
    print("order_id:",order_id,current_user.orders)
    if not orders:
        raise HTTPException(status_code=404,detail="no orders with this id")
    for o in orders:
        print("o:",o.id,order_id)
        if str(o.id)==(order_id):
            print("Matched:",o)
            return jsonable_encoder(o)
    raise HTTPException(status_code=404,detail="Invalid id")
    
@order_router.get("/order/update/{order_id}")
async def updaate_order_using_id(order_id:str,order:OrderModel,Authorize:AuthJWT=Depends(),db:Session=Depends(get_db)):
    """
        ## Updating an order
        This udates an order and requires the following fields
        - quantity : integer
        - pizza_size: str
    
    """
    try:
        Authorize.jwt_required()
    except Exception as e :
        raise HTTPException(status_code=404,detail="invalid token or expired")
    
    
    order_to_update=db.query(Order).filter(Order.id==order_id).first()
    
    order_to_update.pizza_size=order.pizza_size
    order_to_update.quantity=order.quantity
    
    db.commit()
    order_to_update=db.query(Order).filter(Order.id==order_id).first()
    return jsonable_encoder(order_to_update)
    
    
    
@order_router.patch("/update/order_status/{order_id}")
async def update_order_status(order_id:str,order_status:OrderStatusModel,Authorize:AuthJWT=Depends(),db:Session=Depends(get_db)):
    """
        ## Update an order's status
        This is for updating an order's status and requires ` order_status ` in str format
    """
    try:
        Authorize.jwt_required()
    except Exception as e :
        raise HTTPException(status_code=404,detail="invalid token or expired")
    user=Authorize.get_jwt_subject()
    current_user=db.query(User).filter(User.username==user).first()
    
    if current_user.is_staff:
        order_to_updatestatus=db.query(Order).filter(Order.id == order_id).update({
        "order_status": order_status.order_status
        })
    else:
        raise HTTPException(status_code=404,detail="You are not a superuser")
        
    
    if not order_to_updatestatus:
        raise HTTPException(status_code=404, detail="Order not found")

    db.commit()
    updated=db.query(Order).filter(Order.id == order_id).first()
    res={"message": "Order status updated successfully","updated":jsonable_encoder(order_to_updatestatus),"updated_status":updated.order_status}
    
    return JSONResponse(status_code=200,content=res)


   
    
    
@order_router.post("/delete/order/{order_id}")
async def update_order_status(order_id:str,Authorize:AuthJWT=Depends(),db:Session=Depends(get_db)):
    """
        ## Delete an Order
        This deletes an order by its ID
    """
    try:
        Authorize.jwt_required()
    except Exception as e :
        raise HTTPException(status_code=404,detail="invalid token or expired")
    #user=Authorize.get_jwt_subject()
    order_to_delete=db.query(Order).filter(Order.id==order_id).first()
    if order_to_delete:
        db.delete(order_to_delete)
        db.commit()
        return order_to_delete
    raise HTTPException(status_code=404,detail="order not exist")
    
    
    
    
    
    
    
    
    