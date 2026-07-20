"""Vector dataset inspection utilities for ComfyUI-GIS."""

from __future__ import annotations

from pathlib import Path
import hashlib
import sys
from typing import Any, Iterable


def _dataset_component_paths(path: Path) -> list[Path]:
    """Return files whose timestamps should invalidate a cached vector read."""

    if path.is_dir():
        # Directory-backed formats such as FileGDB may contain many files.
        # Limit the scan to keep cache fingerprinting fast and deterministic.
        components = [item for item in path.rglob("*") if item.is_file()]
        return sorted(components, key=lambda item: str(item).casefold())[:2048]

    if path.suffix.casefold() != ".shp":
        return [path]

    components: list[Path] = []
    for suffix in (
        ".shp",
        ".shx",
        ".dbf",
        ".prj",
        ".cpg",
        ".qix",
        ".sbn",
        ".sbx",
        ".aih",
        ".ain",
        ".ixs",
        ".mxs",
        ".atx",
    ):
        candidate = path.with_suffix(suffix)
        if candidate.exists():
            components.append(candidate)

    metadata_xml = Path(str(path) + ".xml")
    if metadata_xml.exists():
        components.append(metadata_xml)

    return sorted(set(components), key=lambda item: str(item).casefold()) or [path]


def vector_dataset_fingerprint(
    vector_path: str,
    layer: str = "",
    extra: Iterable[Any] = (),
) -> str:
    """Create a lightweight cache fingerprint for a local vector dataset.

    ComfyUI caches node outputs. Including file size and modification time means
    externally edited GIS files are re-read even when the path widget is unchanged.
    """

    cleaned = vector_path.strip().strip('"').strip("'")
    digest = hashlib.sha256()
    digest.update(cleaned.encode("utf-8", errors="replace"))
    digest.update(layer.strip().encode("utf-8", errors="replace"))
    digest.update(repr(tuple(extra)).encode("utf-8", errors="replace"))

    if not cleaned:
        return digest.hexdigest()

    path = Path(cleaned).expanduser()
    if not path.exists():
        digest.update(b"missing")
        return digest.hexdigest()

    try:
        resolved = path.resolve()
    except OSError:
        resolved = path

    digest.update(str(resolved).encode("utf-8", errors="replace"))
    for component in _dataset_component_paths(resolved):
        try:
            stat = component.stat()
        except OSError:
            continue
        try:
            relative = component.relative_to(resolved if resolved.is_dir() else resolved.parent)
        except ValueError:
            relative = component
        digest.update(str(relative).encode("utf-8", errors="replace"))
        digest.update(str(stat.st_size).encode("ascii"))
        digest.update(str(stat.st_mtime_ns).encode("ascii"))

    return digest.hexdigest()


def _normalise_path(raw_path: str) -> Path:
    cleaned = raw_path.strip().strip('"').strip("'")
    if not cleaned:
        raise ValueError("Vector path is empty.")

    path = Path(cleaned).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"Vector dataset does not exist: {path}")

    return path.resolve()


def _load_pyogrio() -> Any:
    try:
        import pyogrio  # type: ignore
    except ModuleNotFoundError as exc:
        repository_root = Path(__file__).resolve().parents[2]
        requirements_path = repository_root / "requirements.txt"
        powershell_command = (
            f'& "{sys.executable}" -m pip install -r "{requirements_path}"'
        )
        raise RuntimeError(
            "Pyogrio is not installed in the Python environment used by ComfyUI.\n\n"
            "Open PowerShell and run:\n"
            f"{powershell_command}\n\n"
            "Restart ComfyUI after installation."
        ) from exc

    return pyogrio


def _normalise_layers(raw_layers: Any) -> list[tuple[str, str]]:
    rows = raw_layers.tolist() if hasattr(raw_layers, "tolist") else list(raw_layers)
    if rows and not isinstance(rows[0], (list, tuple)):
        rows = [rows]

    layers: list[tuple[str, str]] = []
    for row in rows:
        if not row:
            continue
        name = str(row[0])
        geometry_type = "Non-spatial" if len(row) < 2 or row[1] is None else str(row[1])
        layers.append((name, geometry_type))
    return layers


def _select_layer(layers: list[tuple[str, str]], requested_layer: str) -> str:
    if not layers:
        raise ValueError("No readable layers were found in the vector dataset.")

    requested = requested_layer.strip()
    if not requested:
        return layers[0][0]

    exact_matches = [name for name, _ in layers if name == requested]
    if exact_matches:
        return exact_matches[0]

    casefold_matches = [name for name, _ in layers if name.casefold() == requested.casefold()]
    if casefold_matches:
        return casefold_matches[0]

    available = ", ".join(name for name, _ in layers)
    raise ValueError(
        f"Layer '{requested}' was not found. Available layers: {available}"
    )


def _as_strings(value: Any) -> list[str]:
    if value is None:
        return []
    items = value.tolist() if hasattr(value, "tolist") else list(value)
    return [str(item) for item in items]


def _format_bounds(bounds: Any, force_exact_metadata: bool) -> str:
    if bounds is None:
        suffix = " Enable force_exact_metadata to request a full calculation." if not force_exact_metadata else ""
        return f"Not reported by the data source.{suffix}"

    values = [float(value) for value in bounds]
    if len(values) != 4:
        return str(bounds)

    xmin, ymin, xmax, ymax = values
    return (
        f"xmin={xmin:.6f}, ymin={ymin:.6f}, "
        f"xmax={xmax:.6f}, ymax={ymax:.6f}"
    )


def inspect_vector_dataset(
    vector_path: str,
    layer: str = "",
    force_exact_metadata: bool = False,
) -> str:
    """Inspect a local vector dataset and return a readable metadata report."""

    path = _normalise_path(vector_path)
    pyogrio = _load_pyogrio()

    layers = _normalise_layers(pyogrio.list_layers(path))
    selected_layer = _select_layer(layers, layer)

    info = pyogrio.read_info(
        path,
        layer=selected_layer,
        force_feature_count=force_exact_metadata,
        force_total_bounds=force_exact_metadata,
    )

    fields = _as_strings(info.get("fields"))
    dtypes = _as_strings(info.get("dtypes"))
    field_lines = [
        f"  - {name} ({dtypes[index] if index < len(dtypes) else 'unknown'})"
        for index, name in enumerate(fields)
    ]
    if not field_lines:
        field_lines = ["  - No attribute fields"]
    elif len(field_lines) > 50:
        hidden_count = len(field_lines) - 50
        field_lines = field_lines[:50] + [f"  - … and {hidden_count} more fields"]

    feature_count = int(info.get("features", -1))
    if feature_count < 0:
        feature_text = "Not reported"
        if not force_exact_metadata:
            feature_text += " (enable force_exact_metadata for an exact count)"
    else:
        feature_text = f"{feature_count:,}"

    layer_lines = [f"  - {name} ({geometry_type})" for name, geometry_type in layers]
    if len(layer_lines) > 25:
        hidden_count = len(layer_lines) - 25
        layer_lines = layer_lines[:25] + [f"  - … and {hidden_count} more layers"]

    geometry_type = info.get("geometry_type") or info.get("geometry") or "Non-spatial / unknown"
    crs = info.get("crs") or "Not defined"
    driver = info.get("driver") or "Unknown"
    encoding = info.get("encoding") or "Unknown"
    fid_column = info.get("fid_column") or "Implicit / not reported"
    geometry_name = info.get("geometry_name") or "Default / not reported"
    bounds_text = _format_bounds(info.get("total_bounds"), force_exact_metadata)

    size_line = ""
    if path.is_file():
        size_mib = path.stat().st_size / (1024 * 1024)
        size_line = f"\nFile size: {size_mib:.2f} MiB"

    report = (
        "ComfyUI-GIS — Vector Dataset Inspector\n"
        "========================================\n"
        f"Path: {path}{size_line}\n"
        f"Driver: {driver}\n"
        f"Selected layer: {selected_layer}\n"
        f"Feature count: {feature_text}\n"
        f"Geometry type: {geometry_type}\n"
        f"CRS: {crs}\n"
        f"Bounds: {bounds_text}\n"
        f"Encoding: {encoding}\n"
        f"FID column: {fid_column}\n"
        f"Geometry column: {geometry_name}\n\n"
        f"Available layers ({len(layers)}):\n"
        + "\n".join(layer_lines)
        + f"\n\nAttribute fields ({len(fields)}):\n"
        + "\n".join(field_lines)
    )

    return report
