# EduROOM — Project Changelog

This file tracks individual contributions from each member of the TechValks team throughout the development, deployment, and presentation of the EduROOM Classroom Reservation System on Microsoft Azure.

## Entry format

Each entry follows this format:

```
- YYYY-MM-DD — Specific description of the change or contribution.
```

Entries must be:

- Dated with the actual date the work was done.
- Specific and descriptive. Avoid vague phrases such as "fixed stuff" or "updated code." Name the file, the parameter, the resource, or the document section that was changed.
- Scoped to a single concrete change or deliverable.

## Required coverage

Entries across the team should collectively span:

- Architecture diagram updates
- Infrastructure as Code (IaC) scripts
- Cost report
- Presentation preparation
- Application code changes required for cloud deployment

---

## Blessie Faith Bongalos

- 2026-05-08 — Added the `schedule_type` ENUM('reservation', 'class') column and `idx_schedule_type` index to the `reservations` table in `eduroom_schema.sql`. Required for the production Azure MySQL deployment to support administrative class plotting alongside faculty reservations.

- 2026-05-09 — Implemented the Class Plotting / Bulk Schedule Input feature: added `ReservationModel.expand_recurring_schedule()` and `ReservationModel.bulk_create_class_schedules()` model methods in `data/models.py` with per-row conflict detection and transactional rollback on failure.

- 2026-05-10 — Built the admin-facing Class Plotting UI in `views/class_plotting_view.py` with Manual Entry and CSV Upload tabs, including CSV preview, row-level validation against existing room and faculty records, and an inline error report before commit.

- 2026-05-11 — Updated the EduROOM SRS to version 2.0: added FR-014 (Class Plotting / Bulk Schedule Input), expanded FR-010 (Activity Logging) to cover bulk schedule events, expanded FR-013 (CSRF-Style Action Protection) to cover class plotting operations, and amended NFR-001 with a bulk CSV import performance target of 10 seconds for 500 rows.

- 2026-05-12 — Removed `.env` (Aiven database credentials) and `ca.pem` (Aiven SSL certificate) from Git tracking after discovering they had been committed to the `local-demo` branch. Updated `.gitignore` to block re-commits and coordinated with the team to rotate the database password before the Azure migration.

- 2026-05-12 — Produced the 15-page EduROOM System Audit Report documenting reliability and performance findings against the SRS v2.0 non-functional requirements, including a code-level review of the data, view, and WebSocket subsystems and a measured-against-target NFR compliance summary.

- 2026-05-12 — Resolved a merge conflict on `.gitignore` between `local-demo` and `main` after the secrets-removal commit, then merged the feature branch into `main` so the latest class plotting code and clean .gitignore would be deployed via the GitHub Actions workflow to Azure.

---

## Renna Israel

_Entries to be added._

- YYYY-MM-DD — [Replace with a specific contribution]

---

## Tischia Ann Olivares

_Entries to be added._

- YYYY-MM-DD — [Replace with a specific contribution]
