import cv2

PARAMETERS = {
    "low_thresh": {
        "type": "int",
        "min": 0,
        "max": 255,
        "default": 100,
        "step": 5
    },
    "high_thresh": {
        "type": "int",
        "min": 0,
        "max": 255,
        "default": 200,
        "step": 5
    }
}

def process(frame, params=None):
    """
    Canny Edge Detection Processing Module
    """
    if frame is None:
        return None

    if params is None:
        params = {}

    low = int(params.get("low_thresh", PARAMETERS["low_thresh"]["default"]))
    high = int(params.get("high_thresh", PARAMETERS["high_thresh"]["default"]))

    if len(frame.shape) == 3:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    else:
        gray = frame

    edges = cv2.Canny(gray, low, high)

    image = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

    return image