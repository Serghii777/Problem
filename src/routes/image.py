from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from typing import List
import services.cv_service # replace with the actual module where your ML model is defined

router = APIRouter()

@router.post("/upload_license_plate/")
async def upload_license_plate(
    file: UploadFile = File(...), db: AsyncSession = Depends(get_db)
):
    try:
        # Read the image
        image_data = await file.read()

        # Pass the image to your ML model to get the license plate text
        license_plate_text = await your_ml_module.read_license_plate(image_data)

        # Optionally, store the result in the database if needed

        return JSONResponse({"license_plate": license_plate_text})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
