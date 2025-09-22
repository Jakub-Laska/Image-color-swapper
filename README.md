# Image Color Swapper

A Streamlit-based web app that lets you **upload an image, adjust brightness, and selectively swap colors** using either the **HSV** or **RGB** color models.  
This tool is useful for experimenting with image recoloring, creating dark-mode variations, or testing color replacements.

---

## Features

- **Upload any image** (PNG, JPG, BMP, TIFF, GIF supported).
- **Default image loads automatically** if no upload is provided.
- **Darkening factor** to adjust overall brightness (0.1 = very dark, 1.0 = no change).
- **Two color models available**:
  - **HSV (Hue, Saturation, Value)** – intuitive for adjusting tones and brightness.
  - **RGB (Red, Green, Blue)** – precise per-channel thresholds.
- **Customizable color swaps**:
  - White / Black (based on luminance thresholds).
  - Yellow, Red, Green, Blue (with adjustable thresholds).
- **Pick replacement colors** using a color picker.
- **Live preview** of original vs. processed image.
- **One-click download** of the processed image.

---

## How to Use

1. **Upload Image**  
   - Click *Upload* or drag & drop your file.  
   - If none is uploaded, a default placeholder image will be used.

2. **Adjust Settings (Sidebar)**  
   - **Darkening Factor**: Control overall brightness (0.1–1.0).  
   - **Color Model**: Choose between HSV or RGB.  
   - **Color Options**: Expand each color block to enable/disable swapping, set thresholds, and pick replacement colors.

3. **Preview & Download**  
   - See the original and processed images side by side.  
   - Click *Download Processed Image* to save the result.

---
