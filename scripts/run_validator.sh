#!/bin/bash

TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
VALIDATOR_OUTPUT=$(python isa/isa_validator.py 2>&1)
VALIDATION_STATUS=$?

echo "---" >> project_journal.md
echo "### ISA Environment Validation Report - $TIMESTAMP" >> project_journal.md
echo "" >> project_journal.md
echo "\`\`\`" >> project_journal.md
echo "$VALIDATOR_OUTPUT" >> project_journal.md
echo "\`\`\`" >> project_journal.md

if [ $VALIDATION_STATUS -eq 0 ]; then
    echo "**Status: ✅ SUCCESS**" >> project_journal.md
else
    echo "**Status: ❌ FAILED**" >> project_journal.md
    echo "Detailed issues: See isa/logs/venv_issues.log" >> project_journal.md
fi
echo "" >> project_journal.md

exit $VALIDATION_STATUS