from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import api_models, db_models
from database.timescale_db import get_db
from auth.security import get_password_hash, verify_password, create_access_token

router = APIRouter()


@router.post(
    "/register",
    response_model=api_models.UserPublic,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    user: api_models.UserCreate, db: AsyncSession = Depends(get_db)
):
    # Check if email already exists
    result = await db.execute(
        select(db_models.User).filter(db_models.User.email == user.email)
    )
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email '{user.email}' already exists. Please use a different email or try logging in.",
        )

    # Check if name already exists (optional, if you want unique names)
    name_result = await db.execute(
        select(db_models.User).filter(db_models.User.name == user.name)
    )
    existing_name = name_result.scalars().first()
    if existing_name:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username '{user.name}' is already taken. Please choose a different username.",
        )

    try:
        hashed_password = get_password_hash(user.password)
        db_user = db_models.User(
            email=user.email, name=user.name, hashed_password=hashed_password
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user account. Please try again later.",
        )


@router.post("/login", response_model=api_models.Token)
async def login_for_access_token(
    form_data: api_models.UserCreate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(db_models.User).filter(db_models.User.email == form_data.email)
    )
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No account found with email '{form_data.email}'. Please check your email or register a new account.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password. Please check your password and try again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
