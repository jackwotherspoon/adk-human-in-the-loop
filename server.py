from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid

app = FastAPI(title="Request Handler API")

class RequestData(BaseModel):
    amount: float
    reason: str

class ResponseData(BaseModel):
    id: str
    status: str
    amount: float
    reason: str
    message: str

class StatusUpdate(BaseModel):
    status: str

# In-memory storage for requests
requests: dict[str, ResponseData] = {}

@app.post("/request", response_model=ResponseData)
async def handle_request(data: RequestData):
    try:
        request_id = str(uuid.uuid4())
        response = ResponseData(
            id=request_id,
            status="pending",
            amount=data.amount,
            reason=data.reason,
            message="Request created successfully"
        )
        requests[request_id] = response
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/requests", response_model=list[ResponseData])
async def get_requests():
    return list(requests.values())

@app.get("/request/{request_id}", response_model=ResponseData)
async def get_request_by_id(request_id: str):
    if request_id not in requests:
        raise HTTPException(status_code=404, detail="Request not found")
    return requests[request_id]

@app.put("/request/{request_id}", response_model=ResponseData)
async def update_request(request_id: str, status_update: StatusUpdate):
    try:
        if request_id not in requests:
            raise HTTPException(status_code=404, detail="Request not found")
            
        request = requests[request_id]
        request.status = status_update.status
        return request
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)