# Changelog

All notable changes to this project will be documented in this file.

This changelog follows the Keep a Changelog format and tracks the individual contributions of the TechValks team for the EduROOM Classroom Reservation System, a cloud web application deployed on Microsoft Azure for the CSEC 3 – Cloud Computing final project.

---

## [Unreleased]

### Added
- No unreleased additions yet.

### Changed
- No unreleased changes yet.

### Fixed
- No unreleased fixes yet.

### Removed
- No unreleased removals yet.

---

## [2026-05-13] - Cloud Deployment and Project Documentation

### Documentation
### Added
- `[Renna Israel]` - Created `report/` and `report/screenshots/` folders in the repository to organize Deliverable 3 files following the required project repository structure.
- `[Renna Israel]` - Added `CostEstimateReport.pdf` inside `report/` folder containing the Azure Pricing Calculator cost estimate for the EduROOM cloud deployment.
- `[Renna Israel]` - Added Azure Pricing Calculator screenshot inside `report/screenshots/` as supporting evidence for the cost estimate report.
- `[Renna Israel]` - Updated `README.md` with project overview, team members, video link, and demo URL following the final project submission requirements.
- `[Tischia Olivares]` - Added deployment screenshots in `/deployment/screenshots/`with README.md to show step-by-step explanations for each screenshot
- `[Tischia Olivares]` - Added architecture diagram to `/diagram/architecture.png` showing all Azure services, connections, protocols, and security boundary

### Removed
- `[Renna Israel]` - Removed misplaced `CostEstimateReport.pdf` from the root directory after identifying it was committed outside the required `report/` folder.


### Deployment
#### Fixed
- `[Tischia Olivares]` - Fixed GitHub Actions login error by updating OIDC federated credentials with correct client ID and tenant ID

#### Removed
- `[Tischia Olivares]` - Removed Dockerfile, .dockerignore, Procfile, and startup.sh that are no longer needed after switching to GitHub Actions


---

## [2026-05-12] - Final Application Preparation

### Added
- `Blessie Faith Bongalos` - Added documentation for the main EduROOM application features demonstrated during the live demo, including user login, room viewing, reservation submission, admin approval, and reservation status tracking.

- `Blessie Faith Bongalos` - Added the final system description explaining how EduROOM works as a classroom reservation system for school-based room scheduling.

### Changed
- `Blessie Faith Bongalos` - Updated the application feature descriptions to make the system easier to explain during the recorded video presentation.

- `Blessie Faith Bongalos` - Updated the system workflow explanation to show how regular users and administrators interact with the application.

### Fixed
- `Blessie Faith Bongalos` - Reviewed the application flow to make sure the system could be demonstrated end-to-end during the live demo.

### Removed
- No removals recorded for this date.


## [2026-05-12] - Azure Infrastructure Planning and Setup

### Deployment
#### Added
- `[Tischia Olivares]` - Created Resource Group `eduroom-rg` and Azure Database for MySQL Flexible Server `eduroom-server`

#### Fixed
- `[Tischia Olivares]` - Fixed GitHub Actions workflow `main_eduroom-app.yml` to deploy to correct app

#### Changed
- `[Tischia Olivares]` - Switched deployment method from Docker/Container Registry to GitHub Actions CI/CD

---

## [2026-05-11] - Azure Infrastructure Planning

### Documentation
#### Added
- `[Renna Israel]` - Reviewed architecture diagram and verified all 4 Azure services are correctly represented
- `[Blessie Bongalos]` - Reviewed cloud optimizations in architecture diagram and confirmed alignment with rubric requirements
- `[Tischia Olivares]` - Designed EduROOM Azure architecture diagram on draw.io showing all services, protocols, and security boundary

---