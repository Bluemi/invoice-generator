from pathlib import Path
import subprocess
import tempfile


def create_pdf(latex_str: str, output_path: Path) -> None:
    output_path = Path(output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        # '-' instructs tectonic to read LaTeX source from stdin.
        # The output is always named 'texput.pdf' in the specified --outdir.
        proc = subprocess.run(
            ["tectonic", "-o", tmpdir, "-"],
            input=latex_str,
            text=True,
            capture_output=True,
        )

        if proc.returncode != 0:
            raise RuntimeError(f"Tectonic compilation failed:\n{proc.stderr}")

        (Path(tmpdir) / "texput.pdf").replace(output_path)
