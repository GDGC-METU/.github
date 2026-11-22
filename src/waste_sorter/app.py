"""Webcam classification and optional Arduino command sender."""
import argparse
import time
from collections import deque
from pathlib import Path

import cv2
from PIL import Image

from .classifier import WasteClassifier, classify_with_threshold
from .serial_protocol import UnoConnection


def run(model_path: Path, camera_index: int, threshold: float, port: str | None,
        dry_run: bool, stable_frames: int = 3):
    classifier = WasteClassifier(model_path)
    connection = None
    if port:
        connection = UnoConnection(port)
        if not connection.wait_ready():
            connection.close()
            raise RuntimeError("Arduino did not report READY; check sketch, cable, port, and baud rate.")
    camera = cv2.VideoCapture(camera_index)
    if not camera.isOpened():
        if connection:
            connection.close()
        raise RuntimeError(f"Could not open camera {camera_index}")
    history = deque(maxlen=stable_frames)
    last_sent = None
    try:
        while True:
            ok, frame = camera.read()
            if not ok:
                raise RuntimeError("Camera frame could not be read")
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            label, confidence = classify_with_threshold(classifier, Image.fromarray(rgb), threshold)
            history.append(label)
            stable = label if len(history) == stable_frames and len(set(history)) == 1 else None
            shown = label.upper() if label != "unknown" else "UNKNOWN"
            cv2.putText(frame, f"{shown}  {confidence:.0%}", (18, 36), cv2.FONT_HERSHEY_SIMPLEX,
                        0.9, (30, 220, 30) if stable else (20, 180, 240), 2)
            cv2.imshow("Waste sorter - q to quit", frame)
            if stable and stable != last_sent:
                if connection and not dry_run:
                    connection.send(stable)
                print(f"decision={stable.upper()} confidence={confidence:.3f}"
                      f" mode={'dry-run' if dry_run or not connection else 'serial'}")
                last_sent = stable
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
            time.sleep(0.01)
    finally:
        camera.release()
        cv2.destroyAllWindows()
        if connection:
            connection.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, default=Path("models/waste_sorter.pth"))
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--threshold", type=float, default=0.70)
    parser.add_argument("--port", help="Arduino serial port, e.g. COM3")
    parser.add_argument("--dry-run", action="store_true", help="Never send commands")
    args = parser.parse_args()
    if not 0.0 <= args.threshold <= 1.0:
        parser.error("--threshold must be between 0 and 1")
    run(args.model, args.camera, args.threshold, args.port, args.dry_run)


if __name__ == "__main__":
    main()
