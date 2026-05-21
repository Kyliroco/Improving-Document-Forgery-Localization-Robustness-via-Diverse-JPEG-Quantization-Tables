"""Example script to load DocQT from Hugging Face Hub and save a JPEG.

The script downloads quantization tables from the Kyliroco/DocQT dataset,
splits them into luminance and chrominance tables, and reuses the local
JPEG-saving helper to compress an image with selected tables.
"""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import cast

import datasets

QuantizationTable = list[int]
QuantizationTables = list[QuantizationTable]
DOCQT_DATASET_ID = "Kyliroco/DocQT"

def load_quantization_tables_from_hub(
    dataset_id: str = DOCQT_DATASET_ID,
) -> tuple[QuantizationTables, QuantizationTables]:
    """Load luminance and chrominance quantization tables from Hugging Face.

    Args:
        dataset_id: Hugging Face dataset identifier.

    Returns:
        A tuple containing luminance tables and chrominance tables.
    """
    dataset = datasets.load_dataset(dataset_id)

    luminance_split = dataset["luminance"]
    chrominance_split = dataset["chrominance"]

    luminance_tables = cast(QuantizationTables, luminance_split["text"])
    chrominance_tables = cast(QuantizationTables, chrominance_split["text"])
    return luminance_tables, chrominance_tables

def save_jpeg_with_selected_qtables(
    input_image: Path,
    output_jpeg: Path,
    luminance_tables: QuantizationTables,
    chrominance_tables: QuantizationTables,
    luminance_index: int,
    chrominance_index: int,
    subsampling: str = "4:2:0",
) -> None:
    """Save an image as JPEG with selected luminance and chrominance tables.

    Args:
        input_image: Path to the input image file.
        output_jpeg: Path to the output JPEG file.
        luminance_tables: Available luminance quantization tables.
        chrominance_tables: Available chrominance quantization tables.
        luminance_index: Index of the luminance table to use.
        chrominance_index: Index of the chrominance table to use.
        subsampling: JPEG chroma subsampling mode (for example "4:2:0").

    Returns:
        None.

    Raises:
        ModuleNotFoundError: If Pillow is not installed in the environment.
    """
    try:
        pil_image_module = importlib.import_module("PIL.Image")
    except ModuleNotFoundError as exc:
        msg = "Pillow is required. Install it with: uv pip install pillow"
        raise ModuleNotFoundError(msg) from exc

    luma_qtable = luminance_tables[luminance_index]
    chroma_qtable = chrominance_tables[chrominance_index]

    with pil_image_module.open(input_image) as image:
        rgb_image = image.convert("RGB")
        # Do not pass a quality value if you want to keep qtables unchanged.
        rgb_image.save(
            output_jpeg,
            format="JPEG",
            qtables=[luma_qtable, chroma_qtable],
            subsampling=subsampling,
            optimize=True,
        )

def main() -> None:
    """Run a minimal Hugging Face based compression example.

    Args:
        None.

    Returns:
        None.
    """
    base_dir = Path(".")
    input_image = base_dir / "input.png"
    output_jpeg = base_dir / "output_custom_qtables_hf.jpg"

    luminance_tables, chrominance_tables = load_quantization_tables_from_hub()

    print(f"Loaded luminance tables from Hub: {len(luminance_tables)}")
    print(f"Loaded chrominance tables from Hub: {len(chrominance_tables)}")

    if not input_image.exists():
        print(f"Input image not found: {input_image}")
        print("Add an input image named 'input.png' to run this example.")
        return

    save_jpeg_with_selected_qtables(
        input_image=input_image,
        output_jpeg=output_jpeg,
        luminance_tables=luminance_tables,
        chrominance_tables=chrominance_tables,
        luminance_index=0,
        chrominance_index=0,
        subsampling="4:2:0",
    )

    print(f"Saved JPEG with Hub qtables: {output_jpeg}")


if __name__ == "__main__":
    main()
