from fastapi import FastAPI
import redis
import sys

app = FastAPI()

REDIS_HOST = "redis"
REDIS_PORT = 6379

print("=" * 60, file=sys.stderr)
print("ATTEMPTING TO CONNECT TO REDIS", file=sys.stderr)
print(f"Redis host: {REDIS_HOST}:{REDIS_PORT}", file=sys.stderr)
print("=" * 60, file=sys.stderr)

def get_redis_connection():
    try:
        print(f"Trying to connect to Redis at {REDIS_HOST}:{REDIS_PORT}...", file=sys.stderr)
        client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            socket_connect_timeout=3,
            decode_responses=True
        )
        # Test the connection
        client.ping()
        print("✓ Successfully connected to Redis!", file=sys.stderr)
        return client
    except redis.ConnectionError as e:
        print(f"✗ Failed to connect to Redis: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"✗ Unexpected error: {e}", file=sys.stderr)
        return None

@app.get("/")
def read_root():
    return {"message": "Counter API", "status": "running"}

@app.get("/health")
def health_check():
    client = get_redis_connection()
    if client:
        return {"status": "healthy", "redis": "connected", "host": REDIS_HOST}
    else:
        return {"status": "unhealthy", "redis": "disconnected", "host": REDIS_HOST}

@app.get("/count")
def increment_counter():
    client = get_redis_connection()
    if not client:
        return {"error": "Cannot connect to Redis", "host": REDIS_HOST}

    try:
        count = client.incr("visit_counter")
        return {"count": count, "message": "Counter incremented"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/reset")
def reset_counter():
    client = get_redis_connection()
    if not client:
        return {"error": "Cannot connect to Redis", "host": REDIS_HOST}

    try:
        client.set("visit_counter", 0)
        return {"count": 0, "message": "Counter reset"}
    except Exception as e:
        return {"error": str(e)}
