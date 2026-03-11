from fastapi import APIRouter, Depends, HTTPException, Query
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
@router.get("/popular", response_model=list[TrackResponse])
async def popular_tracks(
    limit: int = Query(10, ge=1, le=50),
    service: TrackService = Depends(get_track_service)
):
    """Возвращает популярные треки (по убыванию plays)."""
    tracks = await service.get_popular_tracks(limit)
    return tracks

@router.get("/new", response_model=list[TrackResponse])
async def new_tracks(
    limit: int = Query(10, ge=1, le=50),
    service: TrackService = Depends(get_track_service)
):
    """Возвращает новые треки (по убыванию added_date)."""
    tracks = await service.get_new_tracks(limit)
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
    
