import httpx

async def check_image_update(image_ref: str) -> dict | None:
    """
    Prüft ob ein neues Docker Image verfügbar ist via Docker Hub / OCI Registry.
    Vergleich über Manifest-Digest.
    image_ref: z.B. "nginx:latest", "ghcr.io/user/repo:main"
    Returns: {remote_digest: str} oder None bei Fehler.
    """
    if "." in image_ref.split("/")[0] and "/" in image_ref:
        return None

    repo = image_ref.split(":")[0]
    tag = image_ref.split(":")[-1] if ":" in image_ref else "latest"
    if "/" not in repo:
        repo = f"library/{repo}"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            token_r = await client.get(
                f"https://auth.docker.io/token?service=registry.docker.io&scope=repository:{repo}:pull"
            )
            token = token_r.json().get("token", "")
            manifest_r = await client.get(
                f"https://registry.hub.docker.com/v2/{repo}/manifests/{tag}",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.docker.distribution.manifest.v2+json",
                },
            )
            remote_digest = manifest_r.headers.get("Docker-Content-Digest", "")
            return {"remote_digest": remote_digest}
    except Exception:
        return None
