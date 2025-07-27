# Makefile Instructions for Better Transfer

## Quick Start (New Developers)

```bash
# 1. Clone the repository
git clone <repository-url>
cd better-transfer

# 2. Complete setup in one command
make quick-start

# 3. Edit your environment variables
nano .env

# 4. Restart with your credentials
make restart
```

## Common Commands

### Development
```bash
make up          # Start all services
make dev         # Start with logs
make logs        # View logs
make restart     # Restart services
make down        # Stop services
```

### Database & Cache
```bash
make seed        # Populate database
make cache-clear # Clear Redis cache
```

### Testing
```bash
make test        # Run all tests
make lint        # Check code quality
make check       # Run lint + tests
```

### Debugging
```bash
make shell       # Open container shell
make health      # Check if app is running
make status      # See service status
```

### Cleanup
```bash
make clean       # Remove everything
make reset       # Clean + rebuild + start
```

## Environment Setup

1. Copy environment template: `make setup`
2. Edit `.env` file with your credentials:
   - OpenAI API key
   - MongoDB connection string
   - Redis credentials

## Help

Run `make help` to see all available commands with descriptions.