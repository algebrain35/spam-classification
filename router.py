from fastapi import APIRouter, HTTPException
from model import SpamDetectionModel
from pydantic import BaseModel
from typing import List, Optional
import redis
import uuid
import time
import json

router = APIRouter()
model = SpamDetectionModel(from_file=True, filepath="spam.pkl")

redis_client = redis.Redis(host='127.0.0.1', port=6379, db=0, decode_responses=True)

class EmailRequest(BaseModel):
    subject:str
    body: str
    sender: str
    timestamp: Optional[str] = None
    batch_id : Optional[str] = None

    def __str__(self):
        return f"Sender: {self.sender}\nSubject: {self.subject}\n{self.body}"

class EmailClassificationResponse(BaseModel):
    email_id: str
    score: float
    tier: str

@router.get("/classify/{email_id}")
async def classify(email_id: str):
    result_key = f"result:{email_id}"
    response = redis_client.get(result_key)

    if response:
        email_response = json.loads(response)
        return {
            "email_id": email_id,
            "status" : "completed",
            "tier": email_response['tier'],
            "score": email_response['score'],
            "message": "Classifcation successful"
        }

    if redis_client.exists(email_id):
        return {
            "email_id": email_id,
            "status" : "pending",
            "message": "Email is queued for processing"
        }

    raise HTTPException(status_code=404, detail="Error occurred: Email ID not found")


@router.post("/batch")
async def batch_process(batch: List[EmailRequest]):
    batch_id = str(uuid.uuid4())
    email_ids = []
    pipe = redis_client.pipeline()
    try:
        for email_req in batch:
            email_id = str(uuid.uuid4())
            email_ids.append(email_id)

            email_req.batch_id = batch_id

            pipe.set(email_id, email_req.model_dump_json(), ex=3600)
            pipe.lpush("classify_queue", email_id)
        pipe.execute()
    finally:
        pipe.reset()
    return {"batch_id" : batch_id, "email_ids" : email_ids}



@router.get("/health")
async def health():
    pass

@router.get("/reload")
async def reload():
    pass


