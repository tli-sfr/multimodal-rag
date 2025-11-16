# Starting Docker Services

## Quick Start

To run the Multimodal RAG system, you need to start the backend services first.

### 1. Start Docker Desktop

Make sure Docker Desktop is running on your Mac.

### 2. Start All Services

```bash
docker-compose up -d
```

This starts:
- **Qdrant** - Vector database (port 6333)
- **Neo4j** - Graph database (ports 7474, 7687)
- **Redis** - Caching (port 6379)

### 3. Verify Services Are Running

```bash
docker ps
```

You should see 3 containers running.

### 4. Wait for Services to Initialize

Wait 10-20 seconds for all services to fully start.

### 5. Start the Streamlit UI

```bash
streamlit run src/ui/app.py
```

Or:

```bash
python run_ui.py
```

### 6. Open in Browser

Navigate to: http://localhost:8501

You should now see "✅ Pipeline initialized" in the System Status section.

## Verify Individual Services

### Check Qdrant
```bash
curl http://localhost:6333/healthz
```
Should return: `{"title":"healthz","version":"1.x.x"}`

### Check Neo4j
```bash
curl http://localhost:7474
```
Should return HTML content (Neo4j browser interface)

Or open in browser: http://localhost:7474

### Check Redis
```bash
docker exec -it multimodal-redis-1 redis-cli ping
```
Should return: `PONG`

## Stopping Services

When you're done:

```bash
docker-compose down
```

To also remove data volumes:

```bash
docker-compose down -v
```

## Troubleshooting

### "Cannot connect to Docker daemon"

**Solution**: Start Docker Desktop application

### "Port already in use"

**Solution**: Stop the conflicting service or change ports in `docker-compose.yml`

```bash
# Find what's using the port (e.g., 6333)
lsof -i :6333

# Kill the process if needed
kill -9 <PID>
```

### Services won't start

**Solution**: Clean up and restart

```bash
docker-compose down -v
docker-compose up -d
```

### Check service logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs qdrant
docker-compose logs neo4j
docker-compose logs redis
```

## Configuration

### Neo4j Credentials

Default credentials (set in `docker-compose.yml`):
- Username: `neo4j`
- Password: `password123`

You can change these in the `.env` file:
```bash
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```

### Qdrant Configuration

Qdrant runs with default settings. Data is persisted in Docker volume `qdrant_storage`.

### Redis Configuration

Redis runs with default settings. No password required for local development.

## Next Steps

Once services are running:

1. **Configure API Keys** in `.env`:
   ```bash
   OPENAI_API_KEY=your_key_here
   ```

2. **Upload Documents** through the Streamlit UI

3. **Query Your Data** using natural language

4. **View Evaluation Metrics** in the Evaluation tab

