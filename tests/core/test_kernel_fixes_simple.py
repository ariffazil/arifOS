#!/usr/bin/env python3
"""
Simple test script to validate the kernel import fixes and response format standardization
"""

import sys
import asyncio
import json

# Add arifOS to path
sys.path.insert(0, '.')

def test_kernel_imports():
    """Test that all kernel imports are working"""
    print("Testing kernel imports...")
    
    try:
        from arifos.kernel.constitutional import ConstitutionalKernel, PipelineStage
        print("SUCCESS: ConstitutionalKernel import successful")
        print(f"SUCCESS: PipelineStage enum working: {PipelineStage.STAGE_000_VOID}")
        return True
    except ImportError as e:
        print(f"FAILED: Kernel import failed: {e}")
        return False

def test_mcp_server_imports():
    """Test MCP server imports"""
    print("\nTesting MCP server imports...")
    
    try:
        from arifos.kernel.mcp_server import ConstitutionalMCPServer
        print("SUCCESS: ConstitutionalMCPServer import successful")
        return True
    except ImportError as e:
        print(f"FAILED: MCP server import failed: {e}")
        return False

def test_response_format():
    """Test the standardized response format"""
    print("\nTesting response format standardization...")
    
    try:
        from arifos.kernel.mcp_server import ConstitutionalMCPServer
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
        
        print("SUCCESS: Response format standardization working")
        print(f"SUCCESS: Response type: {type(response)}")
        print(f"SUCCESS: Response content: {response.text[:100]}...")
        return True
        
    except Exception as e:
        print(f"FAILED: Response format test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_constitutional_kernel_functionality():
    """Test basic constitutional kernel functionality"""
    print("\nTesting constitutional kernel functionality...")
    
    try:
        from arifos.kernel.constitutional import ConstitutionalKernel
        
        kernel = ConstitutionalKernel()
        
        # Test health check
        health = kernel.health_check()
        assert "status" in health
        assert health["status"] == "healthy"
        
        print("SUCCESS: Constitutional kernel functional")
        print(f"SUCCESS: Health status: {health}")
        return True
        
    except Exception as e:
        print(f"FAILED: Constitutional kernel test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("Testing arifOS Kernel Fixes")
    print("=" * 50)
    
    test_results = []
    
    # Run tests
    test_results.append(("Kernel Imports", test_kernel_imports()))
    test_results.append(("MCP Server Imports", test_mcp_server_imports()))
    test_results.append(("Response Format", test_response_format()))
    test_results.append(("Constitutional Kernel", test_constitutional_kernel_functionality()))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "SUCCESS" if result else "FAILED"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("All kernel fixes are working correctly!")
        print("Import issues resolved")
        print("Response format standardized") 
        print("MCP tools return proper TextContent")
        return 0
    else:
        print("Some tests failed - review required")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)