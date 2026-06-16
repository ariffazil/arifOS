# Mutation Authority Policy
#
# Purpose: Authorize any state-mutating action (DB write, file write, vault seal).
# F1 AMANAH: Fail-closed on uncertainty.
# F13 SOVEREIGN: Only Arif or explicitly delegated actor can mutate.

package arifos.mutation

import future.keywords.if
import future.keywords.in

default allow = false
default deny  = false
default sabar = true

# Sovereign mutations
allow if {
    input.actor_id == "arif"
    input.action_class in {"MUTATE", "SEAL"}
}

# Delegated FORGE lane (Arif has explicitly authorized)
allow if {
    input.actor_id == "FORGE"
    input.action_class == "MUTATE"
    input.resource_kind in {"forge_work", "VAULT999_seal", "file_create"}
}

# Reversible mutations: allow any actor with valid session
allow if {
    input.reversible == true
    input.action_class == "MUTATE"
    input.actor_id != ""
    input.session_id != ""
}

# Irreversible mutations: sovereign only
deny if {
    input.reversible == false
    input.action_class in {"MUTATE", "SEAL"}
    input.actor_id != "arif"
}

# Default SABAR for everything else
sabar if {
    not allow
    not deny
}

override := true

confidence := 0.92 if allow

confidence := 0.95 if {
    not allow
    deny
}

confidence := 0.70 if {
    not allow
    not deny
}
