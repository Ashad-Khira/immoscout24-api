import logging, uvicorn, time, os, hashlib
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from utils import main as helper_parser
from fastapi.staticfiles import StaticFiles

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("scraper")

# Constants
API_KEY = "2f47cdc85bbf468f85a11b3e4b05fcb6"
TARGET_HOST = "immoscout24"
HTML_SAVE_PATH = os.path.join('static', 'page_save')
os.makedirs(HTML_SAVE_PATH, exist_ok=True)


# API Key Verification
def verify_api_key(key: str = Query(..., alias="api_key")):
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return key


# FastAPI app
app = FastAPI(title="ImmoScout24 Scraper API")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/api/get-data", response_class=JSONResponse)
async def get_data(
        request: Request,
        url: str = Query(None, description="ImmoScout24 URL"),
        api_key: str = Query(None, description="API Key"),
):
    start_time = time.time()
    client_ip = request.client.host
    html_url = None
    
    if not api_key or api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    
    try:
        # Input validations
        if not url:
            raise HTTPException(status_code=400, detail="Missing URL")
        
        if TARGET_HOST not in url:
            raise HTTPException(status_code=400, detail=f"Only {TARGET_HOST} allowed")
        
        # Call parser
        data = helper_parser(url)
        
        if "html" in data and data["html"]:
            unique_id = hashlib.md5(url.encode()).hexdigest()[:10]
            filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{unique_id}.html"
            filepath = os.path.join(HTML_SAVE_PATH, filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(data["html"])
            
            html_url = f"{request.base_url}static/page_save/{filename}"
            del data["html"]
        
        if not data:
            data = {"parsed": False, "error": "Failed to parse URL"}
            status_code = 500
        else:
            status_code = 200
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        data = {"parsed": False, "error": f"Internal server error: {str(e)}"}
        status_code = 500
    finally:
        elapsed = round(time.time() - start_time, 4)
    
    response_json = {
        "request_time": datetime.utcnow().isoformat(),
        "request_ip": client_ip,
        "request_elapsed": elapsed,
        "status": status_code,
        "request_headers": {
            "input_url": url,
            "html_url": html_url
        },
        "data": data
    }
    
    return JSONResponse(
        content=response_json,
        status_code=status_code,
        headers={"X-Process-Time": str(elapsed)},
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
