"""
Paint Bubble Rain Effect System
Bubbles fall from top, spread on impact, then disappear

Concept:
- Colorful bubbles fall from sky
- Land on screen/objects
- Spread like liquid on impact
- Fade away over time
"""

import cv2
import numpy as np
from typing import List, Tuple
from dataclasses import dataclass
import random
import logging

logger = logging.getLogger(__name__)


@dataclass
class Bubble:
    """Single falling bubble"""
    start_time: float           # When bubble appears
    start_pos: Tuple[int, int]  # Starting position (top of screen)
    color: Tuple[int, int, int] # BGR color
    size: int                   # Bubble radius
    fall_speed: float           # Falling speed (pixels per second)
    impact_time: float          # When it hits ground
    impact_pos: Tuple[int, int] # Where it lands
    seed: int                   # Random seed for splash pattern


class BubbleRainSystem:
    """
    Bubble rain effect system
    Bubbles fall from top and create paint splashes
    """
    
    def __init__(self, video_width: int, video_height: int):
        self.width = video_width
        self.height = video_height
        
        # Color palette (12 colors - BGR format)
        self.colors = [
            (147, 20, 255),   # Hot Pink
            (0, 255, 255),    # Yellow
            (255, 0, 0),      # Blue
            (0, 165, 255),    # Orange
            (219, 112, 147),  # Purple
            (127, 255, 0),    # Spring Green
            (255, 0, 255),    # Magenta
            (255, 255, 0),    # Cyan
            (0, 255, 0),      # Green
            (0, 0, 255),      # Red
            (180, 105, 255),  # Light Hot Pink
            (203, 192, 255),  # Light Pink
        ]
        
        logger.info(f"Bubble rain system initialized: {video_width}x{video_height}")
    
    def generate_bubbles(
        self,
        duration: float,
        num_bubbles: int = 15
    ) -> List[Bubble]:
        """
        Generate falling bubbles
        
        Args:
            duration: Video duration in seconds
            num_bubbles: Number of bubbles to generate
        
        Returns:
            List of bubbles
        """
        bubbles = []
        
        # Distribute bubbles over time
        for i in range(num_bubbles):
            # Timing - spread throughout video
            start_time = (duration / (num_bubbles + 1)) * (i + 1)
            start_time += random.uniform(-0.3, 0.3)
            start_time = max(0, min(duration - 2.0, start_time))
            
            # Starting position (top of screen, random X)
            start_x = random.randint(50, self.width - 50)
            start_y = -100  # Above screen
            
            # Bubble size
            size = random.randint(40, 80)
            
            # Fall speed (slower = more visible)
            fall_speed = random.uniform(300, 500)  # pixels/second
            
            # Calculate impact time and position
            fall_distance = self.height + 100  # From -100 to bottom
            fall_duration = fall_distance / fall_speed
            impact_time = start_time + fall_duration
            
            # Impact position (where it lands)
            impact_x = start_x + random.randint(-50, 50)  # Slight drift
            impact_y = self.height - 50  # Near bottom
            
            # Color
            color = random.choice(self.colors)
            
            # Random seed for splash pattern
            seed = random.randint(0, 999999)
            
            bubble = Bubble(
                start_time=start_time,
                start_pos=(start_x, start_y),
                color=color,
                size=size,
                fall_speed=fall_speed,
                impact_time=impact_time,
                impact_pos=(impact_x, impact_y),
                seed=seed
            )
            bubbles.append(bubble)
        
        logger.info(f"Generated {len(bubbles)} bubbles")
        return bubbles
    
    def get_bubble_position(
        self,
        bubble: Bubble,
        current_time: float
    ) -> Tuple[int, int, float]:
        """
        Get current bubble position and phase
        
        Returns:
            (x, y, phase) where phase:
            - 0.0 = falling
            - 1.0 = just impacted
            - 2.0 = spreading
            - 3.0 = fading
        """
        if current_time < bubble.start_time:
            return (bubble.start_pos[0], bubble.start_pos[1], -1.0)
        
        time_since_start = current_time - bubble.start_time
        time_since_impact = current_time - bubble.impact_time
        
        # Phase 1: Falling
        if current_time < bubble.impact_time:
            progress = time_since_start / (bubble.impact_time - bubble.start_time)
            x = int(bubble.start_pos[0] + (bubble.impact_pos[0] - bubble.start_pos[0]) * progress)
            y = int(bubble.start_pos[1] + bubble.fall_speed * time_since_start)
            return (x, y, 0.0)
        
        # Phase 2-4: After impact (spread and fade)
        # 0.0-0.3s: Impact splash
        # 0.3-1.5s: Spreading
        # 1.5-3.0s: Fading
        
        if time_since_impact < 0.3:
            return (bubble.impact_pos[0], bubble.impact_pos[1], 1.0)
        elif time_since_impact < 1.5:
            return (bubble.impact_pos[0], bubble.impact_pos[1], 2.0)
        elif time_since_impact < 3.0:
            return (bubble.impact_pos[0], bubble.impact_pos[1], 3.0)
        else:
            return (bubble.impact_pos[0], bubble.impact_pos[1], 4.0)  # Disappeared
    
    def draw_falling_bubble(
        self,
        frame: np.ndarray,
        bubble: Bubble,
        pos: Tuple[int, int]
    ) -> np.ndarray:
        """Draw falling bubble (before impact)"""
        overlay = frame.copy()
        
        # Bubble body (semi-transparent)
        cv2.circle(overlay, pos, bubble.size, bubble.color, -1)
        
        # Shine/highlight
        highlight_offset = bubble.size // 3
        highlight_pos = (pos[0] - highlight_offset, pos[1] - highlight_offset)
        highlight_size = bubble.size // 2
        
        if 0 <= highlight_pos[0] < self.width and 0 <= highlight_pos[1] < self.height:
            cv2.circle(overlay, highlight_pos, highlight_size, (255, 255, 255), -1)
        
        # Blend with transparency
        frame = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)
        
        return frame
    
    def create_splash_mask(
        self,
        bubble: Bubble,
        time_since_impact: float
    ) -> np.ndarray:
        """
        Create SPECTACULAR splash/spread mask after bubble impacts
        
        Args:
            bubble: The bubble
            time_since_impact: Time since impact
        
        Returns:
            Mask (H x W), 0-255
        """
        mask = np.zeros((self.height, self.width), dtype=np.float32)
        
        np.random.seed(bubble.seed)
        
        # MUCH BIGGER SPREAD! ⭐⭐⭐
        if time_since_impact < 0.3:
            # Impact splash - EXPLOSIVE!
            spread_factor = 1.0 + time_since_impact * 8  # Was 3, now 8! Faster spread!
        elif time_since_impact < 1.5:
            # Spreading phase - LARGER!
            progress = (time_since_impact - 0.3) / 1.2
            spread_factor = 2.4 + progress * 3.0  # Was 1.9->3.4, now 2.4->5.4! Much bigger!
        else:
            # Max spread - HUGE!
            spread_factor = 5.4  # Was 3.4, now 5.4!
        
        # BIGGER center splash ⭐⭐⭐
        center_radius = int(bubble.size * spread_factor * 0.8)  # Was 0.6, now 0.8!
        cv2.circle(mask, bubble.impact_pos, center_radius, 0.9, -1)
        
        # MORE radiating splashes ⭐⭐⭐
        num_splashes = random.randint(30, 50)  # Was 15-25, now 30-50! Double!
        for _ in range(num_splashes):
            angle = random.uniform(0, 2 * np.pi)
            distance = bubble.size * spread_factor * random.uniform(0.8, 2.0)  # Was 1.5, now 2.0! Farther!
            
            splash_x = int(bubble.impact_pos[0] + distance * np.cos(angle))
            splash_y = int(bubble.impact_pos[1] + distance * np.sin(angle))
            splash_size = int(bubble.size * random.uniform(0.3, 0.7))  # Was 0.2-0.5, now bigger!
            
            intensity = random.uniform(0.6, 0.9)  # Was 0.5-0.8, now brighter!
            cv2.circle(mask, (splash_x, splash_y), splash_size, intensity, -1)
        
        # MANY MORE droplets ⭐⭐⭐
        num_droplets = random.randint(60, 100)  # Was 20-40, now 60-100! Triple!
        for _ in range(num_droplets):
            angle = random.uniform(0, 2 * np.pi)
            distance = bubble.size * spread_factor * random.uniform(1.5, 3.5)  # Was 2.5, now 3.5! Much farther!
            
            drop_x = int(bubble.impact_pos[0] + distance * np.cos(angle))
            drop_y = int(bubble.impact_pos[1] + distance * np.sin(angle))
            drop_size = int(bubble.size * random.uniform(0.08, 0.25))  # Was 0.05-0.15, now bigger!
            
            if 0 <= drop_x < self.width and 0 <= drop_y < self.height:
                intensity = random.uniform(0.4, 0.7)  # Was 0.3-0.6, now brighter!
                cv2.circle(mask, (drop_x, drop_y), drop_size, intensity, -1)
        
        # ADD SPLASH RAYS! ⭐⭐⭐ NEW!
        num_rays = random.randint(12, 20)
        for i in range(num_rays):
            angle = (2 * np.pi * i / num_rays) + random.uniform(-0.3, 0.3)
            
            # Ray extends from center outward
            ray_length = bubble.size * spread_factor * random.uniform(1.5, 2.5)
            ray_thickness = int(bubble.size * 0.15)
            
            end_x = int(bubble.impact_pos[0] + ray_length * np.cos(angle))
            end_y = int(bubble.impact_pos[1] + ray_length * np.sin(angle))
            
            # Draw ray with gradient
            for seg in range(10):
                seg_progress = seg / 10.0
                seg_x = int(bubble.impact_pos[0] + ray_length * seg_progress * np.cos(angle))
                seg_y = int(bubble.impact_pos[1] + ray_length * seg_progress * np.sin(angle))
                seg_size = int(ray_thickness * (1.0 - seg_progress * 0.5))
                seg_intensity = 0.7 * (1.0 - seg_progress)
                
                if 0 <= seg_x < self.width and 0 <= seg_y < self.height:
                    cv2.circle(mask, (seg_x, seg_y), seg_size, seg_intensity, -1)
        
        # Fade based on time
        if time_since_impact > 1.5:
            fade_progress = (time_since_impact - 1.5) / 1.5  # 0 to 1
            mask *= (1.0 - fade_progress)
        
        # Smooth
        mask = cv2.GaussianBlur(mask, (9, 9), 2.0)  # Was (7,7) 1.5, now bigger blur!
        
        return (mask * 255).astype(np.uint8)


class BubbleRainRenderer:
    """
    Renderer for bubble rain effect
    """
    
    def __init__(self):
        self.bubble_system = None
    
    def process_video(
        self,
        input_path: str,
        output_path: str,
        num_bubbles: int = 15
    ):
        """
        Process video with bubble rain effect
        
        Args:
            input_path: Input video path
            output_path: Output video path
            num_bubbles: Number of bubbles (recommended: 10-20)
        """
        logger.info(f"🫧 BUBBLE RAIN - Processing {input_path}")
        
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
        self.bubble_system = BubbleRainSystem(width, height)
        
        # Generate bubbles
        bubbles = self.bubble_system.generate_bubbles(duration, num_bubbles)
        
        # Pre-generate all splash masks (for impacted bubbles)
        splash_masks = {}
        
        # Streaming write
        logger.info("Starting streaming video write...")
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        if not out.isOpened():
            raise ValueError(f"Cannot open output video: {output_path}")
        
        # Process frames
        frame_num = 0
        
        # Paint accumulation layers
        paint_color_layer = np.zeros((height, width, 3), dtype=np.uint8)
        paint_alpha_layer = np.zeros((height, width), dtype=np.float32)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            current_time = frame_num / fps
            
            # Start with original
            result = frame.copy()
            
            # Update paint layer from impacted bubbles
            for bubble in bubbles:
                pos_x, pos_y, phase = self.bubble_system.get_bubble_position(bubble, current_time)
                
                # If bubble has impacted, add to paint layer
                if phase >= 1.0 and phase < 4.0:
                    time_since_impact = current_time - bubble.impact_time
                    
                    # Create or get splash mask
                    mask_key = (bubble.seed, int(time_since_impact * 10))
                    if mask_key not in splash_masks:
                        splash_masks[mask_key] = self.bubble_system.create_splash_mask(
                            bubble, time_since_impact
                        )
                    
                    mask = splash_masks[mask_key]
                    alpha = mask.astype(np.float32) / 255.0
                    
                    # Mix colors (same as explosion system)
                    bubble_color_bgr = np.array(bubble.color, dtype=np.float32)
                    new_paint = np.ones((height, width, 3), dtype=np.float32) * bubble_color_bgr
                    
                    blend_factor = 0.5
                    
                    paint_mask = alpha > 0.05
                    existing_mask = paint_alpha_layer > 0.01
                    
                    # Mix where overlapping
                    mix_mask = paint_mask & existing_mask
                    if np.any(mix_mask):
                        new_alpha = alpha[mix_mask] * blend_factor
                        old_alpha = paint_alpha_layer[mix_mask]
                        
                        final_alpha = np.maximum(old_alpha, new_alpha)
                        
                        alpha_sum = old_alpha + new_alpha
                        old_weight = old_alpha / alpha_sum
                        new_weight = new_alpha / alpha_sum
                        
                        old_weight_3ch = np.expand_dims(old_weight, axis=1)
                        new_weight_3ch = np.expand_dims(new_weight, axis=1)
                        
                        mixed = (
                            paint_color_layer[mix_mask].astype(np.float32) * old_weight_3ch +
                            new_paint[mix_mask] * new_weight_3ch
                        )
                        
                        paint_color_layer[mix_mask] = np.clip(mixed, 0, 255).astype(np.uint8)
                        paint_alpha_layer[mix_mask] = np.clip(final_alpha, 0, 0.9)
                    
                    # New paint on empty area
                    new_mask = paint_mask & ~existing_mask
                    if np.any(new_mask):
                        paint_color_layer[new_mask] = bubble.color
                        paint_alpha_layer[new_mask] = alpha[new_mask]
            
            # Composite paint onto frame
            if paint_alpha_layer.max() > 0:
                alpha_3ch = np.expand_dims(paint_alpha_layer, axis=2)
                result = (
                    result.astype(np.float32) * (1.0 - alpha_3ch) +
                    paint_color_layer.astype(np.float32) * alpha_3ch
                ).astype(np.uint8)
            
            # Draw falling bubbles (on top of paint)
            for bubble in bubbles:
                pos_x, pos_y, phase = self.bubble_system.get_bubble_position(bubble, current_time)
                
                # Only draw if falling (phase 0)
                if phase == 0.0:
                    if 0 <= pos_y < height:  # Only if visible
                        result = self.bubble_system.draw_falling_bubble(result, bubble, (pos_x, pos_y))
                
                # IMPACT FLASH! ⭐⭐⭐ NEW!
                elif phase == 1.0:
                    # Just impacted - draw bright flash
                    time_since_impact = current_time - bubble.impact_time
                    if time_since_impact < 0.15:  # Very brief flash
                        flash_progress = time_since_impact / 0.15
                        flash_intensity = 1.0 - flash_progress
                        
                        # White flash at impact point
                        flash_size = int(bubble.size * 2.0 * (1.0 + flash_progress))
                        overlay = result.copy()
                        cv2.circle(overlay, bubble.impact_pos, flash_size, (255, 255, 255), -1)
                        
                        # Radial rays
                        num_rays = 16
                        for i in range(num_rays):
                            angle = 2 * np.pi * i / num_rays
                            ray_length = bubble.size * 3 * (1.0 + flash_progress)
                            end_x = int(bubble.impact_pos[0] + ray_length * np.cos(angle))
                            end_y = int(bubble.impact_pos[1] + ray_length * np.sin(angle))
                            cv2.line(overlay, bubble.impact_pos, (end_x, end_y), 
                                   (255, 255, 255), int(bubble.size * 0.3))
                        
                        # Blend flash
                        result = cv2.addWeighted(overlay, flash_intensity * 0.6, result, 1.0 - flash_intensity * 0.6, 0)
            
            # Write frame immediately
            out.write(result)
            frame_num += 1
            
            if frame_num % 30 == 0:
                logger.info(f"🫧 Processed {frame_num}/{total_frames} frames")
        
        cap.release()
        out.release()
        logger.info(f"✅ BUBBLE RAIN complete: {output_path}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test
    renderer = BubbleRainRenderer()
    renderer.process_video(
        './input.mp4',
        'output_bubble_rain.mp4',
        num_bubbles=15
    )
