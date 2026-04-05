#!/usr/bin/env python
"""Convenience wrapper so deployments can run `python manage.py` from the repo root.

The real Django project lives in the `lgflagsite/` subfolder.
"""

import os
import runpy
import sys
from pathlib import Path


if __name__ == "__main__":
	project_dir = Path(__file__).resolve().parent / "lgflagsite"
	project_manage = project_dir / "manage.py"
	os.chdir(project_dir)
	sys.path.insert(0, str(project_dir))
	runpy.run_path(str(project_manage), run_name="__main__")
