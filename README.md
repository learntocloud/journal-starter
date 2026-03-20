# 📘 AWS Two-Tier Architecture (FastAPI + PostgreSQL)

## 👨‍💻 About This Project

This project demonstrates a **production-style two-tier architecture in AWS**, designed with a strong focus on **security, scalability, and real-world best practices**.

Rather than just deploying an application, the goal was to design a system the way it would be built in a professional cloud environment.

---

## 🎯 Why This Project Matters

Most beginner cloud projects focus on getting something running.

This project focuses on **how real systems are designed in production**:

- Isolating resources using public/private subnets  
- Eliminating unnecessary exposure (no public DB, no SSH on private instances)  
- Using IAM roles instead of static credentials  
- Designing for future scalability across Availability Zones  

---

## 📑 Contents

- [Architecture Overview](#️-architecture-overview)
- [Project Summary](#-project-summary)
- [VPC Design](#-vpc-design)
- [Application Tier (Public Subnet)](#-application-tier-public-subnet)
- [Database Tier (Private Subnet)](#️-database-tier-private-subnet)
- [Security & Access](#-security--access)
- [Traffic Flow](#-traffic-flow)
- [Key Design Decisions](#-key-design-decisions)

---

## 🏗️ Architecture Overview

![Architecture Diagram](./architecture/Journal-VPC.drawio.png)

---

## 🚀 Project Summary

This architecture separates the system into two tiers:

- **Application Tier (Public Subnet)** → Handles incoming traffic  
- **Database Tier (Private Subnet)** → Stores and manages data securely  

The design prioritizes:

- Security through isolation  
- Controlled access between tiers  
- Simplicity with production-aligned patterns  

---

## 🌐 VPC Design

- **CIDR Block:** `10.16.0.0/16`
- Subnetted into `/20` ranges to allow **future expansion across Availability Zones**

### Subnets:
- Public Subnet: `10.16.32.0/20`
- Private Subnet: `10.16.16.0/20`

### Routing:
- Public Subnet → Internet Gateway (IGW)  
- Private Subnet → NAT Gateway → IGW  

---

## 🧩 Application Tier (Public Subnet)

The application layer is hosted on an EC2 instance.

### Components:
- FastAPI application  
- Nginx (reverse proxy)
  - Handles HTTP (80) and HTTPS (443)  
  - Forwards traffic to Uvicorn (port 8000)  
- Elastic IP for consistent public access  

### Security:
- Security Group (`api-sg`):
  - Allow HTTP/HTTPS from anywhere  
  - Allow SSH only from trusted IP  
  - Allow all outbound traffic  

### IAM:
- Instance Role (`journalapi-role`):
  - Grants access to AWS Bedrock  
  - Enables GenAI sentiment analysis  
  - No hardcoded credentials  

---

## 🗄️ Database Tier (Private Subnet)

The database layer is fully isolated from the internet.

### Components:
- PostgreSQL EC2 instance  
- No public IP  

### Security:
- Security Group (`db-sg`):
  - Allow port 5432 only from application security group  
  - Allow outbound HTTPS for updates and SSM  

### Networking:
Private Subnet → NAT Gateway → Internet Gateway


### IAM:
- Instance Role (`postgresdb-role`):
  - Enables AWS Systems Manager Session Manager  
  - Eliminates need for SSH keys  

---

## 🔐 Security & Access

This architecture minimizes attack surface:

- No public database access  
- No SSH access to private instances  
- No hardcoded credentials  

### Implemented Best Practices:

- Security Group-to-Security Group communication  
- Least-privilege IAM roles  
- Session Manager (SSM) for secure access  
- VPC Endpoints (PrivateLink) for SSM  
  - No internet traversal  
  - Fully encrypted  
  - Auditable  

---

## 🔄 Traffic Flow

### Inbound:
- Internet → IGW → Public Subnet → Nginx → Uvicorn

### SSH:
- Trusted IP → IGW → FastAPI EC2

### Internal:
- FastAPI → PostgreSQL (port 5432 via private IP)

### Outbound:
- App Server → IGW  
- DB Server → NAT Gateway → IGW  

---

## 🧠 Key Design Decisions

### Why a /16 VPC with /20 Subnets?
To allow future expansion across multiple Availability Zones without redesigning the network.

### Why EC2 Instead of RDS?
To gain hands-on experience managing infrastructure, networking, and database configuration.

### Why NAT Gateway Instead of Public DB Access?
To allow outbound traffic while keeping the database completely private.

### Why SSM Session Manager Instead of SSH?
- No open ports  
- No key management  
- Fully auditable  
- Reduced attack surface  
