import time
import random
from fastapi import FastAPI, Request
from fastapi.responses import Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import logging

app = FastAPI()

REQUESTS = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'Duration of requests', ['method', 'endpoint'])

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("order-service")

@app.middleware("http")
async def add_metrics(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    REQUESTS.labels(method=request.method, endpoint=request.url.path, status=response.status_code).inc()
    REQUEST_DURATION.labels(method=request.method, endpoint=request.url.path).observe(duration)
    return response

@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/order")
async def create_order(product: str, quantity: int):
    if random.random() < 0.15:
        logger.error(f"Order failed: product {product}, quantity {quantity} - payment gateway error")
        return {"status": "failed", "reason": "payment error"}
    logger.info(f"Order created: product {product}, quantity {quantity}")
    return {"status": "success", "order_id": random.randint(1000,9999)}

@app.get("/health")
async def health():
    return {"status": "ok"}
