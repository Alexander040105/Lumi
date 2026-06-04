from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class AdvancedHydrologyOutputs:
    hillshade_path: Optional[Path] = None
    flow_direction_path: Optional[Path] = None
    flow_accumulation_path: Optional[Path] = None


def generate_hillshade(dem_path: Path, output_path: Path, logger: logging.Logger) -> Optional[Path]:
    logger.warning("Hillshade generation disabled: richdem removed")
    return None


def generate_flow_products(dem_path: Path, output_dir: Path, logger: logging.Logger) -> AdvancedHydrologyOutputs:
    try:
        import whitebox
    except Exception:
        logger.warning("whitebox not available; skipping flow direction/accumulation")
        return AdvancedHydrologyOutputs()

    wbt = whitebox.WhiteboxTools()
    wbt.set_working_dir(str(output_dir))
    flow_dir = output_dir / "flow_direction.tif"
    flow_acc = output_dir / "flow_accumulation.tif"

    wbt.d8_pointer(str(dem_path), str(flow_dir))
    wbt.d8_flow_accumulation(str(dem_path), str(flow_acc))
    return AdvancedHydrologyOutputs(
        flow_direction_path=flow_dir,
        flow_accumulation_path=flow_acc,
    )
