FROM ghcr.io/openclaw/openclaw:latest

USER root

RUN set -eux; \
    mkdir -p /var/lib/apt/lists/partial; \
    apt-get update; \
    apt-get install -y --no-install-recommends curl ca-certificates git jq redis-tools; \
    rm -rf /var/lib/apt/lists/*; \
    curl -LsSf https://astral.sh/uv/install.sh | sh; \
    export PATH="/root/.local/bin:${PATH}"; \
    uv tool install --python 3.13 kimi-cli==1.18.0; \
    npm install -g vite@^7.1.9; \
    npm install -g \
      opencode-ai@1.2.24 \
      opencode-linux-x64@1.2.24 \
      @lancedb/lancedb@^0.26.2 \
      @matrix-org/matrix-sdk-crypto-nodejs@^0.4.0 \
      @opentelemetry/api@^1.9.0 \
      @opentelemetry/api-logs@^0.213.0 \
      @opentelemetry/exporter-logs-otlp-proto@^0.213.0 \
      @opentelemetry/exporter-metrics-otlp-proto@^0.213.0 \
      @opentelemetry/exporter-trace-otlp-proto@^0.213.0 \
      @opentelemetry/resources@^2.6.0 \
      @opentelemetry/sdk-logs@^0.213.0 \
      @opentelemetry/sdk-metrics@^2.6.0 \
      @opentelemetry/sdk-node@^0.213.0 \
      @opentelemetry/sdk-trace-base@^2.6.0 \
      @opentelemetry/semantic-conventions@^1.40.0 \
      @pierre/diffs@1.1.0 \
      @twurple/api@^8.0.3 \
      @twurple/auth@^8.0.3 \
      @twurple/chat@^8.0.3 \
      @urbit/aura@^3.0.0 \
      @vector-im/matrix-bot-sdk@0.8.0-element.3 \
      google-auth-library@^10.6.1 \
      nostr-tools@^2.23.3 \
      zca-js@2.1.1; \
    for f in /root/.profile /root/.bashrc; do \
      grep -vF '. "$HOME/.local/bin/env"' "$f" > "${f}.tmp"; \
      mv "${f}.tmp" "$f"; \
    done; \
    ln -sf /root/.local/share/uv/tools/kimi-cli/bin/kimi /usr/local/bin/kimi; \
    ln -sf /usr/local/lib/node_modules/opencode-linux-x64/bin/opencode /usr/local/bin/opencode

COPY infrastructure/openclaw/openclaw-preflight.sh /usr/local/bin/openclaw-preflight
COPY infrastructure/openclaw/openclaw-entrypoint.sh /usr/local/bin/openclaw-forged-entrypoint

RUN chmod +x /usr/local/bin/openclaw-preflight /usr/local/bin/openclaw-forged-entrypoint

ENTRYPOINT ["openclaw-forged-entrypoint"]
CMD ["node","openclaw.mjs","gateway","--allow-unconfigured"]
