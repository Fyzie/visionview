import cv2

PARAMETERS = {
    "mode": {
        "type": "enum",
        "options": ["percentage", "fixed"],
        "default": "percentage"
    },
    "scale": {
        "type": "float",
        "min": 0.1,
        "max": 2.0,
        "default": 1.0,
        "step": 0.1
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
    "interpolation": {
        "type": "enum",
        "options": ["linear", "nearest", "cubic"],
        "default": "linear"
    }
}

def process(frame, params=None):
    """
    Resize Tool: Supports scaling by percentage or fixed pixel dimensions.
    """
    if frame is None:
        return None

    if params is None:
        params = {}

    h, w = frame.shape[:2]
    
    interp_map = {
        "linear": cv2.INTER_LINEAR,
        "nearest": cv2.INTER_NEAREST,
        "cubic": cv2.INTER_CUBIC
    }
    interp = interp_map.get(params.get("interpolation", "linear"), cv2.INTER_LINEAR)

    mode = params.get("mode", PARAMETERS["mode"]["default"])
    
    if mode == "percentage":
        scale = float(params.get("scale", PARAMETERS["scale"]["default"]))
        new_w = int(w * scale)
        new_h = int(h * scale)
    else:
        new_w = int(params.get("width", PARAMETERS["width"]["default"]))
        new_h = int(params.get("height", PARAMETERS["height"]["default"]))

    new_w = max(1, new_w)
    new_h = max(1, new_h)

    resized = cv2.resize(frame, (new_w, new_h), interpolation=interp)

    if len(resized.shape) == 2:
        resized = cv2.cvtColor(resized, cv2.COLOR_GRAY2BGR)

    return resized