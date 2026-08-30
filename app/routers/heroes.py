from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db import get_session
from app.dependencies import get_current_admin, get_current_user
from app.models import Hero, HeroCreate, HeroRead, HeroUpdate, Mission, User

router = APIRouter(prefix="/heroes", tags=["heroes"])


@router.post("", response_model=HeroRead, status_code=status.HTTP_201_CREATED)
def create_hero(
    hero_in: HeroCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    hero = Hero.model_validate(hero_in)
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero


@router.get("", response_model=list[HeroRead])
def list_heroes(session: Session = Depends(get_session)):
    return session.exec(select(Hero)).all()


@router.get("/{hero_id}", response_model=HeroRead)
def get_hero(hero_id: int, session: Session = Depends(get_session)):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hero not found")
    return hero


@router.patch("/{hero_id}", response_model=HeroRead)
def update_hero(
    hero_id: int,
    patch: HeroUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hero not found")

    update_data = patch.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(hero, key, value)

    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero


@router.delete("/{hero_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_hero(
    hero_id: int,
    session: Session = Depends(get_session),
    current_admin: User = Depends(get_current_admin),
):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hero not found")

    active_missions = session.exec(
        select(Mission).where(Mission.hero_id == hero_id, Mission.completed == False)  # noqa: E712
    ).all()
    if active_missions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a hero with active missions",
        )

    session.delete(hero)
    session.commit()
    return None
