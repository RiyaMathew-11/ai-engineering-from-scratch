import gc
import statistics
import time
from collections.abc import Callable, Iterator
from dataclasses import dataclass

import torch
import torch.nn as nn
import torch.nn.functional as F


@dataclass
class Result:
    name: str
    cpu_s: float
    gpu_s: float
    note: str = ""

    @property
    def speedup(self) -> float:
        return self.cpu_s / self.gpu_s


# A setup takes a device name and returns a zero-arg function ready to be timed.
Setup = Callable[[str], Callable[[], object]]


def sync(device: str) -> None:
    if device == "mps":
        torch.mps.synchronize()


def release_memory(device: str) -> None:
    """Drop dead tensors and hand PyTorch's cached MPS blocks back to the system."""
    gc.collect()
    if device == "mps":
        torch.mps.empty_cache()


def timeit(fn: Callable[[], object], device: str, iters: int = 10, warmup: int = 3) -> float:
    """Median wall-clock seconds for fn(), with warm-up runs and GPU sync."""
    for _ in range(warmup):
        fn()
    sync(device)

    times = []
    for _ in range(iters):
        start = time.perf_counter()
        fn()
        sync(device)
        times.append(time.perf_counter() - start)
    return statistics.median(times)


def show_progress(message: str) -> None:
    print(f"  ... {message:<60}", end="\r", flush=True)


def compare(
    name: str,
    setup: Setup,
    gpu: str,
    iters: int = 10,
    cpu_iters: int | None = None,
    warmup: int = 3,
    note: Callable[[float], str] | None = None,
    cpu_setup: Setup | None = None,
) -> Result:
    """Time a workload on the GPU, against the same (or a given baseline) workload on CPU."""
    show_progress(f"{name}: CPU")
    cpu_s = timeit((cpu_setup or setup)("cpu"), "cpu", cpu_iters or iters, warmup)
    show_progress(f"{name}: GPU")
    gpu_s = timeit(setup(gpu), gpu, iters, warmup)
    return Result(name, cpu_s, gpu_s, note(gpu_s) if note else "")


def format_result(r: Result) -> str:
    return f"  {r.name:<32} CPU {r.cpu_s * 1000:>9.1f} ms   GPU {r.gpu_s * 1000:>9.1f} ms   {r.speedup:>5.1f}x  {r.note}"


def print_section(title: str, results: Iterator[Result]) -> None:
    print(f"\n{title}")
    for r in results:  # results are generated lazily, so each row prints as soon as it's done
        print(format_result(r), flush=True)


# --- workloads: each returns a Setup ------------------------------------------------


def matmul_setup(size: int, dtype: torch.dtype) -> Setup:
    def setup(device: str):
        a = torch.randn(size, size, device=device, dtype=dtype)
        b = torch.randn(size, size, device=device, dtype=dtype)
        return lambda: a @ b

    return setup


def add_setup(n: int) -> Setup:
    def setup(device: str):
        x = torch.randn(n, device=device)
        y = torch.randn(n, device=device)
        return lambda: x + y

    return setup


def conv_setup(batch: int, in_ch: int, out_ch: int, hw: int) -> Setup:
    def setup(device: str):
        conv = nn.Conv2d(in_ch, out_ch, kernel_size=3, padding=1).to(device)
        x = torch.randn(batch, in_ch, hw, hw, device=device)

        def run():
            with torch.no_grad():
                return conv(x)

        return run

    return setup


def attention_setup(batch: int, heads: int, seq: int, head_dim: int) -> Setup:
    def setup(device: str):
        q, k, v = (torch.randn(batch, heads, seq, head_dim, device=device) for _ in range(3))
        return lambda: F.scaled_dot_product_attention(q, k, v)

    return setup


def build_mlp(width: int, depth: int, classes: int) -> nn.Module:
    layers: list[nn.Module] = []
    for _ in range(depth - 1):
        layers += [nn.Linear(width, width), nn.ReLU()]
    layers.append(nn.Linear(width, classes))
    return nn.Sequential(*layers)


def train_step_setup(width: int, depth: int, batch: int, classes: int = 10) -> Setup:
    def setup(device: str):
        model = build_mlp(width, depth, classes).to(device)
        opt = torch.optim.AdamW(model.parameters(), lr=1e-3)
        x = torch.randn(batch, width, device=device)
        y = torch.randint(0, classes, (batch,), device=device)

        def step():
            opt.zero_grad()
            F.cross_entropy(model(x), y).backward()
            opt.step()

        return step

    return setup


# --- benchmarks: each yields Results one at a time ----------------------------------


def bench_matmul(gpu: str) -> Iterator[Result]:
    """Compute-bound. A matmul does ~2*n^3 floating-point ops.

    CPUs have no fast fp16 matmul, so fp16 GPU rows are compared against the CPU fp32 baseline.
    """
    for size in (1024, 2048, 4096, 8192):
        tflops = lambda gpu_s, n=size: f"({2 * n**3 / gpu_s / 1e12:.2f} TFLOPS)"
        cpu_iters = 2 if size >= 8192 else 5
        fp32 = matmul_setup(size, torch.float32)
        fp16 = matmul_setup(size, torch.float16)
        yield compare(f"{size}x{size} fp32", fp32, gpu, cpu_iters=cpu_iters, note=tflops)
        yield compare(f"{size}x{size} fp16 (vs CPU fp32)", fp16, gpu, cpu_iters=cpu_iters, note=tflops, cpu_setup=fp32)


def bench_bandwidth(gpu: str) -> Iterator[Result]:
    """Memory-bound. Elementwise add moves lots of bytes and does almost no math."""
    n = 100_000_000
    gb_moved = 3 * n * 4 / 1e9  # read x, read y, write out (fp32)
    gbps = lambda gpu_s: f"({gb_moved / gpu_s:.0f} GB/s on GPU)"
    yield compare("100M-element add", add_setup(n), gpu, iters=5, note=gbps)


def bench_conv(gpu: str) -> Iterator[Result]:
    """Convolution: the workhorse of Phase 4 (vision)."""
    yield compare("conv2d 3x3, 64->128, 112px", conv_setup(32, 64, 128, 112), gpu, iters=3, warmup=1)


def bench_attention(gpu: str) -> Iterator[Result]:
    """Attention: the core op of Phase 7 (transformers)."""
    yield compare("attention seq=1024, 12 heads", attention_setup(8, 12, 1024, 64), gpu, iters=3, warmup=1)


def bench_training(gpu: str) -> Iterator[Result]:
    """End-to-end forward + backward + AdamW step."""
    yield compare("MLP train step (4x2048, b=256)", train_step_setup(2048, 4, 256), gpu)


BENCHMARKS: list[tuple[str, Callable[[str], Iterator[Result]]]] = [
    ("[1] Matmul sweep (compute-bound)", bench_matmul),
    ("[2] Elementwise add (memory-bound)", bench_bandwidth),
    ("[3] Conv2d forward", bench_conv),
    ("[4] Attention", bench_attention),
    ("[5] MLP training step", bench_training),
]


def run_all(gpu: str) -> None:
    print(f"\n=== Benchmark suite (CPU vs {gpu}) ===")
    for title, bench in BENCHMARKS:
        try:
            print_section(title, bench(gpu))
        except Exception as e:  # an unsupported MPS op shouldn't kill the whole suite
            print(f"\n{title}\n  failed: {type(e).__name__}: {e}")
        finally:
            release_memory(gpu)
