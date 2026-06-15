#!/bin/bash
# =============================================================================
# Handcrafts — Local Development Setup
# =============================================================================
# This script bootstraps a local development environment from scratch.
# It checks for prerequisites, creates a virtualenv, installs dependencies,
# runs migrations, and optionally creates a superuser.
#
# Usage:
#   chmod +x scripts/setup_dev.sh
#   ./scripts/setup_dev.sh
#
# Requirements:
#   - Python 3.11+
#   - pip
#   - PostgreSQL client libraries (libpq-dev on Debian, postgresql-devel on RHEL)
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Colors for terminal output
# ---------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info()    { echo -e "${BLUE}[INFO]${NC}  $1"; }
log_success() { echo -e "${GREEN}[OK]${NC}    $1"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC}  $1"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $1"; }

# ---------------------------------------------------------------------------
# Navigate to project root (one level up from scripts/)
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo ""
echo "======================================================"
echo "  Handcrafts — Development Environment Setup"
echo "======================================================"
echo ""

# ---------------------------------------------------------------------------
# 1. Check prerequisites
# ---------------------------------------------------------------------------
log_info "Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    log_error "Python 3 is not installed. Please install Python 3.11+ first."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
log_success "Python ${PYTHON_VERSION} found"

if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    log_error "pip is not installed. Install it with: sudo apt install python3-pip"
    exit 1
fi
log_success "pip found"

# ---------------------------------------------------------------------------
# 2. Create virtual environment
# ---------------------------------------------------------------------------
VENV_DIR="venv"

if [ ! -d "$VENV_DIR" ]; then
    log_info "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    log_success "Virtual environment created at ./${VENV_DIR}/"
else
    log_success "Virtual environment already exists"
fi

# ---------------------------------------------------------------------------
# 3. Activate virtual environment
# ---------------------------------------------------------------------------
log_info "Activating virtual environment..."
# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"
log_success "Virtual environment activated"

# ---------------------------------------------------------------------------
# 4. Upgrade pip and install dependencies
# ---------------------------------------------------------------------------
log_info "Installing Python dependencies (this may take a minute)..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
log_success "All dependencies installed"

# ---------------------------------------------------------------------------
# 5. Check for .env file
# ---------------------------------------------------------------------------
if [ ! -f ".env" ]; then
    log_warn ".env file not found!"
    log_warn "Copy the example and fill in your values:"
    log_warn "  cp .env.example .env"
    echo ""
else
    log_success ".env file found"
fi

# ---------------------------------------------------------------------------
# 6. Run database migrations
# ---------------------------------------------------------------------------
log_info "Running database migrations..."
python manage.py migrate --noinput 2>&1 | tail -1
log_success "Migrations applied"

# ---------------------------------------------------------------------------
# 7. Collect static files
# ---------------------------------------------------------------------------
log_info "Collecting static files..."
python manage.py collectstatic --noinput --clear 2>&1 | tail -1
log_success "Static files collected"

# ---------------------------------------------------------------------------
# 8. Create superuser (optional)
# ---------------------------------------------------------------------------
echo ""
read -p "$(echo -e "${YELLOW}Create a superuser account? (y/N):${NC} ")" -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python manage.py createsuperuser
fi

# ---------------------------------------------------------------------------
# Done!
# ---------------------------------------------------------------------------
echo ""
echo "======================================================"
echo -e "  ${GREEN}✅  Setup complete!${NC}"
echo "======================================================"
echo ""
echo "  Next steps:"
echo "    1. Activate the virtualenv:  source venv/bin/activate"
echo "    2. Start the dev server:     python manage.py runserver"
echo "    3. Start Celery worker:      celery -A Handcrafts worker -l info"
echo ""
