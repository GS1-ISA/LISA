# Dependency Hygiene Assessment Report

**Report Date:** 2025-09-16  
**Scope:** Frontend (npm) and Backend (pip) dependencies  
**Analysis Method:** Automated outdated checks and import scanning  

## Executive Summary

- **Frontend (Node.js/npm):** 16 packages with available updates, 13 with major version lags requiring analysis
- **Backend (Python/pip):** No outdated packages detected in current environment
- **Unused Dependencies:** Identified several potentially unused packages in frontend

## Frontend Dependencies (npm)

### Outdated Packages Table

| Package | Current | Wanted | Latest | Risk Level | Effort to Upgrade | Owner Decision |
|---------|---------|--------|--------|------------|-------------------|----------------|
| @headlessui/react | 1.7.19 | 1.7.19 | 2.2.8 | High | Medium | |
| @hookform/resolvers | 3.10.0 | 3.10.0 | 5.2.2 | Medium | Low | |
| @types/node | 20.19.15 | 20.19.15 | 24.5.0 | Low | Low | |
| @types/react | 18.3.24 | 18.3.24 | 19.1.13 | High | Medium | |
| @types/react-dom | 18.3.7 | 18.3.7 | 19.1.9 | High | Medium | |
| date-fns | 3.6.0 | 3.6.0 | 4.1.0 | Medium | Medium | |
| eslint | 8.57.1 | 8.57.1 | 9.35.0 | Low | Low | |
| eslint-config-next | 14.0.4 | 14.0.4 | 15.5.3 | Low | Low | |
| jspdf | 2.5.2 | 2.5.2 | 3.0.2 | High | High | |
| lucide-react | 0.294.0 | 0.294.0 | 0.544.0 | Low | Low | |
| next | 14.0.4 | 14.0.4 | 15.5.3 | High | High | |
| next-themes | 0.2.1 | 0.2.1 | 0.4.6 | Low | Low | |
| react | 18.3.1 | 18.3.1 | 19.1.1 | High | High | |
| react-dom | 18.3.1 | 18.3.1 | 19.1.1 | High | High | |
| tailwindcss | 3.4.17 | 3.4.17 | 4.1.13 | High | High | |
| zod | 3.25.76 | 3.25.76 | 4.1.8 | Medium | Medium | |

### Major Version Lag Analysis

#### @headlessui/react (1.7.19 → 2.2.8)
- **Risk:** High - Breaking API changes in v2, component structure changes
- **Effort:** Medium - Requires updating component usage and testing UI interactions

#### @hookform/resolvers (3.10.0 → 5.2.2)
- **Risk:** Medium - Breaking changes in validation resolver APIs
- **Effort:** Low - Form validation logic updates

#### @types/react & @types/react-dom (18.x → 19.x)
- **Risk:** High - Breaking type definitions for React 19 features
- **Effort:** Medium - Type updates required when upgrading React

#### date-fns (3.6.0 → 4.1.0)
- **Risk:** Medium - API changes in date manipulation functions
- **Effort:** Medium - Update date utility calls

#### jspdf (2.5.2 → 3.0.2)
- **Risk:** High - Significant API changes in PDF generation
- **Effort:** High - Rewrite PDF creation logic

#### next (14.0.4 → 15.5.3)
- **Risk:** High - Breaking changes in Next.js framework
- **Effort:** High - Framework migration with potential routing/API changes

#### react & react-dom (18.3.1 → 19.1.1)
- **Risk:** High - Breaking changes in React 19
- **Effort:** High - Framework upgrade with testing

#### tailwindcss (3.4.17 → 4.1.13)
- **Risk:** High - Breaking changes in Tailwind CSS v4
- **Effort:** High - CSS class updates and configuration changes

#### zod (3.25.76 → 4.1.8)
- **Risk:** Medium - Schema validation API changes
- **Effort:** Medium - Update validation schemas

## Backend Dependencies (pip)

### Outdated Packages
No outdated packages detected in the current Python environment.

**Note:** This may be due to packages not being installed in the virtual environment or all dependencies being up-to-date. For a complete analysis, ensure all requirements files are installed.

## Unused Dependencies (Dead Weight Candidates)

### Frontend (JavaScript/TypeScript)
Based on import scanning of the codebase, the following packages appear in `package.json` but were not found in any import statements:

- `@headlessui/react` - UI component library
- `html2canvas` - HTML to canvas conversion
- `jspdf` - PDF generation
- `axios` - HTTP client
- `date-fns` - Date utility library
- `react-dropzone` - File upload component
- `xlsx` - Excel file processing

### Backend (Python)
Unable to perform complete unused dependency analysis due to multiple requirements files and potential environment setup differences. The codebase contains imports for packages like `neo4j`, `chromadb`, `fastapi`, `pydantic`, `sqlalchemy`, etc., which may not all be captured in the scanned requirements files.

## Recommendations

1. **High Priority Upgrades:**
   - React ecosystem (React, React-DOM, Next.js) - Plan coordinated upgrade
   - Tailwind CSS v4 - Significant breaking changes

2. **Medium Priority:**
   - Form libraries (@hookform/resolvers, zod)
   - Date utilities (date-fns)

3. **Low Priority:**
   - Type definitions and linting tools

4. **Cleanup:**
   - Review and remove unused frontend dependencies
   - Consolidate Python requirements files for better dependency management

5. **Security Considerations:**
   - Monitor for security updates in major packages
   - Consider automated dependency update workflows

## Next Steps

- Review owner decisions for each outdated package
- Plan upgrade timeline based on risk/effort assessment
- Test upgrades in development environment before production deployment
- Update CI/CD pipelines to include dependency vulnerability scanning