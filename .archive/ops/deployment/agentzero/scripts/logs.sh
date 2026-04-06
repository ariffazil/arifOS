#!/bin/bash
service="${1:-arifos}"
docker compose logs -f "$service"
