"""Code execution tool with local sandbox limits."""

import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict

from core.tools.base import Tool


class CodeExecutionTool(Tool):
    name = "code_exec"
    description = "Run Python code in a constrained local sandbox"
    params_schema = {"code": {"type": "string"}}
    permissions = ["sandbox"]

    def __call__(self, **kwargs: Any) -> Dict[str, Any]:
        code = str(kwargs.get("code", ""))
        with tempfile.TemporaryDirectory() as tmp_dir:
            script_path = Path(tmp_dir) / "script.py"
            script_path.write_text(code, encoding="utf-8")
            proc = subprocess.run(
                ["python3", str(script_path)],
                cwd=tmp_dir,
                capture_output=True,
                text=True,
                timeout=5,
            )
            return {
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "returncode": proc.returncode,
            }

