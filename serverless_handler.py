import runpod
from fastapi.testclient import TestClient
from app.main import app

# FastAPI test client (simulates requests to FastAPI app)
client = TestClient(app)

def handler(event):
    """
    event = {
      "input": {
        "path": "/api/v1/upload",
        "method": "POST",
        "body": {...},
        "files": {...}
      }
    }
    """
    try:
        path = event["input"].get("path", "/")
        method = event["input"].get("method", "GET").upper()
        body = event["input"].get("body", None)
        files = event["input"].get("files", None)

        response = client.request(method, path, json=body, files=files)

        return {
            "status_code": response.status_code,
            "data": response.json()
        }
    except Exception as e:
        return {"error": str(e)}

# Register handler for RunPod Serverless
runpod.serverless.start({"handler": handler})
