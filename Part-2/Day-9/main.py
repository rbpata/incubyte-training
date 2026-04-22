import fastapi
from prometheus_client import Counter,Gauge, Summary, Histogram,make_asgi_app
import uvicorn

app = fastapi.FastAPI()

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

REQUEST_COUNTER = Counter("request_count", "Number of requests received")

@app.get("/")
def read_root():
    REQUEST_COUNTER.inc()
    return {"message": "Hello, World!"}

@app.get("/metric")
def get_metrics():
    return {"request_count": REQUEST_COUNTER._value.get()}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
