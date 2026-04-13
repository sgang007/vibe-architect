#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════════════════════════
#  Vibe Architect — One-command deploy
#
#  Frontend  →  Netlify  (static CDN)
#  Backend   →  Render   (persistent server, required for SSE streaming)
#
#  Usage:
#    chmod +x deploy.sh
#    ./deploy.sh
#
#  Prerequisites (auto-installed if missing):
#    - netlify-cli  (npm install -g netlify-cli)
#    - render-cli   (npm install -g @render-oss/render-cli)  ← optional, needed
#                    only if you want Render deploy from the CLI; otherwise the
#                    script gives you a one-click Render deploy URL
#    - git + a GitHub remote (Render needs a repo)
# ══════════════════════════════════════════════════════════════════════════════
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── Colour helpers ─────────────────────────────────────────────────────────────
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'
RED='\033[0;31m';   BOLD='\033[1m';      NC='\033[0m'
info()    { echo -e "${CYAN}ℹ  $*${NC}"; }
success() { echo -e "${GREEN}✅ $*${NC}"; }
warn()    { echo -e "${YELLOW}⚠  $*${NC}"; }
error()   { echo -e "${RED}❌ $*${NC}"; exit 1; }
header()  { echo -e "\n${BOLD}${GREEN}── $* ──────────────────────────────────${NC}"; }

# ── Banner ─────────────────────────────────────────────────────────────────────
echo -e "${BOLD}${GREEN}"
echo "╔══════════════════════════════════════╗"
echo "║   🏗  Vibe Architect  —  Deploy      ║"
echo "╚══════════════════════════════════════╝${NC}"

# ── Prerequisites ──────────────────────────────────────────────────────────────
header "Checking prerequisites"

need_cmd() {
  if ! command -v "$1" &>/dev/null; then
    warn "$1 not found — installing…"
    npm install -g "$2" || error "Failed to install $2. Please run: npm install -g $2"
  fi
  success "$1 found"
}

command -v npm &>/dev/null || error "npm is required. Install Node.js from https://nodejs.org"
need_cmd netlify netlify-cli

# ── Collect secrets ────────────────────────────────────────────────────────────
header "API Keys"

prompt_secret() {
  local var="$1" label="$2" current="${!1:-}"
  if [[ -n "$current" ]]; then
    echo -e "${CYAN}$label already set in environment${NC}"
  else
    read -rsp "Enter $label: " val
    echo
    export "$var"="$val"
  fi
}

prompt_secret GROQ_API_KEY      "Groq API key (from console.groq.com)"
prompt_secret ANTHROPIC_API_KEY "Anthropic API key (claude.ai/settings — fallback when Groq is rate-limited)"

# ── Step 1: Deploy backend to Render ──────────────────────────────────────────
header "Backend → Render"

GITHUB_REMOTE=$(git -C "$ROOT" remote get-url origin 2>/dev/null || echo "")

if [[ -z "$GITHUB_REMOTE" ]]; then
  warn "No GitHub remote found. Push your repo to GitHub first, then run:"
  echo "  git remote add origin https://github.com/YOUR_USERNAME/vibe-architect.git"
  echo "  git push -u origin main"
  echo ""
fi

info "To deploy the backend on Render (free tier):"
echo ""
echo -e "  ${BOLD}Option A — Dashboard (recommended)${NC}"
echo "  1. Go to  https://dashboard.render.com/select-repo"
echo "  2. Connect your GitHub repo"
echo "  3. Render auto-detects render.yaml and creates the service"
echo "  4. Add secrets in Dashboard → vibe-architect-api → Environment:"
echo -e "       ${YELLOW}GROQ_API_KEY${NC}       = ${GROQ_API_KEY:0:20}..."
echo -e "       ${YELLOW}ANTHROPIC_API_KEY${NC}  = ${ANTHROPIC_API_KEY:0:20}..."
echo ""
echo -e "  ${BOLD}Option B — Deploy button${NC}"
REPO_URL="${GITHUB_REMOTE:-https://github.com/YOUR_USERNAME/vibe-architect}"
RENDER_DEPLOY_URL="https://render.com/deploy?repo=${REPO_URL}"
echo "  Open: ${CYAN}${RENDER_DEPLOY_URL}${NC}"
echo ""

read -rp "Enter your Render backend URL (or press Enter to set up later): " BACKEND_URL
BACKEND_URL="${BACKEND_URL:-https://vibe-architect-api.onrender.com}"

# Validate URL format
if [[ "$BACKEND_URL" != https://* ]]; then
  warn "URL doesn't start with https:// — using as-is"
fi

# ── Step 2: Build frontend ─────────────────────────────────────────────────────
header "Frontend → Build"

cd "$ROOT/frontend"
info "Installing dependencies…"
npm ci --silent
success "Dependencies installed"

info "Building production bundle…"
npm run build
success "Build complete ($(du -sh dist | cut -f1) in dist/)"

# ── Step 3: Deploy frontend to Netlify ────────────────────────────────────────
header "Frontend → Netlify"

cd "$ROOT"

# Log in if not already authenticated
if ! netlify status &>/dev/null 2>&1; then
  info "Logging in to Netlify…"
  netlify login
fi

# Link or create site
if [[ ! -f "$ROOT/.netlify/state.json" ]]; then
  info "Creating new Netlify site…"
  netlify sites:create --name vibe-architect 2>/dev/null || true
  netlify link 2>/dev/null || netlify init
fi

# Push environment variable to Netlify
info "Setting VIBE_BACKEND_URL on Netlify…"
netlify env:set VIBE_BACKEND_URL "$BACKEND_URL" --context production 2>/dev/null || \
  warn "Could not set env var via CLI — set VIBE_BACKEND_URL manually in the Netlify dashboard"

# Deploy
info "Deploying to Netlify…"
DEPLOY_OUTPUT=$(netlify deploy --dir=frontend/dist --prod --json 2>/dev/null || \
                netlify deploy --dir=frontend/dist --prod 2>&1)

NETLIFY_URL=$(echo "$DEPLOY_OUTPUT" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('deploy_url') or d.get('url', ''))
except Exception:
    import re
    m = re.search(r'https://[a-z0-9-]+\.netlify\.app', sys.stdin.read())
    print(m.group(0) if m else '')
" 2>/dev/null || echo "")

# ── Step 4: Update CORS on Render ─────────────────────────────────────────────
if [[ -n "$NETLIFY_URL" ]]; then
  header "Finalising"
  warn "Update CORS_ORIGINS on Render to: ${NETLIFY_URL}"
  echo "  Dashboard → vibe-architect-api → Environment → CORS_ORIGINS = ${NETLIFY_URL}"
fi

# ── Summary ────────────────────────────────────────────────────────────────────
header "Deploy complete"

echo ""
echo -e "${BOLD}Your app:${NC}"
echo -e "  🌐 Frontend  ${GREEN}${NETLIFY_URL:-https://vibe-architect.netlify.app}${NC}"
echo -e "  🖥  Backend   ${GREEN}${BACKEND_URL}${NC}"
echo ""
echo -e "${BOLD}Next steps:${NC}"
echo "  1. If you haven't already — deploy the backend on Render (see above)"
echo "  2. Set GROQ_API_KEY + ANTHROPIC_API_KEY in the Render environment"
echo "  3. Set CORS_ORIGINS = ${NETLIFY_URL:-<your-netlify-url>} in the Render environment"
echo "  4. Visit your app at ${NETLIFY_URL:-<your-netlify-url>}"
echo ""
success "Done!"
