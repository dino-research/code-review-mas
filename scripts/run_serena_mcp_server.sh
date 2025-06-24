#!/bin/bash

# --- CẤU HÌNH ---
SERENA_DIR="/home/dino/Documents/dino-research/serena"

echo "Starting Serena MCP Server..."
echo "Serena directory: $SERENA_DIR"

# Kích hoạt môi trường ảo của SERENA
uv run \
--directory $SERENA_DIR serena-mcp-server \
--context 'agent' \
--mode 'interactive' \
--transport 'sse' \
--host '0.0.0.0' \
--port '50051' \
--enable-web-dashboard 'True' \
--log-level 'DEBUG' \
--trace-lsp-communication 'True'
