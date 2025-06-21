
# 🔐 ISA Environment Configuration & Secrets Management

This document outlines best practices for managing secrets for both staging and production environments.

## 🔧 Environment Variables

Place the following files in your root project directory and do NOT commit them to version control:

- `.env.staging`
- `.env.production`

Use `.env.example` as a public template with placeholder values.

## 🔒 Firebase Secret Management (Recommended)

1. Store all environment variables in [Google Secret Manager](https://cloud.google.com/secret-manager).
2. Use `functions.config().your_key` or runtime injection via Cloud Build substitutions.
3. Rotate keys periodically and audit access policies regularly.
4. Use CI/CD scripts to sync `.env` files from Secret Manager before build.

## 🛡 Security Checklist

- [ ] Never hardcode secrets in your codebase
- [ ] Add `.env.*` files to `.gitignore`
- [ ] Enable IAM policies for fine-grained access control
- [ ] Use audit logging to track access to secrets
- [ ] For production, enforce secrets access only via CI/CD pipeline

