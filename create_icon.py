#!/usr/bin/env python3
"""Generate ROM Downloader icon for macOS app."""

try:
    from PIL import Image, ImageDraw, ImageFont
    import os

    # Create a colorful icon with game/ROM theme
    sizes = [16, 32, 64, 128, 256, 512, 1024]
    icon_dir = "ROM Downloader.app/Contents/Resources"
    os.makedirs(icon_dir, exist_ok=True)

    # Base colors: retro gaming palette
    bg_color = (25, 25, 50)  # Dark blue (like classic consoles)
    accent_color = (255, 100, 0)  # Retro orange/red
    highlight_color = (0, 255, 150)  # Neon green

    # Create icns file (macOS requires this format)
    # For now, create a simple PNG that macOS can convert
    for size in sizes:
        img = Image.new('RGB', (size, size), bg_color)
        draw = ImageDraw.Draw(img)

        # Draw a stylized cartridge/ROM shape
        margin = int(size * 0.15)

        # Main cartridge body
        draw.rectangle(
            [margin, margin + int(size*0.1), size - margin, size - margin - int(size*0.1)],
            fill=accent_color,
            outline=highlight_color,
            width=int(size * 0.05) or 1
        )

        # Label area (like on cartridges)
        label_top = margin + int(size * 0.15)
        label_height = int(size * 0.2)
        draw.rectangle(
            [margin + int(size*0.05), label_top, size - margin - int(size*0.05), label_top + label_height],
            fill=highlight_color
        )

        # Gold contacts at bottom
        contact_y = size - margin - int(size * 0.08)
        contact_spacing = int(size * 0.08)
        num_contacts = 4
        start_x = int((size - (num_contacts - 1) * contact_spacing) / 2)

        for i in range(num_contacts):
            x = start_x + i * contact_spacing
            draw.rectangle(
                [x - int(size*0.03), contact_y, x + int(size*0.03), contact_y + int(size*0.06)],
                fill=(200, 170, 0)  # Gold
            )

        # Save as PNG (will convert to icns separately)
        img.save(f"{icon_dir}/AppIcon_{size}.png")

    print("✅ Icon assets created successfully")
    print(f"   16x16, 32x32, 64x64, 128x128, 256x256, 512x512, 1024x1024 PNGs")
    print(f"   Location: {icon_dir}")

except ImportError:
    print("⚠️  PIL/Pillow not found. Creating placeholder icon...")
    print("   Install with: pip install Pillow")
    # Create a minimal placeholder
    os.makedirs("ROM Downloader.app/Contents/Resources", exist_ok=True)
