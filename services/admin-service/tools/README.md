# Craft Engineering CLI

Welcome to the internal engineering CLI for the Craft platform. This tool simplifies development, testing, and operations by centralizing scripts into a standard, robust command-line interface.

## Usage
Run the CLI from the project root:

```bash
python tools/cli.py <command> [options]
```

## Global Options
- `--verbose`: Enable detailed debug logging.
- `--quiet`: Suppress all non-error output.
- `--dry-run`: Simulate what a command will do without actually modifying the database or filesystem.
- `--yes`: Auto-confirm dangerous actions. (NOTE: This will still block in production environments).

*Note: Global flags can be provided anywhere in the command string (e.g. `python tools/cli.py doctor --verbose` and `python tools/cli.py --verbose doctor` are both valid).*

## Recommended Workflows

### Local development diagnosis
```bash
python tools/cli.py doctor
```

### Before deployment
```bash
python tools/cli.py pre-deploy
```

### Before pushing to GitHub
```bash
python tools/cli.py scan-secrets
python tools/cli.py check-imports
python tools/cli.py check-migrations
```

### Before Docker build
```bash
python tools/cli.py docker-check
python tools/cli.py check-static
python tools/cli.py quick-deploy-check
```

### After database reset in local development
```bash
python tools/cli.py backup-db
python tools/cli.py db-reset --yes
python tools/cli.py generate-dummy-data --yes
```

## Command Taxonomy

### 🏥 Project Health
- `doctor`: Runs a full project health diagnosis (environment, database, migrations, docker, secrets) and provides a summary.
- `pre-deploy`: Runs strict deployment readiness checks. Designed to be run before every release. It fails fast on critical issues.
- `version`: Prints CLI version, Django settings, Environment, and Python info.

### 🛠️ Development & Code
- `clean-cache`: Removes all `__pycache__` and compiled `.pyc`/`.pyo` files.
- `check-imports`: Compiles all Python files to detect syntax or missing import errors.
- `list-urls`: Discovers and prints all registered Django URL patterns.
- `find-missing-translations`: Scans JS files for translation keys and checks if they exist in `i18n.js`.

### 🗄️ Database
- `backup-db`: Creates a timestamped copy of the local `db.sqlite3`.
- `db-reset`: ⚠️ Wipes the local database, runs migrations, and setups base teams. (BLOCKED IN PRODUCTION).
- `check-migrations`: Detects if there are model changes without migrations or unapplied migrations.
- `generate-dummy-data`: ⚠️ Seeds the local database with products, categories, and suppliers for testing.

### 🚀 DevOps
- `check-env`: Validates that all required environment variables are set.
- `check-health`: Performs a quick database connection check.
- `check-services`: Validates connections to the Database and Redis Cache.
- `check-static`: Runs a dry-run collectstatic check for deployment readiness.
- `docker-check`: Audits Dockerfile and .dockerignore for correctness.
- `quick-deploy-check`: Runs Django's built-in `check --deploy`.

### 🛡️ Security
- `scan-secrets`: Scans the codebase for hardcoded passwords, keys, and tokens.
- `audit-permissions`: Audits Django Group permissions and staff users without groups.
- `check-superusers`: Lists all users with superuser privileges.
- `check-staff-users`: Lists all users with staff privileges.

### 🧪 Testing
- `smoke-test`: Pings core API and frontend routes to ensure 200 OK responses.
- `test-endpoints`: Runs an automated endpoint test sequence.
- `load-test`: Simulates heavy traffic load on the system.

### 👔 Operations
- `ops-manager`: Interactive CLI to create teams and operational users.
- `setup-ops-teams`: Seeds the base Ops, Support, and Sales teams.
- `assign-group-permissions`: Associates specific system permissions to the ops teams.
- `upgrade-user`: Upgrades an existing user to Superuser/Staff status.

## Testing Architecture
*Automated tests are prepared in `tools/tests/` for future implementation. Current validation relies on manual command verification.*
