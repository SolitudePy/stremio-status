# Stremio Status
--------------------------------

Access status page at status.stremio-status.com, analytics are at stats.stremio-status.com or through the status page link.


## Self-host with Docker
```
git pull https://github.com/SolitudePy/stremio-status.git
cd stremio-status
cp .env.example .env 
## Edit .env DB_PASSWORD, GRAFANA_PASSWORD, DOMAIN
docker compose up -d
Access through localhost or your reverse-proxy setup (e.g Traefik)
```

