import time
import requests

QDRANT_URL = "http://qdrant:6333"
COLLECTION = "egyptian_civil_code"
SNAPSHOT_PATH = "/snapshots/egyptian_civil_code.snapshot"

def wait_for_qdrant():
    for _ in range(30):
        try:
            r = requests.get(f"{QDRANT_URL}/healthz")
            if r.status_code == 200:
                return
        except:
            time.sleep(1)
    raise RuntimeError()

def restore_if_empty():
    wait_for_qdrant()
    r = requests.get(f"{QDRANT_URL}/collections/{COLLECTION}")
    if r.status_code == 200:
        return
    r = requests.post(
        f"{QDRANT_URL}/collections/{COLLECTION}/snapshots/recover",
        json={"location": SNAPSHOT_PATH}
    )

if __name__ == "__main__":
    restore_if_empty()