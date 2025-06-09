from app.db.database import Base
from sqlalchemy import Column,Text,Boolean,Integer,String,Enum,ForeignKey
from app.db.enums import PizzaSize,OrderStatus
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) 
    username = Column(String(25), unique=True)
    email = Column(String(80), unique=True)
    password = Column(Text, nullable=True)
    is_staff = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    orders = relationship("Order", back_populates="user")
    
    
    def __repr__(self):
        return f"<User {self.username}"



class Order(Base):
    __tablename__ = "orders" 

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) 
    quantity = Column(Integer, nullable=False)
    order_status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.pending)
    pizza_size = Column(Enum(PizzaSize), nullable=False, default=PizzaSize.medium)
    flavour = Column(String(50), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))  # Match users.id
    user = relationship("User", back_populates="orders")
    

    def __repr__(self):#Defines how the Order object is printed — helpful for debugging.
        return f"<Order {self.id}>"

    #order.user         ✅  # See who placed the order
    #user.orders        ✅  # See all orders placed by this user

       