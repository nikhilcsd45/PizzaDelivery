from pydantic import BaseModel,EmailStr
from typing import Optional

class SignUpModel(BaseModel):
    #id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) 
    username:str
    email:EmailStr
    password :str
    is_staff:Optional[bool]
    is_active:Optional[bool]
    class Config:
        orm_mode=True      #Allows reading from ORM objects (like SQLAlchemy models)
        schema_extra={
            "example":{
                "username":"nikhil"
            }
        }
        
        
class Settings(BaseModel):
    authjwt_secret_key:str="1eb5526d6c7577464365fc6ccbeea5b5836ec652049c361faa0a8fea585889d4"
    #impot secrets
    #secrets.token_hex
    
class LoginModel(BaseModel):
    username:str
    password:str



class OrderModel(BaseModel):
    quantity : int
    order_status:Optional[str]="pending"
    pizza_size:Optional[str]="medium"
    user_id :Optional[int]

    class Config:
        orm_mode=True
        
        
        
class OrderStatusModel(BaseModel):
    order_status:Optional[str]="pending"
    
    class Config:
            orm_mode=True
    