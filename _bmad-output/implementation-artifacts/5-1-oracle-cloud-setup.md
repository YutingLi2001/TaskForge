# Story 5.1: Oracle Cloud Setup

Status: ready-for-dev

## Story

As a **developer**,
I want **the application deployed to Oracle Cloud Infrastructure**,
So that **users can access it on the internet for free**.

## Background

> **Architecture Decision (2026-01-27):** Oracle Cloud was chosen over AWS Lightsail.
> See [ADR-2026-01-27-Oracle-Cloud](./adr-2026-01-27-oracle-cloud.md) for rationale.

**Why Oracle Cloud Free Tier:**
- Completely free forever (Always Free tier)
- 24GB RAM + 4 ARM OCPUs (can host 10-15 lightweight apps)
- 200GB block storage included
- Good global accessibility

## Acceptance Criteria

1. **Given** I have Oracle Cloud account configured **When** I provision infrastructure **Then** ARM-based VM instance is created using Always Free tier (Ampere A1, 4 OCPU, 24GB RAM)
2. **Given** VM is provisioned **When** I connect via SSH **Then** Docker and Docker Compose are installed and functional
3. **Given** Docker is installed **When** I deploy the database **Then** PostgreSQL runs in container with persistent volume for data durability
4. **Given** infrastructure is ready **When** I deploy the application **Then** Frontend and backend containers are running and healthy
5. **Given** containers are running **When** I access the public IP **Then** the application is accessible from the internet
6. **Given** application is deployed **When** I check environment variables **Then** secrets are securely configured (not in repo, loaded from .env)
7. **Given** VM is provisioned **When** I check network settings **Then** firewall rules allow HTTP (80) and HTTPS (443) traffic

## Tasks / Subtasks

### Phase 1: Oracle Cloud Account & Infrastructure Setup

- [ ] **Task 1: Create Oracle Cloud Account** (AC: 1)
  - [ ] Sign up for Oracle Cloud Free Tier at cloud.oracle.com
  - [ ] Complete identity verification
  - [ ] Note tenancy OCID and home region
  - [ ] Document account setup in deployment guide

- [ ] **Task 2: Provision ARM VM Instance** (AC: 1)
  - [ ] Navigate to Compute > Instances
  - [ ] Create Always Free eligible instance:
    - Shape: VM.Standard.A1.Flex (ARM)
    - OCPUs: 4 (max free)
    - Memory: 24GB (max free)
    - Image: Oracle Linux 8 or Ubuntu 22.04
  - [ ] Configure boot volume (50GB recommended)
  - [ ] Generate and download SSH key pair
  - [ ] Document instance OCID and public IP

- [ ] **Task 3: Configure Networking** (AC: 7)
  - [ ] Create or use default VCN (Virtual Cloud Network)
  - [ ] Add ingress rules to security list:
    - TCP port 22 (SSH)
    - TCP port 80 (HTTP)
    - TCP port 443 (HTTPS)
  - [ ] Reserve public IP (optional, for static IP)
  - [ ] Document VCN and subnet OCIDs

### Phase 2: Server Configuration

- [ ] **Task 4: SSH Access Setup** (AC: 2)
  - [ ] Connect to VM via SSH: `ssh -i key.pem opc@<public-ip>`
  - [ ] Update system packages
  - [ ] Create deployment user (optional)
  - [ ] Configure SSH key for deployment user

- [ ] **Task 5: Install Docker & Docker Compose** (AC: 2)
  - [ ] Install Docker Engine:
    ```bash
    sudo dnf install -y dnf-utils
    sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    sudo systemctl enable --now docker
    sudo usermod -aG docker $USER
    ```
  - [ ] Verify Docker installation: `docker --version`
  - [ ] Verify Compose: `docker compose version`
  - [ ] Test with hello-world: `docker run hello-world`

- [ ] **Task 6: Configure Firewall (iptables)** (AC: 7)
  - [ ] Open required ports in OS firewall:
    ```bash
    sudo firewall-cmd --permanent --add-port=80/tcp
    sudo firewall-cmd --permanent --add-port=443/tcp
    sudo firewall-cmd --reload
    ```
  - [ ] Verify ports are open: `sudo firewall-cmd --list-ports`

### Phase 3: Application Deployment

- [ ] **Task 7: Build ARM Docker Images** (AC: 4)
  - [ ] Update docker-compose.prod.yml for ARM compatibility
  - [ ] Build images on ARM VM or use multi-arch build:
    ```bash
    docker compose -f docker-compose.prod.yml build
    ```
  - [ ] Verify images are arm64 architecture
  - [ ] Document any ARM-specific changes needed

- [ ] **Task 8: Configure Environment Variables** (AC: 6)
  - [ ] Create `/opt/taskforge/.env` from template
  - [ ] Set secure values:
    - DATABASE_URL (local PostgreSQL container)
    - SECRET_KEY (generate random 32+ char string)
    - POSTGRES_PASSWORD (generate secure password)
  - [ ] Restrict file permissions: `chmod 600 .env`
  - [ ] Document required variables

- [ ] **Task 9: Deploy PostgreSQL with Persistent Volume** (AC: 3)
  - [ ] Create data directory: `sudo mkdir -p /opt/taskforge/data/postgres`
  - [ ] Update docker-compose.prod.yml volume path
  - [ ] Start database container
  - [ ] Verify data persists across container restarts
  - [ ] Document backup location

- [ ] **Task 10: Deploy Application Stack** (AC: 4, 5)
  - [ ] Clone repository to `/opt/taskforge`
  - [ ] Run production stack:
    ```bash
    docker compose -f docker-compose.prod.yml up -d
    ```
  - [ ] Verify all containers are healthy:
    ```bash
    docker compose -f docker-compose.prod.yml ps
    ```
  - [ ] Test health endpoint: `curl http://localhost/api/health`
  - [ ] Test from external network using public IP

### Phase 4: Documentation & Scripts

- [ ] **Task 11: Create Deployment Scripts** (AC: all)
  - [ ] Create `scripts/deploy/setup-server.sh` for initial server setup
  - [ ] Create `scripts/deploy/deploy.sh` for application deployment
  - [ ] Create `scripts/deploy/rollback.sh` for rollback capability
  - [ ] Make scripts idempotent (safe to run multiple times)

- [ ] **Task 12: Create Deployment Guide** (AC: all)
  - [ ] Create `docs/deployment/oracle-cloud-setup.md`
  - [ ] Document step-by-step setup process
  - [ ] Include screenshots of OCI console steps
  - [ ] Add troubleshooting section
  - [ ] Document common issues and solutions

### Phase 5: Validation

- [ ] **Task 13: End-to-End Testing**
  - [ ] Access application via public IP in browser
  - [ ] Test user registration flow
  - [ ] Test user login flow
  - [ ] Test project creation
  - [ ] Test task creation
  - [ ] Verify all features work as expected

- [ ] **Task 14: Persistence Verification**
  - [ ] Create test data (user, project, tasks)
  - [ ] Restart all containers: `docker compose restart`
  - [ ] Verify data persists after restart
  - [ ] Reboot VM: `sudo reboot`
  - [ ] Verify containers auto-start and data persists

## Dev Technical Guidance

### Oracle Cloud Free Tier Limits
- 4 ARM OCPUs total
- 24GB RAM total
- 200GB block storage
- 10TB outbound data/month

### ARM Architecture Notes
- PostgreSQL, nginx, Python images all support ARM64
- Use `platform: linux/arm64` in compose if needed
- Build images on ARM VM for best compatibility

### Directory Structure on Server
```
/opt/taskforge/
├── .env                    # Environment variables (chmod 600)
├── docker-compose.prod.yml # Production compose file
├── data/
│   └── postgres/           # PostgreSQL data volume
└── logs/                   # Application logs (optional)
```

### Security Considerations
- Never commit .env to repository
- Use strong passwords (32+ characters)
- Restrict SSH to key-based auth only
- Consider fail2ban for SSH protection
- Keep system packages updated

### Useful Commands
```bash
# View logs
docker compose -f docker-compose.prod.yml logs -f

# Restart specific service
docker compose -f docker-compose.prod.yml restart backend

# Pull latest and redeploy
git pull && docker compose -f docker-compose.prod.yml up -d --build

# Check resource usage
docker stats
```

## Checklist
- [ ] Oracle Cloud account created
- [ ] ARM VM provisioned (Always Free)
- [ ] Docker and Docker Compose installed
- [ ] Firewall rules configured (80, 443)
- [ ] PostgreSQL running with persistent volume
- [ ] Application containers deployed and healthy
- [ ] Public IP accessible from internet
- [ ] Environment variables secured
- [ ] Deployment guide created
- [ ] End-to-end testing passed
