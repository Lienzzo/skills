# Lienzzo skills

Agent skills by [Lienzzo](https://github.com/Lienzzo), in the open [Agent Skills](https://agentskills.io) format. They work with Claude Code, Cursor, Codex, GitHub Copilot and any agent the [`skills`](https://skills.sh) CLI supports.

```bash
npx skills add Lienzzo/skills --skill ux-top-tier
```

## ux-top-tier

Senior UX/UI audit and «top tier» redesign of any software (admin, back-office, CRM, SaaS, dashboard, app or website), in the spirit of Linear and v0: frictionless, dense and calm, never the «vibecoding» look.

**What it delivers**

1. **A prioritised audit report**: root causes, P0 findings, end-to-end flows today vs. target, findings by module, a new information architecture, a phased plan with quick wins and metrics.
2. **A clickable prototype** of every redesigned screen, with Before/After notes on each one. By default a single HTML page with no dependencies (state, undo, real keyboard shortcuts, ⌘K, light and dark themes); on Claude Code with claude.ai artifacts it can use the Design canvas instead.
3. **A minimal-friction pass on high-use screens**: serial work that opens the next item, undo instead of confirm, visible shortcuts, inline actions, useful defaults and live counters.

**How it works.** It gathers context first (URL and environment, repo, roles, most-used screens, reported pains, brand), walks the real app by task and reads the code, then measures friction and groups findings into root causes. For a narrow request («review this form») it runs a quick mode and answers in chat.

**Safety.** Production is read-only: it opens forms and dialogs but never submits, saves or deletes. The user logs in; the agent never types credentials. Real people are anonymised in the report and the prototype uses fictional data.

**Requirements.** A browser the agent can drive (e.g. Claude in Chrome) to walk the app; without one it works from screenshots. Python 3 and Node for the QA scripts.

**Language.** The instructions are written in Spanish. The agent answers and writes the deliverables in the user's language.

```
skills/ux-top-tier/
├── SKILL.md                 process, phases and lessons learned
├── references/              intake, senior lens, report template, design language,
│                            high-use standard, prototype formats, QA checklist, subagent briefs
├── scripts/                 lint_boards.py · scan_ui.py · check_logic.js · build_canvas.py
└── assets/                  prototype-template.html · canvas board and sidebar templates · layout example
```

---

### En español

Auditoría UX/UI de nivel senior y rediseño «top tier» de cualquier software, inspirado en Linear y v0: sin fricción y sin estética «vibecoding». Reúne el contexto, recorre la app real y el código, y entrega un informe priorizado, un prototipo navegable con notas «Antes / Ahora» y un pulido de fricción mínima en las pantallas de uso intensivo.

Instalación: `npx skills add Lienzzo/skills --skill ux-top-tier`

## License

[MIT](LICENSE)
