---
mode: ask
description: 'UI UX Pro Max workflow for design-system-first UI/UX generation and implementation guidance'
---

Use the `ui-ux-pro-max` skill workflow for this request.

Steps:

1. Extract product type, style keywords, industry, and stack (default `html-tailwind`).
2. Run design system generation first:

```bash
python3 .github/prompts/ui-ux-pro-max/scripts/search.py "<query>" --design-system -p "<Project Name>"
```

3. If needed, run focused domain searches (`style`, `ux`, `typography`, `landing`, etc.).
4. Run stack guidance with `--stack`.
5. Implement concrete UI/UX output with accessibility and responsive behavior.

Return:

- Recommended visual direction
- Core layout + component decisions
- Color + typography system
- UX/accessibility checklist
- Implementation-ready guidance
