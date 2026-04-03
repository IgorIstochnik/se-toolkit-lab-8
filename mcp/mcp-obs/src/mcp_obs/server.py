import os
import httpx
from mcp.server.fastmcp import FastMCP

VICTORIALOGS_URL = os.environ.get("NANOBOT_VICTORIALOGS_URL", "http://victorialogs:9428")
VICTORIATRACES_URL = os.environ.get("NANOBOT_VICTORIATRACES_URL", "http://victoriatraces:10428")

mcp = FastMCP("observability")

@mcp.tool()
def logs_search(query: str, limit: int = 20) -> str:
    """Search VictoriaLogs using LogsQL. Returns matching log entries as JSON lines."""
    url = f"{VICTORIALOGS_URL}/select/logsql/query"
    resp = httpx.post(url, params={"query": query, "limit": limit}, timeout=10)
    resp.raise_for_status()
    lines = resp.text.strip().split("\n")
    if not lines or lines == [""]:
        return "No log entries found."
    return "\n".join(lines[:limit])

@mcp.tool()
def logs_error_count(service: str = "", minutes: int = 60) -> str:
    """Count errors in VictoriaLogs over the last N minutes for a service."""
    time_part = f"_time:{minutes}m"
    svc_part = f'service.name:"{service}"' if service else ""
    query = f"{time_part} {svc_part} severity:ERROR".strip()
    url = f"{VICTORIALOGS_URL}/select/logsql/query"
    resp = httpx.post(url, params={"query": query, "limit": 1000}, timeout=10)
    resp.raise_for_status()
    lines = [l for l in resp.text.strip().split("\n") if l.strip()]
    return f"Found {len(lines)} error(s) in the last {minutes} minutes" + (f" for {service}" if service else "") + "."

@mcp.tool()
def traces_list(service: str = "Learning Management Service", limit: int = 10) -> str:
    """List recent traces from VictoriaTraces (Jaeger-compatible API)."""
    url = f"{VICTORIATRACES_URL}/select/jaeger/api/traces"
    resp = httpx.get(url, params={"service": service, "limit": limit}, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if not data.get("data"):
        return f"No traces found for {service}."
    out = []
    for t in data["data"][:limit]:
        trace_id = t.get("traceID", "unknown")
        spans = [s.get("operationName", "?") for s in t.get("spans", [])]
        out.append(f"trace_id: {trace_id} spans: {spans}")
    return "\n".join(out)

@mcp.tool()
def traces_get(trace_id: str) -> str:
    """Fetch a specific trace by ID from VictoriaTraces."""
    url = f"{VICTORIATRACES_URL}/select/jaeger/api/traces/{trace_id}"
    resp = httpx.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if not data.get("data"):
        return f"Trace {trace_id} not found."
    t = data["data"][0]
    out = [f"Trace: {t.get('traceID', trace_id)}"]
    for span in t.get("spans", []):
        tags = {tag["key"]: tag["value"] for tag in span.get("tags", []) if "key" in tag}
        out.append(f"  {span.get('operationName', '?')} duration={span.get('duration', 0)}us")
        if span.get("logs"):
            for log in span["logs"]:
                fields = {f["key"]: f["value"] for f in log.get("fields", []) if "key" in f}
                out.append(f"    log: {fields}")
    return "\n".join(out)

def main():
    mcp.run()

if __name__ == "__main__":
    main()
