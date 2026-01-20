# Stremio Status
--------------------------------

Access status page at https://status.stremio-status.com, Grafana analytics are at [https://stats.stremio-status.com](https://stats.stremio-status.com/d/home-dashboard/community-status-home?kiosk=true&orgId=1&from=now-24h&to=now&timezone=browser&refresh=1m).

## Self-host with Docker
```
git pull https://github.com/SolitudePy/stremio-status.git
cd stremio-status
cp .env.example .env 
## Edit .env DB_PASSWORD, GRAFANA_PASSWORD, DOMAIN
docker compose up -d
Access through localhost or your reverse-proxy setup (e.g Traefik)
```
