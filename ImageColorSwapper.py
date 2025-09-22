import streamlit as st
from PIL import Image
import numpy as np
import io
import requests
from io import BytesIO

# --- Image processing function ---
def process_image(img, settings):
    img = img.convert("RGB")
    data = np.array(img, dtype=np.uint8)

    # Apply global darkening factor
    if settings["dark_factor"] < 1.0:
        data = (data.astype(np.float32) * settings["dark_factor"]).clip(0, 255).astype(np.uint8)

    hsv = None
    if settings["color_model"] == "HSV":
        hsv = np.array(img.convert("HSV"))
        h, s, v = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]

    # Luminance for white/black detection
    luminance = 0.299 * data[:, :, 0] + 0.587 * data[:, :, 1] + 0.114 * data[:, :, 2]

    for color, opts in settings["colors"].items():
        if not opts["use"]:
            continue

        if color in ["white", "black"]:
            if color == "white":
                mask = luminance > opts["threshold"]
            else:
                mask = luminance < opts["threshold"]
        else:
            if settings["color_model"] == "HSV" and hsv is not None:
                t = opts["threshold"]
                if color == "red":
                    mask = (((h >= t["h1"][0]) & (h <= t["h1"][1])) | ((h >= t["h2"][0]) & (h <= t["h2"][1]))) & \
                           ((s >= t["s"][0]) & (s <= t["s"][1])) & ((v >= t["v"][0]) & (v <= t["v"][1]))
                else:
                    mask = ((h >= t["h"][0]) & (h <= t["h"][1])) & \
                           ((s >= t["s"][0]) & (s <= t["s"][1])) & ((v >= t["v"][0]) & (v <= t["v"][1]))
            else:  # RGB thresholds
                r, g, b = data[:, :, 0], data[:, :, 1], data[:, :, 2]
                t = opts["threshold"]
                mask = ((r >= t["r"][0]) & (r <= t["r"][1])) & \
                       ((g >= t["g"][0]) & (g <= t["g"][1])) & \
                       ((b >= t["b"][0]) & (b <= t["b"][1]))

        data[mask] = opts["new_color"]

    return Image.fromarray(data)

# --- Streamlit UI ---
st.set_page_config(page_title="Image Color Swapper", layout="wide")
st.title("Image Color Swapper")

# File upload or default image
uploaded_file = st.file_uploader("Upload an Image", type=["png", "jpg", "jpeg", "bmp", "tiff", "gif"])
if uploaded_file:
    img = Image.open(uploaded_file)
else:
    try:
        url = "https://raw.githubusercontent.com/Jakub-Laska/Image-color-swapper/refs/heads/main/colorSwapperPlaceholder.png"
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
    except Exception:
        img = Image.new("RGB", (600, 400), "white")

# Resize large images
max_width = 1200
if img.width > max_width:
    ratio = max_width / img.width
    img = img.resize((max_width, int(img.height * ratio)))

# --- Sidebar ---
with st.sidebar:
    st.header("Settings")    
    dark_factor = st.slider("Darkening Factor", 0.1, 1.0, 1.0)
    color_model = st.selectbox("Color Model", ("HSV", "RGB"))
    st.subheader("Color Adjustments")

    color_defs = {
        "white": {"default": "#2A2A2A", "threshold": (240,), "is_bw": True},
        "black": {"default": "#FFFFFF", "threshold": (15,), "is_bw": True},
        "yellow": {"default": "#FFFF99"},
        "red": {"default": "#FF6666"},
        "green": {"default": "#66FF66"},
        "blue": {"default": "#6666FF"},
    }

    colors = {}
    for cname, cdef in color_defs.items():
        with st.expander(f"{cname.capitalize()} Options"):
            use = st.checkbox(f"Enable {cname.capitalize()} Swap", value=(cname in ["white", "black"]))
            if not use:
                colors[cname] = {"use": False}
                continue

            if cname in ["white", "black"]:
                threshold = st.slider(f"{cname.capitalize()} Threshold", 0, 255, cdef["threshold"][0])
                new_hex = st.color_picker(f"Replacement Color for {cname}", cdef["default"])
                new_rgb = tuple(int(new_hex.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))
                colors[cname] = {"use": True, "threshold": threshold, "new_color": new_rgb}
            else:
                st.write(f"Thresholds for {cname} ({color_model}):")
                if color_model == "HSV":
                    if cname == "red":
                        h1 = st.slider("Hue Range 1", 0, 255, (0, 10))
                        h2 = st.slider("Hue Range 2", 0, 255, (245, 255))
                        s = st.slider("Saturation Range", 0, 255, (100, 255))
                        v = st.slider("Value (Brightness) Range", 0, 255, (100, 255))
                        threshold = {"h1": h1, "h2": h2, "s": s, "v": v}
                    else:
                        defaults = {"yellow": (25, 45), "green": (60, 100), "blue": (140, 180)}
                        h = st.slider("Hue Range", 0, 255, defaults.get(cname, (0, 255)))
                        s = st.slider("Saturation Range", 0, 255, (100, 255))
                        v = st.slider("Value (Brightness) Range", 0, 255, (100, 255))
                        threshold = {"h": h, "s": s, "v": v}
                else:
                    defaults = {
                        "red": {"r": (150, 255), "g": (0, 100), "b": (0, 100)},
                        "yellow": {"r": (200, 255), "g": (200, 255), "b": (0, 100)},
                        "green": {"r": (0, 100), "g": (150, 255), "b": (0, 100)},
                        "blue": {"r": (0, 100), "g": (0, 100), "b": (150, 255)},
                    }
                    d = defaults.get(cname, {"r": (0, 255), "g": (0, 255), "b": (0, 255)})
                    r = st.slider("Red Range", 0, 255, d["r"])
                    g = st.slider("Green Range", 0, 255, d["g"])
                    b = st.slider("Blue Range", 0, 255, d["b"])
                    threshold = {"r": r, "g": g, "b": b}

                new_hex = st.color_picker(f"Replacement Color for {cname}", cdef["default"])
                new_rgb = tuple(int(new_hex.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))
                colors[cname] = {"use": True, "threshold": threshold, "new_color": new_rgb}

# --- Process image ---
settings = {"dark_factor": dark_factor, "color_model": color_model, "colors": colors}

try:
    col1, col2 = st.columns(2)
    col1.image(img, caption="Original Image", use_container_width=True)

    processed_img = process_image(img, settings)
    col2.image(processed_img, caption="Processed Image", use_container_width=True)

    buf = io.BytesIO()
    processed_img.save(buf, format="PNG")
    st.download_button("Download Processed Image", data=buf.getvalue(), file_name="processed.png", mime="image/png")

except Exception as e:
    st.error(f"Processing error: {e}")
    st.stop()
