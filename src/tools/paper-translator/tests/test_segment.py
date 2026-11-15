import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "tools"))

from segment import segment_tex


def test_segment_splits_sections():
    tex = r"""
\section{Intro}
Text here.
\section{Method}
More text with $x^2$ math.
"""
    segs = segment_tex(tex)
    assert len(segs) >= 2
    sections = [s["section"] for s in segs]
    assert "Intro" in sections
    assert "Method" in sections


def test_segment_preserves_latex_commands():
    tex = r"See \cite{Curlander1991} and $\rho_{\text{rg}}$."
    segs = segment_tex(tex)
    raw = segs[0]["raw"]
    assert r"\cite{Curlander1991}" in raw
    assert r"$\rho_{\text{rg}}$" in raw


def test_segment_handles_nested_environment():
    tex = r"""
\begin{figure}
  \begin{center}
    \includegraphics{fig.png}
  \end{center}
\end{figure}
"""
    segs = segment_tex(tex)
    assert len(segs) == 1
    assert r"\begin{figure}" in segs[0]["raw"]
    assert r"\end{figure}" in segs[0]["raw"]


def test_segment_splits_on_paragraph():
    tex = r"\section{Intro}\paragraph{First} First para.\paragraph{Second} Second para."
    segs = segment_tex(tex)
    sections = [s["section"] for s in segs]
    assert "Intro" in sections
