---
name: ui-ux-pro-max
description: 'Use when: designing or improving UI/UX, creating landing pages, dashboard redesigns, design systems, typography/color choices, accessibility polish, and implementation-ready frontend UI guidance in React/HTML/Tailwind/Next.js/Vue.'
---

# UI UX Pro Max Skill

Use this skill to turn product intent into an implementation-ready UI direction.

## When to use

Use this skill when the user asks to:

- design, redesign, improve, or review UI/UX
- create landing pages, dashboards, app screens, or design systems
- choose color palettes, typography, spacing, components, or visual style
- apply accessibility and UX best practices while implementing frontend code

## Workflow

1. Parse the request

- Extract product type, style keywords, industry, and target stack.
- If no stack is provided, default to `html-tailwind`.

2. Generate design system first (required)

```bash
python3 .github/prompts/ui-ux-pro-max/scripts/search.py "<product_type> <industry> <keywords>" --design-system -p "<Project Name>"
```

3. Add focused searches as needed

```bash
python3 .github/prompts/ui-ux-pro-max/scripts/search.py "<keyword>" --domain <domain>
```

Domains: `product`, `style`, `typography`, `color`, `landing`, `chart`, `ux`, `react`, `web`, `prompt`

4. Get stack-specific guidance

```bash
python3 .github/prompts/ui-ux-pro-max/scripts/search.py "<keyword>" --stack <stack>
```

Stacks: `html-tailwind`, `react`, `nextjs`, `vue`, `svelte`, `swiftui`, `react-native`, `flutter`, `shadcn`, `jetpack-compose`

5. Implement and validate

- Synthesize recommendations into concrete UI changes.
- Keep accessibility and responsive behavior first-class.
- Avoid generic layouts; choose a clear visual direction.

## Optional persistence

Persist the generated design system for follow-up pages:

```bash
python3 .github/prompts/ui-ux-pro-max/scripts/search.py "<query>" --design-system --persist -p "<Project Name>"
```

For page-specific override:

```bash
python3 .github/prompts/ui-ux-pro-max/scripts/search.py "<query>" --design-system --persist -p "<Project Name>" --page "<page-name>"
```

## Notes

- Use `.github/prompts/ui-ux-pro-max/scripts/search.py` path in this repository.
- If Python is missing, install Python 3 and retry.
