import cv2

PARAMETERS = {
    "thresh": {"type": "int", "min": 0, "max": 255, "default": 20},
    "maxval": {"type": "int", "min": 0, "max": 255, "default": 255}
}

def process(frame, params=None):
    """
    Threshold Processing Module
    """
    if frame is None:
        return None

    if params is None:
        params = {}

    threshold_value = int(params.get("thresh", PARAMETERS["thresh"]["default"]))
    max_value = int(params.get("maxval", PARAMETERS["maxval"]["default"]))

    if len(frame.shape) == 3:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    else:
        gray = frame

    _, binary = cv2.threshold(
        gray,
        threshold_value,
        max_value,
        cv2.THRESH_BINARY
    )

    return cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)