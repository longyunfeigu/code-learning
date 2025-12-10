# FastAPI Forge

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-red.svg)](https://sqlalchemy.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A production-ready FastAPI boilerplate implementing **Domain-Driven Design (DDD) + Hexagonal Architecture** with comprehensive features for modern web applications.

## ✨ Features

- **🏗️ Clean Architecture**: DDD + Hexagonal (Ports & Adapters) + Clean Architecture patterns
- **🚀 High Performance**: Full async/await with FastAPI, SQLAlchemy 2.0, and modern Python
- **📁 Multi-Storage**: Unified file storage supporting Local, AWS S3, and Alibaba OSS
- **💳 Payment Gateway**: Integrated payment processing with Stripe, Alipay, and WeChat Pay
- **🔒 Security First**: Built-in authentication, request validation, and security best practices
- **📊 Observability**: Structured logging, request tracing, and comprehensive monitoring
- **🌐 Internationalization**: Multi-language support with Babel integration
- **🔄 Real-time**: WebSocket support with multiple broker backends (Redis, Kafka, RocketMQ)
- **📝 gRPC Support**: Parallel gRPC service reusing the same application layer
- **🧪 Testing Ready**: Comprehensive test setup with pytest and coverage reporting
- **🐳 Docker**: Production-ready containerization with multi-stage builds
- **⚡ Developer Experience**: Pre-commit hooks, code formatting, and type checking

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL (recommended) or other supported databases
- Redis (optional, for caching and distributed features)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/fastapi-forge.git
cd fastapi-forge

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp env.example .env
# Edit .env and set SECRET_KEY (mandatory)

# Setup pre-commit hooks (recommended)
pre-commit install
```

### Running the Application

```bash
# Development mode
uvicorn main:app --reload

# Or with Docker Compose (includes PostgreSQL)
docker-compose up -d

# Run gRPC service
python grpc_main.py
```

The API will be available at:
- **REST API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **gRPC**: localhost:50051

## 📋 Table of Contents

- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Configuration](#-configuration)
- [Features](#-features)
- [Development](#-development)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [API Documentation](#-api-documentation)

## 🏗️ Architecture

This project implements **Domain-Driven Design (DDD) with Hexagonal Architecture**, ensuring clean separation of concerns and maintainable code structure.

### Dependency Direction

```
API → Application → Domain ← Infrastructure
```

- **Domain Layer**: Pure business logic with no external dependencies
- **Application Layer**: Use case orchestration and transaction management
- **Infrastructure Layer**: Technical implementations (database, external APIs)
- **API Layer**: HTTP I/O and dependency injection

### Key Architectural Patterns

- **Repository Pattern**: Domain defines interfaces, Infrastructure implements them
- **Unit of Work**: Transaction boundary management
- **Ports & Adapters**: Clean separation between application and external systems
- **Domain Events**: Event-driven architecture for important business facts

## 📁 Project Structure

```
fastapi-forge/
├── api/                    # Presentation layer (HTTP endpoints, middleware)
│   ├── dependencies.py     # FastAPI dependencies
│   ├── middleware/         # Request/response middleware
│   └── routes/            # API route definitions
├── application/           # Use case orchestration
│   ├── dto.py             # Data transfer objects
│   ├── ports/             # External service interfaces
│   └── services/          # Application services
├── domain/               # Business logic core
│   ├── common/           # Shared domain logic
│   └── file_asset/       # File asset aggregate
├── infrastructure/       # Technical implementations
│   ├── database.py       # Database configuration
│   ├── external/         # External service clients
│   ├── models/           # ORM models
│   ├── repositories/     # Repository implementations
│   └── unit_of_work.py   # Transaction management
├── core/                 # Shared infrastructure
│   ├── config.py         # Application configuration
│   ├── exceptions.py     # Exception handlers
│   ├── logging_config.py # Structured logging
│   └── response.py       # Standardized API responses
├── grpc_app/            # gRPC service implementation
├── shared/              # Cross-cutting utilities
├── docs/                # Documentation
├── tests/               # Test suite
└── main.py             # Application entry point
```

## ⚙️ Configuration

The application uses **Pydantic Settings v2** with nested environment variables separated by `__`.

### Core Settings

```bash
# Application
APP_NAME=FastAPI Forge
DEBUG=false
ENVIRONMENT=development
SECRET_KEY=your-secret-key-here-change-in-production

# Database
DATABASE__URL=postgresql+asyncpg://user:password@localhost:5432/dbname

# Redis (optional)
REDIS__URL=redis://localhost:6379/0

# Storage
STORAGE__TYPE=local  # local | s3 | oss
STORAGE__BUCKET=my-bucket
```

### Complete Configuration

See `env.example` for all available configuration options.

## 🌟 Features

### File Storage System

Unified storage interface supporting multiple providers:

```python
# Configuration
STORAGE__TYPE=s3  # local | s3 | oss
STORAGE__BUCKET=my-bucket
STORAGE__REGION=us-east-1
```

**Two upload modes**:
1. **Direct Upload**: Client uploads directly to storage via presigned URLs
2. **Proxied Upload**: API receives files and uploads to storage

### Payment Gateway

Multi-provider payment processing:

```python
# Default provider
PAYMENT__DEFAULT_PROVIDER=stripe  # stripe | alipay | wechat

# Provider credentials
STRIPE_API_KEY=sk_...
ALIPAY_APP_ID=...
WECHAT_APP_ID=...
```

### Real-time WebSocket

Multi-backend WebSocket support:

```python
# Broker selection
REALTIME_BROKER=redis  # auto | redis | kafka | rocketmq
```

### Internationalization

Multi-language support:

```bash
# Supported languages
LOCALES=en,zh_Hans,zh_Hant
DEFAULT_LOCALE=en
```

### gRPC Service

Parallel gRPC implementation:

```python
# Enable gRPC
GRPC__ENABLED=true
GRPC__PORT=50051
```

## 🛠️ Development

### Code Quality Tools

```bash
# Format code
black .
isort .

# Type checking
mypy .

# Linting
flake8 .

# Security check
bandit -r . -c pyproject.toml

# Run all pre-commit checks
pre-commit run --all-files
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one version
alembic downgrade -1
```

### Protocol Buffers

```bash
# Generate Python stubs from .proto files
bash scripts/gen_protos.sh
```

### Internationalization

```bash
# Extract messages for translation
pybabel extract -F babel.cfg -k _l -o locales/messages.pot .

# Update translations
pybabel update -i locales/messages.pot -d locales/

# Compile translations
pybabel compile -d locales/
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test file
pytest tests/test_payments_skeleton.py

# Run tests in parallel
pytest tests/ -n auto

# Run only unit tests
pytest tests/ -m unit
```

### Test Structure

```
tests/
├── conftest.py              # Pytest configuration
├── test_payments_skeleton.py   # API skeleton tests
└── payments/               # Payment-related tests
    ├── test_service_idempotency.py
    ├── test_stripe_webhook.py
    ├── test_alipay_webhook.py
    └── test_wechat_webhook.py
```

### Test Strategy

- **Unit Tests**: Domain logic and individual components
- **Integration Tests**: API endpoints and external service integrations
- **Mock External Dependencies**: Storage, payment gateways, and third-party APIs

## 📦 Deployment

### Docker

Production-ready multi-stage Docker build:

```bash
# Build production image
docker build -t fastapi-forge:latest .

# Build development image
docker build --target development -t fastapi-forge:dev .
```

### Docker Compose

Complete development environment:

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Environment Variables

**Critical**: `SECRET_KEY` must be set in all environments:

```bash
# Production example
SECRET_KEY=your-very-secure-secret-key-here
DEBUG=false
ENVIRONMENT=production
DATABASE__URL=postgresql+asyncpg://user:password@db:5432/proddb
REDIS__URL=redis://redis:6379/0
STORAGE__TYPE=s3
STORAGE__BUCKET=production-bucket
```

### Performance Considerations

- **Database**: Use connection pooling (configured by default)
- **Redis**: Enable for caching and session storage in production
- **Storage**: Use S3/OSS for production, local for development
- **Logging**: JSON format in production, console in development
- **Monitoring**: Enable health checks and metrics collection

## 📚 API Documentation

### Core Endpoints

- **`GET /`** - API root with service information
- **`GET /health`** - Health check endpoint
- **`GET /docs`** - Interactive API documentation (Swagger UI)
- **`GET /redoc`** - Alternative API documentation (ReDoc)

### File Management

- **`POST /api/v1/storage/presigned`** - Generate presigned upload URL
- **`POST /api/v1/storage/complete`** - Complete direct upload
- **`POST /api/v1/storage/upload`** - Proxied file upload
- **`GET /api/v1/files`** - List files with pagination
- **`GET /api/v1/files/{id}`** - Get file details
- **`GET /api/v1/files/{id}/download`** - Generate download URL
- **`DELETE /api/v1/files/{id}`** - Delete file

### Response Format

All endpoints return standardized responses:

```json
{
  "code": "success",
  "message": "Operation completed successfully",
  "data": {},
  "request_id": "req_123456789",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Error Handling

Consistent error responses with detailed information:

```json
{
  "code": "validation_error",
  "message": "Invalid input data",
  "error": {
    "field": "email",
    "message": "Invalid email format"
  },
  "request_id": "req_123456789",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 🔧 Advanced Configuration

### Security Headers

```python
# Custom security headers
SECURITY_HEADERS=true
SECURITY_HSTS_MAX_AGE=31536000
SECURITY_CONTENT_TYPE_NOSNIFF=true
```

### Rate Limiting

```python
# Rate limiting configuration
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_REDIS_PREFIX=ratelimit
```

### CORS Configuration

```python
# CORS settings
CORS_ORIGINS=["https://app.example.com"]
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=["GET", "POST", "PUT", "DELETE"]
```

## 📖 Documentation

- **[Architecture Guide](docs/architecture.md)** - Comprehensive architecture documentation
- **[Development Guide](docs/development.md)** - Development workflow and best practices
- **[API Reference](docs/api.md)** - Detailed API documentation
- **[Database Guide](docs/alembic.md)** - Database migration and management
- **[Testing Guide](docs/tests.md)** - Testing strategies and examples

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Workflow

```bash
# 1. Setup development environment
pip install -r requirements-dev.txt
pre-commit install

# 2. Create feature branch
git checkout -b feature/new-feature

# 3. Make changes and test
pytest tests/
pre-commit run --all-files

# 4. Commit with conventional commit message
git commit -m "feat: add new feature"

# 5. Push and create PR
git push origin feature/new-feature
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/fastapi-forge/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/fastapi-forge/discussions)

## 🔗 Related Projects

- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework for building APIs
- [SQLAlchemy](https://sqlalchemy.org/) - Python SQL toolkit and ORM
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation using Python type hints
- [Alembic](https://alembic.sqlalchemy.org/) - Database migration tool

---

**Built with ❤️ using FastAPI and Domain-Driven Design principles**