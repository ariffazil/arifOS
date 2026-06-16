# Lease Authority Policy
#
# Purpose: Authorize a lease based on actor_id, action_class, scope, and tool.
# Used by: arif_lease_issue() and arif_lease_inspect() in arifOS.
# F13: Sovereign override always allowed.

package arifos.lease

import future.keywords.if
import future.keywords.in

default allow = false
default deny  = false
default sabar = true   # When in doubt, SABAR (ask)

# Sovereign override is always allowed
override = true if {
    input.actor_id == "arif"
    input.action_class in {"SEAL", "GOVERNED"}
}

# Read-only tools: any actor with valid session can lease
allow if {
    input.action_class == "OBSERVE"
    input.session_id != ""
}

# Mutation tools: require sovereign or governance authority
allow if {
    input.action_class == "MUTATE"
    input.actor_id in {"arif", "FORGE", "HERMES"}
    input.session_id != ""
}

# Seal tools: sovereign only (with override path for F13 vouches)
allow if {
    input.action_class == "SEAL"
    input.actor_id == "arif"
}

# Anything else: SABAR (default)
deny if {
    input.action_class in {"MUTATE", "SEAL"}
    not allow
}

confidence := 0.85 if allow

confidence := 0.90 if {
    not allow
    deny
}

confidence := 0.70 if {
    not allow
    not deny
}
