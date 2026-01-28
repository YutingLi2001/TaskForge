# Architecture Decision Record: Oracle Cloud for Production Deployment

**Date:** 2026-01-27
**Status:** Accepted
**Deciders:** Project Owner

---

## Context

Story 5.1 originally specified AWS Lightsail for production deployment. Before implementation, we evaluated cloud hosting options considering:

1. **Cost** - Minimize ongoing hosting expenses
2. **Capacity** - Support ~100 users per application
3. **Scalability** - Ability to host multiple lightweight applications
4. **Simplicity** - Reasonable setup complexity

---

## Decision

**Replace AWS Lightsail with Oracle Cloud Infrastructure (OCI) Always Free Tier.**

---

## Options Considered

| Provider | Monthly Cost | RAM | CPU | Storage |
|----------|--------------|-----|-----|---------|
| AWS Lightsail | $5-20 | 1GB | 2 vCPU | 40GB |
| DigitalOcean | $6+ | 1GB | 1 vCPU | 25GB |
| Hetzner | ~$3.50 | 2GB | 2 vCPU | 20GB |
| Render | Free (with limits) | 512MB | Shared | 1GB |
| **Oracle Cloud Free** | **$0** | **24GB** | **4 OCPU** | **200GB** |

---

## Rationale

### Why Oracle Cloud?

1. **Completely Free Forever**
   - "Always Free" tier doesn't expire
   - No credit card charges after trial
   - 24GB RAM + 4 ARM OCPUs included

2. **Generous Resources**
   - Can host 10-15 lightweight apps like TaskForge
   - 200GB block storage
   - 10TB outbound data transfer

3. **Production Ready**
   - Real VMs (not serverless with cold starts)
   - Full Docker support
   - Persistent storage

4. **Good Global Access**
   - Multiple regions worldwide
   - Generally accessible (including from China)

### Trade-offs Accepted

| Concern | Mitigation |
|---------|------------|
| ARM architecture | Build ARM Docker images (multi-arch support) |
| Setup complexity | One-time effort; document thoroughly |
| Oracle reputation | Free tier is stable; many use it successfully |
| Account reclamation | Stay active; Oracle warns before reclaiming |

---

## Implications

### Changes Required

1. **Epic 5 Stories** - Update all references from AWS Lightsail to Oracle Cloud
2. **Docker Images** - Build for ARM64 architecture (linux/arm64)
3. **Documentation** - Create Oracle Cloud setup guide
4. **CI/CD** - Update deployment workflows for OCI

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Oracle Cloud VM (4 OCPU ARM, 24GB RAM)                 │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Docker Compose                                  │   │
│  │                                                  │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │   │
│  │  │ Frontend │  │ Backend  │  │  PostgreSQL  │  │   │
│  │  │  nginx   │  │ FastAPI  │  │              │  │   │
│  │  │  :80     │  │  :8000   │  │    :5432     │  │   │
│  │  └──────────┘  └──────────┘  └──────────────┘  │   │
│  │                                                  │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Caddy / Nginx (Reverse Proxy + SSL)            │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## References

- [Oracle Cloud Free Tier](https://www.oracle.com/cloud/free/)
- Previous decision: [Tech Debt Decisions 2026-01-22](./tech-debt-decisions-2026-01-22.md)
- Epic 5 stories updated in [epics-post-mvp.md](../planning-artifacts/epics-post-mvp.md)
