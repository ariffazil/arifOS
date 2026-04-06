#!/bin/bash
echo "=== SYSTEMCTL STATUS ===" > /tmp/e2e_report.txt
systemctl status arifos-embeddings --no-pager >> /tmp/e2e_report.txt 2>&1

echo -e "\n=== JOURNALCTL ===" >> /tmp/e2e_report.txt
journalctl -u arifos-embeddings -n 30 --no-pager >> /tmp/e2e_report.txt 2>&1

echo -e "\n=== OPENCLAW CONFIG (MEMORY) ===" >> /tmp/e2e_report.txt
cat /root/openclaw_data/config/openclaw.json | grep -A 15 '"memory"' >> /tmp/e2e_report.txt 2>&1

echo -e "\n=== API TEST ===" >> /tmp/e2e_report.txt
docker exec openclaw curl -s -X POST http://172.17.0.1:8000/v1/embeddings \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer dummy_key' \
  -d '{"input":["Testing the AGI_ASI constitutional floors."], "model":"/opt/arifos-embeddings/bge-arifOS"}' >> /tmp/e2e_report.txt 2>&1

echo "Report generated at /tmp/e2e_report.txt"
