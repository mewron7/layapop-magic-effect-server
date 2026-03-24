# Holi Paint Explosion Effect System

**Version:** 1.0  
**Date:** January 21, 2026  
**Author:** Asuka

---

## 📖 Overview

An explosive paint effect system inspired by the Holi festival. Adds colorful, dynamic explosion effects to videos with vibrant paints.

### Key Features

- ✅ Explosive paint effects with radial burst patterns
- ✅ 12 vibrant colors
- ✅ Color mixing (overlapping paints blend naturally)
- ✅ Gradual transparency (opaque center, transparent edges)
- ✅ 600-1000 particles per explosion
- ✅ Triple shockwave rings
- ✅ Screen shake effect
- ✅ Glow effects
- ✅ Streaming processing (memory-efficient)

---

## 🎨 Visual Effects

### Effect Layers (5 Layers)

1. **Paint Body**: Radial explosion pattern with gradual transparency
2. **Shockwave**: Triple expanding rings, 0.4s duration
3. **Projectile**: Glowing incoming projectile, 0.4s flight time
4. **Particles**: 600-1000 explosive particles with glow effects
5. **Screen Shake**: Camera shake effect, 0.15s duration

### Color Palette (12 Colors)

```
Hot Pink, Yellow, Blue, Orange, Purple, Spring Green
Magenta, Cyan, Green, Red, Light Pink variations x2
```

### Color Mixing

- Overlapping paints blend together (additive blending)
- Transparency is preserved (maximum value method)
- Natural and enjoyable color combinations

---

## 🚀 Usage

### Basic Usage

```python
from splatoon_paint_explosion import ExplosionPaintRenderer

# Initialize renderer
renderer = ExplosionPaintRenderer()

# Process video
renderer.process_video(
    input_path='input.mp4',
    output_path='output.mp4',
    num_splats=4  # Number of explosions (recommended: 3-6)
)
```

### Parameters

#### `num_splats` (int)
- **Description**: Number of explosions
- **Recommended**: 3-6
- **Range**: 1-10
- **Effect**: More explosions = more spectacular, but longer processing time

---

## ⚙️ Technical Specifications

### Dependencies

```python
opencv-python (cv2)
numpy
mediapipe (optional, for person segmentation)
```

### Performance

| Metric | Value |
|--------|-------|
| 10s video (1080p) | ~40-45 seconds |
| Memory usage | ~100-150MB |
| Particles per explosion | 600-1000 |
| Processing method | Streaming (memory-safe) |

### Optimization Points

✅ **Streaming write**: Frames written immediately, not accumulated in memory  
✅ **Vectorized operations**: NumPy array operations minimize loops  
✅ **Optimized particle count**: Balanced between visual impact and performance  

---

## 🎯 Recommended Settings

### Short videos (~10s)
```python
num_splats=4  # Balanced
```

### Medium videos (~30s)
```python
num_splats=6-8  # Well-distributed
```

### Long videos (60s+)
```python
num_splats=10-15  # Spaced out
```

---

## 🔧 Integration Guide

### Integration into Existing System

#### 1. File Placement
```
your-app/
├── processors/
│   └── splatoon_paint_explosion.py  # ← Place here
├── api/
│   └── paint_effect_endpoint.py     # ← Create new
└── tasks/
    └── paint_effect_task.py         # ← Celery task
```

#### 2. API Endpoint Example

```python
from fastapi import APIRouter, UploadFile
from processors.splatoon_paint_explosion import ExplosionPaintRenderer

router = APIRouter()

@router.post("/effects/paint-explosion")
async def apply_paint_explosion(
    video: UploadFile,
    num_splats: int = 4
):
    # Save uploaded video
    input_path = save_upload(video)
    output_path = generate_output_path()
    
    # Apply effect
    renderer = ExplosionPaintRenderer()
    renderer.process_video(input_path, output_path, num_splats)
    
    # Return result
    return {"output_url": upload_to_storage(output_path)}
```

#### 3. Celery Task Example

```python
from celery import shared_task
from processors.splatoon_paint_explosion import ExplosionPaintRenderer

@shared_task
def process_paint_explosion(video_id: str, num_splats: int = 4):
    # Get video from database
    video = get_video_from_db(video_id)
    
    # Apply effect
    renderer = ExplosionPaintRenderer()
    renderer.process_video(
        video.input_path,
        video.output_path,
        num_splats
    )
    
    # Update status
    update_video_status(video_id, "completed")
```

---

## 🎨 Customization

### Changing Colors

```python
# In splatoon_paint_explosion.py __init__ method
self.colors = [
    (147, 20, 255),   # BGR format
    # ... add your colors
]
```

### Adjusting Particle Count

```python
# In generate_explosion_particles method
num_particles = random.randint(600, 1000)  # Adjust this value
```

### Adjusting Transparency

```python
# In create_explosion_mask method
# Center opacity
cv2.circle(mask, splat.center, core_radius, 0.9, -1)  # Change 0.9

# Edge fade
radial_fade = radial_fade ** 0.7  # Change 0.7 (lower = stronger fade)
```

---

## 🐛 Troubleshooting

### Processing is Slow
- Reduce `num_splats` (4 → 3)
- Reduce particle count (600-1000 → 400-600)

### Out of Memory
- Reduce video resolution
- Verify streaming processing (not accumulating frames in list)

### Colors Don't Match Expectations
- Ensure colors are in BGR format
- RGB → BGR conversion: `(R, G, B)` → `(B, G, R)`

### Transparency Too Strong/Weak
- Adjust opacity in `create_explosion_mask`
- Adjust `blend_factor` (current default: 0.5)

---

## 📊 Performance Benchmarks

### Test Environment
- CPU: Intel i7 / AMD Ryzen 5 equivalent
- RAM: 16GB
- Video: 1920x1080, 30fps

### Processing Times

| Duration | Explosions | Processing Time | Memory |
|----------|-----------|-----------------|--------|
| 5s | 3 | ~15s | ~80MB |
| 10s | 4 | ~40s | ~120MB |
| 30s | 6 | ~140s | ~150MB |
| 60s | 10 | ~320s | ~180MB |

---

## 📝 Release Notes

### v1.0 (January 21, 2026)
- ✅ Initial release
- ✅ 12-color palette
- ✅ Color mixing feature
- ✅ Gradual transparency
- ✅ Streaming processing
- ✅ Performance optimizations
- ✅ Larger particles (3-12px) with enhanced glow

---

## 🔑 Important Notes

### BGR Color Format
OpenCV uses BGR (not RGB). All colors must be specified in BGR format:
```python
# Example
(147, 20, 255)  # Hot Pink in BGR
# NOT (255, 20, 147) which would be RGB
```

### Memory Safety
The system uses streaming write to avoid memory accumulation:
```python
# ✅ Correct (streaming)
out.write(frame)

# ❌ Wrong (accumulates in memory)
frames.append(frame)
# ... later
for frame in frames:
    out.write(frame)
```

### Performance Considerations
- Processing time ≈ video duration × 4
- Longer videos require proportionally longer processing
- Memory usage remains constant regardless of video length (streaming)

---

## 📧 Support

For questions or bug reports:
- Engineer: Asuka
- Project: Holi App

---

## 📄 License

Internal project use

---

## 🎉 Final Notes

This effect is designed with **fun as the top priority**. 
It recreates the explosive color celebration of the Holi festival in video form!

**Enjoy! 🎨💥✨**
