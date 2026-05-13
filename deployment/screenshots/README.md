# EduROOM – Deployment Documentation

This document provides step-by-step deployment documentation for EduROOM on Microsoft Azure, following Method B (GUI screenshots).

## Deployment Overview

| Resource | Service | Region |
|----------|---------|--------|
| eduroom-rg | Resource Group | Korea Central |
| eduroom-plan | App Service Plan (B1) | Korea Central |
| eduroom-app | Azure App Service | Korea Central |
| eduroom-server | Azure Database for MySQL | Korea Central |
| eduroom-keyvault | Azure Key Vault | Korea Central |
| eduroom-rg-vnet | Virtual Network | Korea Central |
| eduroom-communications | Azure Communication Service | Global |

---

## Cloud Optimizations Implemented

| # | Optimization | Category |
|---|-------------|----------|
| ① | GitHub Actions CI/CD | Security & DevOps |
| ② | Managed Identity + Key Vault | Advanced Security Controls |
| ③ | 3 App Service instances | Fault Tolerance |

---

## Step-by-Step Screenshots

### 1. Resource Group
![Resource Group](screenshots/01-resource-group.png)

Resource group `eduroom-rg` serves as the container for all EduROOM project resources, deployed in Korea Central region. All resources are grouped together for easier management, access control, and cost tracking.

---

### 2. App Service Plan
![App Service Plan](screenshots/02-app-service-plan.png)

App Service Plan `eduroom-plan` uses the Basic B1 tier in Korea Central, providing 1.75GB RAM and 100 ACU for running the EduROOM backend on Linux.

---

### 3. App Service 
![App Service Overview](screenshots/07-app-service.png)

Azure App Service `eduroom-app` hosts the EduROOM Python/Flet application, running on Python 3.11 on Linux. The app is accessible at `https://eduroom-app.azurewebsites.net`. App Service is scaled to **3 instances** to ensure fault tolerance and high availability. Azure's built-in load balancer automatically distributes incoming traffic across all 3 instances. If one instance becomes unavailable, traffic is automatically routed to the remaining healthy instances — ensuring EduROOM stays online even during failures.

> **Optimization ③ — Fault Tolerance:** 3 instances with Azure built-in load balancing.

---

### 4. MySQL Overview
![MySQL Overview](screenshots/03-database-mysql.png)

Azure Database for MySQL Flexible Server `eduroom-server` hosts the EduROOM database in Korea Central, running MySQL 8.0 on Burstable B1ms tier. It stores all reservation, user, classroom, and notification data for EduROOM. MySQL server is configured with **Private access only** via VNet integration with `eduroom-rg-vnet`. This ensures the database is not directly accessible from the public internet — only the App Service can reach it through the private network.

---

### 5. Managed Identity
![Managed Identity](screenshots/04-managed-identity.png)

System-assigned Managed Identity is enabled on `eduroom-app`, allowing it to securely authenticate to Azure Key Vault without storing any credentials in the application code or environment variables. Azure automatically manages the identity lifecycle.

> **Optimization ② — Advanced Security Controls:** Managed Identity eliminates hardcoded credentials.

---

### 6. Key Vault Access Control
![Key Vault IAM](screenshots/05-keyvault-iam.png)

`eduroom-app`'s Managed Identity is assigned the **Key Vault Secrets User** role on `eduroom-keyvault`, granting read-only access to secrets. This follows the principle of least privilege — the app can only read secrets, not create or modify them.

---

### 7. Key Vault Secrets
![Key Vault Secrets](screenshots/06-keyvault-secrets.png)

All sensitive credentials are stored securely in Azure Key Vault, including:
- Database connection details (host, name, user, password, port)
- Azure Communication Service connection string
- ACS sender email
- OTP hash salt

No plaintext credentials are stored anywhere in the application code or configuration.

---

### 8. App Service Environment Variables
![App Service Environment Variables](screenshots/08-app-service-envvars.png)

Environment variables reference Key Vault secrets using the `@Microsoft.KeyVault()` syntax. Azure automatically fetches the secret values at runtime — no code changes were required in the EduROOM application.

---

### 9. Virtual Network Overview
![Virtual Network](screenshots/09-vnet-overview.png)

Virtual Network `eduroom-rg-vnet` in Korea Central isolates private resources within a secure network boundary. The VNet contains three subnets: `default` (MySQL), `keyvault-subnet` (Key Vault), and `appservice-subnet` (App Service outbound).

---

### 10. App Service Networking
![App Service Networking](screenshots/10-app-service-networking.png)

App Service is integrated with `eduroom-rg-vnet` via VNet Integration, allowing secure outbound communication to MySQL and Key Vault within the private network. Inbound traffic from users is still accepted over HTTPS.

---

### 11. GitHub Actions Workflow
![GitHub Actions Run](screenshots/11-github-actions-workflow.png)

GitHub Actions CI/CD pipeline successfully deployed EduROOM to Azure App Service. The pipeline is triggered automatically on every push to the `main` branch, ensuring consistent and automated deployments. The workflow file `main_eduroom-app.yml` defines the build and deploy steps. It uses OIDC federated credentials via `eduroom-github` app registration for secure, passwordless authentication to Azure — no secrets are hardcoded in the workflow.

> **Optimization ① — CI/CD Automation:** GitHub Actions deploys EduROOM on every push to main.

---

### 12. Azure Communication Service
![Azure Communication Service](screenshots/12-communication-service.png)

Azure Communication Service `eduroom-communications` handles CSPC email authentication. It sends OTP codes to verify user identity before granting access to EduROOM, ensuring only verified CSPC email holders can log in.

---

## Security Boundary

| Zone | Resources |
|------|-----------|
| **Public** | CSPC Users (browser), GitHub Actions |
| **Private (Azure Cloud)** | Azure Communication Service |
| **Private (VNet)** | App Service, MySQL, Key Vault |

---

## Notes

- MySQL was deployed in Korea Central due to Azure for Students regional restrictions on MySQL Flexible Server provisioning.
- App Service Plan is on Basic B1 tier which supports up to 3 instances for fault tolerance.
- All sensitive credentials are managed through Azure Key Vault with Managed Identity — no hardcoded secrets anywhere in the codebase.