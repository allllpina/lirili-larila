# Docker-compose configuration
The `docker-compose.yml` file describes the project infrastructure, including all services, databases, networks, and dependencies.
## Configuration
```yaml
version: "3.9"

# Shared network for communication between containers

networks: 
	backend: 
		driver: bridge

services:
	# ------------------------------------------------------- 
	# 1. API Gateway (Nginx) 
	# -------------------------------------------------------
	nginx: build: ./nginx 
		ports: 
			- "1313:1313" # The only port exposed to the outside 
		depends_on: 
			- auth_service 
			- tasks_service
			- frontend 
		networks: 
			- backend 
		restart: 
			unless-stopped
	# ------------------------------------------------------- 
	# 2. Frontend (React) 
	# -------------------------------------------------------
	frontend:
		build:
			context: ./frontend
			dockerfile: Dockerfile
		networks:
			- backend
		restart: unless-stopped
		#ports are not exposed to the host machine; access is only via Gateway
		
	# ------------------------------------------------------- 
	# 3. Auth Service (Python FastAPI) 
	# -------------------------------------------------------	
	auth_service: 
	build: ./auth 
	depends_on: 
		- db-users 
	networks: 
		- backend 
	restart: unless-stopped
	# ------------------------------------------------------- 
	# 4. Tasks Service (Python FastAPI + WebSockets) 
	# -------------------------------------------------------
	tasks_service: 
		build: ./tasks_mservice 
		depends_on: 
			- db-tasks
		networks: 
			- backend 
		restart: unless-stopped
	# ------------------------------------------------------- 
	# 5. Database: Users (PostgreSQL)
	# -------------------------------------------------------
	db-users: 
		build: ./db_users 
		env_file: ./db_users/.env 
		volumes: 
			- db_users_data:/var/lib/postgresql/data # Data persistence 
		networks: 
			- backend 
		restart: unless-stopped
	# ------------------------------------------------------- 
	# 6. Database: Tasks (MongoDB) 
	# -------------------------------------------------------
	db-tasks: 
		image: mongo:latest 
		volumes: 
			- db_tasks_data:/data/db # Data persistence 
		networks: 
			- backend 
		restart: unless-stopped
	# Volumes for storing database data
	volumes:
		db_users_data:
		db_tasks_data:
```