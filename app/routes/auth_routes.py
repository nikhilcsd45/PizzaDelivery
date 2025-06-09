from fastapi import APIRouter,Depends,HTTPException
from app.schemas.schema import SignUpModel,LoginModel
from app.dependencies.dependency import get_db
from sqlalchemy.orm import Session
from app.db import models
from werkzeug.security import generate_password_hash, check_password_hash
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
auth_router=APIRouter()

@auth_router.get("/")
async def hello(Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=404,detail="token expired or invalid ")
    return {"message: hello"}






@auth_router.post("/signup")
async def signup(user:SignUpModel,db:Session=Depends(get_db)):
    """
        ## Create a user
        This requires the following
        ```
                username:int
                email:str
                password:str
                is_staff:bool
                is_active:bool
        ```
    """
    db_email=db.query(models.User).filter(models.User.email==user.email).first()
    if db_email is not None:
        raise HTTPException(status_code=404,detail="user already exist")
    
    new_user=models.User(
        username=user.username,
        email=user.email,
        password=generate_password_hash(user.password),
        is_active=user.is_active,
        is_staff=user.is_staff
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    res={
        "username":new_user.username,
        "email":new_user.email,
        "is_active":new_user.is_active,
        "is_staff":new_user.is_staff
    }
    return JSONResponse(status_code=200,content=res)
    
    
    
    
    
@auth_router.post("/login")
async def login(user:LoginModel,db:Session=Depends(get_db),Authorize:AuthJWT=Depends()):
    """     
        ## Login a user
        This requires
            ```
                username:str
                password:str
            ```
        and returns a token pair `access` and `refresh`
    """
    db_user=db.query(models.User).filter(models.User.username==user.username).first()
    
    if db_user and check_password_hash(str(db_user.password),user.password):
        access_token=Authorize.create_access_token(subject=user.username)
        refresh_token=Authorize.create_refresh_token(subject=user.username)
        
        res={
            "access_token":access_token,
            "refresh_token":refresh_token
        }
        
        return JSONResponse(status_code=200,content=res)
    raise HTTPException(status_code=401, detail="Invalid username or password")








@auth_router.get("/refresh")
async def refresh(Authorize:AuthJWT=Depends()):
    """
    ## Create a fresh token
    This creates a fresh token. It requires an refresh token.
    """
    try:
        Authorize.jwt_refresh_token_required()
    except Exception as e:
        raise HTTPException(status_code=404,detail="please provide a valid refresh token ")
    current_token=Authorize._get_jwt_identifier()
    access_token=Authorize.create_access_token(subject=current_token)
    res={
        "access_token":access_token
    }
    return JSONResponse(status_code=200,content=res)


