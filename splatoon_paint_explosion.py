"""
Splatoon Paint System - EXPLOSION/BURST Edition
Fun > Realism - Maximum Impact!

Focus on:
- Massive explosion effects
- Shockwaves
- Intense particle bursts
- Screen shake
- Bloom/glow effects
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass
import random
import logging

# MediaPipe for person segmentation
# Disabled because it hangs on macOS
MEDIAPIPE_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class PaintSplat:
    time: float
    center: Tuple[int, int]
    radius: int
    color: Tuple[int, int, int]
    shape_seed: int


@dataclass
class InkProjectile:
    splat: PaintSplat
    start_pos: Tuple[int, int]


@dataclass
class InkParticle:
    start_pos: Tuple[float, float]
    velocity: Tuple[float, float]
    lifetime: float
    size: int
    color: Tuple[int, int, int]


class ExplosionPaintSystem:
    """
    EXPLOSION-FOCUSED paint system
    Maximum fun, maximum impact!
    """
    
    def __init__(self, video_width: int, video_height: int):
        self.width = video_width
        self.height = video_height
        
        # Vibrant explosion colors (BGR format!) - 12 COLORS ⭐⭐⭐
        self.colors = [
            # Original 6 colors
            (147, 20, 255),   # Hot Pink (BGR)
            (0, 255, 255),    # Yellow (BGR)
            (255, 0, 0),      # Blue (BGR)
            (0, 165, 255),    # Orange (BGR)
            (219, 112, 147),  # Purple (BGR)
            (127, 255, 0),    # Spring Green (BGR)
            
            # NEW 6 colors ⭐
            (255, 0, 255),    # Magenta (BGR)
            (255, 255, 0),    # Cyan (BGR)
            (0, 255, 0),      # Green (BGR)
            (0, 0, 255),      # Red (BGR)
            (180, 105, 255),  # Hot Pink Light (BGR)
            (203, 192, 255),  # Light Pink (BGR)
        ]
        
        # Person segmentation (optional)
        self.segmenter = None
        if MEDIAPIPE_AVAILABLE:
            try:
                mp_selfie = mp.solutions.selfie_segmentation
                self.segmenter = mp_selfie.SelfieSegmentation(model_selection=1)
                logger.info("✅ Person segmentation enabled")
            except (AttributeError, Exception) as e:
                logger.warning(f"⚠️  MediaPipe person segmentation unavailable (version incompatibility): {e}")
                logger.info("📌 Continuing without person segmentation (effect will work normally)")
    
    def get_person_mask(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """Get person mask (optional for paint exclusion)"""
        if self.segmenter is None:
            return None
        
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.segmenter.process(rgb)
        
        if results.segmentation_mask is None:
            return None
        
        return results.segmentation_mask.astype(np.float32)
    
    def create_explosion_mask(
        self,
        splat: PaintSplat
    ) -> np.ndarray:
        """
        Create EXPLOSIVE paint mask with GRADUAL TRANSPARENCY ⭐⭐⭐
        
        Center: 90% opaque (strong impact)
        Edges: fade to 0% (fully transparent - see original video)
        """
        mask = np.zeros((self.height, self.width), dtype=np.float32)
        
        np.random.seed(splat.shape_seed)
        
        # Small core (explosion origin) - MAXIMUM opacity
        core_radius = int(splat.radius * 0.2)
        cv2.circle(mask, splat.center, core_radius, 0.9, -1)  # 90% at center
        
        # MASSIVE radial burst arms (40-60 rays!)
        num_rays = random.randint(40, 60)
        for _ in range(num_rays):
            angle = random.uniform(0, 2 * np.pi)
            
            # Long rays for explosion feel
            ray_length = splat.radius * random.uniform(1.5, 3.0)
            
            # Draw ray in segments for fade effect
            end_x = int(splat.center[0] + ray_length * np.cos(angle))
            end_y = int(splat.center[1] + ray_length * np.sin(angle))
            
            thickness = random.randint(3, 12)
            
            # Draw ray with fade: strong at center, fade at edges
            segments = 10
            for seg in range(segments):
                seg_progress = seg / segments
                seg_start_x = int(splat.center[0] + (end_x - splat.center[0]) * seg_progress)
                seg_start_y = int(splat.center[1] + (end_y - splat.center[1]) * seg_progress)
                seg_end_x = int(splat.center[0] + (end_x - splat.center[0]) * (seg_progress + 1/segments))
                seg_end_y = int(splat.center[1] + (end_y - splat.center[1]) * (seg_progress + 1/segments))
                
                # Fade from 0.8 at center to 0.0 at end
                intensity = 0.8 * (1.0 - seg_progress)
                
                temp_mask = np.zeros_like(mask)
                cv2.line(temp_mask, (seg_start_x, seg_start_y), (seg_end_x, seg_end_y), intensity, thickness)
                mask = np.maximum(mask, temp_mask)
            
            # Add blob at ray end (fading)
            blob_size = int(splat.radius * random.uniform(0.1, 0.3))
            blob_intensity = random.uniform(0.3, 0.5)  # Medium opacity
            cv2.circle(mask, (end_x, end_y), blob_size, blob_intensity, -1)
        
        # TONS of scattered droplets (fade with distance)
        num_droplets = random.randint(100, 150)
        for _ in range(num_droplets):
            angle = random.uniform(0, 2 * np.pi)
            distance = splat.radius * random.uniform(2.0, 4.5)
            
            drop_x = int(splat.center[0] + distance * np.cos(angle))
            drop_y = int(splat.center[1] + distance * np.sin(angle))
            drop_size = int(splat.radius * random.uniform(0.02, 0.12))
            
            if 0 <= drop_x < self.width and 0 <= drop_y < self.height:
                # Fade with distance: close=0.6, far=0.2
                distance_ratio = min(distance / (splat.radius * 4.5), 1.0)
                intensity = 0.6 * (1.0 - distance_ratio)
                cv2.circle(mask, (drop_x, drop_y), drop_size, intensity, -1)
        
        # Apply radial fade from center
        y, x = np.ogrid[:self.height, :self.width]
        dist_from_center = np.sqrt((x - splat.center[0])**2 + (y - splat.center[1])**2)
        
        # Radial fade: strong at center, weak at edges
        max_dist = splat.radius * 3.5
        radial_fade = np.clip(1.0 - dist_from_center / max_dist, 0, 1)
        radial_fade = radial_fade ** 0.7  # Softer falloff
        
        mask = mask * radial_fade
        
        # Light blur
        mask = cv2.GaussianBlur(mask, (5, 5), 1.0)
        
        # Convert to 0-255 (will be used as opacity 0-90%)
        return (mask * 255).astype(np.uint8)
    
    def draw_explosion_shockwave(
        self,
        frame: np.ndarray,
        splat: PaintSplat,
        current_time: float
    ) -> np.ndarray:
        """
        Draw MASSIVE shockwave effect
        Multiple expanding rings + flash
        """
        time_since_impact = current_time - splat.time
        
        # Shockwave duration: 0.4s (longer than normal)
        if time_since_impact < 0 or time_since_impact > 0.4:
            return frame
        
        overlay = frame.copy()
        
        # Progress (0-1)
        progress = time_since_impact / 0.4
        alpha = 1.0 - progress
        
        # MULTIPLE SHOCKWAVE RINGS (3 rings!)
        for ring_idx in range(3):
            ring_delay = ring_idx * 0.1
            ring_progress = min(1.0, max(0, (time_since_impact - ring_delay) / 0.3))
            
            if ring_progress > 0:
                ring_radius = int(splat.radius * (1 + ring_progress * 8))  # Huge expansion!
                ring_alpha = (1.0 - ring_progress) * 0.7
                ring_thickness = max(5, int(25 * (1 - ring_progress)))  # Thick rings
                
                cv2.circle(overlay, splat.center, ring_radius, splat.color, ring_thickness)
                frame = cv2.addWeighted(overlay, ring_alpha, frame, 1 - ring_alpha, 0)
                overlay = frame.copy()
        
        # MASSIVE CENTER FLASH (longer duration, brighter)
        if time_since_impact < 0.15:
            flash_progress = time_since_impact / 0.15
            flash_alpha = (1.0 - flash_progress) * 0.9  # Very bright!
            flash_radius = int(splat.radius * (0.8 + flash_progress * 0.5))
            
            cv2.circle(overlay, splat.center, flash_radius, (255, 255, 255), -1)
            frame = cv2.addWeighted(overlay, flash_alpha, frame, 1 - flash_alpha, 0)
            overlay = frame.copy()
        
        # RADIAL LIGHT RAYS (explosion rays)
        if time_since_impact < 0.2:
            ray_progress = time_since_impact / 0.2
            ray_alpha = (1.0 - ray_progress) * 0.6
            
            np.random.seed(splat.shape_seed)
            num_rays = 12
            for i in range(num_rays):
                angle = (2 * np.pi * i / num_rays) + np.random.uniform(-0.2, 0.2)
                ray_length = int(splat.radius * (2 + ray_progress * 4))
                
                end_x = int(splat.center[0] + ray_length * np.cos(angle))
                end_y = int(splat.center[1] + ray_length * np.sin(angle))
                
                cv2.line(overlay, splat.center, (end_x, end_y), (255, 255, 255), 3)
            
            frame = cv2.addWeighted(overlay, ray_alpha, frame, 1 - ray_alpha, 0)
        
        return frame
    
    def draw_screen_shake(
        self,
        frame: np.ndarray,
        splat: PaintSplat,
        current_time: float
    ) -> np.ndarray:
        """
        Simulate screen shake effect (camera shake)
        """
        time_since_impact = current_time - splat.time
        
        # Shake duration: 0.15s
        if time_since_impact < 0 or time_since_impact > 0.15:
            return frame
        
        # Shake intensity (decreases over time)
        shake_intensity = 15 * (1.0 - time_since_impact / 0.15)
        
        # Random offset
        np.random.seed(int(time_since_impact * 1000))
        offset_x = int(np.random.uniform(-shake_intensity, shake_intensity))
        offset_y = int(np.random.uniform(-shake_intensity, shake_intensity))
        
        # Create translation matrix
        h, w = frame.shape[:2]
        M = np.float32([[1, 0, offset_x], [0, 1, offset_y]])
        
        # Apply shake
        shaken = cv2.warpAffine(frame, M, (w, h), borderMode=cv2.BORDER_REPLICATE)
        
        return shaken
    
    def generate_explosion_particles(self, splat: PaintSplat) -> List[InkParticle]:
        """
        Generate particle burst - OPTIMIZED COUNT ⭐
        500-800 particles (down from 2000-3000) for performance
        Still plenty explosive!
        """
        particles = []
        num_particles = random.randint(600, 1000)  # Was 500-800, now 600-1000! More particles!
        
        np.random.seed(splat.shape_seed)
        
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * np.pi)
            
            # VERY HIGH speed for explosion
            speed = random.uniform(200, 800)  # Fast burst!
            
            vx = speed * np.cos(angle)
            vy = speed * np.sin(angle) - 250  # Strong upward blast
            
            # BIGGER particles for more impact ⭐⭐⭐
            size = random.randint(3, 12)  # Was 1-8, now 3-12! Much bigger!
            
            # Varied lifetimes (some particles last longer)
            lifetime = random.uniform(0.4, 1.2)
            
            particles.append(InkParticle(
                (float(splat.center[0]), float(splat.center[1])),
                (vx, vy),
                lifetime,
                size,
                splat.color
            ))
        
        return particles
    
    def draw_particles(
        self,
        frame: np.ndarray,
        particles: List[InkParticle],
        splat_time: float,
        current_time: float
    ) -> np.ndarray:
        """Draw particles with GLOW effect"""
        time_since_start = current_time - splat_time
        
        if time_since_start < 0:
            return frame
        
        overlay = frame.copy()
        
        for particle in particles:
            age = time_since_start
            
            if age > particle.lifetime:
                continue
            
            # Calculate position
            gravity = 500.0
            x = particle.start_pos[0] + particle.velocity[0] * age
            y = particle.start_pos[1] + particle.velocity[1] * age + 0.5 * gravity * age * age
            
            pos = (int(x), int(y))
            
            if not (0 <= pos[0] < self.width and 0 <= pos[1] < self.height):
                continue
            
            # Fade over lifetime
            alpha = 1.0 - (age / particle.lifetime)
            
            # Size changes over time - LESS shrinking for bigger presence ⭐⭐⭐
            current_size = max(2, int(particle.size * (0.7 + alpha * 0.3)))  # Was 0.5+alpha*0.5, now less shrink
            
            # BIGGER GLOW EFFECT ⭐⭐⭐
            # Outer glow (much larger, semi-transparent)
            glow_size = current_size + 8  # Was +4, now +8! Much bigger glow!
            glow_color = particle.color
            cv2.circle(overlay, pos, glow_size, glow_color, -1)
            
            # Inner particle (brighter)
            cv2.circle(overlay, pos, current_size, particle.color, -1)
            
            # Bigger white highlight ⭐
            highlight_size = max(2, current_size // 2)  # Minimum 2 instead of 1
            highlight_pos = (pos[0] - current_size//3, pos[1] - current_size//3)
            if 0 <= highlight_pos[0] < self.width and 0 <= highlight_pos[1] < self.height:
                cv2.circle(overlay, highlight_pos, highlight_size, (255, 255, 255), -1)
        
        # Blend with glow
        frame = cv2.addWeighted(overlay, 0.8, frame, 0.2, 0)
        
        return frame
    
    def draw_projectile(
        self,
        frame: np.ndarray,
        projectile: InkProjectile,
        current_time: float
    ) -> np.ndarray:
        """Draw flying projectile with MEGA GLOW"""
        splat = projectile.splat
        
        # Projectile visible 0.4s before impact
        time_until_impact = splat.time - current_time
        
        if time_until_impact > 0.4 or time_until_impact < 0:
            return frame
        
        # Progress (0-1, 0=start, 1=impact)
        progress = 1.0 - (time_until_impact / 0.4)
        progress = progress ** 2  # Ease-in (acceleration)
        
        # Position
        start_x, start_y = projectile.start_pos
        end_x, end_y = splat.center
        
        curr_x = int(start_x + (end_x - start_x) * progress)
        curr_y = int(start_y + (end_y - start_y) * progress)
        
        overlay = frame.copy()
        
        # MASSIVE projectile size (grows as it gets closer)
        base_size = int(splat.radius * 0.35)
        size = int(base_size * (0.7 + progress * 0.3))
        
        # HUGE GLOW (3 layers!)
        glow_size_1 = size + 30
        glow_size_2 = size + 15
        glow_size_3 = size + 5
        
        cv2.circle(overlay, (curr_x, curr_y), glow_size_1, splat.color, -1)
        frame = cv2.addWeighted(overlay, 0.15, frame, 0.85, 0)
        
        overlay = frame.copy()
        cv2.circle(overlay, (curr_x, curr_y), glow_size_2, splat.color, -1)
        frame = cv2.addWeighted(overlay, 0.3, frame, 0.7, 0)
        
        overlay = frame.copy()
        cv2.circle(overlay, (curr_x, curr_y), glow_size_3, splat.color, -1)
        frame = cv2.addWeighted(overlay, 0.5, frame, 0.5, 0)
        
        # Main projectile
        overlay = frame.copy()
        cv2.circle(overlay, (curr_x, curr_y), size, splat.color, -1)
        frame = cv2.addWeighted(overlay, 0.95, frame, 0.05, 0)
        
        # BRIGHT white highlight
        highlight_size = size // 2
        highlight_pos = (curr_x - size//3, curr_y - size//3)
        overlay = frame.copy()
        cv2.circle(overlay, highlight_pos, highlight_size, (255, 255, 255), -1)
        frame = cv2.addWeighted(overlay, 0.9, frame, 0.1, 0)
        
        return frame
    
    def generate_splats(
        self,
        duration: float,
        num_splats: int = 4
    ) -> Tuple[List[PaintSplat], List[InkProjectile], List[List[InkParticle]]]:
        """Generate explosion events"""
        splats = []
        projectiles = []
        all_particles = []
        
        time_step = duration / (num_splats + 1)
        
        for i in range(num_splats):
            t = time_step * (i + 1) + random.uniform(-0.3, 0.3)
            t = max(0.5, min(duration - 0.5, t))
            
            margin = 100
            x = random.randint(margin, self.width - margin)
            y = random.randint(margin, self.height - margin)
            
            # LARGER splats for bigger explosions
            base_size = min(self.width, self.height) * 0.30  # Was 0.25
            radius = int(base_size * random.uniform(0.9, 1.3))
            
            color = random.choice(self.colors)
            shape_seed = random.randint(0, 999999)
            
            splat = PaintSplat(t, (x, y), radius, color, shape_seed)
            splats.append(splat)
            
            # Projectile
            edge = random.randint(0, 3)
            if edge == 0:
                start_x, start_y = x + random.randint(-100, 100), -50
            elif edge == 1:
                start_x, start_y = self.width + 50, y + random.randint(-100, 100)
            elif edge == 2:
                start_x, start_y = x + random.randint(-100, 100), self.height + 50
            else:
                start_x, start_y = -50, y + random.randint(-100, 100)
            
            projectiles.append(InkProjectile(splat, (start_x, start_y)))
            
            # EXPLOSION particles
            particles = self.generate_explosion_particles(splat)
            all_particles.append(particles)
        
        return splats, projectiles, all_particles


class ExplosionPaintRenderer:
    """
    Renderer for explosion paint system
    Simple approach: paint sticks to screen, no complex physics
    """
    
    def __init__(self):
        self.paint_system = None
    
    def process_video(
        self,
        input_path: str,
        output_path: str,
        num_splats: int = 4
    ):
        """Process video with EXPLOSION effects"""
        logger.info(f"🎨 EXPLOSION PAINT MODE - Maximum Fun!")
        
        cap = cv2.VideoCapture(input_path)
        
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {input_path}")
        
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps
        
        logger.info(f"Video: {width}x{height}, {duration:.1f}s, {fps:.1f}fps")
        
        # Initialize
        self.paint_system = ExplosionPaintSystem(width, height)
        
        # Generate explosions!
        splats, projectiles, all_particles = self.paint_system.generate_splats(
            duration, num_splats
        )
        
        # Pre-generate masks
        splat_masks = []
        for splat in splats:
            mask = self.paint_system.create_explosion_mask(splat)
            splat_masks.append(mask)
        
        logger.info(f"💥 {len(splats)} EXPLOSIONS ready!")
        
        # STREAMING WRITE - open writer first ⭐⭐⭐
        logger.info("Starting streaming video write...")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        if not out.isOpened():
            raise ValueError(f"Cannot open output video: {output_path}")
        
        # Process frames - WRITE IMMEDIATELY ⭐⭐⭐
        frame_num = 0
        
        # Paint layer: store color AND opacity separately
        paint_color_layer = np.zeros((height, width, 3), dtype=np.uint8)
        paint_alpha_layer = np.zeros((height, width), dtype=np.float32)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            current_time = frame_num / fps
            
            # Start with original
            result = frame.copy()
            
            # Apply paint with COLOR MIXING ⭐⭐⭐
            for i, splat in enumerate(splats):
                if current_time >= splat.time:
                    mask = splat_masks[i]
                    
                    # Get alpha values from mask (0-1)
                    alpha = mask.astype(np.float32) / 255.0
                    
                    # COLOR MIXING APPROACH - VECTORIZED ⭐⭐⭐
                    # Mix colors but PRESERVE TRANSPARENCY ⭐
                    
                    # Create paint contribution (broadcast color to full frame)
                    splat_color_bgr = np.array(splat.color, dtype=np.float32)
                    new_paint = np.ones((height, width, 3), dtype=np.float32) * splat_color_bgr
                    
                    # Blend factor: how much new paint vs mixing
                    blend_factor = 0.5  # Reduced from 0.6 to maintain transparency
                    
                    # Mask for where paint exists
                    paint_mask = alpha > 0.05
                    existing_mask = paint_alpha_layer > 0.01
                    
                    # Case 1: New paint on existing paint (MIXING!)
                    mix_mask = paint_mask & existing_mask
                    if np.any(mix_mask):
                        # New paint alpha (scaled)
                        new_alpha = alpha[mix_mask] * blend_factor
                        old_alpha = paint_alpha_layer[mix_mask]
                        
                        # IMPORTANT: Use MAX instead of ADD to preserve transparency ⭐⭐⭐
                        # This prevents accumulation that makes everything opaque
                        final_alpha = np.maximum(old_alpha, new_alpha)
                        
                        # But still mix colors based on relative strengths
                        # Weight by alpha values
                        alpha_sum = old_alpha + new_alpha
                        old_weight = old_alpha / alpha_sum
                        new_weight = new_alpha / alpha_sum
                        
                        old_weight_3ch = np.expand_dims(old_weight, axis=1)
                        new_weight_3ch = np.expand_dims(new_weight, axis=1)
                        
                        # Weighted color mixing
                        mixed = (
                            paint_color_layer[mix_mask].astype(np.float32) * old_weight_3ch +
                            new_paint[mix_mask] * new_weight_3ch
                        )
                        
                        paint_color_layer[mix_mask] = np.clip(mixed, 0, 255).astype(np.uint8)
                        paint_alpha_layer[mix_mask] = np.clip(final_alpha, 0, 0.9)
                    
                    # Case 2: New paint on empty area (FIRST PAINT)
                    new_mask = paint_mask & ~existing_mask
                    if np.any(new_mask):
                        paint_color_layer[new_mask] = splat.color
                        paint_alpha_layer[new_mask] = alpha[new_mask]
            
            # Composite paint onto frame with PROPER ALPHA BLENDING ⭐⭐⭐
            if paint_alpha_layer.max() > 0:
                # Expand alpha for broadcasting
                alpha_3ch = np.expand_dims(paint_alpha_layer, axis=2)
                
                # Alpha blend: result = original * (1 - alpha) + paint * alpha
                result = (
                    result.astype(np.float32) * (1.0 - alpha_3ch) +
                    paint_color_layer.astype(np.float32) * alpha_3ch
                ).astype(np.uint8)
            
            # Layer 2: EXPLOSION SHOCKWAVES (OVER paint)
            for splat in splats:
                result = self.paint_system.draw_explosion_shockwave(result, splat, current_time)
            
            # Layer 3: Projectiles
            for proj in projectiles:
                result = self.paint_system.draw_projectile(result, proj, current_time)
            
            # Layer 4: EXPLOSION PARTICLES (with glow)
            for i, splat in enumerate(splats):
                result = self.paint_system.draw_particles(result, all_particles[i], splat.time, current_time)
            
            # Layer 5: SCREEN SHAKE
            for splat in splats:
                result = self.paint_system.draw_screen_shake(result, splat, current_time)
            
            # WRITE IMMEDIATELY - no memory accumulation ⭐⭐⭐
            out.write(result)
            frame_num += 1
            
            if frame_num % 30 == 0:
                logger.info(f"💥 Processed {frame_num}/{total_frames} frames")
        
        cap.release()
        out.release()
        logger.info(f"✅ EXPLOSION complete: {output_path}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test
    renderer = ExplosionPaintRenderer()
    renderer.process_video(
        './input.mp4',
        'output_explosion.mp4',
        num_splats=5
    )