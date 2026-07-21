# Paper Translator

Structured review workflow for English LaTeX papers.

## Workflow

1. **Segment**: `python src/tools/paper-translator/segment.py papers/single-sat-quality/small-paper-ijae.tex`
   - Produces `src/tools/paper-translator/output/segments.json`
2. **Translate**: Agent reads `segments.json` and writes `translations.json`
   - Produces `src/tools/paper-translator/output/translations.json`
3. **Annotate**: `python src/tools/paper-translator/annotate.py`
   - Reads `segments.json` + `translations.json`
   - Produces `src/tools/paper-translator/output/comparison.md`
4. **User review**: Edit `comparison.md` — fill `chinese_translation` and `your_annotation`
5. **Merge**: `python src/tools/paper-translator/merge.py`
   - Reads `comparison.md` + original `.tex`
   - Writes `<stem>.revised.tex` next to the original file

## Outputs

- `src/tools/paper-translator/output/segments.json`
- `src/tools/paper-translator/output/translations.json`
- `src/tools/paper-translator/output/comparison.md`
- `<original-stem>.revised.tex` beside the source `.tex`

## Design

- Segmentation preserves LaTeX environments as atomic blocks via FSM depth tracking.
- Translation is agent-driven, not API-driven, to leverage SAR domain knowledge.
- Annotations live in Markdown for easy review.
- Merger writes `.revised.tex` by default; original never overwritten in-place.
