from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time
from collections import defaultdict
from typing import Dict, Tuple

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.visitor_records: Dict[str, list] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean up old records
        self.visitor_records[client_ip] = [
            t for t in self.visitor_records[client_ip] 
            if current_time - t < 60
        ]
        
        if len(self.visitor_records[client_ip]) >= self.requests_per_minute:
            raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")
            
        self.visitor_records[client_ip].append(current_time)
        
        response = await call_next(request)
        return response
