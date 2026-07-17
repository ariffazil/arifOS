#!/bin/bash
# arifOS Guard — Capital Approval
echo "🔱 arifOS Guard — Capital Approval Protection"
echo ""
echo "Action: transfer(amount=500000, currency=USD, to=external)"
echo "Identity: finance-agent (exceeds delegated limit)"
echo ""
echo "→ arif_judge(capital_transfer, identity=finance-agent)"
echo "VERDICT: HOLD"
echo "REASON:  Transfer exceeds delegated authority ($50K limit). Requires dual approval."
echo "FLOOR:   F1 AMANAH + F13 SOVEREIGN"
echo ""
echo "MUTATION PERFORMED: false"
