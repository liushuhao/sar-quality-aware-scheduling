@echo off
rem Chinese manuscript build: bibtex FIRST, then xelatex twice.
rem Running xelatex alone leaves newly added citations as "(?)" in the PDF
rem (2026-11-02 incident: three added keys showed up undefined).
cd /d "%~dp0"
bibtex small-paper-ijae-zh
xelatex -interaction=nonstopmode -halt-on-error small-paper-ijae-zh
xelatex -interaction=nonstopmode -halt-on-error small-paper-ijae-zh
