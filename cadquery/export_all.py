#!/usr/bin/env python3
"""Export all CadQuery/OpenCascade banana clip CAD files."""
from __future__ import annotations

import banana_clip_cq as model
import config_cq as CQ


def main() -> None:
    written = model.generate(CQ.OUTPUTS_STEP, CQ.OUTPUTS_CAD_STL)
    print("Generated CadQuery/OpenCascade outputs:")
    for path in written:
        print(" -", path.relative_to(CQ.ROOT))


if __name__ == "__main__":
    main()
