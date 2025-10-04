"""Utilities for running converted ONNX models with PyTorch."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, Iterable, Tuple

import numpy as np


@dataclass(frozen=True)
class _ModelCacheEntry:
    module: "torch.nn.Module"
    input_names: Tuple[str, ...]
    output_names: Tuple[str, ...]
    mtime: float


def _lazy_import_torch():
    import importlib

    torch = importlib.import_module("torch")
    return torch


def _lazy_import_onnx():
    import importlib

    return importlib.import_module("onnx")


def _lazy_import_onnx2torch():
    import importlib

    return importlib.import_module("onnx2torch")


_ONNX2TORCH_PATCHED = False


def _ensure_onnx2torch_patches():
    """Register runtime patches for onnx2torch used by our models."""

    global _ONNX2TORCH_PATCHED
    if _ONNX2TORCH_PATCHED:
        return

    try:
        from onnx2torch.node_converters import registry
        from onnx2torch.node_converters.shape import OnnxShape
        from onnx2torch.onnx_graph import OnnxGraph
        from onnx2torch.onnx_node import OnnxNode
        from onnx2torch.utils.common import OperationConverterResult, onnx_mapping_from_node
    except Exception as exc:  # pragma: no cover - defensive logging only
        logging.debug("Failed to import onnx2torch internals for patching: %s", exc)
        return

    try:
        registry.get_converter("Shape", 19)
    except NotImplementedError:

        @registry.add_converter(operation_type="Shape", version=19)
        def _shape_v19_converter(  # type: ignore[unused-ignore]
            node: OnnxNode, graph: OnnxGraph
        ) -> OperationConverterResult:
            return OperationConverterResult(
                torch_module=OnnxShape(
                    start=node.attributes.get("start", 0),
                    end=node.attributes.get("end", None),
                ),
                onnx_mapping=onnx_mapping_from_node(node=node),
            )

    _ONNX2TORCH_PATCHED = True


def get_inference_device(gpu_acceleration: bool = True) -> Tuple["torch.device", str]:
    """Return the most suitable torch device for inference.

    The provider order roughly matches the previous onnxruntime providers order
    (DirectML, CoreML/MPS, CUDA, CPU).
    """

    torch = _lazy_import_torch()

    candidates: Iterable[Tuple[str, "torch.device"]]

    if gpu_acceleration:
        candidates = []
        # DirectML (Windows)
        try:
            import importlib

            torch_directml = importlib.import_module("torch_directml")
            candidates.append(("directml", torch_directml.device()))
        except ModuleNotFoundError:
            pass
        except Exception as exc:  # pragma: no cover - best effort logging
            logging.warning("Failed to initialise DirectML backend: %s", exc)

        # CoreML via PyTorch MPS backend on Apple Silicon
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            candidates.append(("mps", torch.device("mps")))

        # CUDA
        if torch.cuda.is_available():
            candidates.append(("cuda", torch.device("cuda")))

        # Always fall back to CPU
        candidates.append(("cpu", torch.device("cpu")))
    else:
        candidates = [("cpu", torch.device("cpu"))]

    for name, device in candidates:
        try:
            # Smoke test in case the runtime is not actually usable.
            torch.empty(1, device=device)
        except Exception:  # pragma: no cover - device probing is best effort
            continue
        logging.info("Using torch device '%s' for inference", name)
        return device, name

    logging.warning("No accelerated backend available, falling back to CPU")
    return torch.device("cpu"), "cpu"


@lru_cache(maxsize=8)
def _load_model(ai_path: str, device_type: str) -> _ModelCacheEntry:
    """Load and convert an ONNX model to a torch module for the given device."""

    torch = _lazy_import_torch()
    onnx = _lazy_import_onnx()
    onnx2torch = _lazy_import_onnx2torch()

    _ensure_onnx2torch_patches()

    logging.info("Loading AI model '%s' for device '%s'", ai_path, device_type)

    onnx_model = onnx.load(ai_path)
    module = onnx2torch.convert(onnx_model)
    module.eval()
    module.to(device_type)

    input_names = tuple(inp.name for inp in onnx_model.graph.input)
    output_names = tuple(out.name for out in onnx_model.graph.output)

    try:
        mtime = os.path.getmtime(ai_path)
    except OSError:
        mtime = 0.0

    return _ModelCacheEntry(module=module, input_names=input_names, output_names=output_names, mtime=mtime)


def _ensure_cache_is_fresh(ai_path: str, device_type: str) -> _ModelCacheEntry:
    cache_entry = _load_model(ai_path, device_type)

    try:
        current_mtime = os.path.getmtime(ai_path)
    except OSError:
        current_mtime = cache_entry.mtime

    if current_mtime != cache_entry.mtime:
        _load_model.cache_clear()
        cache_entry = _load_model(ai_path, device_type)

    return cache_entry


def run_model(ai_path: str, feeds: Dict[str, np.ndarray], device: "torch.device") -> Dict[str, np.ndarray]:
    """Execute the converted model using PyTorch and return numpy outputs."""

    torch = _lazy_import_torch()

    cache_entry = _ensure_cache_is_fresh(ai_path, device.type)
    module = cache_entry.module
    module.to(device)

    tensors = []
    for name in cache_entry.input_names:
        if name not in feeds:
            raise KeyError(f"Missing required model input '{name}'")
        array = feeds[name]
        if not isinstance(array, np.ndarray):
            array = np.asarray(array)
        tensor = torch.from_numpy(array).to(device=device, dtype=torch.float32)
        tensors.append(tensor)

    with torch.no_grad():
        result = module(*tensors)

    if isinstance(result, tuple):
        outputs = list(result)
    else:
        outputs = [result]

    np_outputs: Dict[str, np.ndarray] = {}
    for name, tensor in zip(cache_entry.output_names, outputs):
        np_outputs[name] = tensor.detach().to("cpu").numpy()

    return np_outputs

