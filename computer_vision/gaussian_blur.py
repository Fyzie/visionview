import cv2

PARAMETERS = {
    "ksize": {
        "type": "int",
        "min": 1,
        "max": 99,
        "default": 5,
        "step": 2
    },
    "sigma": {
        "type": "float",
        "min": 0.0,
        "max": 10.0,
        "default": 0.0,
        "step": 0.1,
        "decimals": 1
    }
}

def process(frame, params=None):
    """
    Gaussian Blur Processing Module
    """
    if frame is None:
        return None

    if params is None:
        params = {}

    # Kernel size (must be positive odd)
    ksize = int(params.get("ksize",  PARAMETERS["ksize"]["default"]))
    if ksize < 1:
        ksize = 1
    if ksize % 2 == 0:
        ksize += 1

    sigma = float(params.get("sigma", PARAMETERS["sigma"]["default"]))

    if len(frame.shape) == 2:
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

    blurred = cv2.GaussianBlur(frame, (ksize, ksize), sigma)

    return blurred