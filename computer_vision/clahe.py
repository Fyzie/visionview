import cv2

PARAMETERS = {
    "clipLimit": {
        "type": "float",
        "min": 0.0,
        "max": 40.0,
        "default": 2.0,
        "step": 0.1,
        "decimals": 1
    },
    "grid_size": {
        "type": "int",
        "min": 1,
        "max": 64,
        "default": 8,
        "step": 1
    }
}

def process(frame, params=None):
    """
    CLAHE (Contrast Limited Adaptive Histogram Equalization)
    Works on Grayscale or Color (via LAB space)
    """
    if frame is None:
        return None

    if params is None:
        params = {}

    clip_limit = max(0.1, float(params.get("clipLimit", PARAMETERS["clipLimit"]["default"])))
    grid_val = max(1, int(params.get("grid_size", PARAMETERS["grid_size"]["default"])))
    tile_grid_size = (grid_val, grid_val)

    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)

    if len(frame.shape) == 2:
        processed = clahe.apply(frame)
        return cv2.cvtColor(processed, cv2.COLOR_GRAY2BGR)
    
    else:
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)

        l_clahe = clahe.apply(l)
        lab_clahe = cv2.merge((l_clahe, a, b))
        
        return cv2.cvtColor(lab_clahe, cv2.COLOR_LAB2BGR)