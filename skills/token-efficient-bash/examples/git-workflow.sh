#!/usr/bin/env bash

exec 2>&1
set -xeuo pipefail

git add -A
git commit -m "Update documentation

- Add new examples
- Fix formatting issues
- Update installation guide"
git status
git push origin main
