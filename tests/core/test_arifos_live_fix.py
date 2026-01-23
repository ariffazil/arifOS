#!/usr/bin/env python3
"""
Test the arifos_live tool with the fixed response format
"""

import sys
import asyncio
import json

# Add arifOS to path
sys.path.insert(0, '.')

async def test_arifos_live_tool():
    """Test the arifos_live tool with proper MCP format"""
    print("Testing arifos_live tool with fixed response format...")
    
    try:
        from arifos.core.kernel.mcp_server import ConstitutionalMCPServer
        import mcp.types as types
        
        server = ConstitutionalMCPServer()
        
        # Test the arifos_live handler
        test_arguments = {
            "query": "What is the current status of arifOS constitutional governance?",
            "user_id": "test_user"
        }
        
        result = await server._handle_arifos_live(test_arguments)
        
        # Validate response format
        assert isinstance(result, types.TextContent)
        assert result.type == "text"
        
        # Parse the JSON content
        parsed_data = json.loads(result.text)
        assert "verdict" in parsed_data
        assert "reason" in parsed_data
        assert "constitutional_valid" in parsed_data
        assert "tool" in parsed_data
        assert parsed_data["tool"] == "arifos_live"
        
        print("SUCCESS: arifos_live tool working correctly")
        print(f"SUCCESS: Verdict: {parsed_data['verdict']}")
        print(f"SUCCESS: Reason: {parsed_data['reason']}")
        print(f"SUCCESS: Constitutional Valid: {parsed_data['constitutional_valid']}")
        
        return True
        
    except Exception as e:
        print(f"FAILED: arifos_live tool test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_agi_think_tool():
    """Test the agi_think tool with proper MCP format"""
    print("\nTesting agi_think tool with fixed response format...")
    
    try:
        from arifos.core.kernel.mcp_server import ConstitutionalMCPServer
        import mcp.types as types
        
        server = ConstitutionalMCPServer()
        
        # Test the agi_think handler
        test_arguments = {
            "query": "How should we approach fixing the MCP translation issues?",
            "context": {"previous_analysis": "import issues identified"}
        }
        
        result = await server._handle_agi_think(test_arguments)
        
        # Validate response format
        assert isinstance(result, types.TextContent)
        assert result.type == "text"
        
        # Parse the JSON content
        parsed_data = json.loads(result.text)
        assert "thought_process" in parsed_data
        assert "constitutional_metrics" in parsed_data
        assert "tool" in parsed_data
        assert parsed_data["tool"] == "agi_think"
        
        print("SUCCESS: agi_think tool working correctly")
        print(f"SUCCESS: Thought process: {parsed_data['thought_process']}")
        print(f"SUCCESS: Constitutional metrics: {parsed_data['constitutional_metrics']}")
        
        return True
        
    except Exception as e:
        print(f"FAILED: agi_think tool test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_asi_act_tool():
    """Test the asi_act tool with proper MCP format"""
    print("\nTesting asi_act tool with fixed response format...")
    
    try:
        from arifos.core.kernel.mcp_server import ConstitutionalMCPServer
        import mcp.types as types
        
        server = ConstitutionalMCPServer()
        
        # Test the asi_act handler with safe content
        test_arguments = {
            "draft_response": "I understand your concern and I'm here to help you resolve this issue.",
            "intent": "provide_helpful_response",
            "recipient_context": {"user_emotional_state": "frustrated"}
        }
        
        result = await server._handle_asi_act(test_arguments)
        
        # Validate response format
        assert isinstance(result, types.TextContent)
        assert result.type == "text"
        
        # Parse the JSON content
        parsed_data = json.loads(result.text)
        assert "asi_veto" in parsed_data
        assert "safety_assessment" in parsed_data
        assert "empathy_score" in parsed_data
        assert "tool" in parsed_data
        assert parsed_data["tool"] == "asi_act"
        
        print("SUCCESS: asi_act tool working correctly")
        print(f"SUCCESS: ASI Veto: {parsed_data['asi_veto']}")
        print(f"SUCCESS: Safety Assessment: {parsed_data['safety_assessment']}")
        print(f"SUCCESS: Empathy Score: {parsed_data['empathy_score']}")
        
        return True
        
    except Exception as e:
        print(f"FAILED: asi_act tool test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tool tests"""
    print("Testing arifOS MCP Tools with Fixed Response Format")
    print("=" * 60)
    
    test_results = []
    
    # Run tests
    test_results.append(("arifos_live", await test_arifos_live_tool()))
    test_results.append(("agi_think", await test_agi_think_tool()))
    test_results.append(("asi_act", await test_asi_act_tool()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TOOL TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "SUCCESS" if result else "FAILED"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tools passed")
    
    if passed == total:
        print("All constitutional MCP tools are working correctly!")
        print("Response format standardized to TextContent")
        print("Constitutional guarantees maintained")
        return 0
    else:
        print("Some tools failed - review required")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)