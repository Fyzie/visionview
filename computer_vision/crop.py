import cv2

PARAMETERS = {
    "mode": {
        "type": "enum", 
        "options": ["center", "dynamic"], 
        "default": "center"
    },
    "width": {
        "type": "int",
        "min": 1,
        "max": 4000,
        "default": 640
    },
    "height": {
        "type": "int",
        "min": 1,
        "max": 4000,
        "default": 480
    },
    "x_pos": {
        "type": "int",
        "min": 0,
        "max": 4000,
        "default": 0
    },
    "y_pos": {
        "type": "int",
        "min": 0,
        "max": 4000,
        "default": 0
    }
}

def process(frame, params=None):
    """
    Cropping Tool: Supports Center and Dynamic (XY) modes.
    Ensures output is always valid BGR or Grayscale.
    """
    if frame is None:
        return None

    if params is None:
        params = {}

    h, w = frame.shape[:2]
    
    mode = params.get("mode", PARAMETERS["mode"]["default"])
    cw = max(1, min(int(params.get("width", PARAMETERS["width"]["default"])), w))
    ch = max(1, min(int(params.get("height", PARAMETERS["height"]["default"])), h))

    if mode == "center":
        start_x = max(0, (w - cw) // 2)
        start_y = max(0, (h - ch) // 2)
    elif mode == "dynamic":
        start_x = int(params.get("x_pos", PARAMETERS["x_pos"]["default"]))
        start_y = int(params.get("y_pos", PARAMETERS["y_pos"]["default"]))

        max_x = max(0, w - cw)
        max_y = max(0, h - ch)
        start_x = max(0, min(start_x, max_x))
        start_y = max(0, min(start_y, max_y))
    else:
        return frame

    end_x = start_x + cw
    end_y = start_y + ch
    
    cropped = frame[start_y:end_y, start_x:end_x]

    if len(cropped.shape) == 2:
        cropped = cv2.cvtColor(cropped, cv2.COLOR_GRAY2BGR)

    return cropped