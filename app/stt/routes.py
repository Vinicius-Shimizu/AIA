from fastapi import APIRouter
from pydantic import BaseModel

class STTResponse(BaseModel):
    status: str
    message: str

router = APIRouter(prefix="/stt")

@router.post("")
def getSTTTranscription(payload: STTResponse):
    print(payload.status)
    print(payload.message)