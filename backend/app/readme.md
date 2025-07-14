# Aerich Migration Tool for FastAPI

A quick reference guide for managing database migrations with Aerich and Tortoise ORM in FastAPI applications.

## 📋 Table of Contents
- [Initial Setup](#-initial-setup)
- [Migration Workflow](#-migration-workflow)
- [Rollback Commands](#-rollback-commands)
- [Inspection Tools](#-inspection-tools)
- [Docker Integration](#-docker-integration)
- [Troubleshooting](#-troubleshooting)

## 🏁 Initial Setup

```bash
# Initialize Aerich configuration (first time only)
aerich init -t your_app.tortoise_config.TORTOISE_ORM

# Generate initial migration (after models exist)
aerich init-db