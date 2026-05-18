# DocQT - Improving-Document-Forgery-Localization-Robustness-via-Diverse-JPEG-Quantization-Tables

Repository containing JPEG quantization tables used for the Real-QT protocol.
Dataset name: DocQT.
Only header-extracted quantization matrices are provided.

## Available quantization tables

- Luminance tables: `quantification_luminance.json`
	- Number of tables: 859
- Chrominance tables: `quantification_chrominance.json`
	- Number of tables: 294

## File format

Both files are stored in JSON for better portability and long-term compatibility.

- Root object: a list of quantization tables
- One table: a flat list of 64 integers
- Table values: integers

In other words, each file follows this structure:

- list[table]
- table = list[64 integer values]

## Example: use quantization tables with Pillow JPEG compression

```python
import json
from pathlib import Path
from PIL import Image


def load_quantization_tables(base_dir: str = ".") -> tuple[list, list]:
	base_path = Path(base_dir)

	luminance_tables = json.loads(
		(base_path / "quantification_luminance.json").read_text(encoding="utf-8")
	)
	chrominance_tables = json.loads(
		(base_path / "quantification_chrominance.json").read_text(encoding="utf-8")
	)

	return luminance_tables, chrominance_tables

luminance_tables, chrominance_tables = load_quantization_tables(".")

# Choose the table indices you want to use for compression.
luma_idx = 0
chroma_idx = 0

luma_qtable = luminance_tables[luma_idx]
chroma_qtable = chrominance_tables[chroma_idx]

with Image.open("input.png") as image:
	image = image.convert("RGB")
	image.save(
		"output_custom_qtables.jpg",
		format="JPEG",
		qtables=[luma_qtable, chroma_qtable],
		subsampling="4:2:0",
		optimize=True,
	)

# Note: avoid passing a quality value if you want to keep your custom qtables as-is.
```
