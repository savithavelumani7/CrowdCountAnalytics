# import cv2
# from ultralytics import YOLO

# # Load model
# model = YOLO("yolov8s.pt")

# # Load video
# video_path = r"E:\crowd\crowd_count\uploaded.mp4"
# cap = cv2.VideoCapture(video_path)

# # Define one rectangular zone (x1, y1, x2, y2)
# zone = (750, 750, 1500, 1500) # change values as needed

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break

#     results = model(frame, stream=True)
#     zone_count = 0

#     # Draw the zone
#     cv2.rectangle(frame, (zone[0], zone[1]), (zone[2], zone[3]), (255, 0, 0), 2)
#     cv2.putText(frame, "Zone", (zone[0], zone[1] - 10),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 5)

#     for result in results:
#         for box in result.boxes:
#             cls_id = int(box.cls[0])
#             if model.names[cls_id] == "person":
#                 x1, y1, x2, y2 = map(int, box.xyxy[0])
#                 cx, cy = int((x1 + x2) / 2), int((y1 + y2) / 2)

#                 # Draw bounding box
#                 cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
#                 cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)

#                 # Count if person center is inside the zone
#                 if zone[0] < cx < zone[2] and zone[1] < cy < zone[3]:
#                     zone_count += 1

#     # Show count
#     cv2.putText(frame, f"People in Zone: {zone_count}", (20, 40),
#                 cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
#     display_frame = cv2.resize(frame, (1280, 720))
#     cv2.imshow("People Counting with Zone", display_frame)

#     if cv2.waitKey(1) & 0xFF == ord("q"):
#         break

# cap.release()
# cv2.destroyAllWindows()



import cv2
import json
from ultralytics import YOLO

# Load model
model = YOLO("yolov8s.pt")

# Load video
video_path = r"E:\crowd\crowd_count\uploaded.mp4"
cap = cv2.VideoCapture(video_path)

zones = []  # store drawn zones (x1, y1, x2, y2)
drawing = False
ix, iy = -1, -1

def draw_zone(event, x, y, flags, param):
    global ix, iy, drawing, zones
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        zones.append((ix, iy, x, y))

# Window and callback
cv2.namedWindow("Draw Zones")
cv2.setMouseCallback("Draw Zones", draw_zone)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # ✅ Resize before drawing and detection
    frame = cv2.resize(frame, (1280, 720))

    # Draw existing zones
    for (x1, y1, x2, y2) in zones:
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
        cv2.putText(frame, "Zone", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

    results = model(frame, stream=True)
    zone_count = [0] * len(zones)

    for result in results:
        for box in result.boxes:
            cls_id = int(box.cls[0])
            if model.names[cls_id] == "person":
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cx, cy = int((x1 + x2) / 2), int((y1 + y2) / 2)

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)

                for i, (zx1, zy1, zx2, zy2) in enumerate(zones):
                    if zx1 < cx < zx2 and zy1 < cy < zy2:
                        zone_count[i] += 1

    for i, (x1, y1, _, _) in enumerate(zones):
        cv2.putText(frame, f"Count: {zone_count[i]}", (x1, y1 + 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    cv2.imshow("Draw Zones", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

# Save drawn zones as JSON
with open("zones.json", "w") as f:
    json.dump(zones, f, indent=4)

print(f"Saved {len(zones)} zones to zones.json")

cap.release()
cv2.destroyAllWindows()
