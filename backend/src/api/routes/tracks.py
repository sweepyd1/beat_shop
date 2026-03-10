from fastapi import APIRouter, Depends, HTTPException
from schemas.track import TrackResponse, TrackCreate, TrackUpdate
from core.services.track import TrackService
from api.dependencies import get_track_service

router = APIRouter(prefix="/tracks", tags=["tracks"])

@router.get("/", response_model=list[TrackResponse])
async def get_tracks(
    skip: int = 0,
    limit: int = 100,
    service: TrackService = Depends(get_track_service)
):
    tracks = await service.repo.get_all(skip=skip, limit=limit)
    return tracks

@router.get("/{track_id}", response_model=TrackResponse)
async def get_track(
    track_id: int,
    service: TrackService = Depends(get_track_service)
):
    track = await service.get_track(track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    return track

@router.post("/", response_model=TrackResponse, status_code=201)
async def create_track(
    track_data: TrackCreate,
    service: TrackService = Depends(get_track_service)
):
    # Здесь можно добавить проверку прав администратора
    return await service.create_track(track_data)

@router.put("/{track_id}", response_model=TrackResponse)
async def update_track(
    track_id: int,
    track_data: TrackUpdate,
    service: TrackService = Depends(get_track_service)
):
    track = await service.update_track(track_id, track_data)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    return track

@router.delete("/{track_id}", status_code=204)
async def delete_track(
    track_id: int,
    service: TrackService = Depends(get_track_service)
):
    deleted = await service.delete_track(track_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Track not found")