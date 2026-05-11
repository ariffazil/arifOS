/**
 * arifOS MCP Apps — Governed Wisdom Registry v2
 *
 * Sources mapped from actual VPS files:
 *  - /root/arifOS/arifosmcp/runtime/constitutional_quotes.json (100 tool-mapped quotes)
 *  - /root/arifOS/archive/DATA/wisdom_quotes.json (arifOS Foundry corpus)
 *  - /root/arifOS/archive/DATA/philosophy_atlas.json (27-zone S×G×Ω atlas)
 *
 * v2 additions:
 *  - attributionConfidence
 *  - scarWeight / shadowWeight / paradoxWeight
 *  - contrastPair / polarity
 *  - void, partial, sabar surfaces
 */

export type WisdomSurface =
  | "anchor"
  | "monitor"
  | "sense"
  | "mind"
  | "heart"
  | "judge"
  | "hold"
  | "vault"
  | "forge"
  | "ops"
  | "empty"
  | "void"
  | "partial"
  | "sabar";

export type WisdomCategory =
  | "truth"
  | "humility"
  | "restraint"
  | "judgment"
  | "memory"
  | "discipline"
  | "responsibility"
  | "peribahasa"
  | "founder"
  | "seal"
  | "love"
  | "paradox"
  | "scar"
  | "power"
  | "wisdom"
  | "shadow";

export type WisdomTone = "calm" | "firm" | "reflective" | "severe";

export interface WisdomQuote {
  id: string;
  text: string;
  author: string;
  source?: string;
  category: WisdomCategory;
  surfaces: WisdomSurface[];
  tone: WisdomTone;
  language: "en" | "ms" | "mixed";
  priority: number;
  active: boolean;
  toolOrigin?: string;
  zoneId?: string;
  attributionConfidence: "verified" | "traditional" | "commonly_attributed" | "disputed";
  sourceUrl?: string;
  scarWeight: number;
  shadowWeight: number;
  paradoxWeight: number;
  contrastPair?: string;
  polarity?: "truth" | "doubt" | "order" | "chaos" | "mercy" | "judgment" | "power" | "restraint" | "seal" | "humility" | "shadow";
}

// ═══════════════════════════════════════════════════════════════════════════════
// LAYER A — Civilizational Canon
// ═══════════════════════════════════════════════════════════════════════════════

const CIVILIZATIONAL_CANON: WisdomQuote[] = [
  {
    id: "INIT_Q_001",
    text: "A journey of a thousand miles begins with a single step.",
    author: "Lao Tzu",
    source: "Tao Te Ching",
    category: "discipline",
    surfaces: ["anchor"],
    tone: "calm",
    language: "en",
    priority: 10,
    active: true,
    toolOrigin: "arifos.init",
    attributionConfidence: "commonly_attributed",
    scarWeight: 0,
    shadowWeight: 0,
    paradoxWeight: 0,
    contrastPair: "VAULT_Q_002",
    polarity: "order",
  },
  {
    id: "INIT_Q_004",
    text: "The only true wisdom is in knowing you know nothing.",
    author: "Socrates",
    source: "Platonic Dialogues",
    category: "humility",
    surfaces: ["anchor", "sense"],
    tone: "reflective",
    language: "en",
    priority: 10,
    active: true,
    toolOrigin: "arifos.init",
    attributionConfidence: "commonly_attributed",
    scarWeight: 0,
    shadowWeight: 1,
    paradoxWeight: 2,
    contrastPair: "MIND_Q_004",
    polarity: "doubt",
  },
  {
    id: "INIT_Q_003",
    text: "No wind serves him who addresses his voyage to no certain port.",
    author: "Michel de Montaigne",
    source: "Essays",
    category: "discipline",
    surfaces: ["anchor"],
    tone: "firm",
    language: "en",
    priority: 9,
    active: true,
    toolOrigin: "arifos.init",
    attributionConfidence: "verified",
    scarWeight: 0,
    shadowWeight: 0,
    paradoxWeight: 0,
    polarity: "order",
  },
  {
    id: "SENSE_Q_002",
    text: "The first principle is that you must not fool yourself—and you are the easiest person to fool.",
    author: "Richard Feynman",
    source: "Cargo Cult Science",
    category: "truth",
    surfaces: ["sense", "monitor", "mind"],
    tone: "firm",
    language: "en",
    priority: 10,
    active: true,
    toolOrigin: "arifos.sense",
    attributionConfidence: "verified",
    scarWeight: 0,
    shadowWeight: 1,
    paradoxWeight: 1,
    contrastPair: "JUDGE_Q_005",
    polarity: "truth",
  },
  {
    id: "SENSE_Q_001",
    text: "It is wrong always, everywhere, and for anyone, to believe anything upon insufficient evidence.",
    author: "W. K. Clifford",
    source: "The Ethics of Belief",
    category: "truth",
    surfaces: ["sense", "judge"],
    tone: "severe",
    language: "en",
    priority: 9,
    active: true,
    toolOrigin: "arifos.sense",
    attributionConfidence: "verified",
    scarWeight: 0,
    shadowWeight: 1,
    paradoxWeight: 0,
    polarity: "truth",
  },
  {
    id: "SENSE_Q_004",
    text: "No man ever steps in the same river twice.",
    author: "Heraclitus",
    source: "Fragments",
    category: "truth",
    surfaces: ["sense", "vault"],
    tone: "reflective",
    language: "en",
    priority: 8,
    active: true,
    toolOrigin: "arifos.sense",
    attributionConfidence: "commonly_attributed",
    scarWeight: 0,
    shadowWeight: 1,
    paradoxWeight: 2,
    polarity: "chaos",
  },
  {
    id: "MIND_Q_004",
    text: "Doubt is not a pleasant condition, but certainty is absurd.",
    author: "Voltaire",
    source: "Letter to Frederick II",
    category: "humility",
    surfaces: ["mind", "judge", "partial"],
    tone: "reflective",
    language: "en",
    priority: 10,
    active: true,
    toolOrigin: "arifos.mind",
    attributionConfidence: "commonly_attributed",
    scarWeight: 0,
    shadowWeight: 1,
    paradoxWeight: 2,
    contrastPair: "INIT_Q_004",
    polarity: "doubt",
  },
  {
    id: "MIND_Q_005",
    text: "Perfection is achieved, not when there is nothing more to add, but when there is nothing left to take away.",
    author: "Antoine de Saint-Exupéry",
    source: "Wind, Sand and Stars",
    category: "discipline",
    surfaces: ["mind", "forge"],
    tone: "calm",
    language: "en",
    priority: 9,
    active: true,
    toolOrigin: "arifos.mind",
    attributionConfidence: "verified",
    scarWeight: 0,
    shadowWeight: 0,
    paradoxWeight: 1,
    polarity: "order",
  },
  {
    id: "HEART_Q_001",
    text: "First, do no harm.",
    author: "Hippocrates",
    source: "Epidemics",
    category: "restraint",
    surfaces: ["heart", "judge", "hold"],
    tone: "firm",
    language: "en",
    priority: 10,
    active: true,
    toolOrigin: "arifos.heart",
    attributionConfidence: "traditional",
    scarWeight: 0,
    shadowWeight: 1,
    paradoxWeight: 0,
    contrastPair: "PW1",
    polarity: "mercy",
  },
  {
    id: "HEART_Q_002",
    text: "Act in such a way that you treat humanity, whether in your own person or in the person of another, always as an end and never as a means only.",
    author: "Immanuel Kant",
    source: "Groundwork of the Metaphysics of Morals",
    category: "responsibility",
    surfaces: ["heart", "judge"],
    tone: "severe",
    language: "en",
    priority: 9,
    active: true,
    toolOrigin: "arifos.heart",
    attributionConfidence: "verified",
    scarWeight: 0,
    shadowWeight: 1,
    paradoxWeight: 0,
    polarity: "judgment",
  },
  {
    id: "JUDGE_Q_002",
    text: "Power tends to corrupt, and absolute power corrupts absolutely.",
    author: "Lord Acton",
    source: "Letter to Bishop Mandell Creighton",
    category: "restraint",
    surfaces: ["judge", "hold", "void"],
    tone: "severe",
    language: "en",
    priority: 10,
    active: true,
    toolOrigin: "arifos.judge",
    attributionConfidence: "verified",
    scarWeight: 1,
    shadowWeight: 2,
    paradoxWeight: 1,
    contrastPair: "PW1",
    polarity: "power",
  },
  {
    id: "JUDGE_Q_004",
    text: "Injustice anywhere is a threat to justice everywhere.",
    author: "Martin Luther King Jr.",
    source: "Letter from Birmingham Jail",
    category: "judgment",
    surfaces: ["judge"],
    tone: "firm",
    language: "en",
    priority: 9,
    active: true,
    toolOrigin: "arifos.judge",
    attributionConfidence: "verified",
    scarWeight: 1,
    shadowWeight: 1,
    paradoxWeight: 1,
    polarity: "judgment",
  },
  {
    id: "JUDGE_Q_005",
    text: "The sad truth is that most evil is done by people who never make up their minds to be good or evil.",
    author: "Hannah Arendt",
    source: "The Life of the Mind",
    category: "judgment",
    surfaces: ["judge", "hold", "void"],
    tone: "reflective",
    language: "en",
    priority: 9,
    active: true,
    toolOrigin: "arifos.judge",
    attributionConfidence: "verified",
    scarWeight: 2,
    shadowWeight: 2,
    paradoxWeight: 1,
    contrastPair: "SENSE_Q_002",
    polarity: "shadow",
  },
  {
    id: "FORGE_Q_001",
    text: "Perfection is achieved, not when there is nothing more to add, but when there is nothing left to take away.",
    author: "Antoine de Saint-Exupéry",
    source: "Wind, Sand and Stars",
    category: "discipline",
    surfaces: ["forge"],
    tone: "calm",
    language: "en",
    priority: 10,
    active: true,
    toolOrigin: "arifos.forge",
    attributionConfidence: "verified",
    scarWeight: 0,
    shadowWeight: 0,
    paradoxWeight: 1,
    polarity: "order",
  },
  {
    id: "OPS_Q_002",
    text: "An ounce of practice is worth more than tons of preaching.",
    author: "Mahatma Gandhi",
    category: "discipline",
    surfaces: ["forge", "ops"],
    tone: "firm",
    language: "en",
    priority: 9,
    active: true,
    toolOrigin: "arifos.ops",
    attributionConfidence: "commonly_attributed",
    scarWeight: 0,
    shadowWeight: 0,
    paradoxWeight: 0,
    polarity: "order",
  },
  {
    id: "OPS_Q_001",
    text: "Well done is better than well said.",
    author: "Benjamin Franklin",
    source: "Poor Richard's Almanack",
    category: "discipline",
    surfaces: ["forge", "ops"],
    tone: "firm",
    language: "en",
    priority: 8,
    active: true,
    toolOrigin: "arifos.ops",
    attributionConfidence: "verified",
    scarWeight: 0,
    shadowWeight: 0,
    paradoxWeight: 0,
    polarity: "order",
  },
  {
    id: "VAULT_Q_002",
    text: "Those who cannot remember the past are condemned to repeat it.",
    author: "George Santayana",
    source: "The Life of Reason",
    category: "memory",
    surfaces: ["vault"],
    tone: "severe",
    language: "en",
    priority: 10,
    active: true,
    toolOrigin: "arifos.vault",
    attributionConfidence: "verified",
    scarWeight: 1,
    shadowWeight: 1,
    paradoxWeight: 1,
    contrastPair: "INIT_Q_001",
    polarity: "memory",
  },
  {
    id: "VAULT_Q_004",
    text: "The struggle of man against power is the struggle of memory against forgetting.",
    author: "Milan Kundera",
    source: "The Book of Laughter and Forgetting",
    category: "memory",
    surfaces: ["vault", "void"],
    tone: "reflective",
    language: "en",
    priority: 9,
    active: true,
    toolOrigin: "arifos.vault",
    attributionConfidence: "verified",
    scarWeight: 2,
    shadowWeight: 2,
    paradoxWeight: 1,
    polarity: "memory",
  },
  {
    id: "Z01-Q01",
    text: "You have power over your mind—not outside events. Realize this, and you will find strength.",
    author: "Marcus Aurelius",
    source: "Meditations",
    category: "power",
    surfaces: ["monitor", "judge"],
    tone: "calm",
    language: "en",
    priority: 8,
    active: true,
    zoneId: "Z01",
    attributionConfidence: "verified",
    scarWeight: 0,
    shadowWeight: 0,
    paradoxWeight: 0,
    polarity: "power",
  },
  {
    id: "Z03-Q01",
    text: "Everything can be taken from a man but one thing: the last of the human freedoms—to choose one's attitude.",
    author: "Viktor Frankl",
    source: "Man's Search for Meaning",
    category: "wisdom",
    surfaces: ["heart", "hold"],
    tone: "firm",
    language: "en",
    priority: 8,
    active: true,
    zoneId: "Z03",
    attributionConfidence: "verified",
    scarWeight: 1,
    shadowWeight: 1,
    paradoxWeight: 1,
    polarity: "mercy",
  },
  {
    id: "Z05-Q01",
    text: "We are what we repeatedly do. Excellence, then, is not an act, but a habit.",
    author: "Aristotle",
    source: "Nicomachean Ethics",
    category: "discipline",
    surfaces: ["forge", "ops"],
    tone: "calm",
    language: "en",
    priority: 9,
    active: true,
    zoneId: "Z05",
    attributionConfidence: "commonly_attributed",
    scarWeight: 0,
    shadowWeight: 0,
    paradoxWeight: 0,
    polarity: "order",
  },
  {
    id: "Z19-Q01",
    text: "Either mathematics is too big for the human mind, or the human mind is more than a machine.",
    author: "Kurt Gödel",
    category: "paradox",
    surfaces: ["mind", "judge", "partial"],
    tone: "reflective",
    language: "en",
    priority: 7,
    active: true,
    zoneId: "Z19",
    attributionConfidence: "commonly_attributed",
    scarWeight: 0,
    shadowWeight: 1,
    paradoxWeight: 3,
    polarity: "doubt",
  },
];

// ═══════════════════════════════════════════════════════════════════════════════
// LAYER B — Malay Wisdom (Peribahasa / Simpulan Bahasa)
// ═══════════════════════════════════════════════════════════════════════════════

const MALAY_WISDOM: WisdomQuote[] = [
  {
    id: "MS_001",
    text: "Ikut resmi padi, makin berisi makin tunduk.",
    author: "Peribahasa Melayu",
    category: "humility",
    surfaces: ["anchor", "heart", "judge"],
    tone: "calm",
    language: "ms",
    priority: 10,
    active: true,
    attributionConfidence: "traditional",
    scarWeight: 0,
    shadowWeight: 0,
    paradoxWeight: 0,
    polarity: "humility",
  },
  {
    id: "MS_002",
    text: "Biar lambat, asal selamat.",
    author: "Peribahasa Melayu",
    category: "restraint",
    surfaces: ["hold", "judge", "forge"],
    tone: "firm",
    language: "ms",
    priority: 10,
    active: true,
    attributionConfidence: "traditional",
    scarWeight: 0,
    shadowWeight: 1,
    paradoxWeight: 0,
    polarity: "restraint",
  },
  {
    id: "MS_003",
    text: "Sedikit-sedikit, lama-lama jadi bukit.",
    author: "Peribahasa Melayu",
    category: "discipline",
    surfaces: ["anchor", "forge", "ops", "sabar"],
    tone: "calm",
    language: "ms",
    priority: 9,
    active: true,
    attributionConfidence: "traditional",
    scarWeight: 0,
    shadowWeight: 0,
    paradoxWeight: 0,
    polarity: "order",
  },
  {
    id: "MS_004",
    text: "Bagai aur dengan tebing, saling mengisi.",
    author: "Peribahasa Melayu",
    category: "responsibility",
    surfaces: ["heart", "judge"],
    tone: "reflective",
    language: "ms",
    priority: 8,
    active: true,
    attributionConfidence: "traditional",
    scarWeight: 0,
    shadowWeight: 0,
    paradoxWeight: 0,
    polarity: "mercy",
  },
  {
    id: "MS_005",
    text: "Harimau mati meninggalkan belang, manusia mati meninggalkan nama.",
    author: "Peribahasa Melayu",
    category: "memory",
    surfaces: ["vault"],
    tone: "severe",
    language: "ms",
    priority: 8,
    active: true,
    attributionConfidence: "traditional",
    scarWeight: 1,
    shadowWeight: 1,
    paradoxWeight: 0,
    polarity: "memory",
  },
];

// ═══════════════════════════════════════════════════════════════════════════════
// LAYER C — arifOS Forged Canon
// ═══════════════════════════════════════════════════════════════════════════════

const ARIFOS_FORGED_CANON: WisdomQuote[] = [
  {
    id: "SE4",
    text: "DITEMPA, BUKAN DIBERI.",
    author: "arifOS Foundry",
    category: "seal",
    surfaces: ["anchor", "forge", "monitor"],
    tone: "firm",
    language: "ms",
    priority: 11,
    active: true,
    attributionConfidence: "verified",
    scarWeight: 0,
    shadowWeight: 0,
    paradoxWeight: 0,
    polarity: "seal",
  },
  {
    id: "WI3",
    text: "Truth ages well; shortcuts do not.",
    author: "arifOS Foundry",
    category: "truth",
    surfaces: ["sense", "judge", "vault"],
    tone: "calm",
    language: "en",
    priority: 9,
    active: true,
    attributionConfidence: "verified",
    scarWeight: 0,
    shadowWeight: 1,
    paradoxWeight: 0,
    polarity: "truth",
  },
  {
    id: "WI6",
    text: "Humility is an operating constraint, not a mood.",
    author: "arifOS Foundry",
    category: "humility",
    surfaces: ["anchor", "monitor", "mind"],
    tone: "firm",
    language: "en",
    priority: 9,
    active: true,
    attributionConfidence: "verified",
    scarWeight: 0,
    shadowWeight: 0,
    paradoxWeight: 0,
    polarity: "humility",
  },
  {
    id: "WI7",
    text: "If the witness is weak, the claim must wait.",
    author: "arifOS Foundry",
    category: "judgment",
    surfaces: ["judge", "hold", "sense"],
    tone: "severe",
    language: "en",
    priority: 9,
    active: true,
    attributionConfidence: "verified",
    scarWeight: 0,
    shadowWeight: 1,
    paradoxWeight: 1,
    polarity: "restraint",
  },
  {
    id: "WI13",
    text: "What you cannot explain clearly, do not ship proudly.",
    author: "arifOS Foundry",
    category: "discipline",
    surfaces: ["forge", "ops"],
    tone: "firm",
    language: "en",
    priority: 8,
    active: true,
    attributionConfidence: "verified",
    scarWeight: 0,
    shadowWeight: 0,
    paradoxWeight: 0,
    polarity: "order",
  },
  {
    id: "PX8",
    text: "A map is useful because it is not the territory.",
    author: "arifOS Foundry",
    category: "paradox",
    surfaces: ["sense", "mind"],
    tone: "reflective",
    language: "en",
    priority: 8,
    active: true,
    attributionConfidence: "verified",
    scarWeight: 0,
    shadowWeight: 1,
    paradoxWeight: 2,
    polarity: "doubt",
  },
  {
    id: "PX20",
    text: "The limit is part of the design, not the enemy of it.",
    author: "arifOS Foundry",
    category: "discipline",
    surfaces: ["forge", "judge", "void"],
    tone: "calm",
    language: "en",
    priority: 8,
    active: true,
    attributionConfidence: "verified",
    scarWeight: 0,
    shadowWeight: 1,
    paradoxWeight: 1,
    contrastPair: "ARIF_VOID_001",
    polarity: "restraint",
  },
  {
    id: "PW1",
    text: "Power without restraint is noise pretending to be force.",
    author: "arifOS Foundry",
    category: "restraint",
    surfaces: ["judge", "hold", "forge", "void"],
    tone: "severe",
    language: "en",
    priority: 9,
    active: true,
    attributionConfidence: "verified",
    scarWeight: 1,
    shadowWeight: 2,
    paradoxWeight: 1,
    contrastPair: "HEART_Q_001",
    polarity: "restraint",
  },
  {
    id: "PW3",
    text: "Command begins with self-command.",
    author: "arifOS Foundry",
    category: "discipline",
    surfaces: ["forge", "ops", "judge"],
    tone: "firm",
    language: "en",
    priority: 8,
    active: true,
    attributionConfidence: "verified",
    scarWeight: 0,
    shadowWeight: 1,
    paradoxWeight: 0,
    polarity: "order",
  },
  {
    id: "SE1",
    text: "What is forged with witness can survive the night.",
    author: "arifOS Foundry",
    category: "seal",
    surfaces: ["vault", "forge"],
    tone: "reflective",
    language: "en",
    priority: 9,
    active: true,
    attributionConfidence: "verified",
    scarWeight: 0,
    shadowWeight: 1,
    paradoxWeight: 1,
    polarity: "seal",
  },
  {
    id: "LV3",
    text: "Mercy does not erase truth; it carries it gently.",
    author: "arifOS Foundry",
    category: "love",
    surfaces: ["heart", "judge"],
    tone: "calm",
    language: "en",
    priority: 8,
    active: true,
    attributionConfidence: "verified",
    scarWeight: 0,
    shadowWeight: 1,
    paradoxWeight: 1,
    polarity: "mercy",
  },
  {
    id: "LV8",
    text: "The safest room is one where dignity remains intact.",
    author: "arifOS Foundry",
    category: "love",
    surfaces: ["heart", "judge"],
    tone: "firm",
    language: "en",
    priority: 8,
    active: true,
    attributionConfidence: "verified",
    scarWeight: 0,
    shadowWeight: 1,
    paradoxWeight: 0,
    polarity: "mercy",
  },
  // Verdict-specific forged quotes
  {
    id: "ARIF_VOID_001",
    text: "What is forbidden is not a mistake to fix; it is a boundary to honor.",
    author: "arifOS Foundry",
    category: "restraint",
    surfaces: ["void", "judge"],
    tone: "severe",
    language: "en",
    priority: 10,
    active: true,
    attributionConfidence: "verified",
    scarWeight: 2,
    shadowWeight: 3,
    paradoxWeight: 1,
    contrastPair: "PX20",
    polarity: "restraint",
  },
  {
    id: "ARIF_VOID_002",
    text: "Crossing the line once makes the line invisible forever.",
    author: "arifOS Foundry",
    category: "shadow",
    surfaces: ["void", "judge"],
    tone: "severe",
    language: "en",
    priority: 9,
    active: true,
    attributionConfidence: "verified",
    scarWeight: 3,
    shadowWeight: 3,
    paradoxWeight: 2,
    polarity: "shadow",
  },
  {
    id: "ARIF_PARTIAL_001",
    text: "Incomplete is not the same as broken. Some truths need more turns.",
    author: "arifOS Foundry",
    category: "paradox",
    surfaces: ["partial", "judge"],
    tone: "reflective",
    language: "en",
    priority: 10,
    active: true,
    attributionConfidence: "verified",
    scarWeight: 1,
    shadowWeight: 1,
    paradoxWeight: 2,
    contrastPair: "MIND_Q_004",
    polarity: "doubt",
  },
  {
    id: "ARIF_PARTIAL_002",
    text: "Sabar — the floor strains but does not break. Adjust, then proceed.",
    author: "arifOS Foundry",
    category: "discipline",
    surfaces: ["partial", "sabar", "judge"],
    tone: "calm",
    language: "en",
    priority: 9,
    active: true,
    attributionConfidence: "verified",
    scarWeight: 1,
    shadowWeight: 0,
    paradoxWeight: 1,
    polarity: "order",
  },
  {
    id: "ARIF_HOLD_001",
    text: "Restraint is the first act of sovereignty.",
    author: "arifOS Foundry",
    category: "restraint",
    surfaces: ["hold", "judge"],
    tone: "firm",
    language: "en",
    priority: 10,
    active: true,
    attributionConfidence: "verified",
    scarWeight: 0,
    shadowWeight: 2,
    paradoxWeight: 1,
    polarity: "restraint",
  },
  {
    id: "ARIF_SABAR_001",
    text: "Stop, acknowledge, breathe, adjust, resume. The floor protects.",
    author: "arifOS Foundry",
    category: "discipline",
    surfaces: ["sabar", "anchor", "hold"],
    tone: "calm",
    language: "en",
    priority: 10,
    active: true,
    attributionConfidence: "verified",
    scarWeight: 0,
    shadowWeight: 0,
    paradoxWeight: 0,
    polarity: "mercy",
  },
];

// ═══════════════════════════════════════════════════════════════════════════════
// UNIFIED REGISTRY
// ═══════════════════════════════════════════════════════════════════════════════

export const WISDOM_REGISTRY: WisdomQuote[] = [
  ...CIVILIZATIONAL_CANON,
  ...MALAY_WISDOM,
  ...ARIFOS_FORGED_CANON,
];

const DEFAULT_QUOTE: WisdomQuote = {
  id: "DEFAULT",
  text: "DITEMPA BUKAN DIBERI — Forged, not given.",
  author: "arifOS",
  category: "seal",
  surfaces: ["empty"],
  tone: "firm",
  language: "ms",
  priority: 0,
  active: true,
  attributionConfidence: "verified",
  scarWeight: 0,
  shadowWeight: 0,
  paradoxWeight: 0,
  polarity: "seal",
};

function scoreCandidate(
  q: WisdomQuote,
  tone?: WisdomTone,
  language?: "en" | "ms" | "mixed",
  shadowProfile?: string
): number {
  let score = q.priority;
  if (tone && q.tone === tone) score += 5;
  if (language && language !== "mixed" && q.language === language) score += 3;
  if (shadowProfile) {
    const map: Record<string, keyof WisdomQuote> = {
      scar: "scarWeight",
      shadow: "shadowWeight",
      paradox: "paradoxWeight",
      restraint: "shadowWeight",
      humility: "shadowWeight",
      doubt: "paradoxWeight",
    };
    const key = map[shadowProfile];
    if (key) {
      score += (q[key] as number) * 2;
    }
  }
  return score;
}

export function pickQuote(
  surface: WisdomSurface,
  tone?: WisdomTone,
  opts?: {
    language?: "en" | "ms" | "mixed";
    shadowProfile?: string;
  }
): WisdomQuote {
  const candidates = WISDOM_REGISTRY.filter((q) => q.active && q.surfaces.includes(surface));

  for (const relax of [
    { lang: false, tone: false, shadow: false },
    { lang: true, tone: false, shadow: false },
    { lang: true, tone: true, shadow: false },
    { lang: true, tone: true, shadow: true },
  ]) {
    const _lang = relax.lang ? undefined : opts?.language;
    const _tone = relax.tone ? undefined : tone;
    const _shadow = relax.shadow ? undefined : opts?.shadowProfile;
    const scored = candidates
      .map((q) => ({ q, score: scoreCandidate(q, _tone, _lang, _shadow) }))
      .sort((a, b) => b.score - a.score);
    if (scored.length) return scored[0].q;
  }

  return DEFAULT_QUOTE;
}

export function pickRandomQuote(surface: WisdomSurface): WisdomQuote | null {
  const candidates = WISDOM_REGISTRY.filter((q) => q.active && q.surfaces.includes(surface));
  if (candidates.length === 0) return null;
  return candidates[Math.floor(Math.random() * candidates.length)];
}

export function quotesForSurface(surface: WisdomSurface): WisdomQuote[] {
  return WISDOM_REGISTRY.filter((q) => q.active && q.surfaces.includes(surface)).sort(
    (a, b) => b.priority - a.priority
  );
}

export function registryStats() {
  const total = WISDOM_REGISTRY.length;
  const byCategory = WISDOM_REGISTRY.reduce((acc, q) => {
    acc[q.category] = (acc[q.category] || 0) + 1;
    return acc;
  }, {} as Record<WisdomCategory, number>);
  const bySurface = WISDOM_REGISTRY.reduce((acc, q) => {
    q.surfaces.forEach((s) => {
      acc[s] = (acc[s] || 0) + 1;
    });
    return acc;
  }, {} as Record<WisdomSurface, number>);
  return { total, byCategory, bySurface };
}
