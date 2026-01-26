// arifOS v52.5.1 k6 Load Test for /checkpoint endpoint
// Tests constitutional governance performance under load

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');

export let options = {
  vus: 10,
  duration: '30s',
  thresholds: {
    http_req_duration: ['p(95)<50'], // p95 < 50ms (target)
    http_req_failed: ['rate<0.1'],   // <10% errors
    errors: ['rate<0.1'],
  },
};

const BASE_URL = __ENV.RAILWAY_URL || 'http://localhost:8000';

export default function () {
  const payload = JSON.stringify({
    query: 'Is this action safe?',
    context: 'k6 load test for constitutional checkpoint',
    stakeholders: ['user', 'system'],
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  let res = http.post(`${BASE_URL}/checkpoint`, payload, params);

  // Validate response
  const checkRes = check(res, {
    'status is 200': (r) => r.status === 200,
    'has verdict': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.verdict !== undefined;
      } catch (e) {
        return false;
      }
    },
    'verdict is valid': (r) => {
      try {
        const body = JSON.parse(r.body);
        return ['SEAL', 'PARTIAL', 'VOID', 'SABAR', '888_HOLD'].includes(body.verdict);
      } catch (e) {
        return false;
      }
    },
    'response time OK': (r) => r.timings.duration < 50,
  });

  // Track errors
  errorRate.add(!checkRes);

  sleep(1);
}

export function handleSummary(data) {
  return {
    'stdout': textSummary(data, { indent: ' ', enableColors: true }),
  };
}

function textSummary(data, options) {
  const indent = options.indent || '';
  const colors = options.enableColors || false;
  
  let summary = '\n';
  summary += indent + '========================================\n';
  summary += indent + 'arifOS v52.5.1 Load Test Results\n';
  summary += indent + '========================================\n\n';
  
  const metrics = data.metrics;
  
  // Request stats
  if (metrics.http_reqs) {
    summary += indent + `Total Requests: ${metrics.http_reqs.values.count}\n`;
  }
  
  if (metrics.http_req_duration) {
    summary += indent + `Request Duration:\n`;
    summary += indent + `  avg: ${metrics.http_req_duration.values.avg.toFixed(2)}ms\n`;
    summary += indent + `  min: ${metrics.http_req_duration.values.min.toFixed(2)}ms\n`;
    summary += indent + `  max: ${metrics.http_req_duration.values.max.toFixed(2)}ms\n`;
    summary += indent + `  p95: ${metrics.http_req_duration.values['p(95)'].toFixed(2)}ms\n`;
  }
  
  if (metrics.http_req_failed) {
    const failRate = (metrics.http_req_failed.values.rate * 100).toFixed(2);
    summary += indent + `Failed Requests: ${failRate}%\n`;
  }
  
  if (metrics.checks) {
    const passRate = (metrics.checks.values.rate * 100).toFixed(2);
    summary += indent + `Check Pass Rate: ${passRate}%\n`;
  }
  
  summary += indent + '\n========================================\n';
  
  return summary;
}
