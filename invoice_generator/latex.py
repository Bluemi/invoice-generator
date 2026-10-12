import shutil
from pathlib import Path
import subprocess
import tempfile
import re

TEX_NAME = 'tmp'


def create_pdf(latex_str: str, output_path: Path) -> None:
    output_path = Path(output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_input_file = Path(tmpdir) / f'{TEX_NAME}.tex'
        with open(tmp_input_file, mode='w') as f:
            f.write(latex_str)
        # '-' instructs tectonic to read LaTeX source from stdin.
        # The output is always named 'texput.pdf' in the specified --outdir.
        proc = subprocess.run(
            ["tectonic", "-o", tmpdir, str(tmp_input_file)],
            text=True,
            capture_output=True,
        )

        if proc.returncode != 0:
            raise RuntimeError(f"Tectonic compilation failed:\n{proc.stderr}")

        gen_path = (Path(tmpdir) / f'{TEX_NAME}.pdf')
        shutil.move(gen_path, output_path)


def latex_escape(text: str) -> str:
    """
    Escapes special characters and German umlauts in a string for safe use in LaTeX.
    """
    # Character mapping for LaTeX equivalents
    latex_map = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
        '"': r"\textquotedbl{}",
        # German Umlauts and Eszett
        "ä": r'\"a',
        "ö": r'\"o',
        "ü": r'\"u',
        "Ä": r'\"A',
        "Ö": r'\"O',
        "Ü": r'\"U',
        "ß": r"\ss{}",
    }

    # Match any character present in the dictionary keys
    pattern = re.compile("|".join(re.escape(k) for k in latex_map.keys()))
    return pattern.sub(lambda match: latex_map[match.group(0)], text)
