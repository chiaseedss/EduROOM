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
#### Added
- `[TechValks Team]` - Conducted final review and validation of deployment workflow, documentation, and project deliverables before submission
- `[Blessie Bongalos]` - Verified application workflow and deployment demo readiness before final submission
- `[Renna Israel]` - Reviewed deployment documentation formatting and repository structure consistency
- `[Renna Israel]` - Created `report/` and `report/screenshots/` folders in the repository to organize Deliverable 3 files following the required project repository structure.
- `[Renna Israel]` - Added `CostEstimateReport.pdf` inside `report/` folder containing the Azure Pricing Calculator cost estimate for the EduROOM cloud deployment.
- `[Renna Israel]` - Added Azure Pricing Calculator screenshot inside `report/screenshots/` as supporting evidence for the cost estimate report.
- `[Renna Israel]` - Updated `README.md` with project overview, team members, video link, and demo URL following the final project submission requirements.
- `[Tischia Olivares]` - Added deployment screenshots in `/deployment/screenshots/` with README.md explanations for each deployment step
- `[Tischia Olivares]` - Added architecture diagram to `/diagram/architecture.png` showing all Azure services, connections, protocols, and security boundary
- `[Blessie Bongalos]` - Created `CHANGELOG.md` at the repository root following the Keep a Changelog format, structured to log individual contributions across the four project deliverables (architecture diagram, deployment documentation, cost report, and video presentation).

#### Removed
- `[Renna Israel]` - Removed misplaced `CostEstimateReport.pdf` from the root directory after identifying it was committed outside the required `report/` folder.
### Deployment
#### Fixed
- `[Tischia Olivares]` - Fixed GitHub Actions login error by updating OIDC federated credentials with correct client ID and tenant ID
#### Removed
- `[Tischia Olivares]` - Removed Dockerfile, .dockerignore, Procfile, and startup.sh that are no longer needed after switching to GitHub Actions

---
## [2026-05-12] - Final Application Preparation
#### Added
- `[Blessie Bongalos]` - Added `schedule_type` ENUM('reservation', 'class') column and `idx_schedule_type` index to `eduroom_schema.sql` so the production Azure Database for MySQL Flexible Server schema would match the application's current data model upon deployment.
#### Changed
- `[Blessie Bongalos]` - Updated `.gitignore` to include `.env`, `ca.pem`, `venv/`, and `__pycache__/` to prevent credential and environment files from being committed to the GitHub repository connected to the Azure App Service deployment workflow.
#### Fixed
- `[Blessie Bongalos]` - Resolved merge conflict on `.gitignore` between the `local-demo` and `main` branches, then merged the feature code into `main` so the latest application state would be picked up by the GitHub Actions deployment pipeline targeting Azure App Service.
### Removed
- `[Blessie Bongalos]` - Removed `.env` (database connection credentials) and `ca.pem` (SSL certificate) from Git tracking after discovering they had been committed to the `local-demo` branch. Removal was required before migrating secret handling to Azure Key Vault with Managed Identity authentication.

## [2026-05-12] - Azure Infrastructure Setup
### Deployment
#### Added
- `[Tischia Olivares]` - Configured Resource Group `eduroom-rg` and Azure Database for MySQL Flexible Server `eduroom-server`
- `[Tischia Olivares]` - Configured Virtual Network `eduroom-rg-vnet` and integrated App Service with private Azure resources for secure internal communication
- `[Tischia Olivares]` - Created Azure Key Vault `eduroom-keyvault` with selected network access
- `[Tischia Olivares]` - Enabled System-assigned Managed Identity on `eduroom-app` for secure Key Vault access
- `[Tischia Olivares]` - Assigned `Key Vault Secrets User` role to `eduroom-app` Managed Identity following principle of least privilege

#### Fixed
- `[Tischia Olivares]` - Fixed GitHub Actions workflow `main_eduroom-app.yml` to deploy to correct app
#### Changed
- `[Tischia Olivares]` - Switched deployment method from Docker/Container Registry to GitHub Actions CI/CD
---
## [2026-05-11] - Azure Infrastructure Planning
### Documentation
#### Added
- `[Renna Israel]` - Reviewed architecture diagram and verified all 4 Azure services are correctly represented
- `[Blessie Bongalos]` - Reviewed the three cloud optimization callouts on the architecture diagram (GitHub Actions CI/CD, multi-instance App Service Plan, and Managed Identity for Key Vault) and confirmed each maps to a distinct optimization category required by Section 6 of the project rubric.
- `[Tischia Olivares]` - Created and refined the EduROOM Azure architecture diagram on draw.io showing all services, protocols, and security boundary
---
