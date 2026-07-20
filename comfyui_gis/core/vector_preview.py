"""Static vector preview rendering utilities for ComfyUI-GIS."""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any


_DARK_THEME = {
    "figure": "#081018",
    "axes": "#0f1a24",
    "text": "#e8f3f8",
    "muted": "#9db1bd",
    "grid": "#365064",
    "polygon_face": "#18c77e",
    "polygon_edge": "#70f3c2",
    "line": "#45caff",
    "point": "#ff5fa2",
    "other": "#b58cff",
    "warning": "#ffc857",
}

_LIGHT_THEME = {
    "figure": "#eef3f6",
    "axes": "#ffffff",
    "text": "#14212b",
    "muted": "#526672",
    "grid": "#c6d2d9",
    "polygon_face": "#36b37e",
    "polygon_edge": "#087f5b",
    "line": "#1479b8",
    "point": "#d6336c",
    "other": "#7048e8",
    "warning": "#9a6700",
}


def _normalise_path(raw_path: str) -> Path:
    cleaned = raw_path.strip().strip('"').strip("'")
    if not cleaned:
        raise ValueError("Vector path is empty.")

    path = Path(cleaned).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"Vector dataset does not exist: {path}")

    return path.resolve()


def _requirements_install_command() -> str:
    repository_root = Path(__file__).resolve().parents[2]
    requirements_path = repository_root / "requirements.txt"
    return f'& "{sys.executable}" -m pip install -r "{requirements_path}"'


def _load_dependencies() -> tuple[Any, Any, Any, Any, Any]:
    missing: list[str] = []

    try:
        import pyogrio  # type: ignore
    except ModuleNotFoundError:
        pyogrio = None
        missing.append("pyogrio")

    try:
        import geopandas  # type: ignore
    except ModuleNotFoundError:
        geopandas = None
        missing.append("geopandas")

    try:
        import numpy  # type: ignore
    except ModuleNotFoundError:
        numpy = None
        missing.append("numpy")

    try:
        import torch  # type: ignore
    except ModuleNotFoundError:
        torch = None
        missing.append("torch")

    try:
        from matplotlib.backends.backend_agg import FigureCanvasAgg  # type: ignore
        from matplotlib.figure import Figure  # type: ignore
    except ModuleNotFoundError:
        FigureCanvasAgg = None
        Figure = None
        missing.append("matplotlib")

    if missing:
        names = ", ".join(sorted(set(missing)))
        raise RuntimeError(
            f"Missing preview dependencies: {names}.\n\n"
            "Close ComfyUI, open PowerShell, and run:\n"
            f"{_requirements_install_command()}\n\n"
            "Restart ComfyUI after installation."
        )

    return pyogrio, geopandas, numpy, torch, (Figure, FigureCanvasAgg)


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

    for name, _ in layers:
        if name == requested:
            return name

    for name, _ in layers:
        if name.casefold() == requested.casefold():
            return name

    available = ", ".join(name for name, _ in layers)
    raise ValueError(f"Layer '{requested}' was not found. Available layers: {available}")


def _finite_bounds(values: Any, numpy: Any) -> tuple[float, float, float, float] | None:
    if values is None:
        return None

    try:
        bounds = numpy.asarray(values, dtype=float).reshape(-1)
    except Exception:
        return None

    if bounds.size != 4 or not numpy.isfinite(bounds).all():
        return None

    xmin, ymin, xmax, ymax = (float(value) for value in bounds)
    if xmax < xmin or ymax < ymin:
        return None
    return xmin, ymin, xmax, ymax


def _padded_bounds(
    bounds: tuple[float, float, float, float],
    padding_fraction: float = 0.06,
) -> tuple[float, float, float, float]:
    xmin, ymin, xmax, ymax = bounds
    width = xmax - xmin
    height = ymax - ymin
    scale = max(abs(xmin), abs(ymin), abs(xmax), abs(ymax), 1.0)

    if width <= 0:
        width = scale * 0.04
    if height <= 0:
        height = scale * 0.04

    x_padding = width * padding_fraction
    y_padding = height * padding_fraction
    return (
        xmin - x_padding,
        ymin - y_padding,
        xmax + x_padding,
        ymax + y_padding,
    )


def _short_crs(crs: Any, limit: int = 96) -> str:
    if not crs:
        return "CRS not defined"
    text = " ".join(str(crs).split())
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def _read_preview_frame(
    pyogrio: Any,
    path: Path,
    selected_layer: str,
    max_features: int,
    feature_count: int,
):
    read_limit = max_features if feature_count < 0 or feature_count > max_features else None
    kwargs = {
        "layer": selected_layer,
        "columns": [],
        "force_2d": True,
        "max_features": read_limit,
    }

    try:
        frame = pyogrio.read_dataframe(path, on_invalid="warn", **kwargs)
    except TypeError:
        # Compatibility fallback for older Pyogrio releases.
        frame = pyogrio.read_dataframe(path, **kwargs)

    return frame, read_limit


def _render_geometry_layers(frame: Any, axis: Any, palette: dict[str, str]) -> dict[str, int]:
    try:
        exploded = frame.explode(index_parts=False, ignore_index=True)
    except TypeError:
        exploded = frame.explode(index_parts=False).reset_index(drop=True)
    except Exception:
        exploded = frame

    geometry_types = exploded.geometry.geom_type.fillna("")
    polygon_mask = geometry_types.str.contains("Polygon", case=False, regex=False)
    line_mask = geometry_types.str.contains("LineString", case=False, regex=False) | geometry_types.str.contains(
        "LinearRing", case=False, regex=False
    )
    point_mask = geometry_types.str.contains("Point", case=False, regex=False)
    known_mask = polygon_mask | line_mask | point_mask

    counts = {
        "polygons": int(polygon_mask.sum()),
        "lines": int(line_mask.sum()),
        "points": int(point_mask.sum()),
        "other": int((~known_mask).sum()),
    }

    if counts["polygons"]:
        exploded.loc[polygon_mask].plot(
            ax=axis,
            facecolor=palette["polygon_face"],
            edgecolor=palette["polygon_edge"],
            linewidth=0.9,
            alpha=0.42,
        )

    if counts["lines"]:
        line_width = 1.5 if counts["lines"] < 5000 else 0.65
        exploded.loc[line_mask].plot(
            ax=axis,
            color=palette["line"],
            linewidth=line_width,
            alpha=0.92,
        )

    if counts["points"]:
        point_count = counts["points"]
        if point_count <= 100:
            marker_size = 30
        elif point_count <= 1000:
            marker_size = 14
        elif point_count <= 10000:
            marker_size = 5
        else:
            marker_size = 2
        exploded.loc[point_mask].plot(
            ax=axis,
            color=palette["point"],
            edgecolor=palette["axes"],
            linewidth=0.25,
            markersize=marker_size,
            alpha=0.88,
        )

    if counts["other"]:
        exploded.loc[~known_mask].plot(
            ax=axis,
            color=palette["other"],
            edgecolor=palette["other"],
            linewidth=1.0,
            alpha=0.8,
        )

    return counts


def render_vector_preview(
    vector_path: str,
    layer: str = "",
    width: int = 1024,
    height: int = 768,
    max_features: int = 25000,
    theme: str = "dark",
    show_metadata: bool = True,
    show_axes: bool = False,
):
    """Render a local vector layer as a ComfyUI IMAGE tensor and summary string."""

    path = _normalise_path(vector_path)
    pyogrio, _geopandas, numpy, torch, matplotlib_types = _load_dependencies()
    Figure, FigureCanvasAgg = matplotlib_types

    layers = _normalise_layers(pyogrio.list_layers(path))
    selected_layer = _select_layer(layers, layer)

    info = pyogrio.read_info(
        path,
        layer=selected_layer,
        force_feature_count=False,
        force_total_bounds=True,
    )

    geometry_type = info.get("geometry_type") or info.get("geometry")
    if not geometry_type:
        raise ValueError(
            f"Layer '{selected_layer}' is non-spatial and cannot be rendered as a vector preview."
        )

    width = int(max(256, min(2048, width)))
    height = int(max(256, min(2048, height)))
    max_features = int(max(100, min(1_000_000, max_features)))

    feature_count = int(info.get("features", -1))
    frame, read_limit = _read_preview_frame(
        pyogrio=pyogrio,
        path=path,
        selected_layer=selected_layer,
        max_features=max_features,
        feature_count=feature_count,
    )

    if frame.empty:
        raise ValueError(f"Layer '{selected_layer}' contains no readable features.")

    valid_mask = frame.geometry.notna() & ~frame.geometry.is_empty
    frame = frame.loc[valid_mask].copy()
    if frame.empty:
        raise ValueError(f"Layer '{selected_layer}' contains no non-empty geometries.")

    full_bounds = _finite_bounds(info.get("total_bounds"), numpy)
    if full_bounds is None:
        full_bounds = _finite_bounds(frame.total_bounds, numpy)
    if full_bounds is None:
        raise ValueError("The layer bounds could not be calculated.")

    palette = _DARK_THEME if theme.casefold() == "dark" else _LIGHT_THEME

    dpi = 100
    figure = Figure(
        figsize=(width / dpi, height / dpi),
        dpi=dpi,
        facecolor=palette["figure"],
    )
    canvas = FigureCanvasAgg(figure)

    if show_metadata:
        axis = figure.add_axes([0.055, 0.11, 0.89, 0.74])
    else:
        axis = figure.add_axes([0.035, 0.045, 0.93, 0.91])
    axis.set_facecolor(palette["axes"])

    geometry_counts = _render_geometry_layers(frame, axis, palette)

    padded = _padded_bounds(full_bounds)
    axis.set_xlim(padded[0], padded[2])
    axis.set_ylim(padded[1], padded[3])
    axis.set_aspect("equal", adjustable="box")

    if show_axes:
        axis.grid(True, color=palette["grid"], alpha=0.28, linewidth=0.6)
        axis.tick_params(colors=palette["muted"], labelsize=7)
        for spine in axis.spines.values():
            spine.set_color(palette["grid"])
    else:
        axis.set_axis_off()

    previewed_count = len(frame)
    total_text = f"{feature_count:,}" if feature_count >= 0 else "unknown"
    sampled = (
        feature_count > max_features
        if feature_count >= 0
        else read_limit is not None and previewed_count >= max_features
    )
    crs_text = _short_crs(info.get("crs"))

    if show_metadata:
        title = f"{path.name} — {selected_layer}"
        figure.text(
            0.055,
            0.94,
            title,
            color=palette["text"],
            fontsize=14,
            fontweight="bold",
            va="top",
        )
        subtitle = (
            f"{geometry_type}  •  Previewed {previewed_count:,} of {total_text} features  •  {crs_text}"
        )
        figure.text(
            0.055,
            0.895,
            subtitle,
            color=palette["muted"],
            fontsize=8.5,
            va="top",
        )
        footer = "Static preview — the source dataset was not modified."
        if sampled:
            footer += f" Preview limited to the first {max_features:,} features."
        figure.text(
            0.055,
            0.04,
            footer,
            color=palette["warning"] if sampled else palette["muted"],
            fontsize=7.5,
            va="bottom",
        )

    canvas.draw()
    pixels = numpy.asarray(canvas.buffer_rgba(), dtype=numpy.uint8)[..., :3].copy()
    image = torch.from_numpy(pixels.astype(numpy.float32) / 255.0).unsqueeze(0)
    figure.clear()

    type_parts = [
        f"{count:,} {name}"
        for name, count in geometry_counts.items()
        if count
    ]
    type_summary = ", ".join(type_parts) if type_parts else "geometry"
    summary = (
        "ComfyUI-GIS — Vector Preview\n"
        "==============================\n"
        f"Path: {path}\n"
        f"Layer: {selected_layer}\n"
        f"Declared geometry: {geometry_type}\n"
        f"Rendered geometry parts: {type_summary}\n"
        f"Previewed features: {previewed_count:,}\n"
        f"Dataset feature count: {total_text}\n"
        f"CRS: {crs_text}\n"
        f"Canvas: {width} × {height}\n"
        f"Theme: {theme}\n"
        f"Preview limited: {'yes' if sampled else 'no'}\n"
        "Source modified: no"
    )

    return image, summary
