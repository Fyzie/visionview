# ==============================================================================
# VisionView - Device Hardware & Library Compatibility Checker
# Manages graceful degradation on laptops/devices without PyTorch / CUDA
# ==============================================================================

import os
import sys
from PySide6.QtWidgets import QMessageBox

_COMPATIBILITY_CACHE = None

def check_deep_learning_support(force_refresh=False):
    """
    Checks whether PyTorch, Torchvision, and AI inference can run on this device.
    Returns:
        tuple (is_supported: bool, message: str, details: dict)
    """
    global _COMPATIBILITY_CACHE
    if _COMPATIBILITY_CACHE is not None and not force_refresh:
        return _COMPATIBILITY_CACHE

    # Allow testing unsupported state via environment variable
    if os.environ.get("VISIONVIEW_FORCE_NO_TORCH", "0") == "1":
        res = (
            False,
            "Deep Learning is disabled by environment override (VISIONVIEW_FORCE_NO_TORCH=1).",
            {"torch": False, "torchvision": False, "cuda": False, "device": "None"}
        )
        _COMPATIBILITY_CACHE = res
        return res

    details = {
        "torch": False,
        "torchvision": False,
        "cuda": False,
        "device": "CPU",
        "reason": ""
    }

    # 1. Check PyTorch installation
    try:
        import torch
        details["torch"] = True
        details["torch_version"] = torch.__version__
    except ImportError:
        res = (
            False,
            "The PyTorch ('torch') deep learning library is not installed or bundled in this application build.",
            details
        )
        _COMPATIBILITY_CACHE = res
        return res
    except Exception as e:
        res = (
            False,
            f"PyTorch failed to load on this device: {e}",
            details
        )
        _COMPATIBILITY_CACHE = res
        return res

    # 2. Check Torchvision installation
    try:
        import torchvision
        details["torchvision"] = True
        details["torchvision_version"] = torchvision.__version__
    except ImportError:
        res = (
            False,
            "The 'torchvision' computer vision library is not installed on this system.",
            details
        )
        _COMPATIBILITY_CACHE = res
        return res
    except Exception as e:
        res = (
            False,
            f"Torchvision failed to load on this device: {e}",
            details
        )
        _COMPATIBILITY_CACHE = res
        return res

    # 3. Check CPU instruction execution (catches AVX/AVX2 instruction crashes on older CPUs)
    try:
        t = torch.zeros(1) + 1.0
        if float(t.item()) != 1.0:
            raise RuntimeError("CPU tensor computation returned unexpected result.")
    except Exception as e:
        res = (
            False,
            f"Your CPU cannot execute PyTorch operations (missing required AVX instruction set): {e}",
            details
        )
        _COMPATIBILITY_CACHE = res
        return res

    # 4. Check CUDA / GPU availability
    try:
        if torch.cuda.is_available():
            details["cuda"] = True
            details["device"] = torch.cuda.get_device_name(0)
        else:
            details["cuda"] = False
            details["device"] = "CPU (No NVIDIA CUDA GPU detected)"
    except Exception:
        details["cuda"] = False
        details["device"] = "CPU"

    # 5. Check RF-DETR framework availability
    try:
        import rfdetr
        details["rfdetr"] = True
    except ImportError:
        details["rfdetr"] = False

    res = (True, "Supported", details)
    _COMPATIBILITY_CACHE = res
    return res

def show_unsupported_feature_popup(parent=None, feature_name="Deep Learning", reason=None):
    """
    Displays a user-friendly modal warning dialog when a user attempts
    to use a feature that is not supported by their laptop or system.
    """
    if reason is None:
        _, reason, _ = check_deep_learning_support()

    if os.environ.get("VISIONVIEW_HEADLESS_TEST", "0") == "1":
        return 1

    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Warning)
    msg_box.setWindowTitle("Feature Not Supported")
    msg_box.setText(f"<b>This feature is not supported on your device.</b>")
    
    info_text = (
        f"The <b>{feature_name}</b> feature requires PyTorch and compatible hardware, "
        f"which is currently unavailable on this device.<br><br>"
        f"<b>Reason:</b><br>{reason}<br><br>"
        f"<i>All other VisionView features (camera streaming, OpenCV filters, measurement tools, and recording) "
        f"will continue to work normally.</i>"
    )
    msg_box.setInformativeText(info_text)
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.setDefaultButton(QMessageBox.Ok)
    return msg_box.exec()
