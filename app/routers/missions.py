from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db import get_session
from app.dependencies import get_current_admin, get_current_user
from app.models import Hero, Mission, MissionCreate, MissionRead, MissionUpdate, User

router = APIRouter(prefix="/missions", tags=["missions"])


@router.post("", response_model=MissionRead, status_code=status.HTTP_201_CREATED)
def create_mission(
    mission_in: MissionCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    hero = session.get(Hero, mission_in.hero_id)
    if not hero:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hero not found")

    mission = Mission.model_validate(mission_in)
    session.add(mission)
    session.commit()
    session.refresh(mission)
    return mission


@router.get("", response_model=list[MissionRead])
def list_missions(session: Session = Depends(get_session)):
    return session.exec(select(Mission)).all()


@router.get("/{mission_id}", response_model=MissionRead)
def get_mission(mission_id: int, session: Session = Depends(get_session)):
    mission = session.get(Mission, mission_id)
    if not mission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mission not found")
    return mission


@router.patch("/{mission_id}", response_model=MissionRead)
def update_mission(
    mission_id: int,
    patch: MissionUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    mission = session.get(Mission, mission_id)
    if not mission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mission not found")

    update_data = patch.model_dump(exclude_unset=True)

    if "hero_id" in update_data:
        hero = session.get(Hero, update_data["hero_id"])
        if not hero:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hero not found")

    for key, value in update_data.items():
        setattr(mission, key, value)

    session.add(mission)
    session.commit()
    session.refresh(mission)
    return mission


@router.delete("/{mission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mission(
    mission_id: int,
    session: Session = Depends(get_session),
    current_admin: User = Depends(get_current_admin),
):
    mission = session.get(Mission, mission_id)
    if not mission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mission not found")

    session.delete(mission)
    session.commit()
    return None
