from pathlib import Path


def get_project_root() -> Path:
    return Path(__file__).absolute().parent


def chunk_even_groups(lst, n_groups):
    approx_sizes = len(lst) / n_groups
    for i in range(n_groups):
        yield lst[int(i * approx_sizes):int((i + 1) * approx_sizes)]