# Docker Setup for Beckn DEG Bot

This document explains how to set up and run the Beckn DEG Bot application using Docker.

## Prerequisites

- Docker
- Docker Compose
- Environment variables configured

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```bash
# FastAPI Configuration
PORT=3050

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Beckn Configuration
BAP_ID=bap-ps-network-deg.becknprotocol.io
BAP_URI=https://bap-ps-network-deg.becknprotocol.io
BASE_URL=https://bap-ps-client-deg.becknprotocol.io

# MongoDB Configuration
MONGODB_URL=mongodb://mongodb:27017
DATABASE_NAME=beckn_deg_bot

# JWT Authentication Configuration
SECRET_KEY=your-super-secret-jwt-key-here-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Development/Production Environment
ENVIRONMENT=development
```

## Quick Start

1. **Build and run the application:**

   ```bash
   docker-compose up --build
   ```

2. **Run in detached mode:**

   ```bash
   docker-compose up -d --build
   ```

3. **Stop the application:**
   ```bash
   docker-compose down
   ```

## Services

The application includes the following services:

### 1. beckn-deg-bot

- FastAPI application with AI chatbot functionality
- Integrates with Beckn Open Network
- Uses OpenAI for AI processing
- JWT authentication support

### 2. mongodb

- MongoDB database for user data and sessions
- Persistent data storage
- Health checks for reliability

## Development Mode

For development with hot reload, you can modify the docker-compose.yml to mount the source code:

```yaml
volumes:
  - ./src:/app/src:ro # Uncomment this line
```

## API Endpoints

Once running, the application will be available at:

- **Health Check**: `http://localhost:3050/ping`
- **API Documentation**: `http://localhost:3050/docs`
- **AI Chat**: `http://localhost:3050/api/ai/chat`
- **AI Health**: `http://localhost:3050/api/ai/health`

## Docker Commands

### Build the image

```bash
docker build -t beckn-deg-bot .
```

### Run the container

```bash
docker run -p 3050:3050 --env-file .env beckn-deg-bot
```

### View logs

```bash
docker-compose logs -f beckn-deg-bot
```

### Access container shell

```bash
docker-compose exec beckn-deg-bot bash
```

### Access MongoDB shell

```bash
docker-compose exec mongodb mongosh
```

## Database Management

### MongoDB Data Persistence

- MongoDB data is persisted in a Docker volume
- Data survives container restarts
- To reset data: `docker-compose down -v && docker-compose up`

### Database Initialization

- Create a `mongo-init/` directory for initialization scripts
- Place `.js` or `.sh` files in this directory for automatic execution

## Production Considerations

1. **Environment Variables**: Ensure all required environment variables are properly set
2. **Secrets Management**: Use Docker secrets or external secret management for sensitive data
3. **Logging**: Configure proper logging volumes and rotation
4. **Monitoring**: Set up health checks and monitoring
5. **Scaling**: Use Docker Swarm or Kubernetes for production scaling
6. **Database**: Consider using managed MongoDB service for production
7. **Security**: Change default JWT secret key and use strong passwords

## Troubleshooting

### Common Issues

1. **Port already in use**: Change the port mapping in docker-compose.yml
2. **Environment variables not loaded**: Ensure `.env` file exists and is properly formatted
3. **Build failures**: Check if all dependencies are properly specified in pyproject.toml
4. **MongoDB connection issues**: Ensure MongoDB service is healthy before starting the app
5. **Permission issues**: Check file permissions for logs directory

### Health Check

The application includes a health check endpoint at `/ping`. You can verify the application is running:

```bash
curl http://localhost:3050/ping
```

Expected response: `{"message": "PONG!! Hello, World!"}`

### MongoDB Health Check

Check MongoDB status:

```bash
docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')"
```

Expected response: `{ ok: 1 }`
