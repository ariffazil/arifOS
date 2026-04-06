import sys

path = 'docker-compose.yml'
with open(path, 'r') as f:
    lines = f.readlines()

new_lines = []
in_ollama = False

for line in lines:
    stripped = line.strip()
    
    # SERVICE DEFINITION: Looking for exactly '  ollama:' (2 spaces)
    if stripped == 'ollama:' and line.startswith('  ') and not line.startswith('   '):
        in_ollama = True
        new_lines.append(line)
        new_lines.append('    image: ollama/ollama:latest\n')
        new_lines.append('    container_name: ollama_engine\n')
        new_lines.append('    init: true\n')
        new_lines.append('    environment:\n')
        new_lines.append('      - OLLAMA_KEEP_ALIVE=24h\n')
        new_lines.append('      - OLLAMA_MAX_LOADED_MODELS=2\n')
        new_lines.append('      - OLLAMA_NUM_PARALLEL=2\n')
        new_lines.append('      - OLLAMA_HOST=0.0.0.0\n')
        new_lines.append('      - OMP_NUM_THREADS=4\n')
        new_lines.append('    volumes:\n')
        new_lines.append('      - /opt/arifos/data/ollama:/root/.ollama\n')
        new_lines.append('    networks:\n')
        new_lines.append('      - arifos_trinity\n')
        new_lines.append('    healthcheck:\n')
        new_lines.append('      test: ["CMD-SHELL", "OLLAMA_HOST=http://127.0.0.1:11434 ollama list >/dev/null 2>&1 || exit 1"]\n')
        new_lines.append('      interval: 30s\n')
        new_lines.append('      timeout: 10s\n')
        new_lines.append('      retries: 3\n')
        new_lines.append('      start_period: 30s\n')
        new_lines.append('    deploy:\n')
        new_lines.append('      resources:\n')
        new_lines.append('        limits:\n')
        new_lines.append('          cpus: "3.0"\n')
        new_lines.append('          memory: 12G\n')
        new_lines.append('        reservations:\n')
        new_lines.append('          cpus: "0.5"\n')
        new_lines.append('          memory: 512M\n')
        new_lines.append('    mem_limit: 12G\n')
        new_lines.append('    mem_reservation: 512M\n')
        new_lines.append('    restart: unless-stopped\n')
        new_lines.append('    security_opt:\n')
        new_lines.append('      - no-new-privileges:true\n')
        new_lines.append('    depends_on:\n')
        new_lines.append('      - traefik\n')
        new_lines.append('      - qdrant\n')
        continue
    
    if in_ollama:
        if stripped == '':
            continue
        indent = len(line) - len(line.lstrip())
        if indent > 2:
            continue
        else:
            in_ollama = False
            new_lines.append(line)
    else:
        new_lines.append(line)

with open(path + '.new', 'w') as f:
    f.writelines(new_lines)
