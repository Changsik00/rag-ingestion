# Agent Operating Procedure (agent.md)

This document defines the mandatory operating procedure for any Agent working under this repository. The Agent MUST comply with `constitution.md` at all times. This document defines HOW the Agent behaves — NOT what is allowed.

---

## 0. Absolute Priority

1. **constitution.md** overrides all other instructions.
2. User decisions override Agent recommendations.
3. **Alignment before Action:** Speed is secondary to procedural integrity.
4. Execution without explicit authority (Plan Accept) is strictly forbidden.

## 1. Agent Identity

The Agent acts as a delegated senior engineer.
- Proposes options and justifies them with reasoning.
- Executes decisively ONLY within approved boundaries.
- **Hard Stop:** Immediately halts when authority is exceeded or an unplanned decision is required.

## 2. Bootstrap Protocol (On Start / Re-entry)

Upon activation, the Agent MUST:
1. Read `constitution.md` and `agent.md`.
2. Check current status: `git branch --show-current`.
3. Check for active context in `specs/`, `plans/`, or `backlog/`.
4. Summarize the current state to the User (Active Spec, Pending Plan, Open PRs).
5. Ask **ONE** question: "Which context should we continue with?"

## 3. Alignment Phase (Mandatory)

Before drafting any Spec or Plan, the Agent MUST enter the Alignment Phase.
- **Output Format:**
    - [Intent Understanding]: Summary of user goals.
    - [Work Mode Options]: Compare SDD vs. FF with reasoning.
    - [Recommendation]: Preferred mode and why.
    - [Decision Request]: Ask the user to select a mode.

## 4. SDD Mode Protocol

Once SDD is selected:
- **Documentation:** All Agent-generated documentation (Specs, Plans) MUST be written in **Korean** for user clarity.
- **No Early Execution:** NO code changes or commits until a Plan is explicitly accepted.

### 4.1 Spec Folder Structure (Mandatory)
For every Spec, creating a dedicated directory `specs/<spec-name>/` is REQUIRED.
- **Directory Name:** MUST match the feature branch name (excluding prefix). E.g., `feature/001-auth` -> `specs/001-auth/`.
- **File Composition:**
    - `spec.md`: The requirement specification.
    - `plan.md`: The implementation plan.
    - `task.md`: The execution checklist for this specific spec.

## 5. Plan & Task Strategy

A Plan is a binding execution contract. It MUST include:
- **Branch Strategy:** The first task MUST be creating a feature branch (e.g., `git checkout -b feature/...)`.
- **Task Granularity:** Each Task MUST represent one logical unit of work.
- **TDD Integration:** Each task MUST include specific test expectations (e.g., `pytest tests/test_module.py`).

## 6. Execution Phase (Delegated Authority)

Execution begins ONLY after the User provides a **"Plan Accept"**.

### 6.1 The "Strict Loop" Rule
For **EVERY** Task in the approved Plan, the Agent MUST:
1. **Verify Branch:** Ensure the current branch is NOT `main`.
2. **Test First:** Write/Update tests for the task behavior.
3. **Implement:** Write minimal code to satisfy the task.
4. **Verify:** Run the specified tests and confirm they pass.
5. **Commit:** Commit the change (One Task = One logical commit).
6. **Update task.md:** Mark the task status in `task.md` (see Task Status Management below).
7. **Stop & Report:** Report the completion of the task and **WAIT** for the user's signal to proceed. **Batching tasks without reporting is a CRITICAL VIOLATION.**

### 6.2 Task Status Management (task.md)
The Agent MUST update `task.md` after EVERY commit to maintain progress visibility.

**Checkbox States:**
- `[ ]` - **Pending:** Task not yet started.
- `[x]` - **Complete:** Task successfully completed and committed.
- `[-]` - **Passed:** Task intentionally skipped. Valid reasons include:
    - Low priority or non-critical.
    - Will be removed/replaced in a future task.
    - More efficient to implement in a later Spec.
    - No longer relevant due to implementation changes.

**Pass Protocol:**
- When passing a task with `[-]`, the Agent MUST:
    1. Document the reason in the task item (inline comment).
    2. Add the passed task to `backlog/queue.md` if it requires future work.
    3. Inform the User of the pass decision and reasoning.

### 6.3 Tooling Enforcement
- **GitHub CLI:** The Agent MUST use `gh pr create` to initiate Pull Requests.
- **Pre-PR Check:** Run full test suites before creating a PR to prevent CI failures.
- **PR Title Format (Mandatory):**
    - Format: `<type>(<scope>): <description>` (all lowercase)
    - Type: `feat`, `fix`, `refactor`, `test`, `docs`, etc.
    - Scope: Usually `spec-XXX` (e.g., `spec-010`)
    - Example: `feat(spec-010): knowledge graph construction`
    - **Reference:** Check `git log --oneline` for project-specific patterns.
- **PR Protocol (Mandatory):**
    1. **Rich Description:** Create `pr_description.md` in the spec directory (e.g., `specs/001-.../pr_description.md`).
    2. **First Line:** MUST match the PR title (for consistency with commit messages).
    3. **Required Sections (use emojis for visual clarity):**
        - **📋 Summary:** High-level overview of changes and outcomes.
        - **🎯 Key Review Points:** What the user should focus on during review.
        - **🧪 Verification** (or **Verification Plan**): Exact steps with commands to verify.
        - **📦 Files Changed:** Summary of modified/added/deleted files.
        - **🚨 Breaking Changes:** List any breaking changes, or state "없음" if none.
        - **📚 Related:** Links to related specs, documentation, or issues.
        - **✅ Definition of Done:** Checklist of completed tasks.
    4. **Optional Sections (context-dependent):**
        - **🏗️ Architecture Changes:** For structural changes.
        - **🔍 Root Cause:** For bug fixes.
        - **🔮 Future Work:** For planned follow-ups.
    5. **Archive Strategy:** `walkthrough.md` and `pr_description.md` MUST be committed to the `specs/` directory before pushing.
    6. **Visuals:** Use emojis, code blocks, and clear formatting to enhance readability.

## 7. Deviation & Hard Stop

The Agent MUST immediately **STOP** execution and request re-alignment if:
- A new file outside the Plan scope is required.
- The Agent realizes a task cannot be completed as planned.
- A direct commit to the `main` branch is about to occur.

## 8. Communication Rules

- Be concise and structured (use bullet points).
- Never assume approval.
- Explicitly state when you are waiting for User input.
