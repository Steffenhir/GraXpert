"""Utilities for running packaged PyTorch models across multiple backends."""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, Iterable, Optional, Tuple

import numpy as np


@dataclass(frozen=True)
class _ModelCacheEntry:
    module: "torch.nn.Module"
    input_names: Optional[Tuple[str, ...]]
    output_names: Optional[Tuple[str, ...]]
    model_mtime: float
    metadata_mtime: float
    metadata_path: Optional[str]


def _lazy_import_torch():
    import importlib

    torch = importlib.import_module("torch")
    return torch
def get_inference_device(gpu_acceleration: bool = True) -> Tuple["torch.device", str]:
    """Return the most suitable torch device for inference.

    Preference order: CUDA, DirectML, CoreML/MPS, CPU.
    """

    torch = _lazy_import_torch()

    candidates: Iterable[Tuple[str, "torch.device"]]

    if gpu_acceleration:
        candidates_list = []

        # CUDA (Windows/Linux with NVIDIA GPUs)
        if torch.cuda.is_available():
            candidates_list.append(("cuda", torch.device("cuda")))

        # DirectML (Windows)
        try:
            import importlib

            torch_directml = importlib.import_module("torch_directml")
            if hasattr(torch_directml, "is_available") and not torch_directml.is_available():
                raise RuntimeError("DirectML backend reported unavailable")
            candidates_list.append(("directml", torch_directml.device()))
        except ModuleNotFoundError:
            pass
        except Exception as exc:  # pragma: no cover - best effort logging
            logging.warning("Failed to initialise DirectML backend: %s", exc)

        # CoreML via PyTorch MPS backend on Apple Silicon
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            candidates_list.append(("mps", torch.device("mps")))

        # Always fall back to CPU
        candidates_list.append(("cpu", torch.device("cpu")))
        candidates = candidates_list
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


def _safe_mtime(path: Optional[str]) -> float:
    if not path:
        return 0.0
    try:
        return os.path.getmtime(path)
    except OSError:
        return 0.0


def _load_torch_module(torch, ai_path: str):
    """Load a packaged torch module, preferring TorchScript archives."""

    try:
        return torch.jit.load(ai_path, map_location="cpu")
    except (RuntimeError, ValueError) as exc:
        logging.debug("TorchScript load failed for %s: %s", ai_path, exc)

    package = torch.load(ai_path, map_location="cpu")

    if isinstance(package, torch.nn.Module):
        return package

    if isinstance(package, dict):
        module = package.get("module") or package.get("model")
        if isinstance(module, torch.nn.Module):
            state_dict = package.get("state_dict")
            if state_dict is not None:
                module.load_state_dict(state_dict)
            return module

    raise TypeError(f"Unsupported torch model package at '{ai_path}'")


def _load_metadata(ai_path: str) -> Tuple[Optional[Tuple[str, ...]], Optional[Tuple[str, ...]], Optional[str]]:
    base_dir = os.path.dirname(ai_path)
    candidates = [
        os.path.join(base_dir, "model.json"),
        os.path.splitext(ai_path)[0] + ".json",
    ]

    for path in candidates:
        if not os.path.isfile(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except Exception as exc:  # pragma: no cover - best effort logging
            logging.warning("Failed to load model metadata '%s': %s", path, exc)
            continue

        inputs = payload.get("inputs") or payload.get("input_names")
        outputs = payload.get("outputs") or payload.get("output_names")

        input_names = tuple(inputs) if inputs else None
        output_names = tuple(outputs) if outputs else None
        return input_names, output_names, path

    return None, None, None


def _extract_names_from_module(module) -> Tuple[Optional[Tuple[str, ...]], Optional[Tuple[str, ...]]]:
    input_names = getattr(module, "input_names", None)
    output_names = getattr(module, "output_names", None)

    if isinstance(input_names, (list, tuple)):
        input_tuple: Optional[Tuple[str, ...]] = tuple(str(name) for name in input_names)
    else:
        input_tuple = None

    if isinstance(output_names, (list, tuple)):
        output_tuple: Optional[Tuple[str, ...]] = tuple(str(name) for name in output_names)
    else:
        output_tuple = None

    return input_tuple, output_tuple


@lru_cache(maxsize=8)
def _load_model(ai_path: str, device_type: str) -> _ModelCacheEntry:
    """Load a PyTorch model package for the given device."""

    torch = _lazy_import_torch()

    logging.info("Loading AI model '%s' for device '%s'", ai_path, device_type)

    module = _load_torch_module(torch, ai_path)
    module.eval()
    module.to(device_type)

    metadata_inputs, metadata_outputs, metadata_path = _load_metadata(ai_path)
    module_inputs, module_outputs = _extract_names_from_module(module)

    input_names = metadata_inputs or module_inputs
    output_names = metadata_outputs or module_outputs

    model_mtime = _safe_mtime(ai_path)
    metadata_mtime = _safe_mtime(metadata_path)

    return _ModelCacheEntry(
        module=module,
        input_names=input_names,
        output_names=output_names,
        model_mtime=model_mtime,
        metadata_mtime=metadata_mtime,
        metadata_path=metadata_path,
    )


def _ensure_cache_is_fresh(ai_path: str, device_type: str) -> _ModelCacheEntry:
    cache_entry = _load_model(ai_path, device_type)

    current_model_mtime = _safe_mtime(ai_path)
    current_metadata_mtime = _safe_mtime(cache_entry.metadata_path)

    if (
        current_model_mtime != cache_entry.model_mtime
        or current_metadata_mtime != cache_entry.metadata_mtime
    ):
        _load_model.cache_clear()
        cache_entry = _load_model(ai_path, device_type)

    return cache_entry


def run_model(ai_path: str, feeds: Dict[str, np.ndarray], device: "torch.device") -> Dict[str, np.ndarray]:
    """Execute the converted model using PyTorch and return numpy outputs."""

    torch = _lazy_import_torch()

    cache_entry = _ensure_cache_is_fresh(ai_path, device.type)
    module = cache_entry.module
    module.to(device)

    if cache_entry.input_names:
        input_sequence = []
        for name in cache_entry.input_names:
            if name not in feeds:
                raise KeyError(f"Missing required model input '{name}'")
            input_sequence.append((name, feeds[name]))
    else:
        input_sequence = list(feeds.items())

    tensors = []
    for name, array in input_sequence:
        if not isinstance(array, np.ndarray):
            array = np.asarray(array)
        tensor = torch.from_numpy(array).to(device=device, dtype=torch.float32)
        tensors.append(tensor)

    with torch.no_grad():
        result = module(*tensors)

    if isinstance(result, dict):
        iterable = result.items()
    elif isinstance(result, (tuple, list)):
        output_names = cache_entry.output_names
        if output_names and len(output_names) != len(result):
            logging.warning(
                "Model reported %d outputs but metadata lists %d entries", len(result), len(output_names)
            )
        if output_names:
            iterable = zip(output_names, result)
        else:
            iterable = ((f"output_{idx}", tensor) for idx, tensor in enumerate(result))
    else:
        name = cache_entry.output_names[0] if cache_entry.output_names else "output_0"
        iterable = [(name, result)]

    np_outputs: Dict[str, np.ndarray] = {}
    for name, tensor in iterable:
        np_outputs[str(name)] = tensor.detach().to("cpu").numpy()

    return np_outputs

