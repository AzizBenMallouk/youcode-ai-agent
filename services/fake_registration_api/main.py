from fastapi import FastAPI, Query, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional, Literal
from datetime import date, datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fake-registration-api")

app = FastAPI(title="Fake Registration API")

class RegistrationStatusData(BaseModel):
    program: str
    campus: Optional[str] = None
    status: Literal["open", "upcoming", "closed", "unknown"]
    opening_date: Optional[date] = None
    closing_date: Optional[date] = None
    registration_url: Optional[str] = None
    available_places: Optional[int] = None
    message: Optional[str] = None
    updated_at: Optional[datetime] = None

def verify_api_key(x_api_key: Optional[str] = Header(None)):
    # Simple validation if needed, or we can just accept anything for the fake API
    if x_api_key == "invalid_key":
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key

@app.get("/registration/status", response_model=RegistrationStatusData)
async def get_registration_status(
    program: str = Query(..., description="Program to check registration for"),
    campus: Optional[str] = Query(None, description="Campus filter"),
    api_key: str = Depends(verify_api_key)
):
    logger.info(f"Received request for program={program}, campus={campus}")
    
    # Mocked static logic
    if program == "full_program":
        if campus == "safi":
            return RegistrationStatusData(
                program=program,
                campus=campus,
                status="closed",
                closing_date=date(2025, 10, 1),
                message="Les inscriptions pour Safi sont actuellement fermées.",
                updated_at=datetime.utcnow()
            )
        elif campus == "youssoufia":
            return RegistrationStatusData(
                program=program,
                campus=campus,
                status="upcoming",
                opening_date=date(2026, 9, 1),
                message="Les inscriptions pour Youssoufia ouvrent bientôt.",
                updated_at=datetime.utcnow()
            )
        else:
            return RegistrationStatusData(
                program=program,
                campus=campus,
                status="open",
                opening_date=date(2026, 8, 1),
                closing_date=date(2026, 12, 1),
                registration_url="https://candidature.youcode.ma",
                available_places=50,
                message="Les inscriptions sont ouvertes pour ce programme.",
                updated_at=datetime.utcnow()
            )
            
    elif program == "bootcamps":
        return RegistrationStatusData(
            program=program,
            campus=campus,
            status="open",
            registration_url="https://bootcamp.youcode.ma",
            message="Bootcamps disponibles.",
            updated_at=datetime.utcnow()
        )
    
    # Default fallback
    return RegistrationStatusData(
        program=program,
        campus=campus,
        status="unknown",
        message="Aucune information trouvée pour ce programme.",
        updated_at=datetime.utcnow()
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9001)
