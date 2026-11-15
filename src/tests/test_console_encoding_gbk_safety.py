"""Console-encoding guard (GBK 控制台): 打印不可编码字符的脚本必须自带兜底。

故障模式（本仓库 Windows 默认控制台=cp936/GBK）：
脚本 `print()` 里出现 GBK 编不出的字符（± − Δ ≈ ✓ ⚠ ← 等）→
UnicodeEncodeError 直接崩。2026-11-09 `analyze_acquisition_delay.py`
打印 "%.0f±%.0f ... Δ(3−2)" 实测崩在第一次输出。

这是同一根因的第二犯（第一犯 2026-11-05：subprocess text=True 用 GBK 解
UTF-8 中文，修法=encoding='utf-8'+PYTHONIOENCODING+被调脚本 reconfigure）。
按「二犯即闸」把判据机械化为本测试：受管脚本若要打印 GBK 不支持的字符，
必须显式 reconfigure（或 encode(errors=...)）兜底，否则红。

判据：解析每个受管 .py 的 print(...) 实参，取其中 >127 的字符，
GBK 编码失败的集合非空且文件未做 stdout 兜底 → 失败。
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]

# 受管面：会被人手工运行、输出直连控制台的脚本。archive/ 是历史快照，不修。
MANAGED = [
    REPO / "src",
    REPO / "papers/single-sat-quality/experiments",
    REPO / "papers/single-sat-quality/scripts",
    REPO / "papers/constellation-scheduling/experiments",
    REPO / "papers/sliding-spotlight-scheduling",
    REPO / "literature/scripts",
]
SKIP_PARTS = {"archive", "__pycache__", ".git", "build", ".scratch"}

GUARD_TOKENS = (
    "reconfigure(encoding",
    "reconfigure(errors",
    "sys.stdout = io.TextIOWrapper",
    "PYTHONIOENCODING",
)


def _managed_files():
    seen = set()
    for root in MANAGED:
        if not root.exists():
            continue
        for p in sorted(root.rglob("*.py")):
            if SKIP_PARTS & set(p.parts):
                continue
            if p in seen:
                continue
            seen.add(p)
            yield p


def _gbk_unsafe_print_chars(src: str) -> set[str]:
    """Chars used inside print(...) that cp936 cannot encode."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return set()
    bad: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        name = getattr(fn, "id", None) or getattr(fn, "attr", None)
        if name != "print":
            continue
        chunk = ast.get_source_segment(src, node) or ""
        for ch in chunk:
            if ord(ch) < 128:
                continue
            try:
                ch.encode("gbk")
            except UnicodeEncodeError:
                bad.add(ch)
    return bad


def _has_guard(src: str) -> bool:
    return any(tok in src for tok in GUARD_TOKENS)


@pytest.mark.parametrize("py", list(_managed_files()), ids=lambda p: str(p.relative_to(REPO)))
def test_printable_chars_survive_gbk_console(py: Path):
    src = py.read_text(encoding="utf-8", errors="ignore")
    bad = _gbk_unsafe_print_chars(src)
    if not bad:
        return
    if _has_guard(src):
        return
    pytest.fail(
        f"{py.relative_to(REPO)} 的 print() 含 GBK 控制台编不出的字符 "
        f"{''.join(sorted(bad))!r}，且文件未做 stdout 兜底。\n"
        "修法（任选）：文件顶部加\n"
        "    if hasattr(sys.stdout, 'reconfigure'):\n"
        "        sys.stdout.reconfigure(encoding='utf-8')\n"
        "或改用可 GBK 编码的替代字符。"
    )


def test_guard_detects_known_bad_and_good():
    """判别力自测：坏样例必红、好样例必绿（防空跑假绿）。

    样例字符选择有讲究：± (U+00B1) **GBK 可编码**，不能当坏样例
    （会造恒绿假闸，本测试自身首版就是这个 bug）；真正编不出的是
    − (U+2212 减号)、Δ、✓ 等。
    """
    bad_src = 'print("%.1f\u2212%.1f" % (1.0, 2.0))\n'
    good_src = (
        "import sys\n"
        "if hasattr(sys.stdout, 'reconfigure'):\n"
        "    sys.stdout.reconfigure(encoding='utf-8')\n"
        'print("%.1f\u2212%.1f" % (1.0, 2.0))\n'
    )
    plain_src = 'print("plain ascii and \u4e2d\u6587 all GBK-encodable")\n'
    assert _gbk_unsafe_print_chars(bad_src) == {"\u2212"}
    assert not _has_guard(bad_src)
    assert _has_guard(good_src)
    assert _gbk_unsafe_print_chars(plain_src) == set()
    assert "±".encode("gbk")  # 反例钉住：± 可编码，不得进坏集
    assert _gbk_unsafe_print_chars('print("±")\n') == set()
