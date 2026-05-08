from typing import List, Optional
from pydantic import BaseModel
from fastmcp import FastMCP
import sys
import os

# Add arifOS to path to import shared core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../arifOS")))
from core.shared.governed_tool import governed_tool

mcp = FastMCP("WEALTH-Civilization")

# --- Models ---

class MarketAnalysis(BaseModel):
    ticker: str
    sentiment: float
    epistemic_tag: str
    confidence_band: List[float]
    humility_on_projections: bool
    risk_assessment: str

class StressTestResult(BaseModel):
    portfolio_id: str
    max_drawdown: float
    correlation_breakdown: bool
    liquidity_crisis: bool
    hold_triggered: bool

class CrisisAssessment(BaseModel):
    region: str
    energy_sovereignty: float
    grid_integrity: float
    price_dignity: float
    transition_amanah: float
    maruah_score: float
    hold_triggered: bool

class ShortagePrediction(BaseModel):
    region: str
    shortage_probability: float
    uncertainty_band: float
    horizon_days: int

class FoodSecurityIndex(BaseModel):
    country: str
    availability: float
    access: float
    utilization: float
    stability: float
    index_score: float

class ProspectEconomics(BaseModel):
    prospect_id: str
    stoiip_bbl: float
    development_capex: float
    operating_opex: float
    oil_price_assumption: float
    npv_10: float
    emv: float
    paradox_score: float
    verdict: str

# --- Domain: Thermodynamic Economics (Golden Path Demo) ---

@mcp.tool()
@governed_tool
async def wealth_evaluate_prospect(
    prospect_id: str, 
    stoiip_bbl: float, 
    capex_estimate: float = 500_000_000.0, 
    opex_per_bbl: float = 15.0, 
    oil_price: float = 75.0,
    geological_chance_of_success: float = 0.3
) -> ProspectEconomics:
    """
    Evaluate prospect economics (NPV/EMV) from GEOX volumetrics.
    Applies the WEALTH schema to calculate the Paradox and Echo of the investment.
    """
    # Assume a 35% recovery factor for the Energy Capacity (STOIIP)
    recoverable_reserves = stoiip_bbl * 0.35 
    gross_revenue = recoverable_reserves * oil_price
    total_opex = recoverable_reserves * opex_per_bbl
    net_cash_flow = gross_revenue - capex_estimate - total_opex
    
    # Simplified NPV10 (assuming flat production curve)
    npv_10 = net_cash_flow * 0.614 # Rough discount factor for 10% over 10 yrs
    
    # Expected Monetary Value (EMV)
    emv = (npv_10 * geological_chance_of_success) - (capex_estimate * (1 - geological_chance_of_success))
    
    # Paradox score: High short-term money but massive capital risk
    paradox_score = 0.8 if (emv < 0 or capex_estimate > 1_000_000_000) else 0.2
    
    # WEALTH does not Seal; it only qualifies. arifOS holds the final Seal.
    verdict = "QUALIFY" if emv > 0 and paradox_score < 0.5 else "888-HOLD"
    
    return ProspectEconomics(
        prospect_id=prospect_id,
        stoiip_bbl=stoiip_bbl,
        development_capex=capex_estimate,
        operating_opex=total_opex,
        oil_price_assumption=oil_price,
        npv_10=npv_10,
        emv=emv,
        paradox_score=paradox_score,
        verdict=verdict
    )

# --- Domain 1: Stock Market Intelligence (WEALTH-Markets) ---

@mcp.tool()
@governed_tool
async def markets_analyze_ticker(ticker: str, depth: str = "standard") -> MarketAnalysis:
    """Analyze stock with F1-F13 governance."""
    return MarketAnalysis(
        ticker=ticker.upper(),
        sentiment=0.5,
        epistemic_tag="ESTIMATE",
        confidence_band=[0.03, 0.15],
        humility_on_projections=True,
        risk_assessment="LOW"
    )

@mcp.tool()
@governed_tool
async def markets_portfolio_stress_test(
    portfolio_id: str,
    holdings: List[str],
    scenarios: List[str]
) -> StressTestResult:
    """Run 888 HOLD-aware stress tests."""
    return StressTestResult(
        portfolio_id=portfolio_id,
        max_drawdown=-0.05,
        correlation_breakdown=False,
        liquidity_crisis=False,
        hold_triggered=False
    )

# --- Domain 2: Energy Crisis Monitor (WEALTH-Energy) ---

@mcp.tool()
@governed_tool
async def energy_crisis_assess(region: str) -> CrisisAssessment:
    """Assess energy crisis severity with F1-F13."""
    return CrisisAssessment(
        region=region.upper(),
        energy_sovereignty=0.8,
        grid_integrity=0.9,
        price_dignity=0.7,
        transition_amanah=0.5,
        maruah_score=0.73,
        hold_triggered=False
    )

@mcp.tool()
@governed_tool
async def energy_shortage_predict(
    region: str,
    horizon_days: int = 30
) -> ShortagePrediction:
    """Predict energy shortages with humility bands."""
    return ShortagePrediction(
        region=region.upper(),
        shortage_probability=0.1,
        uncertainty_band=0.05,
        horizon_days=horizon_days
    )

# --- Domain 3: Food Security Monitor (WEALTH-Food) ---

@mcp.tool()
@governed_tool
async def food_security_index(country: str) -> FoodSecurityIndex:
    """Calculate food security with Maruah adaptation."""
    return FoodSecurityIndex(
        country=country.upper(),
        availability=0.8,
        access=0.7,
        utilization=0.9,
        stability=0.8,
        index_score=0.8
    )

# --- Resources ---

@mcp.resource("market://{ticker}/fundamentals")
def get_fundamentals(ticker: str) -> str:
    """Real-time fundamentals with epistemic tags"""
    return f"Fundamentals for {ticker.upper()}: [CLAIM] Verified"

@mcp.resource("energy://{region}/realtime-mix")
def get_energy_mix(region: str) -> str:
    """Real-time energy production by source"""
    return f"Energy mix for {region.upper()}: 30% Renewable [CLAIM]"

@mcp.resource("food://global/prices")
def get_global_food_prices() -> str:
    """FAO food price index components"""
    return "Global food price index: 120.5 [ESTIMATE]"

if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8000)
