#!/usr/bin/env python3
"""
Simple example script to run the paint explosion effect
"""

from splatoon_paint_explosion import ExplosionPaintRenderer
import os

def main():
    # Initialize renderer
    renderer = ExplosionPaintRenderer()
    
    # Define paths
    input_video = './input.mp4'  # Change this to your input video path
    output_video = 'output_explosion.mp4'
    
    # Check if input exists
    if not os.path.exists(input_video):
        print(f"❌ Error: Input video '{input_video}' not found!")
        print(f"\n💡 Please:")
        print(f"   1. Place your video file in this directory")
        print(f"   2. Rename it to 'input.mp4', OR")
        print(f"   3. Update the 'input_video' variable in this script")
        return
    
    # Process video
    print(f"🎨 Processing video with paint explosions...")
    print(f"📹 Input: {input_video}")
    print(f"💾 Output: {output_video}")
    print(f"💥 Number of explosions: 4")
    print(f"\n⏳ This may take a few minutes depending on video length...")
    
    renderer.process_video(
        input_path=input_video,
        output_path=output_video,
        num_splats=4  # Adjust this for more/fewer explosions (recommended: 3-6)
    )
    
    print(f"\n✅ Done! Output saved to: {output_video}")

if __name__ == "__main__":
    main()
