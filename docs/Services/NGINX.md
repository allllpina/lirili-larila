# NGINX Configuration
The main Nginx Gateway acts as the single entry point (Reverse Proxy) for the entire microservices cluster. It routes requests between the frontend, the auth service, and the tasks service, and also handles WebSocket connections.
## Configuration (`main_nginx.conf`)
Most important information:
```nginx
server {
	# External port where the application runs (accessible from the browser)     listen 1313;
	# ========================================================= 
	# 1. Frontend Service (Site Root) 
	# ========================================================= 
	location / { 
		# Redirect to the internal 'frontend' service (port 80) 
		proxy_pass http://frontend:80; 
		proxy_set_header Host $host; 
		proxy_set_header X-Real-IP $remote_addr; 
		
		# WebSocket support (essential for Hot Module Replacement in dev mode) 
		proxy_http_version 1.1; 
		proxy_set_header Upgrade $http_upgrade; 
		proxy_set_header Connection "upgrade"; 
	}
	
	# ========================================================= 
	# 2. Auth Service (Authorization Microservice) 
	# ========================================================= 
	location /auth { 
		# Redirect to the 'auth_service' 
		# Nginx passes all requests with the /auth prefix here 
		proxy_pass http://auth_service:8000; 
		proxy_set_header Host $host; 
		proxy_set_header X-Real-IP $remote_addr; 
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; 
	}
	
	# ========================================================= 
	# 3. Tasks Service (Projects & Tasks Microservice) 
	# =========================================================
	location /lirililarila {
		# Redirect to the 'tasks_service' 
		proxy_pass http://tasks_service:8000; 
		proxy_set_header Host $host; 
		proxy_set_header X-Real-IP $remote_addr;
		
		# ----------------------------------------------------- 
		# WebSocket Configuration (Critical for Real-time) 
		# ----------------------------------------------------- 
		# These headers are required for the correct handshake 
		# of the WebSocket protocol. Without them, Nginx will close the connection.
		proxy_http_version 1.1; 
		proxy_set_header Upgrade $http_upgrade; 
		proxy_set_header Connection "upgrade";
		# Increased timeout to prevent disconnection during idle times 
		proxy_read_timeout 86400;
	}
}
```
### Architecture Features
- **Single Origin:** Thanks to the Gateway, both frontend and backend are available on the same port (`1313`). This eliminates CORS (Cross-Origin Resource Sharing) issues.
- **Service Discovery:** Nginx uses internal Docker DNS to resolve services by their names (`frontend`, `auth_service`, `tasks_service`).