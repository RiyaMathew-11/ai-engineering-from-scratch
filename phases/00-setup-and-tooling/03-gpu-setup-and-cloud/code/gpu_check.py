import os

from benchmarks import run_all


def get_device(torch) -> str:
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def total_memory_gb() -> float:
    # Apple Silicon uses unified memory: the GPU shares system RAM
    return os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / 1e9


def print_device_info(torch, device: str) -> None:
    print("=== GPU Check ===\n")
    print(f"PyTorch version: {torch.__version__}")
    print(f"MPS available: {torch.backends.mps.is_available()}")
    print(f"Device: {device}")

    if device == "mps":
        print("GPU: Apple Silicon (Metal / MPS)")
        print(f"Unified memory: {total_memory_gb():.1f} GB")


def print_model_size_estimate() -> None:
    params_billions = total_memory_gb() / 2  # fp16 = 2 bytes per parameter
    print(f"\nEstimated max model size (fp16, unified memory, upper bound; OS needs RAM too): ~{params_billions:.0f}B parameters")


def check_gpu() -> None:
    try:
        import torch
    except ImportError:
        print("PyTorch not installed. Run: pip install torch")
        return

    device = get_device(torch)
    print_device_info(torch, device)

    if device == "cpu":
        print("\nNo GPU detected. That's fine for most lessons.")
        print("For GPU-heavy lessons, use Google Colab (free).")
        return

    run_all(device)
    print_model_size_estimate()


check_gpu()
