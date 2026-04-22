"""Example script to save a JPEG with selected quantization tables using Pillow.

The script loads luminance/chrominance tables from JSON files, chooses one flat
64-value table for each component, and uses them during JPEG compression.
"""

from __future__ import annotations

import importlib
import json
from pathlib import Path

QuantizationTable = list[int]
QuantizationTables = list[QuantizationTable]


def load_quantization_tables(base_dir: Path) -> tuple[QuantizationTables, QuantizationTables]:
	"""Load luminance and chrominance quantization tables from JSON files.

	Args:
		base_dir: Directory containing quantification_luminance.json and
			quantification_chrominance.json.

	Returns:
		A tuple containing luminance tables and chrominance tables.
	"""
	base_path = Path(base_dir)

	luminance_tables = json.loads(
		(base_path / "quantification_luminance.json").read_text(encoding="utf-8")
	)
	chrominance_tables = json.loads(
		(base_path / "quantification_chrominance.json").read_text(encoding="utf-8")
	)

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
	"""Run a minimal example of JPEG compression with selected qtables.

	Args:
		None.

	Returns:
		None.
	"""
	base_dir = Path(".")
	input_image = base_dir / "input.png"
	output_jpeg = base_dir / "output_custom_qtables.jpg"

	luminance_tables, chrominance_tables = load_quantization_tables(base_dir)

	print(f"Loaded luminance tables: {len(luminance_tables)}")
	print(f"Loaded chrominance tables: {len(chrominance_tables)}")

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

	print(f"Saved JPEG with selected qtables: {output_jpeg}")


if __name__ == "__main__":
	main()