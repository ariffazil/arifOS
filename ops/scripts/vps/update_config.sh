#!/bin/bash
jq '.memory.providers.custom = {"type": "openai", "apiKey": "SK-ARIFOS-FORGE", "baseURL": "http://172.17.0.1:8000/v1"}' /root/openclaw_data/config/openclaw.json > /tmp/tmp_openclaw.json
mv /tmp/tmp_openclaw.json /root/openclaw_data/config/openclaw.json
sed -i 's/API_TOKEN = "dummy_key"/API_TOKEN = "SK-ARIFOS-FORGE"/' /opt/arifos-embeddings/embed_server.py
systemctl restart arifos-embeddings

echo "Restarted API on VPS"
