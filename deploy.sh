#!/usr/bin/env bash
set -euo pipefail

# Meridian deploy script — safety checks before Cloudflare Pages deploy

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

fail() { echo -e "${RED}ABORT:${NC} $1"; exit 1; }
ok()   { echo -e "${GREEN}OK:${NC} $1"; }

# 1. Clean working directory
if [ -n "$(git status --porcelain)" ]; then
  fail "Working directory is not clean. Commit or stash changes first."
fi
ok "Working directory clean"

# 2. Run tests
echo "Running Playwright smoke tests..."
npm test || fail "Tests failed — fix before deploying."
ok "All tests passed"

# 3. Tag the deploy
TAG="deploy-$(date +%Y-%m-%d-%H%M)"
git tag "$TAG"
ok "Tagged as $TAG"

# 4. Deploy
echo "Deploying to Cloudflare Pages..."
npx wrangler pages deploy . --project-name=meridian --branch=main --commit-dirty=true
ok "Deployed to production"

echo ""
echo -e "${GREEN}Deploy complete.${NC} Tag: $TAG"
