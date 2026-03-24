"""
Example: Integration with existing media-worker system

This shows how to integrate the paint explosion effect
into the existing Holi app architecture.
"""

# ============================================================
# 1. FastAPI Endpoint Example
# ============================================================

from fastapi import APIRouter, UploadFile, HTTPException
from pydantic import BaseModel
import os
import uuid

router = APIRouter(prefix="/api/v1/effects", tags=["effects"])


class PaintEffectRequest(BaseModel):
    num_splats: int = 4  # Number of explosions (default: 4)


@router.post("/paint-explosion")
async def apply_paint_explosion(
    video: UploadFile,
    request: PaintEffectRequest
):
    """
    Apply paint explosion effect to video
    
    Args:
        video: Uploaded video file
        request: Effect parameters
    
    Returns:
        {
            "job_id": "...",
            "status": "processing",
            "estimated_time": 45
        }
    """
    # Validate
    if not video.filename.endswith(('.mp4', '.mov', '.avi')):
        raise HTTPException(400, "Invalid video format")
    
    if not 1 <= request.num_splats <= 10:
        raise HTTPException(400, "num_splats must be between 1-10")
    
    # Save uploaded file
    job_id = str(uuid.uuid4())
    input_path = f"uploads/{job_id}_input.mp4"
    
    with open(input_path, "wb") as f:
        f.write(await video.read())
    
    # Queue job (Celery)
    from tasks.paint_effect_task import process_paint_explosion_task
    task = process_paint_explosion_task.delay(job_id, request.num_splats)
    
    return {
        "job_id": job_id,
        "task_id": task.id,
        "status": "processing",
        "estimated_time": estimate_processing_time(input_path, request.num_splats)
    }


@router.get("/paint-explosion/{job_id}")
async def get_paint_explosion_status(job_id: str):
    """
    Get processing status
    
    Returns:
        {
            "status": "completed" | "processing" | "failed",
            "output_url": "..." (if completed),
            "error": "..." (if failed)
        }
    """
    # Check job status in database
    job = get_job_from_db(job_id)
    
    if job.status == "completed":
        return {
            "status": "completed",
            "output_url": job.output_url,
            "duration": job.processing_duration
        }
    elif job.status == "failed":
        return {
            "status": "failed",
            "error": job.error_message
        }
    else:
        return {
            "status": "processing",
            "progress": job.progress
        }


def estimate_processing_time(video_path: str, num_splats: int) -> int:
    """Estimate processing time in seconds"""
    import cv2
    
    cap = cv2.VideoCapture(video_path)
    duration = cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    
    # Rough estimate: 3.5x real-time + overhead
    return int(duration * 3.5 + 10)


# ============================================================
# 2. Celery Task Example
# ============================================================

from celery import shared_task
from processors.splatoon_paint_explosion import ExplosionPaintRenderer
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def process_paint_explosion_task(self, job_id: str, num_splats: int = 4):
    """
    Celery task for paint explosion effect
    
    Args:
        job_id: Unique job identifier
        num_splats: Number of explosions
    """
    try:
        # Update status
        update_job_status(job_id, "processing", progress=0)
        
        # Paths
        input_path = f"uploads/{job_id}_input.mp4"
        output_path = f"outputs/{job_id}_output.mp4"
        
        # Process video
        logger.info(f"Processing job {job_id} with {num_splats} explosions")
        
        renderer = ExplosionPaintRenderer()
        renderer.process_video(
            input_path=input_path,
            output_path=output_path,
            num_splats=num_splats
        )
        
        # Upload to storage (Supabase, S3, etc.)
        output_url = upload_to_storage(output_path, job_id)
        
        # Update status
        update_job_status(
            job_id, 
            "completed", 
            progress=100,
            output_url=output_url
        )
        
        logger.info(f"Job {job_id} completed: {output_url}")
        
        return {"status": "completed", "output_url": output_url}
        
    except Exception as e:
        logger.error(f"Job {job_id} failed: {str(e)}")
        update_job_status(job_id, "failed", error=str(e))
        raise


def update_job_status(job_id: str, status: str, **kwargs):
    """Update job status in database"""
    # Implement database update
    pass


def upload_to_storage(file_path: str, job_id: str) -> str:
    """Upload to Supabase/S3 and return URL"""
    # Implement storage upload
    # Example with Supabase:
    # from supabase import create_client
    # supabase = create_client(url, key)
    # result = supabase.storage.from_('videos').upload(
    #     f"{job_id}_output.mp4",
    #     file_path
    # )
    # return result.public_url
    pass


# ============================================================
# 3. React Native / Expo Integration Example
# ============================================================

"""
// Frontend (React Native)

import * as DocumentPicker from 'expo-document-picker';
import axios from 'axios';

export const applyPaintExplosion = async (numSplats = 4) => {
  try {
    // Pick video
    const result = await DocumentPicker.getDocumentAsync({
      type: 'video/*',
    });
    
    if (result.type === 'cancel') return;
    
    // Upload and process
    const formData = new FormData();
    formData.append('video', {
      uri: result.uri,
      type: 'video/mp4',
      name: 'video.mp4',
    });
    
    const response = await axios.post(
      'https://your-api.com/api/v1/effects/paint-explosion',
      formData,
      {
        params: { num_splats: numSplats },
        headers: { 'Content-Type': 'multipart/form-data' },
      }
    );
    
    const { job_id, estimated_time } = response.data;
    
    // Poll for completion
    return pollForCompletion(job_id, estimated_time);
    
  } catch (error) {
    console.error('Paint explosion failed:', error);
    throw error;
  }
};

const pollForCompletion = async (jobId, estimatedTime) => {
  const maxAttempts = Math.ceil(estimatedTime / 2); // Poll every 2 seconds
  
  for (let i = 0; i < maxAttempts; i++) {
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    const response = await axios.get(
      `https://your-api.com/api/v1/effects/paint-explosion/${jobId}`
    );
    
    if (response.data.status === 'completed') {
      return response.data.output_url;
    } else if (response.data.status === 'failed') {
      throw new Error(response.data.error);
    }
    
    // Update progress UI
    console.log(`Progress: ${response.data.progress}%`);
  }
  
  throw new Error('Processing timeout');
};

// Usage in component:
const handleApplyEffect = async () => {
  setLoading(true);
  try {
    const outputUrl = await applyPaintExplosion(4);
    setVideoUrl(outputUrl);
    Alert.alert('Success', 'Paint explosion applied!');
  } catch (error) {
    Alert.alert('Error', error.message);
  } finally {
    setLoading(false);
  }
};
"""


# ============================================================
# 4. Database Schema Example
# ============================================================

"""
CREATE TABLE paint_effect_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    status VARCHAR(20) NOT NULL,  -- 'processing', 'completed', 'failed'
    input_path VARCHAR(500),
    output_path VARCHAR(500),
    output_url VARCHAR(500),
    num_splats INTEGER DEFAULT 4,
    progress INTEGER DEFAULT 0,
    error_message TEXT,
    processing_duration INTEGER,  -- seconds
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_paint_jobs_user ON paint_effect_jobs(user_id);
CREATE INDEX idx_paint_jobs_status ON paint_effect_jobs(status);
"""
