# MEMORY LIFECYCLE SPECIFICATION
> **Authority:** 888_JUDGE  
> **Version:** v1.0.0-SEAL  
> **Status:** CONSTITUTIONAL MANDATE  
> **Band:** 000_KERNEL (F1 Amanah, F11 Auditability)

---

## 🎯 PURPOSE

Define data retention, expiration, and purge policies for the vault_ledger system. Ensures data hygiene, regulatory compliance, and the right to be forgotten while maintaining audit integrity.

**F1 (Amanah):** Users must be able to retract their data.  
**F11 (Auditability):** Retraction must itself be auditable.

---

## 📐 DATA CLASSIFICATION

### Sensitivity Tiers

| Tier | Description | Examples | Default TTL |
|------|-------------|----------|-------------|
| **T0: Public** | Non-sensitive, shareable | Documentation, public configs | 7 years |
| **T1: Operational** | Session working data | Tool outputs, intermediate results | 30 days |
| **T2: Personal** | User-specific data | Preferences, history | 90 days |
| **T3: Sensitive** | High privacy impact | API keys, personal identifiers | 7 days |
| **T4: Critical** | Security/audit critical | Auth events, violations | 7 years |

### Classification Rules

```python
def classify_data(payload: dict, context: Context) -> SensitivityTier:
    """
    Automatically classify data sensitivity.
    """
    
    # Critical: Always audit events
    if payload.get('event_type') in ['AUTH', 'VIOLATION', 'OVERRIDE']:
        return SensitivityTier.CRITICAL
    
    # Sensitive: Contains secrets
    if any(keyword in str(payload) for keyword in ['key', 'password', 'secret', 'token']):
        return SensitivityTier.SENSITIVE
    
    # Personal: Linked to user identity
    if payload.get('actor_id') not in ['anonymous', 'system']:
        return SensitivityTier.PERSONAL
    
    # Operational: Working session data
    if payload.get('session_id') and payload.get('tool'):
        return SensitivityTier.OPERATIONAL
    
    # Default: Public
    return SensitivityTier.PUBLIC
```

---

## ⏰ TTL (TIME-TO-LIVE) POLICY

### Default Retention Schedule

```
┌─────────────────────────────────────────────────────────────────┐
│  DEFAULT TTL SCHEDULE                                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  T0 Public      ████████████████████████████████████████████    │
│                 0        1y       3y       5y       7y           │
│                                                                  │
│  T1 Operational ████                                            │
│                 0   30d                                          │
│                                                                  │
│  T2 Personal    ████████████                                    │
│                 0       90d                                      │
│                                                                  │
│  T3 Sensitive   ███                                             │
│                 0   7d                                           │
│                                                                  │
│  T4 Critical    ████████████████████████████████████████████    │
│                 0        1y       3y       5y       7y           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### TTL Overrides

| Override | Effect | Authority Required |
|----------|--------|-------------------|
| `persist` | Prevent auto-expiry | 888_JUDGE |
| `accelerate` | Purge before TTL | Data owner OR 888 |
| `extend` | Increase TTL | Data owner |
| `classify_up` | Move to higher tier | 888_JUDGE |

---

## 🗑️ PURGE PROTOCOLS

### Automatic Expiration

```python
async def auto_purge_expired_records():
    """
    Daily cron job to purge expired records.
    Runs at 03:00 UTC (low-traffic period).
    """
    
    now = datetime.utcnow()
    expired = await vault.query({
        'expires_at': {'$lt': now},
        'persist': {'$ne': True}
    })
    
    for record in expired:
        # Soft delete first (24h grace period)
        await vault.update(record.id, {
            'status': 'pending_purge',
            'purge_scheduled_at': now + timedelta(hours=24)
        })
        
        # Log the pending purge
        await vault.insert({
            'event_type': 'PURGE_SCHEDULED',
            'target_record': record.id,
            'scheduled_at': now + timedelta(hours=24)
        })
```

### Hard Purge

```python
async def hard_purge(record_id: str, actor_id: str, reason: str):
    """
    Permanently delete a record.
    F11: The purge itself is recorded (meta-audit).
    """
    
    record = await vault.get(record_id)
    
    # Verify authority
    if actor_id != "888_JUDGE" and actor_id != record.owner:
        raise PermissionError("VOID_AUTH: Insufficient authority for purge")
    
    # Create purge record before deletion (F11)
    purge_record = {
        'event_type': 'PURGE_EXECUTED',
        'purged_record_id': record_id,
        'purged_at': datetime.utcnow().isoformat(),
        'purged_by': actor_id,
        'purged_reason': reason,
        'record_metadata': {
            'created_at': record.created_at,
            'sensitivity_tier': record.sensitivity_tier,
            'size_bytes': record.size_bytes
        }
    }
    
    # Insert purge record
    await vault.insert(purge_record)
    
    # Hard delete the record
    await vault.delete(record_id)
    
    # Verify deletion
    verify = await vault.get(record_id)
    if verify:
        raise RuntimeError("Purge failed: record still exists")
```

### Right to Forget

```python
async def right_to_forget(
    actor_id: str,
    scope: ForgetScope
) -> ForgetReport:
    """
    User-initiated data purge.
    
    Scope options:
      - 'session': Current session only
      - 'today': All data from today
      - 'week': All data from past 7 days
      - 'all': All data (requires 888 confirmation)
    """
    
    if scope == 'all' and actor_id != "888_JUDGE":
        # Require 888 confirmation for complete purge
        await request_confirmation('888_JUDGE', {
            'request_type': 'right_to_forget',
            'requester': actor_id,
            'scope': scope
        })
    
    # Find all matching records
    cutoff = calculate_cutoff(scope)
    records = await vault.query({
        'actor_id': actor_id,
        'created_at': {'$gte': cutoff},
        'event_type': {'$ne': 'PURGE_EXECUTED'}  # Don't purge purge records
    })
    
    # Cannot purge CRITICAL tier (audit requirement)
    critical_records = [r for r in records if r.sensitivity_tier == 'CRITICAL']
    if critical_records:
        # Redact instead of purge
        for record in critical_records:
            await vault.update(record.id, {
                'payload': '[REDACTED - Right to Forget exercised]',
                'redacted_at': datetime.utcnow().isoformat(),
                'redacted_by': actor_id
            })
    
    # Purge non-critical records
    purged = []
    for record in records:
        if record.sensitivity_tier != 'CRITICAL':
            await hard_purge(record.id, actor_id, 'Right to Forget')
            purged.append(record.id)
    
    return ForgetReport(
        scope=scope,
        records_purged=len(purged),
        records_redacted=len(critical_records),
        purge_ids=purged
    )
```

---

## 🔄 VECTOR MEMORY LIFECYCLE

### Vector Store Operations

```python
class VectorMemoryLifecycle:
    """
    Lifecycle management for vector embeddings.
    """
    
    TTL_BY_RELEVANCE = {
        'hot': timedelta(days=7),      # Frequently accessed
        'warm': timedelta(days=30),    # Occasionally accessed
        'cold': timedelta(days=90),    # Rarely accessed
        'frozen': timedelta(days=365)  # Archived
    }
    
    async def store_with_ttl(
        self,
        content: str,
        embedding: List[float],
        metadata: dict
    ):
        """
        Store vector with automatic TTL assignment.
        """
        # Determine initial relevance
        relevance = self.assess_relevance(content, metadata)
        
        # Calculate expiration
        ttl = self.TTL_BY_RELEVANCE[relevance]
        expires_at = datetime.utcnow() + ttl
        
        await self.vector_store.insert({
            'content': content,
            'embedding': embedding,
            'metadata': metadata,
            'relevance': relevance,
            'access_count': 0,
            'created_at': datetime.utcnow(),
            'expires_at': expires_at
        })
    
    async def access_vector(self, vector_id: str):
        """
        Track access and update relevance.
        """
        vector = await self.vector_store.get(vector_id)
        
        # Increment access count
        vector.access_count += 1
        
        # Promote relevance on frequent access
        if vector.access_count > 10 and vector.relevance == 'warm':
            vector.relevance = 'hot'
            vector.expires_at = datetime.utcnow() + self.TTL_BY_RELEVANCE['hot']
        
        await self.vector_store.update(vector_id, vector)
        return vector
    
    async def decay_old_vectors(self):
        """
        Demote relevance of old vectors.
        """
        old_vectors = await self.vector_store.query({
            'last_accessed': {'$lt': datetime.utcnow() - timedelta(days=30)}
        })
        
        for vector in old_vectors:
            # Demote relevance tier
            if vector.relevance == 'hot':
                vector.relevance = 'warm'
            elif vector.relevance == 'warm':
                vector.relevance = 'cold'
            elif vector.relevance == 'cold':
                vector.relevance = 'frozen'
            
            await self.vector_store.update(vector.id, vector)
```

---

## 📊 HYGIENE METRICS

### Data Hygiene Dashboard

| Metric | Target | Description |
|--------|--------|-------------|
| Storage Efficiency | > 80% | (Active data) / (Total storage) |
| Purge Lag | < 24h | Time from expiry to actual purge |
| Access Recency | < 30d | Avg days since last access |
| Zombie Records | < 1% | Orphaned records (no owner) |
| Redaction Ratio | < 5% | Redacted / Total CRITICAL |

### Hygiene Report

```python
async def generate_hygiene_report() -> HygieneReport:
    """
    Generate monthly data hygiene report.
    """
    
    total_records = await vault.count()
    expired_pending = await vault.count({'status': 'pending_purge'})
    by_tier = await vault.aggregate('$sensitivity_tier')
    
    avg_age = await vault.average_age()
    storage_bytes = await vault.total_size()
    
    return HygieneReport(
        generated_at=datetime.utcnow(),
        total_records=total_records,
        expired_pending=expired_pending,
        distribution_by_tier=by_tier,
        average_record_age_days=avg_age,
        total_storage_bytes=storage_bytes,
        recommendations=generate_recommendations(by_tier, avg_age)
    )
```

---

## 📋 COMPLIANCE CHECKLIST

For memory implementers:

- [ ] Classify all data on ingestion
- [ ] Set TTL based on sensitivity tier
- [ ] Implement soft-delete before hard purge
- [ ] Log all purge operations
- [ ] Support right_to_forget
- [ ] Redact (don't purge) CRITICAL tier
- [ ] Run daily auto-purge cron
- [ ] Generate monthly hygiene reports
- [ ] Respect persist overrides (888 only)

---

## 🔗 RELATED DOCUMENTS

- `000_CONSTITUTION.md` (F1 Amanah, F11 Auditability)
- `VERDICT_SCHEMA_STANDARD.md` (trace.integrity_hash)
- `AUTH_PROTOCOL.md` (session revocation)

---

*Ditempa Bukan Diberi* [ΔΩΨ|888] 🗑️
