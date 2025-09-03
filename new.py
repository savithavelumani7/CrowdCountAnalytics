import cv2
import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import json
from pathlib import Path

ZONE_FILE = "zones.json"

st.set_page_config(layout="wide")
st.title("Video Zone Dashboard")

# video_source = "sample2.mp4"  # change to 0 for webcam
# cap = cv2.VideoCapture(video_source)

uploaded_file = st.file_uploader("Upload a video", type=["mp4", "avi", "mov"])
if uploaded_file is not None:
    with open(rf'uploaded_file', "wb") as f:
        f.write(uploaded_file.read())
    cap = cv2.VideoCapture(uploaded_file.name)
else:
    st.warning("Please upload a video file.")
    st.stop()

ret, frame = cap.read()
if not ret:
    st.error("Could not load video")
    st.stop()

frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

# --- resize frame ---
def resize_frame(frame, max_width=640):
    h, w, _ = frame.shape
    scale = max_width / w
    new_w = int(w * scale)
    new_h = int(h * scale)
    resized = cv2.resize(frame, (new_w, new_h))
    return resized

frame = resize_frame(frame, max_width=640)

# Sidebar
mode = st.sidebar.radio("Mode", ["Draw Zones", "Preview Zones", "Delete Zones"])

# Load saved zones
zones = []
if Path(ZONE_FILE).exists():
    with open(ZONE_FILE, "r") as f:
        zones = json.load(f)

# Draw Zones
if mode == "Draw Zones":
    st.info("Draw rectangles on the video frame below 👇")

    canvas = st_canvas(
        fill_color="rgba(0, 255, 0, 0.3)",
        stroke_width=2,
        stroke_color="red",
        background_image=Image.fromarray(frame),
        update_streamlit=True,
        height=frame.shape[0],
        width=frame.shape[1],
        drawing_mode="rect",  # "polygon" also works
        key="canvas",
    )

    if canvas.json_data is not None:
        drawn_objects = canvas.json_data["objects"]

        zone_label = st.text_input("Enter label for this zone")

        if st.button("Save Zone"):
            if zone_label and drawn_objects:
                obj = drawn_objects[-1]   # ✅ save only latest
                zones.append({"label": zone_label, "shape": obj})
                with open(ZONE_FILE, "w") as f:
                    json.dump(zones, f)
                st.success(f"Zone '{zone_label}' saved!")
                st.experimental_rerun()   # ✅ refresh UI

# Preview Zones
elif mode == "Preview Zones":
    preview_frame = frame.copy()
    for zone in zones:
        obj = zone["shape"]
        label = zone["label"]

        if "left" in obj and "top" in obj and "width" in obj and "height" in obj:
            x1, y1 = int(obj["left"]), int(obj["top"])
            x2, y2 = x1 + int(obj["width"]), y1 + int(obj["height"])
            cv2.rectangle(preview_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                preview_frame, label, (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2
            )

    st.image(preview_frame, channels="RGB")

# Delete Zones
elif mode == "Delete Zones":
    if not zones:
        st.warning("No zones to delete.")
    else:
        zone_labels = [f"{i+1}. {z['label']}" for i, z in enumerate(zones)]
        choice = st.selectbox("Select a zone to delete", zone_labels)

        if st.button("Delete Selected Zone"):
            idx = zone_labels.index(choice)
            deleted_label = zones[idx]["label"]
            zones.pop(idx)
            with open(ZONE_FILE, "w") as f:
                json.dump(zones, f)
            st.success(f"Zone '{deleted_label}' deleted!")
            st.experimental_rerun()
