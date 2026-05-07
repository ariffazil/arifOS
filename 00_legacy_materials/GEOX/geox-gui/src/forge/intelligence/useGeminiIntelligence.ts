/**
 * useGeminiIntelligence — Earth Intelligence LLM Bridge
 * ═══════════════════════════════════════════════════════════════════════════════
 * DITEMPA BUKAN DIBERI
 *
 * Gemini API integration for geological interpretations and decision verdicts.
 * Implements exponential backoff, constitutional validation, and structured output.
 */

import { useState, useCallback, useRef } from 'react';

/**
 * Configuration for Gemini API
 */
export interface GeminiConfig {
  apiKey: string;
  model: 'gemini-2.5-flash-preview-09-2025' | 'gemini-2.5-pro' | 'gemini-1.5-pro';
  baseUrl: string;
  maxRetries: number;
  timeout: number;
  temperature: number;
  maxTokens: number;
}

/**
 * System instruction templates for different geological contexts
 */
export type GeologicalContext =
  | 'interpretation'
  | 'risk_assessment'
  | 'analog_matching'
  | 'chronostratigraphy'
  | 'petrophysics'
  | 'structural'
  | 'general';

/**
 * Request payload for Gemini
 */
interface GeminiRequest {
  contents: Array<{
    parts: Array<{ text: string }>;
    role?: 'user' | 'model';
  }>;
  systemInstruction?: {
    parts: Array<{ text: string }>;
  };
  generationConfig?: {
    temperature?: number;
    maxOutputTokens?: number;
    topP?: number;
    topK?: number;
    responseMimeType?: string;
  };
}

/**
 * Response from Gemini
 */
interface GeminiResponse {
  candidates: Array<{
    content: {
      parts: Array<{ text: string }>;
      role: string;
    };
    finishReason: string;
    index: number;
    safetyRatings: Array<{
      category: string;
      probability: string;
    }>;
  }>;
  usageMetadata?: {
    promptTokenCount: number;
    candidatesTokenCount: number;
    totalTokenCount: number;
  };
}

/**
 * Structured geological interpretation result
 */
export interface GeologicalInterpretation {
  interpretation: string;
  confidence: number; // 0-1
  uncertaintyFactors: string[];
  recommendedActions: string[];
  constitutionalVerdict: {
    f2Evidence: 'grounded' | 'partial' | 'speculative';
    f7Humility: number; // 0-1
    f9AntiHantu: boolean;
  };
  analogReferences?: Array<{
    basin: string;
    formation: string;
    similarity: number;
  }>;
  stratigraphicContext?: {
    estimatedAge?: number; // Ma
    period?: string;
    confidence: number;
  };
}

/**
 * Hook return type
 */
export interface UseGeminiIntelligenceReturn {
  generate: (prompt: string, context?: GeologicalContext) => Promise<GeologicalInterpretation>;
  generateStream: (prompt: string, context?: GeologicalContext, onChunk?: (chunk: string) => void) => Promise<void>;
  isLoading: boolean;
  error: string | null;
  lastResponse: GeologicalInterpretation | null;
  tokenUsage: { input: number; output: number; total: number } | null;
  cancel: () => void;
}

/**
 * System instructions for different contexts
 */
const SYSTEM_INSTRUCTIONS: Record<GeologicalContext, string> = {
  interpretation: `You are an elite geological AI assistant for GEOX Earth Intelligence Core.
Your task is to interpret geological data with extreme rigor and uncertainty quantification.

Rules:
1. Always state confidence levels (0-100%) for every interpretation
2. List explicit uncertainty factors
3. Ground all claims in physical principles
4. Never claim certainty where data is ambiguous
5. Reference geological analogs when appropriate
6. Acknowledge limitations of the dataset

Output format: JSON with fields: interpretation, confidence, uncertaintyFactors[], recommendedActions[], constitutionalVerdict{}`,

  risk_assessment: `You are a petroleum risk assessment AI for GEOX AC_Risk Console.
Analyze geological risk factors with brutal honesty and quantitative rigor.

Rules:
1. Calculate GCOS components (Charge, Trap, Reservoir, Seal)
2. Provide P10/P50/P90 ranges for all estimates
3. Identify key risk drivers
4. Recommend data acquisition to reduce uncertainty
5. Flag any assumptions explicitly

Output format: JSON with risk breakdown, confidence intervals, and mitigation strategies.`,

  analog_matching: `You are an analog matching specialist for GEOX Analog Forge.
Compare current geological scenarios to global analogs with similarity scoring.

Rules:
1. Match on tectonic setting, depositional environment, burial history
2. Provide similarity scores (0-100%) for each analog
3. Highlight key differences that affect prediction validity
4. Rank analogs by relevance

Output format: JSON with ranked analog list and similarity metrics.`,

  chronostratigraphy: `You are a chronostratigraphic AI integrated with Macrostrat.
Estimate geological ages and correlate stratigraphy.

Rules:
1. Use Macrostrat API data when available
2. Provide age ranges with uncertainty
3. Reference International Chronostratigraphic Chart
4. Flag diachronous units

Output format: JSON with age estimates, period/epoch/stage, and confidence levels.`,

  petrophysics: `You are a petrophysical interpretation AI for GEOX Well Context Desk.
Analyze log data for lithology, porosity, and fluid content.

Rules:
1. State calibration assumptions
2. Provide multiple interpretation scenarios
3. Identify data quality issues
4. Recommend additional logging if needed

Output format: JSON with lithology breakdown, petrophysical parameters, and QC flags.`,

  structural: `You are a structural geology AI for GEOX Basin Explorer.
Interpret fault patterns, stress regimes, and trap geometry.

Rules:
1. Distinguish observation from interpretation
2. Provide alternative structural models
3. Assess seal risk from fault geometry
4. Estimate structural uncertainty

Output format: JSON with structural model, alternatives, and risk assessment.`,

  general: `You are GEOX Earth Intelligence, a geological AI assistant.
Provide helpful, accurate geological information with appropriate caveats.

Rules:
1. Be concise but thorough
2. Cite principles, not just conclusions
3. Acknowledge uncertainty
4. Stay within geological domain expertise`,
};

/**
 * Default configuration
 */
const DEFAULT_CONFIG: GeminiConfig = {
  apiKey: '', // Should be provided by environment or props
  model: 'gemini-2.5-flash-preview-09-2025',
  baseUrl: 'https://generativelanguage.googleapis.com/v1beta',
  maxRetries: 3,
  timeout: 60000,
  temperature: 0.1,
  maxTokens: 4096,
};

/**
 * Exponential backoff delay
 */
const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

/**
 * Main hook for Gemini Intelligence
 */
export function useGeminiIntelligence(
  config: Partial<GeminiConfig> = {}
): UseGeminiIntelligenceReturn {
  const fullConfig = { ...DEFAULT_CONFIG, ...config };

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastResponse, setLastResponse] = useState<GeologicalInterpretation | null>(null);
  const [tokenUsage, setTokenUsage] = useState<{ input: number; output: number; total: number } | null>(null);

  const abortControllerRef = useRef<AbortController | null>(null);

  /**
   * Cancel ongoing request
   */
  const cancel = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
  }, []);

  /**
   * Parse Gemini response to structured interpretation
   */
  const parseResponse = (text: string): GeologicalInterpretation => {
    try {
      // Try to parse as JSON
      const json = JSON.parse(text);
      return {
        interpretation: json.interpretation || json.response || text,
        confidence: json.confidence ?? 0.7,
        uncertaintyFactors: json.uncertaintyFactors || json.uncertainty_factors || [],
        recommendedActions: json.recommendedActions || json.recommended_actions || [],
        constitutionalVerdict: {
          f2Evidence: json.constitutionalVerdict?.f2Evidence || 'grounded',
          f7Humility: json.constitutionalVerdict?.f7Humility ?? 0.7,
          f9AntiHantu: json.constitutionalVerdict?.f9AntiHantu ?? true,
        },
        analogReferences: json.analogReferences,
        stratigraphicContext: json.stratigraphicContext,
      };
    } catch {
      // Fallback: treat as plain text
      return {
        interpretation: text,
        confidence: 0.5,
        uncertaintyFactors: ['Response parsing failed - manual review required'],
        recommendedActions: ['Verify interpretation against primary data'],
        constitutionalVerdict: {
          f2Evidence: 'partial',
          f7Humility: 0.5,
          f9AntiHantu: true,
        },
      };
    }
  };

  /**
   * Generate interpretation with retries
   */
  const generate = useCallback(
    async (prompt: string, context: GeologicalContext = 'general'): Promise<GeologicalInterpretation> => {
      setIsLoading(true);
      setError(null);

      const systemInstruction = SYSTEM_INSTRUCTIONS[context];

      const request: GeminiRequest = {
        contents: [{ parts: [{ text: prompt }] }],
        systemInstruction: { parts: [{ text: systemInstruction }] },
        generationConfig: {
          temperature: fullConfig.temperature,
          maxOutputTokens: fullConfig.maxTokens,
          topP: 0.95,
          topK: 40,
          responseMimeType: 'application/json',
        },
      };

      let lastError: Error | null = null;

      for (let attempt = 0; attempt < fullConfig.maxRetries; attempt++) {
        try {
          abortControllerRef.current = new AbortController();
          const timeoutId = setTimeout(() => abortControllerRef.current?.abort(), fullConfig.timeout);

          const response = await fetch(
            `${fullConfig.baseUrl}/models/${fullConfig.model}:generateContent?key=${fullConfig.apiKey}`,
            {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(request),
              signal: abortControllerRef.current.signal,
            }
          );

          clearTimeout(timeoutId);

          if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error?.message || `HTTP ${response.status}`);
          }

          const data: GeminiResponse = await response.json();

          if (data.candidates.length === 0) {
            throw new Error('No candidates in response');
          }

          const text = data.candidates[0].content.parts[0].text;
          const interpretation = parseResponse(text);

          setLastResponse(interpretation);
          setTokenUsage(data.usageMetadata ? {
            input: data.usageMetadata.promptTokenCount,
            output: data.usageMetadata.candidatesTokenCount,
            total: data.usageMetadata.totalTokenCount,
          } : null);

          return interpretation;

        } catch (err) {
          lastError = err as Error;

          // Don't retry on abort
          if (err instanceof DOMException && err.name === 'AbortError') {
            throw err;
          }

          // Exponential backoff
          if (attempt < fullConfig.maxRetries - 1) {
            const backoffMs = Math.min(1000 * Math.pow(2, attempt), 8000);
            await delay(backoffMs);
          }
        }
      }

      const errorMessage = lastError?.message || 'Unknown error';
      setError(errorMessage);
      throw new Error(`Gemini request failed after ${fullConfig.maxRetries} attempts: ${errorMessage}`);

    }, [fullConfig]
  );

  /**
   * Generate streaming response
   */
  const generateStream = useCallback(
    async (
      prompt: string,
      context: GeologicalContext = 'general',
      onChunk?: (chunk: string) => void
    ): Promise<void> => {
      setIsLoading(true);
      setError(null);

      const systemInstruction = SYSTEM_INSTRUCTIONS[context];

      const request: GeminiRequest = {
        contents: [{ parts: [{ text: prompt }] }],
        systemInstruction: { parts: [{ text: systemInstruction }] },
        generationConfig: {
          temperature: fullConfig.temperature,
          maxOutputTokens: fullConfig.maxTokens,
        },
      };

      try {
        abortControllerRef.current = new AbortController();

        const response = await fetch(
          `${fullConfig.baseUrl}/models/${fullConfig.model}:streamGenerateContent?alt=sse&key=${fullConfig.apiKey}`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(request),
            signal: abortControllerRef.current.signal,
          }
        );

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const reader = response.body?.getReader();
        if (!reader) throw new Error('No response body');

        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const json = line.slice(6);
              if (json === '[DONE]') continue;

              try {
                const data = JSON.parse(json);
                const chunk = data.candidates?.[0]?.content?.parts?.[0]?.text;
                if (chunk && onChunk) {
                  onChunk(chunk);
                }
              } catch {
                // Skip malformed chunks
              }
            }
          }
        }

      } catch (err) {
        const errorMessage = (err as Error).message;
        setError(errorMessage);
        throw err;
      } finally {
        setIsLoading(false);
      }
    }, [fullConfig]
  );

  return {
    generate,
    generateStream,
    isLoading,
    error,
    lastResponse,
    tokenUsage,
    cancel,
  };
}

/**
 * Convenience hook for quick interpretations
 */
export function useQuickInterpretation() {
  const { generate, isLoading } = useGeminiIntelligence();

  const interpretLog = useCallback(
    async (curveData: string, depthRange: string) => {
      const prompt = `Interpret this well log data:\nCurve: ${curveData}\nDepth Range: ${depthRange}\n\nProvide lithology interpretation with confidence.`;
      return generate(prompt, 'petrophysics');
    }, [generate]
  );

  const assessRisk = useCallback(
    async (prospectData: string) => {
      const prompt = `Assess geological risk for this prospect:\n${prospectData}\n\nProvide GCOS breakdown and key risk drivers.`;
      return generate(prompt, 'risk_assessment');
    }, [generate]
  );

  const correlateStratigraphy = useCallback(
    async (formationData: string, location: string) => {
      const prompt = `Correlate stratigraphy for this formation:\n${formationData}\nLocation: ${location}\n\nProvide age estimates and regional correlation.`;
      return generate(prompt, 'chronostratigraphy');
    }, [generate]
  );

  return {
    interpretLog,
    assessRisk,
    correlateStratigraphy,
    isLoading,
  };
}

export default useGeminiIntelligence;
