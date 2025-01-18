from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordBearer
from core.auth import create_access_token, create_refresh_token
from jose import jwt, JWTError


router = APIRouter(prefix="/token")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/refresh")
def refresh_token(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        # Создать новые токены
        access_token = create_access_token({"sub": user_id}, expires_delta=timedelta(minutes=120))
        new_refresh_token = create_refresh_token({"sub": user_id})
        return {"access_token": access_token, "refresh_token": new_refresh_token}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
