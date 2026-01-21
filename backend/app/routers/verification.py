from fastapi import APIRouter, HTTPException
from ..database import get_supabase_client

router = APIRouter(prefix="/verification", tags=["verification"])

@router.get("/rankings")
async def get_rankings():
    supabase = get_supabase_client()
    try:
        response = supabase.table("model_rankings").select("*").order("elo_score", desc=True).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
