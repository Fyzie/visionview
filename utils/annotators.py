# THIS SCRIPT PROVIDES FUNCTIONS TO ANNOTATE IMAGES OUT OF THE PREDICTIONS (BBOX, MASK, CLASS LABELS)
import cv2
import numpy as np

try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

def mask_annotator(image, masks, colors, alpha=0.3):
    overlay = image.copy()

    for i, mask in enumerate(masks):
        if HAS_TORCH and isinstance(mask, torch.Tensor):
            mask_np = mask.detach().cpu().numpy()
        else:
            mask_np = np.asarray(mask)

        mask_np = mask_np.astype(bool)

        col = colors[i % len(colors)] if colors else (0, 255, 0)
        color = np.array(col, dtype=np.uint8)

        color_mask = np.zeros_like(image, dtype=np.uint8)
        color_mask[mask_np] = color

        blended = cv2.addWeighted(overlay, 1 - alpha, color_mask, alpha, 0)
        overlay[mask_np] = blended[mask_np]

    return overlay


def box_annotator(image, boxes, colors, thickness=2):
    for i, box in enumerate(boxes):
        x1, y1, x2, y2 = map(int, box)
        col = colors[i % len(colors)] if colors else (0, 255, 0)
        cv2.rectangle(
            image, (x1, y1), (x2, y2),
            col,
            thickness,
            cv2.LINE_AA
        )
    return image


def label_annotator(image, boxes, labels, colors):
    font = cv2.FONT_HERSHEY_SIMPLEX

    for i, (box, label) in enumerate(zip(boxes, labels)):
        x1, y1, _, _ = map(int, box)
        color = colors[i % len(colors)] if colors else (0, 255, 0)

        (tw, th), _ = cv2.getTextSize(label, font, 0.5, 1)
        y1 = max(y1, th + 6)

        cv2.rectangle(image, (x1, y1 - th - 6), (x1 + tw + 4, y1), color, -1)
        cv2.putText(
            image, label, (x1 + 2, y1 - 4),
            font, 0.5, (0, 0, 0), 1, cv2.LINE_AA
        )

    return image

# ----- ANNOTATE AN IMAGE ------
def annotate_image(image, detections, class_names, colors):
    if detections is None or not hasattr(detections, 'xyxy') or len(detections.xyxy) == 0:
        return image
    
    boxes = detections.xyxy
    masks = getattr(detections, 'mask', None)
    scores = getattr(detections, 'confidence', None)
    class_ids = getattr(detections, 'class_id', [])

    detected_class = []
    for cid in list(class_ids):
        if isinstance(class_names, dict) and cid in class_names:
            detected_class.append(class_names[cid])
        elif isinstance(class_names, (list, tuple)) and 0 <= int(cid) < len(class_names):
            detected_class.append(class_names[int(cid)])
        else:
            detected_class.append(str(cid))
    
    mapped_colors = []
    for name in detected_class:
        if isinstance(colors, dict) and name in colors:
            mapped_colors.append(colors[name])
        elif isinstance(colors, (list, tuple)) and len(colors) > 0:
            mapped_colors.append(colors[0])
        else:
            mapped_colors.append((0, 255, 0))

    if scores is None:
        labels = [f"{c}" for c in detected_class]
    else:
        labels = [f"{c}: {s:.2f}" for c, s in zip(detected_class, scores)]

    image = np.ascontiguousarray(image).copy()
    
    if masks is not None:
        image = mask_annotator(image, masks, mapped_colors, alpha=0.1)
    
    image = box_annotator(image, boxes, mapped_colors)
    image = label_annotator(image, boxes, labels, mapped_colors)

    return image