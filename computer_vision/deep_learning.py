import cv2
import importlib
import os
from pathlib import Path

_MODEL_CACHE = {}

PARAMETERS = {
    "model_script": {
        "type": "ai_modules", 
        "options": ["None"],
        "default": "rfdetr_inference"
    },
    "model_dir": {
        "type": "dir",
        "default": ""
    },
    "resolution":{
        "type": "enum",
        "options": ['320', '640', '800', '1024', '1280'],
        "default": '640'
    },
    "conf_thresh": {
        "type": "float",
        "min": 0.0, "max": 1.0, "default": 0.5, "step": 0.05
    }
}

def get_ai_scripts():
    """Helper to find all scripts in the ai_modules folder"""
    import sys
    ai_path = Path(__file__).resolve().parent.parent / "ai_modules"
    if not ai_path.exists() and getattr(sys, 'frozen', False):
        base = Path(getattr(sys, '_MEIPASS', Path(sys.executable).parent))
        if (base / "ai_modules").exists():
            ai_path = base / "ai_modules"

    if not ai_path.exists():
        return ["rfdetr_inference"]
    ai_module_list = list({f.stem for f in ai_path.iterdir() if f.suffix in [".py", ".pyc"] and f.stem != "__init__"})
    return sorted(ai_module_list) if ai_module_list else ["rfdetr_inference"]

def process(frame, params=None):
    if frame is None:
        return None
    if params is None:
        params = {}

    from utils.device_compatibility import check_deep_learning_support
    supported, _, _ = check_deep_learning_support()
    if not supported:
        return frame

    script_name = params.get("model_script", "None")
    model_dir = params.get("model_dir", "")

    if script_name == "None" or not os.path.exists(model_dir): 
        return frame
    
    model_path = os.path.join(model_dir, "checkpoint_best_total.pth")
    metadata_path = os.path.join(model_dir, "metadata.json")

    if not os.path.exists(model_path):
        return frame
    if not os.path.exists(metadata_path):
        return frame

    cache_key = f"{script_name}_{model_dir}"

    target_width = int(params.get("resolution", '640'))
    conf = float(params.get("conf_thresh", 0.5))

    orig_height, orig_width = frame.shape[:2]
    if orig_width > 0:
        scale = target_width / orig_width
        new_height = max(1, int(orig_height * scale))
        frame_resized = cv2.resize(frame, (target_width, new_height))
    else:
        frame_resized = frame

    try:
        module = importlib.import_module(f"ai_modules.{script_name}")
        
        # check cache using the unique key
        if cache_key not in _MODEL_CACHE:
            print(f"{'-'*5} INITIALIZING MODEL: {cache_key} {'-'*5}")
            if hasattr(module, 'MODEL'):
                # store the instance
                _MODEL_CACHE[cache_key] = module.MODEL(metadata_path, model_path)
            else:
                return frame

        model_wrapper = _MODEL_CACHE[cache_key]
        return model_wrapper.predict(frame_resized, conf_thresh=conf)

    except Exception as e:
        print(f"Deep Learning Error: {e}")
        return frame