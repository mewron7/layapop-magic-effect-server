import shutil
import uuid
import os
import logging
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import effect renderers
# Adjust imports based on actual file locations in magic_effect/
try:
    from splatoon_paint_explosion import ExplosionPaintRenderer
    from paint_bubble_rain import BubbleRainRenderer
except ImportError:
    # Fallback/Mock for testing if imports fail (e.g. cv2 missing in env)
    print("Warning: Effect modules not found or dependencies missing.")
    ExplosionPaintRenderer = None
    BubbleRainRenderer = None

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories (ending in .nosync so iCloud ignores them and doesn't freeze the Mac)
UPLOAD_DIR = "uploads.nosync"
OUTPUT_DIR = "outputs.nosync"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Mount static files to serve outputs (URL is still just /outputs)
app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")

@app.post("/process-effect")
async def process_effect(file: UploadFile = File(...), effect_type: str = Form(...)):
    """
    Process uploaded video with selected effect.
    effect_type: 'explosion' | 'bubble'
    """
    if not file.filename.endswith(('.mp4', '.mov', '.avi')):
        raise HTTPException(status_code=400, detail="Invalid video format")
    
    video_id = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_DIR, f"{video_id}_input.mp4")
    output_filename = f"{video_id}_output.mp4"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    # Save input file
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    logger.info(f"Received video: {input_path}, Effect: {effect_type}")
    
    try:
        if effect_type == 'explosion':
            if ExplosionPaintRenderer:
                renderer = ExplosionPaintRenderer()
                renderer.process_video(input_path, output_path, num_splats=5)
            else:
                raise HTTPException(500, "Explosion renderer not available")
                
        elif effect_type == 'bubble':
            if BubbleRainRenderer:
                renderer = BubbleRainRenderer()
                renderer.process_video(input_path, output_path, num_bubbles=15)
            else:
                raise HTTPException(500, "Bubble renderer not available")
        
        else:
            raise HTTPException(400, f"Unknown effect type: {effect_type}")
            
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        raise HTTPException(500, f"Processing failed: {str(e)}")
        
    # Return a relative path so the frontend can prepend its known server URL
    output_url = f"/outputs/{output_filename}"
    
    return {"status": "completed", "output_url": output_url}

if __name__ == "__main__":
    import uvicorn

    # Render.com provides a PORT environment variable. Default to 8000 for local testing.
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
