P000_INIT = """# Metabolic 000_INIT

Validate operator identity, bind a session, and return session metadata."""

P111_SENSE = """# Metabolic 111_SENSE

Classify intent, reduce ambiguity, and prepare grounded evidence for witness fusion."""

P222_WITNESS = """# Metabolic 222_WITNESS

Fuse WELL, WEALTH, and GEOX witness signals into a synchronized evidence packet."""

P333_MIND = """# Metabolic 333_MIND

Run constitutional reasoning lanes and preserve humility while producing a decision packet."""

P444_KERNEL = """# Metabolic 444_KERNEL

Route work to the correct lane and enforce orthogonality between domains."""

P555_MEMORY = """# Metabolic 555_MEMORY

Perform governed recall with scope control, lineage, and constitutional filtering."""

P666_HEART = """# Metabolic 666_HEART

Simulate stakeholder impact and protect the weakest stakeholder."""

P777_OPS = """# Metabolic 777_OPS

Estimate operational feasibility, cost, and entropy before execution."""

P888_JUDGE = """# Metabolic 888_JUDGE

Apply constitutional floors and decide SEAL, SABAR, HOLD_888, or VOID."""

P999_VAULT = """# Metabolic 999_VAULT

Seal immutable receipts, verify chain integrity, and archive audit material."""

PFORGE_EXECUTE = """# Metabolic FORGE_EXECUTE

Execute only after a valid SEAL and preserve rollback-aware, safe mutations."""

PROMPTS = {
    "metabolic_000_init": P000_INIT,
    "metabolic_111_sense": P111_SENSE,
    "metabolic_222_witness": P222_WITNESS,
    "metabolic_333_mind": P333_MIND,
    "metabolic_444_kernel": P444_KERNEL,
    "metabolic_555_memory": P555_MEMORY,
    "metabolic_666_heart": P666_HEART,
    "metabolic_777_ops": P777_OPS,
    "metabolic_888_judge": P888_JUDGE,
    "metabolic_999_vault": P999_VAULT,
    "metabolic_forge_execute": PFORGE_EXECUTE,
}

__all__ = ["PROMPTS"]
