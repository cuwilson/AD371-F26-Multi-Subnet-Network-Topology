# AD371-F26-Multi-Subnet-Network-Topology


### Initial Prompt — Network Topology Generation
Act as a senior network systems architect. I need a multi-container network topology configured using Docker Compose demonstrating isolated subnets and reverse-proxy load balancing for a web application.
8
 

The architecture must include:

Two Isolated Network Subnets:
   - 'public_subnet': Accessible from the host/internet.

   - 'private_subnet': Isolated backend network with no direct external port exposure.

A Load Balancer (Nginx or HAProxy):
   - Dual-homed on both 'public_subnet' and 'private_subnet'.

   - Exposes port 80/443 to the host.

   - Configured with an upstream pool distributing requests across backend instances using Round-Robin.

At least Two Web Application Backend Replicas (e.g., Node.js or Python):
   - Connected ONLY to 'private_subnet'.

   - Each instance must return a unique identifier (e.g., container hostname or server ID) so I can verify which instance handled the request.

   - Includes a simple health-check endpoint (/healthz).

 

Provide the Docker Compose file, the load balancer configuration file (e.g., nginx.conf), the minimal backend application code, and step-by-step instructions to run and test it. 

## AI Disclosure & Configuration Audit

### AI Tool Used

ChatGPT (OpenAI) was used to generate the initial Docker Compose network topology, Nginx configuration, and Python backend application.

### What the AI Generated Correctly

The initial configuration included:

- Two Docker bridge networks: `public_subnet` and `private_subnet`.
- Nginx connected to both networks.
- Two backend instances connected only to the private subnet.
- No backend ports published directly to the host.
- Round-robin load balancing using Nginx.
- A `/healthz` endpoint for health checks.
- An `/api/instance` endpoint to identify the responding backend.

### Configuration Issue Identified

During the audit, I identified that the initial Nginx configuration did not explicitly define connection timeouts or upstream retry behavior.

Although Nginx provides some default failover functionality, I added the following settings to make its behavior more predictable:

- `proxy_connect_timeout 2s`
- `proxy_send_timeout 5s`
- `proxy_read_timeout 5s`
- `proxy_next_upstream error timeout http_502 http_503 http_504`
- `proxy_next_upstream_tries 2`

I also changed `max_fails` from 3 to 1 so Nginx would temporarily mark an unresponsive backend unavailable after one failed attempt.

### Verification

After making these changes, I tested the configuration using Docker Compose. All 10 requests succeeded during the failover test, and both backend instances resumed handling traffic after recovery.

These results confirm that the configuration behaved as expected during the local tests, although they do not guarantee zero downtime under every failure condition.


## Network Architecture

The application uses two isolated Docker bridge networks, with Nginx acting as the load balancer between the public and private tiers.

```text
           Host / Browser
          http://localhost
                 |
                 | Port 80
                 v
+-----------------------------------+
| PUBLIC SUBNET                     |
| 172.28.10.0/24                    |
|                                   |
|       Nginx Load Balancer         |
|       Round-Robin Routing         |
|                                   |
+-----------------+-----------------+
                  |
                  | Private network connection
                  v
+-----------------------------------+
| PRIVATE SUBNET                    |
| 172.28.20.0/24                    |
|                                   |
|  +-------------+ +-------------+  |
|  |  backend1   | |  backend2   |  |
|  |  Port 3000  | |  Port 3000  |  |
|  +-------------+ +-------------+  |
|                                   |
|  No direct host port exposure     |
+-----------------------------------+
```

### Network Security

- **Public subnet:** Provides the host-facing network for Nginx.
- **Private subnet:** Contains both backend instances and uses `internal: true` to restrict external connectivity.
- **Nginx:** Connects to both networks and distributes incoming requests using round-robin.
- **Backend instances:** Connect only to the private subnet and do not publish ports to the host.

The load balancer acts as the single public entry point for application traffic.


## QA Test Results

The Docker Compose network topology was tested locally to verify load balancing, backend availability, network isolation, and application health.

| Test | Result | Findings |
|---|---|---|
| Round-Robin Distribution | PASS | 10 consecutive requests alternated between backend1 and backend2, with 5 requests handled by each instance. |
| High Availability / Failover | PASS | After stopping backend1, all 10 requests were successfully handled by backend2 without failed requests. |
| Backend Recovery | PASS | After restarting backend1, both backend instances resumed receiving requests. |
| Network Isolation | PASS | Direct connections to localhost:3000 and localhost:3001 failed, while requests through Nginx on port 80 succeeded. |
| Health Check | PASS | The /healthz endpoint returned HTTP 200 and `{"status":"ok"}`. |
| Browser Inspection | PASS | Requests returned HTTP 200, and the browser Console showed no errors after correcting a missing favicon. |
| Container Logs | PASS | Docker logs confirmed successful HTTP requests to the backend instances. |

### Testing Conclusion

All planned QA tests passed. Nginx successfully distributed traffic between two backend instances and continued serving requests when one backend was stopped. The private backend ports were not directly accessible through localhost, while the public Nginx endpoint remained available.

These results demonstrate the intended load-balancing behavior, recovery, and host-port isolation in the local Docker environment.


