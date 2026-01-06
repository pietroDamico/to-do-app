# Agent-Driven Development Methodology

This document describes the **agent-driven development methodology** used in this project - a systematic approach to software development where AI agents collaborate under human oversight to deliver traceable, high-quality software.

**Audience**: Development teams looking to implement AI-agent-based development workflows.

---

## Table of Contents

1. [Overview](#overview)
2. [Core Principles](#core-principles)
3. [Architecture: HL/LL Agent Model](#architecture-hlll-agent-model)
4. [Requirements Traceability](#requirements-traceability)
5. [GitHub-Native Workflow](#github-native-workflow)
6. [Workflow Phases](#workflow-phases)
7. [Quality Gates](#quality-gates)
8. [Benefits and Challenges](#benefits-and-challenges)
9. [Adapting This Methodology](#adapting-this-methodology)

---

## Overview

This methodology implements a **hierarchical agent coordination system** where:

- A **High-Level (HL) Agent** works with a **human** to decompose requirements into executable tasks
- Multiple **Low-Level (LL) Agents** implement tasks autonomously with clear specifications
- All work is **fully traceable** from requirements through to merged code
- **GitHub** serves as the single source of truth for coordination

**Key Innovation**: Separation of concerns between strategic decomposition (HL) and tactical implementation (LL), with humans providing oversight and final decision-making.

---

## Core Principles

### 1. Traceability First
Every artifact must trace back to requirements. No "orphan" work without clear justification.

**Chain**: `Code → PR → Task → Epic → Requirements → Documentation`

### 2. Explicit Over Implicit
Everything must be written down:
- Acceptance criteria (not "make it work")
- Risks and mitigations (not "be careful")
- Dependencies (not "figure it out")
- Test requirements (not "add some tests")

### 3. Verifiable Completion
"Done" must be objectively verifiable through checklists, not subjective judgment.

### 4. Atomic Work Units
Each task should ideally result in ONE pull request with a clear, testable outcome.

### 5. Quality Gates
Security, testing, and observability are mandatory, not optional.

### 6. GitHub as Source of Truth
All coordination happens through GitHub artifacts (issues, PRs, projects). No external task trackers.

---

## Architecture: HL/LL Agent Model

### The HL Agent (High-Level Orchestrator)

**Role**: Strategic decomposition and coordination

**Responsibilities**:
- Parse and structure requirements documents
- Assign stable requirement IDs (REQ-xxx)
- Decompose requirements into epics (macro-features)
- Break epics into implementable tasks
- Define acceptance criteria and test requirements
- Map dependencies between tasks
- Review LL agent output for integration
- Maintain architectural coherence

**Key Artifact**: System prompt defining decomposition methodology and quality standards

**Collaboration**: Works in partnership with human for:
- Resolving ambiguities
- Making architectural decisions
- Approving decomposition plans
- Final PR approval

### The LL Agent (Low-Level Implementer)

**Role**: Tactical implementation

**Responsibilities**:
- Retrieve assigned task from GitHub
- Implement solution following specifications
- Write comprehensive tests (minimum 80% coverage)
- Create pull request with full traceability
- Iterate based on review feedback

**Key Artifact**: Generic implementation prompt with quality standards and PR template

**Autonomy**: Works independently within task boundaries; asks questions only for blockers

### The Human

**Role**: Decision maker and quality arbiter

**Responsibilities**:
- Provide initial requirements
- Resolve ambiguities flagged by HL agent
- Make product/architectural decisions
- Review and approve/reject PRs
- Monitor overall progress
- Intervene on quality issues

**Critical**: Humans provide context AI agents cannot infer (business priorities, user needs, strategic direction)

---

## Requirements Traceability

### Requirements Document Structure

Requirements are version-controlled files in the repository:

```
docs/
  requirements/
    requirements-v1.md
    requirements-v2.md
    ...
```

Each requirement has:
- **Stable ID**: `REQ-001`, `REQ-002`, etc.
- **Description**: What needs to be built
- **Priority**: High/Medium/Low
- **Dependencies**: Links to other requirements
- **Acceptance Criteria**: Verifiable conditions for completion
- **Risks**: Identified concerns and mitigations

### Traceability Chain

```
requirements-v1.md
    ↓ (contains)
REQ-001, REQ-002, REQ-003
    ↓ (grouped into)
Epic: Feature Name (GitHub Issue with 'epic' label)
    ↓ (broken down into)
Task: Specific Implementation (GitHub Issue)
    ↓ (implemented in)
Pull Request (references task)
    ↓ (merged into)
Code in Repository
```

### Maintaining Traceability

Every GitHub artifact must reference its parent:

- **Epic**: Lists covered requirements (REQ-xxx)
- **Task**: Links to epic and requirements
- **PR**: References task ("Closes #X"), epic, and requirements
- **Commit messages**: Include requirement IDs

**Verification**: Any piece of code can be traced back to a specific requirement.

---

## GitHub-Native Workflow

All coordination happens through GitHub features. No external tools required.

### 1. Issues as Work Units

**Epics** = GitHub Issues with `epic` label
- Contain: objectives, scope, requirements covered, definition of done, task list
- Link to child task issues

**Tasks** = GitHub Issues assigned to LL agents
- Contain: acceptance criteria, implementation details, test requirements, risks
- Link to parent epic and requirements

### 2. Labels for Organization

**Epic identification**: `epic`

**Agent assignment**: `agent:ll-1`, `agent:ll-2`, `agent:ll-N`

**Work type**: `backend`, `frontend`, `testing`, `documentation`

**Priority**: `priority:high`, `priority:medium`, `priority:low`

**Status** (optional): `blocked`, `in-review`, `ready`

### 3. Pull Requests for Delivery

Each completed task results in a PR with:
- **Title**: `<Task Description> (REQ-xxx) #<issue-number>`
- **Description**: Summary, changes, testing, security, rollout notes
- **Links**: `Closes #<issue>`, references to epic and requirements
- **Base branch**: Default branch (e.g., `dev`) for auto-close to work

### 4. Project Boards for Visibility

Optional but recommended: GitHub Project Board with columns:
- **Intake**: New requirements/requests
- **Decomposed**: Epics/tasks defined, ready for assignment
- **In Progress**: Actively being worked on
- **Review**: PR submitted, awaiting review
- **Done**: Merged and verified

Custom fields:
- Priority
- Area (backend/frontend/infra)
- Risk level
- Assignee/Agent
- Release/Milestone

### 5. Branches Strategy

```
main (production-ready)
  ↓
dev (integration branch - set as default for auto-close)
  ↓
feature/* (agent work branches)
  - feature/user-registration
  - feature/login-ui
  - feature/todo-crud
```

**Flow**:
1. LL agent creates feature branch from `dev`
2. LL agent implements and commits
3. LL agent creates PR: `feature/x → dev`
4. Human/HL reviews and merges
5. Issue auto-closes (if `dev` is default branch)
6. Periodically: `dev → main` for releases

---

## Workflow Phases

### Phase 1: Requirements Gathering

**Actors**: Human + HL Agent

**Activities**:
1. Human provides requirements (document, user stories, feature requests)
2. HL Agent structures requirements into atomic units
3. HL Agent assigns stable IDs (REQ-xxx)
4. HL Agent identifies dependencies and priorities
5. Human reviews and approves requirements document
6. Requirements committed to repository (`docs/requirements/`)

**Output**: Versioned requirements document

---

### Phase 2: Epic Decomposition

**Actors**: HL Agent + Human

**Activities**:
1. HL Agent groups related requirements into epics
2. For each epic, HL Agent defines:
   - Objective and scope
   - Requirements covered
   - Dependencies on other epics
   - Decisions and assumptions
   - Risk assessment
   - Definition of done
3. HL Agent creates epic as GitHub Issue with `epic` label
4. Human reviews epic structure

**Output**: Epic issues in GitHub

---

### Phase 3: Task Breakdown

**Actors**: HL Agent

**Activities**:
1. HL Agent breaks each epic into implementable tasks
2. For each task, HL Agent defines:
   - Context (epic + requirements)
   - Acceptance criteria (verifiable bullets)
   - Implementation guidance (architecture, code examples)
   - Required tests (unit/integration/e2e)
   - Security considerations
   - Observability requirements
   - Rollout/rollback notes
3. HL Agent identifies task dependencies
4. HL Agent creates task as GitHub Issue linked to epic
5. HL Agent assigns task to LL agent (via label or assignee)

**Output**: Task issues in GitHub, ready for implementation

---

### Phase 4: Implementation

**Actors**: LL Agents

**Activities** (per task):
1. LL Agent retrieves assigned task from GitHub
2. LL Agent verifies dependencies are complete
3. LL Agent creates feature branch
4. LL Agent implements solution following specifications
5. LL Agent writes tests (minimum 80% coverage)
6. LL Agent runs tests locally, ensures all pass
7. LL Agent commits with descriptive message including requirement IDs
8. LL Agent pushes feature branch
9. LL Agent creates PR with full description and traceability links

**Output**: Pull request ready for review

---

### Phase 5: Review & Integration

**Actors**: Human + HL Agent

**Activities**:
1. Review PR for:
   - Acceptance criteria met (from task)
   - Tests included and passing
   - Security risks mitigated
   - Code quality acceptable
   - Traceability maintained (links to issue/epic/requirements)
   - No breaking changes (unless documented)
2. If issues found: request changes, LL agent iterates
3. If acceptable: approve and merge PR
4. Issue auto-closes (if using default branch)
5. HL Agent verifies integration with existing code

**Output**: Code merged into integration branch, issue closed

---

### Phase 6: Release

**Actors**: Human + HL Agent

**Activities**:
1. When epic is complete (all tasks done), verify definition of done
2. Perform end-to-end testing
3. Create release PR: `dev → main`
4. Deploy to production (if applicable)
5. Close epic issue
6. Document release notes

**Output**: Production release, completed epic

---

## Quality Gates

These are **mandatory** checks enforced at task definition and PR review.

### 1. Testing Requirements

Every task must specify:
- Minimum test types required (unit/integration/e2e)
- Specific scenarios to test
- Target coverage (minimum 80%)

Every PR must include:
- Tests for all new code
- Tests for error cases, not just happy path
- All tests passing in CI (if configured)

### 2. Security Requirements

Every task must identify:
- OWASP risks relevant to the change (injection, XSS, CSRF, authz, secrets, etc.)
- Specific mitigations required

Every PR must demonstrate:
- No hardcoded secrets
- Input validation where applicable
- Secure defaults (e.g., password hashing, HTTPS, etc.)

### 3. Observability Requirements

For tasks involving I/O or external services:
- Logging strategy defined
- Error handling specified
- Metrics/monitoring considered (if applicable)

### 4. Documentation Requirements

For significant changes:
- API documentation updated
- README updated if setup changes
- Code comments for complex logic
- Environment variables documented in `.env.example`

### 5. Traceability Requirements

Every PR must:
- Reference the task issue ("Closes #X")
- Reference the epic
- Reference the requirements (REQ-xxx)
- Include rationale for significant design decisions

---

## Benefits and Challenges

### Benefits

**1. Complete Traceability**
- Every line of code traces to a requirement
- Audit trail from idea to implementation
- Easy to understand "why" code exists

**2. Parallel Development**
- Multiple LL agents work simultaneously
- Dependencies clearly mapped prevent conflicts
- Faster delivery than sequential development

**3. Consistent Quality**
- Quality gates enforced uniformly
- No "forgotten" tests or documentation
- Security considered upfront

**4. Reduced Cognitive Load**
- HL agent handles strategic complexity
- LL agents focus on tactical implementation
- Humans focus on decisions, not minutiae

**5. Knowledge Preservation**
- Requirements and decisions documented
- Architecture rationale captured in epics/tasks
- New team members can onboard via GitHub history

**6. Flexibility**
- Easy to reassign tasks between agents
- Can add/remove agents as needed
- Human can intervene at any point

### Challenges

**1. Upfront Planning Overhead**
- Decomposition takes time before coding starts
- May feel slow for very simple features
- Requires discipline to maintain structure

**2. Agent Coordination**
- LL agents may interpret tasks differently
- Merge conflicts if dependency management fails
- Requires clear, unambiguous task specifications

**3. Human Bottleneck**
- Humans must review all PRs
- Decisions require human input
- Can slow down if human is unavailable

**4. Tooling Dependencies**
- Relies on GitHub features working correctly
- Agents need API access and proper permissions
- Changes to GitHub API can break workflow

**5. Learning Curve**
- Team must understand the methodology
- Agents need proper prompts and training
- Initial setup requires investment

---

## Adapting This Methodology

### For Different Project Types

**Small projects** (<10 tasks):
- Skip epics, work directly with tasks
- Single LL agent sufficient
- Simpler review process

**Large projects** (>50 tasks):
- Add sub-epics for organization
- More LL agents in parallel
- Introduce integration testing phase
- Consider staged releases

**Research/experimental**:
- Looser acceptance criteria
- Emphasize documentation over tests
- More iteration expected

### For Different Teams

**Solo developer + agents**:
- Developer acts as human + HL agent
- LL agents handle implementation
- Faster decisions, less overhead

**Team of humans + agents**:
- Distribute HL review across team
- Use GitHub code owners for PR routing
- Add human pair programming with agents

**Enterprise setting**:
- Add compliance gates (security scans, legal review)
- Integrate with existing project management tools
- Add release approval workflows

### Technology Adaptations

This methodology is **technology agnostic**. It works with:
- Any programming language
- Any framework (web, mobile, embedded, etc.)
- Any architecture (monolith, microservices, serverless)
- Any deployment target (cloud, on-prem, edge)

**Key**: Adapt the task templates and quality gates to your stack's best practices.

---

## Conclusion

The **Agent-Driven Development Methodology** provides a structured approach to leverage AI agents for software development while maintaining human oversight, quality standards, and complete traceability.

**Core Success Factors**:
1. Clear separation between HL (strategic) and LL (tactical) concerns
2. Everything documented in GitHub for transparency
3. Mandatory quality gates enforced consistently
4. Human involvement at decision points
5. Traceability from requirements to code

This methodology is **iterative** - it can be refined based on team experience and project needs. The key is maintaining the core principles while adapting the details to your context.
