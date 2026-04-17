/**
 * EpistemicTag — Classification of assertion certainty
 * DITEMPA BUKAN DIBERI
 */

export enum EpistemicTag {
  CLAIM = "CLAIM",       // Definitive, high confidence, direct evidence
  PLAUSIBLE = "PLAUSIBLE", // Consistent but not uniquely validated
  HYPOTHESIS = "HYPOTHESIS", // Exploratory model for testing
  ESTIMATE = "ESTIMATE", // Derived from proxy data
  UNKNOWN = "UNKNOWN",   // Explicit acknowledgment of gap
}

export function isValidEpistemicTag(tag: string): tag is EpistemicTag {
  return Object.values(EpistemicTag).includes(tag as EpistemicTag);
}

/**
 * Tag upgrade is an F2 violation — downgrades are allowed.
 * CLAIM → ESTIMATE is fine. ESTIMATE → CLAIM is a violation.
 */
export function canUpgradeTag(from: EpistemicTag, to: EpistemicTag): boolean {
  const hierarchy: Record<EpistemicTag, number> = {
    [EpistemicTag.UNKNOWN]: 0,
    [EpistemicTag.ESTIMATE]: 1,
    [EpistemicTag.HYPOTHESIS]: 2,
    [EpistemicTag.PLAUSIBLE]: 3,
    [EpistemicTag.CLAIM]: 4,
  };
  return hierarchy[to] >= hierarchy[from];
}