/**
 * Mock company claims data
 *
 * Provides placeholder ESG claims for the comparison board until the
 * backend returns real grounded comparisons.
 */

const DEFAULT_CLAIMS = [
  {
    id: "claim-recycling",
    focus: "Recycling",
    claim: "We aim for 100% recycled or sustainably sourced materials by 2030.",
    note: "85% of materials met this standard in 2023 according to company reports.",
    stance: "supports",
  },
  {
    id: "claim-emissions",
    focus: "Emissions",
    claim: "We will achieve net zero greenhouse gas emissions by 2040.",
    note: "Critics say the pace of absolute emissions reduction is too slow given continued growth.",
    stance: "questions",
  },
  {
    id: "claim-greenwashing",
    focus: "Greenwashing",
    claim: "Our sustainability communications are transparent and accurate.",
    note: "The company has faced lawsuits alleging misleading sustainability marketing.",
    stance: "contradicts",
  },
  {
    id: "claim-supply-chain",
    focus: "Supply chain",
    claim: "We are improving working conditions across our supply chain.",
    note: "External audits show progress but significant gaps remain in some regions.",
    stance: "questions",
  },
];

export function getMockClaims(_company) {
  return DEFAULT_CLAIMS;
}
