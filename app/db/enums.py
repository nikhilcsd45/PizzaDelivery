from sqlalchemy import Enum
import enum

class PizzaSize(str, enum.Enum):
    small = "small"
    medium = "medium"        
    large = "large"
    extra_large = "extra_large"  

class OrderStatus(str, enum.Enum):
    pending = "pending"
    in_transit = "in_transit"    
    delivered = "delivered"     
