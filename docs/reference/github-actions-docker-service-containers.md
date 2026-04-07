# GitHub Actions: Docker service containers (reference)

**Source:** [Communicating with Docker service containers](https://docs.github.com/en/actions/tutorials/use-containerized-services/use-docker-service-containers) (GitHub Docs)

**Purpose:** Quick context for workflows that attach databases, caches, or other services via `services:` — e.g. future CI work that runs OrangeHRM or backing services in containers.

---

## What service containers are

- Docker containers defined under `jobs.<job_id>.services` that host dependencies (DB, Redis, etc.) for a job.
- GitHub starts a fresh container per service and destroys it when the job ends.
- Steps in the **same job** can talk to those services; you **cannot** use service containers inside a **composite action**.

## Runner requirements

If the workflow uses Docker container actions, **job** containers, or **service** containers:

- **GitHub-hosted:** use an **Ubuntu** runner (e.g. `ubuntu-latest`).
- **Self-hosted:** use a **Linux** runner with **Docker installed**.

## Networking: job in a container vs on the runner

| Job runs… | How to reach a service |
|-----------|-------------------------|
| **In a container** (`container:`) | Use the **service label** as hostname (e.g. `redis`). Bridge network; no host port mapping required between job and services. |
| **On the runner VM** (no job `container:`) | Use **`localhost:<port>`** or **`127.0.0.1:<port>`**. You must **map** service ports to the host with `ports:` under that service. |

Mapping uses Docker publish semantics (e.g. `6379:6379`). See also: [About service containers — port mapping](https://docs.github.com/en/actions/using-containerized-services/about-service-containers#mapping-docker-host-and-service-container-ports).

## Minimal examples (from docs)

**Service + job in container** (hostname = label `redis`):

```yaml
container-job:
  runs-on: ubuntu-latest
  container: node:16-bullseye
  services:
    redis:
      image: redis
```

**Service + job on runner** (map Redis 6379):

```yaml
runner-job:
  runs-on: ubuntu-latest
  services:
    redis:
      image: redis
      ports:
        - 6379:6379
```

## `ports` value patterns

| `ports` entry | Meaning |
|----------------|--------|
| `8080:80` | TCP 80 in container → 8080 on Docker host |
| `8080:80/udp` | UDP 80 in container → 8080 on host |
| `8080/udp` | UDP 8080 in container → random free port on host |

If only the container port is fixed, the host port may be random; use `job.services.<id>.ports[...]` context where documented.

## Registry auth

Use `credentials:` under a service for Docker Hub, GHCR, etc. (username/password or secrets).

## Custom `command` / `entrypoint`

Override image defaults when you need flags (e.g. MySQL `command:`, or `entrypoint` + `command` for etcd-style images). Matches Docker Compose behavior.

## Further reading (official)

- [Creating Redis service containers](https://docs.github.com/en/actions/using-containerized-services/creating-redis-service-containers)
- [Creating PostgreSQL service containers](https://docs.github.com/en/actions/using-containerized-services/creating-postgresql-service-containers)
- [Workflow syntax — `jobs.<job_id>.services`](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#jobsjob_idservices)

---

*This file is a project-local summary; defer to GitHub’s documentation for authoritative, up-to-date behavior.*
