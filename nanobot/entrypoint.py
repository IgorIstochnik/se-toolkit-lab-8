#!/usr/bin/env python3
import json, os, sys

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
RESOLVED_PATH = os.path.join(os.path.dirname(__file__), "config.resolved.json")

def resolve_config():
    with open(CONFIG_PATH) as f:
        cfg = json.load(f)

    api_key = os.environ.get("LLM_API_KEY", "")
    api_base = os.environ.get("LLM_API_BASE_URL", "")
    model = os.environ.get("LLM_API_MODEL", "")
    if api_key:
        cfg["providers"]["custom"]["apiKey"] = api_key
    if api_base:
        cfg["providers"]["custom"]["apiBase"] = api_base
    if model:
        cfg["agents"]["defaults"]["model"] = model

    gw_host = os.environ.get("NANOBOT_GATEWAY_CONTAINER_ADDRESS", "")
    gw_port = os.environ.get("NANOBOT_GATEWAY_CONTAINER_PORT", "")
    if gw_host:
        cfg["gateway"]["host"] = gw_host
    if gw_port:
        cfg["gateway"]["port"] = int(gw_port)

    webchat_addr = os.environ.get("NANOBOT_WEBCHAT_CONTAINER_ADDRESS", "")
    webchat_port = os.environ.get("NANOBOT_WEBCHAT_CONTAINER_PORT", "")
    if "webchat" not in cfg.get("channels", {}):
        cfg.setdefault("channels", {})["webchat"] = {}
    if webchat_addr:
        cfg["channels"]["webchat"]["host"] = webchat_addr
    if webchat_port:
        cfg["channels"]["webchat"]["port"] = int(webchat_port)
    cfg["channels"]["webchat"]["enabled"] = True
    cfg["channels"]["webchat"].setdefault("allowFrom", ["*"])

    lms_backend_url = os.environ.get("NANOBOT_LMS_BACKEND_URL", "")
    lms_api_key = os.environ.get("NANOBOT_LMS_API_KEY", "")
    if lms_backend_url:
        cfg["tools"]["mcpServers"]["lms"]["env"]["NANOBOT_LMS_BACKEND_URL"] = lms_backend_url
    if lms_api_key:
        cfg["tools"]["mcpServers"]["lms"]["env"]["NANOBOT_LMS_API_KEY"] = lms_api_key

    # MCP observability server
    obs_logs_url = os.environ.get("NANOBOT_VICTORIALOGS_URL", "")
    obs_traces_url = os.environ.get("NANOBOT_VICTORIATRACES_URL", "")
    if "mcp_obs" not in cfg["tools"]["mcpServers"]:
        cfg["tools"]["mcpServers"]["mcp_obs"] = {
            "command": "python",
            "args": ["-m", "mcp_obs"],
            "env": {}
        }
    if obs_logs_url:
        cfg["tools"]["mcpServers"]["mcp_obs"]["env"]["NANOBOT_VICTORIALOGS_URL"] = obs_logs_url
    if obs_traces_url:
        cfg["tools"]["mcpServers"]["mcp_obs"]["env"]["NANOBOT_VICTORIATRACES_URL"] = obs_traces_url

    access_key = os.environ.get("NANOBOT_ACCESS_KEY", "")
    ws_url = os.environ.get("NANOBOT_WS_URL", "")
    if "mcp_webchat" not in cfg["tools"]["mcpServers"]:
        cfg["tools"]["mcpServers"]["mcp_webchat"] = {
            "command": "python",
            "args": ["-m", "mcp_webchat"],
            "env": {}
        }
    if ws_url:
        cfg["tools"]["mcpServers"]["mcp_webchat"]["env"]["NANOBOT_WS_URL"] = ws_url
    if access_key:
        cfg["tools"]["mcpServers"]["mcp_webchat"]["env"]["NANOBOT_ACCESS_KEY"] = access_key

    with open(RESOLVED_PATH, "w") as f:
        json.dump(cfg, f, indent=2)
    return RESOLVED_PATH

if __name__ == "__main__":
    resolved = resolve_config()
    workspace = os.environ.get("NANOBOT_WORKSPACE", "./workspace")
    os.execvp("nanobot", ["nanobot", "gateway", "--config", resolved, "--workspace", workspace])
