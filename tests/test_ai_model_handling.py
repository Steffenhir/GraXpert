import sys
from types import SimpleNamespace

import numpy as np
import pytest


# onnxruntime is installed separately per target platform and is intentionally
# absent from requirements.txt. A fake module keeps these unit tests portable.
fake_onnxruntime = SimpleNamespace(
    get_available_providers=lambda: [],
    InferenceSession=None,
    SessionOptions=None,
)
sys.modules.setdefault("onnxruntime", fake_onnxruntime)

from graxpert import ai_model_handling, denoising


def test_coreml_provider_defaults_to_mlprogram(monkeypatch):
    monkeypatch.setattr(
        ai_model_handling.ort,
        "get_available_providers",
        lambda: ["CoreMLExecutionProvider", "CPUExecutionProvider"],
    )

    providers = ai_model_handling.get_execution_providers_ordered()

    assert providers == [
        (
            "CoreMLExecutionProvider",
            {
                "ModelFormat": "MLProgram",
                "MLComputeUnits": "ALL",
                "RequireStaticInputShapes": "0",
            },
        ),
        "CPUExecutionProvider",
    ]


def test_coreml_provider_supports_configurable_neuralnetwork_format(monkeypatch):
    monkeypatch.setattr(
        ai_model_handling.ort,
        "get_available_providers",
        lambda: ["CoreMLExecutionProvider", "CPUExecutionProvider"],
    )

    providers = ai_model_handling.get_execution_providers_ordered(
        coreml_model_format=ai_model_handling.COREML_MODEL_FORMAT_NEURALNETWORK,
    )

    assert providers[0] == (
        "CoreMLExecutionProvider",
        {
            "ModelFormat": "NeuralNetwork",
            "MLComputeUnits": "ALL",
            "RequireStaticInputShapes": "0",
        },
    )


def test_invalid_coreml_model_format_is_rejected():
    with pytest.raises(ValueError, match="Unsupported Core ML model format"):
        ai_model_handling.get_execution_providers_ordered(coreml_model_format="invalid")


def test_denoising_fixes_and_pads_coreml_batch_dimension(monkeypatch):
    captured = {}

    def fake_get_execution_providers(gpu_acceleration):
        captured["gpu_acceleration"] = gpu_acceleration
        return ["CoreMLExecutionProvider", "CPUExecutionProvider"]

    class FakeSessionOptions:
        def __init__(self):
            captured["dimension_overrides"] = []

        def add_free_dimension_override_by_name(self, name, value):
            captured["dimension_overrides"].append((name, value))

    class FakeInferenceSession:
        def __init__(self, model_path, sess_options, providers):
            captured["model_path"] = model_path
            captured["session_options"] = sess_options
            captured["providers"] = providers
            captured["input_shapes"] = []

        def get_providers(self):
            return captured["providers"]

        def run(self, _output_names, inputs):
            captured["input_shapes"].append(inputs["gen_input_image"].shape)
            return [inputs["gen_input_image"]]

    monkeypatch.setattr(denoising, "get_execution_providers_ordered", fake_get_execution_providers)
    monkeypatch.setattr(denoising.ort, "SessionOptions", FakeSessionOptions)
    monkeypatch.setattr(denoising.ort, "InferenceSession", FakeInferenceSession)
    monkeypatch.setattr(denoising, "cached_denoised_image", None)

    image = np.random.default_rng(42).random((8, 8, 3), dtype=np.float32)
    result = denoising.denoise(
        image,
        "model.onnx",
        strength=1.0,
        batch_size=4,
        window_size=4,
        stride=2,
    )

    assert result.shape == image.shape
    assert captured["gpu_acceleration"] is True
    assert captured["dimension_overrides"] == [("batch_size", 4)]
    assert captured["model_path"] == "model.onnx"
    assert captured["providers"] == ["CoreMLExecutionProvider", "CPUExecutionProvider"]
    assert all(shape == (4, 4, 4, 3) for shape in captured["input_shapes"])
