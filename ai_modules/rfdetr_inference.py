import cv2
import json
import numpy as np

try:
    import torch
    import torch.nn.functional as torch_F
    import torchvision.ops as ops
    from torchvision.transforms import functional as F
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

try:
    import rfdetr
    from rfdetr import config
    HAS_RFDETR = True
except ImportError:
    HAS_RFDETR = False

from utils.annotators import annotate_image

class MODEL():
    def __init__(self, metadata_path, model_path):
        print("RFDETR inference.")
        if not HAS_RFDETR:
            raise ImportError("The 'rfdetr' package is not installed. Please install rfdetr to run this model.")
        self.load_metadata(metadata_path)
        self.load_model(model_path)

    def load_metadata(self, metadata_path):
        with open(metadata_path, 'r') as f:
            self.metadata = json.load(f)

    def load_model(self, model_path):
        self.model_type = self.metadata["model"]["model_type"]
        self.class_names = self.metadata["dataset"]["class_names"]
        self.colors = self.metadata["dataset"]["colors"]
        try:
            model_class = getattr(rfdetr, self.model_type)
            self.model = model_class(pretrain_weights=model_path)
            self.model.optimize_for_inference()
        except AttributeError:
            raise ImportError(f"Model type '{self.model_type}' not found.")
    
    def predict(self, img, conf_thresh=0.5):
        det = self.model.predict(img, threshold=conf_thresh)
        annotated_image = annotate_image(img, det, self.class_names, self.colors)
        return annotated_image