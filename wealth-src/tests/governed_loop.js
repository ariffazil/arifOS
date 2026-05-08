import { computeCashflow } from "../host/wealth/cashflow.js";
import { computeMaruahScore } from "../host/wealth/maruah-score.js";
import { calculateRiskAdjustedRate } from "../host/kernel/capitalx.js";

async function runLoop() {
  console.log("--- 1. 777_MEMORY Recall (Simulated) ---");
  const memoryRecalled = {
    income: 7000,
    expenses: 5000,
    defaults: 0,
    years_operating: 3,
    locality: "Seri Kembangan",
    leverage: "low"
  };
  console.log("Recalled Context:", memoryRecalled);

  console.log("\n--- 2. WEALTH Cashflow ---");
  const income = [{ monthly_amount: 7000, active: true }];
  const expenses = [{ monthly_amount: 5000, active: true }];
  const cashflow = computeCashflow(income, expenses);
  console.log("Cashflow Result:", JSON.stringify(cashflow, null, 2));

  console.log("\n--- 3. WEALTH Maruah ---");
  const maruahInput = {
    financial_integrity: 0.9,
    sovereignty: 0.8,
    debt_dignity: 0.9,
    amanah_index: 0.85,
    community_contribution: 0.3
  };
  const maruah = computeMaruahScore(maruahInput);
  console.log("Maruah Result:", JSON.stringify(maruah, null, 2));

  console.log("\n--- 4. CapitalX Score (r_adj) ---");
  const signals = {
    base_rate: 0.05,
    dS: -0.01,
    peace2: 1.1,
    maruahScore: maruah.maruah_score,
    trustIndex: 0.75,
    deltaCiv: 0.02
  };
  const capitalx = calculateRiskAdjustedRate(signals.base_rate, signals);
  console.log("CapitalX Result:", JSON.stringify(capitalx, null, 2));

  console.log("\n--- 5. 888_JUDGE + 999_SEAL (Simulated) ---");
  const finalDecision = {
    actor_id: "borrower_profile_001",
    decision: "APPROVE",
    r_adj: capitalx.r_adj,
    maruah_band: maruah.maruah_band,
    witness: { human: true, ai: true, earth: true },
    vault_seal: "VAULT999",
    epoch: new Date().toISOString()
  };
  console.log("FINAL SEALED DECISION:", JSON.stringify(finalDecision, null, 2));
}

runLoop().catch(console.error);
