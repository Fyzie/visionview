"""
List available adjustable parameters on the camera accordingly hera
"""
BASLER_PARAMETERS = {
    "pixel format": {
        "type": "enum",
        "options": ["BayerGB8","BayerGB10","BayerGB10p","BayerGB12","BayerGB12p",
                    "Mono8","Mono10","Mono10p","Mono12","Mono12p"],
        "default": "BayerGB8"
    },

    "exposure": {
        "type": "int",
        "min": 100,
        "max": 100000,
        "default": 5000
    },

    "gain": {
        "type": "int",
        "min": 0,
        "max": 10,
        "default": 0
    },

    "contrast": {
        "type": "float",
        "min": -1,
        "max": 1,
        "step": 0.1,
        "default": 0.0
    },

    "hue": {
        "type": "int",
        "min": -180,
        "max": 180,
        "default": 0
    },

    "saturation": {
        "type": "float",
        "min": 0,
        "max": 2,
        "step": 0.1,
        "default": 1.0
    },

    "brightness": {
        "type": "float",
        "min": -1,
        "max": 1,
        "step": 0.1,
        "default": 0.0
    },

    "reversex": {
        "type": "bool",
        "default": False
    },

    "reversey": {
        "type": "bool",
        "default": False
    }
}