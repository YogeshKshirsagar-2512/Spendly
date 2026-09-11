---
name: spec-doc
description: >-
  Creates a detailed, production-ready feature specification document ("spec doc") for any proposed
  or requested feature. Triggers when the user runs the `/spec-doc` slash command or asks to write a feature spec.
---

# Feature Specification Document Generator (`/spec-doc`)

Use this skill whenever the user invokes `/spec-doc [feature name or details]` or requests a specification document (spec doc) for a feature.

This skill produces an exhaustive, high-quality technical specification aligned with the repository's architecture, conventions, and design system.

---

## Workflow Instructions

When this command is triggered, execute the following steps:

### 1. Requirements Intake & Clarification
1. Extract the feature title and any details provided by the user in the prompt (e.g. `/spec-doc Recurring monthly subscriptions`).
2. If the feature scope is underspecified or ambiguous, identify the 2-3 most critical architectural or UX decisions and clarify them with the user before finalizing or draft sensible defaults while noting open assumptions.

### 2. Codebase & Context Exploration
Inspect the existing codebase to ensure the spec integrates seamlessly:
- Review [AGENTS.md](file:///C:/Users/Samsung/Downloads/expense-tracker/expense-tracker/AGENTS.md) for tech stack constraints, design tokens, route patterns, and testing conventions.
- Check current database schema in [database/db.py](file:///C:/Users/Samsung/Downloads/expense-tracker/expense-tracker/database/db.py).
- Check existing route handlers in [app.py](file:///C:/Users/Samsung/Downloads/expense-tracker/expense-tracker/app.py).
- Inspect existing templates in `templates/` and styles in `static/css/`.

### 3. Generate the Spec Document
Using the template structure from [resources/spec-template.md](./resources/spec-template.md), draft the complete specification document:
1. **Executive Summary & Problem Statement**: Clear explanation of user friction, proposed solution, in-scope vs. out-of-scope.
2. **User Stories & Acceptance Criteria**: Written in standard persona and Gherkin format (`Given / When / Then`).
3. **Architecture & Technical Design**:
   - Exact SQL table definitions or schema migrations (`sqlite3` compatible).
   - Route definitions (HTTP methods, endpoints, parameters, return codes, redirects).
   - Controller logic and helper functions needed.
4. **UI / UX Design & Presentation**:
   - Templates to create or update (extending `base.html`).
   - Reusable CSS classes (`.btn-primary`, `.auth-card`, etc.) and CSS variables (`var(--paper)`, `var(--accent)`, `var(--font-display)`).
   - Frontend JavaScript interactions in `static/js/main.js` (if any).
5. **Security, Validation & Edge Cases**:
   - Session authentication (`session['user_id']`).
   - Data ownership isolation (prevent cross-user access).
   - Edge cases (null values, negative amounts, boundary dates, empty states).
6. **Testing Strategy**:
   - Pytest unit and integration test plan for `tests/`.
   - Test cases for authenticated, unauthenticated, valid, and invalid inputs.
7. **Implementation Checklist**:
   - Phased, step-by-step checklist ready for execution.
8. **Git & GitHub Automation Rules**:
   - Target branch strategy (`feat/<feature-slug>` or `main`).
   - Pre-commit verification commands (`pytest`, syntax checks).
   - Conventional Commit definitions for the feature.
   - GitHub Actions CI trigger specifications.
   - Pull Request template with title and markdown description.

### 4. Output & Persistence
1. Save the generated document into the workspace at:
   `docs/specs/<feature-slug>-spec.md` (create the directory if it does not exist).
2. Present a concise summary of the generated spec to the user, with:
   - A clickable link to the created spec file.
   - Key highlights (Data model changes, new routes, UI components, Git actions).
   - Recommended next step (e.g. "Run `/plan` or begin Phase 1 implementation").

### 5. Autonomous Git & GitHub Actions (Executed on User's Behalf)
Whenever generating a spec, updating it, or completing feature implementation milestones:
1. **Branch & State Inspection**: Inspect `git status`, branch name, and untracked files.
2. **Quality Gate Execution**: Run test suites (`pytest`) and verify clean passes before committing.
3. **Automated Staging & Commits**: Proactively stage modified files (`git add`) and craft structured Conventional Commits (`feat(...)`, `docs(...)`, `test(...)`).
4. **Push to GitHub**: Autonomously push commits to remote (`git push origin <branch>` or `git push origin main`) on behalf of the user.
5. **CI Monitoring**: Ensure the pushed commits trigger GitHub Actions (`.github/workflows/ci.yml`) cleanly.
