# Isolated Docker Networks and Nginx Round-Robin Load Balancing

## Requirements
Docker Desktop or Docker Engine with Compose. Port 80 must be free.

## Run
```sh
docker compose config
docker compose up --build -d
docker compose ps
```
Open http://localhost and click **Send test request** repeatedly.

## Test the backend pool
Run repeatedly:
```sh
curl http://localhost/api/instance
```
Typical responses alternate between `backend1` and `backend2`.
For PowerShell:
```powershell
1..6 | ForEach-Object { (Invoke-RestMethod http://localhost/api/instance).server_id }
```

## Health check
```sh
curl http://localhost/healthz
docker compose ps
```

## Verify networks and port isolation
```sh
docker network inspect network-topology_public_subnet
docker network inspect network-topology_private_subnet
docker compose ps
```
Only nginx should publish `0.0.0.0:80->80/tcp` (or equivalent). Backend port 3000 is **not published**. Both backends only join `private_subnet` and nginx joins both.

## Observe logs
```sh
docker compose logs -f nginx backend1 backend2
```

## Stop
```sh
docker compose down
```

## Vercel
This repository includes `Dockerfile.vercel` at the root so the same Python HTTP application can run on Vercel as a container-based Function. Import the repository as a Vercel project (root directory at repository root), or run `vercel deploy` with the Vercel CLI. Vercel will not run `compose.yaml`, local Docker bridge networks, or the local Nginx reverse proxy. The platform controls scaling and routing; `/healthz` and `/api/instance` remain available. Vercel-generated container hostnames may change with instances and should not be treated as proof of round-robin balancing.

## Notes
- This is an HTTP-only local architecture demo. For public internet deployment, configure trusted TLS certificates on a real ingress/edge proxy.
- Docker's `internal: true` blocks normal external connectivity on `private_subnet`. The dual-homed proxy is intentionally able to reach both networks.
- Nginx open-source passive failover is separate from Docker health status. If a backend becomes unreachable, Nginx can temporarily mark it failed. Startup `depends_on` checks initial backend health.
- If the preselected 172.28.x.x address ranges overlap with your VPN or existing Docker networks, adjust the Compose subnets.
