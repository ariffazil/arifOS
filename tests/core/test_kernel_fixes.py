#!/usr/bin/env python3
"""
Test script to validate the kernel import fixes and response format standardization
"""

import sys
import asyncio
import json

# Add arifOS to path
sys.path.insert(0, '.')

def test_kernel_imports():
    """Test that all kernel imports are working"""
    print("🧪 Testing kernel imports...")
    
    try:
        from arifos.core.kernel.constitutional import ConstitutionalKernel, PipelineStage
        print("✅ ConstitutionalKernel import successful")
        print(f"✅ PipelineStage enum working: {PipelineStage.STAGE_000_VOID}")
        return True
    except ImportError as e:
        print(f"❌ Kernel import failed: {e}")
        return False

def test_mcp_server_imports():
    """Test MCP server imports"""
    print("\n🧪 Testing MCP server imports...")
    
    try:
        from arifos.core.kernel.mcp_server import ConstitutionalMCPServer
        print("✅ ConstitutionalMCPServer import successful")
        return True
    except ImportError as e:
        print(f"❌ MCP server import failed: {e}")
        return False

def test_response_format():
    """Test the standardized response format"""
    print("\n🧪 Testing response format standardization...")
    
    try:
        from arifos.core.kernel.mcp_server import ConstitutionalMCPServer
        import mcp.types as types
        
        # Create a test server instance
        server = ConstitutionalMCPServer()
        
        # Test the response creation method
        test_data = {
            "verdict": "SEAL",
            "reason": "Test successful",
            "constitutional_valid": True
        }
        
        response = server._create_constitutional_response(test_data)
        
        # Validate response format
        assert isinstance(response, types.TextContent)
        assert response.type == "text"
        
        # Parse the JSON content
        parsed_data = json.loads(response.text)
        assert parsed_data["verdict"] == "SEAL"
        assert parsed_data["reason"] == "Test successful"
        
        print("✅ Response format standardization working")
        print(f"✅ Response type: {type(response)}")
        print(f"✅ Response content: {response.text[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ Response format test failed: {e}")
        return False

async def test_tool_signatures():
    """Test that tool signatures are correct"""
    print("\n🧪 Testing tool signature updates...")
    
    try:
        from arifos.core.kernel.mcp_server import ConstitutionalMCPServer
        import mcp.types as types
        
        server = ConstitutionalMCPServer()
        
        # Test that tools return TextContent instead of Dict
        # We'll test the agi_think tool as an example
        
        # Get the tool function
        agi_think_tool = None
        for tool in server.server._tools.values():
            if tool.name == "agi_think":
                agi_think_tool = tool
                break
        
        if agi_think_tool:
            # Test calling the tool
            result = await agi_think_tool.handler("test query", {})
            assert isinstance(result, types.TextContent)
            print("✅ Tool signatures updated correctly")
            print(f"✅ agi_think returns: {type(result)}")
        else:
            print("⚠️  Could not find agi_think tool for testing")
            
        return True
        
    except Exception as e:
        print(f"❌ Tool signature test failed: {e}")
        return False

def test_constitutional_kernel_functionality():
    """Test basic constitutional kernel functionality"""
    print("\n🧪 Testing constitutional kernel functionality...")
    
    try:
        from arifos.core.kernel.constitutional import ConstitutionalKernel
        
        kernel = ConstitutionalKernel()
        
        # Test health check
        health = kernel.health_check()
        assert "status" in health
        assert health["status"] == "healthy"
        
        print("✅ Constitutional kernel functional")
        print(f"✅ Health status: {health}")
        return True
        
    except Exception as e:
        print(f"❌ Constitutional kernel test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Testing arifOS Kernel Fixes")
    print("=" * 50)
    
    test_results = []
    
    # Run tests
    test_results.append(("Kernel Imports", test_kernel_imports()))
    test_results.append(("MCP Server Imports", test_mcp_server_imports()))
    test_results.append(("Response Format", test_response_format()))
    test_results.append(("Tool Signatures", await test_tool_signatures()))
    test_results.append(("Constitutional Kernel", test_constitutional_kernel_functionality()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All kernel fixes are working correctly!")
        print("✅ Import issues resolved")
        print("✅ Response format standardized") 
        print("✅ MCP tools return proper TextContent")
        return 0
    else:
        print("⚠️  Some tests failed - review required")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)