"""
Basic usage example for CodeModeClient.
This demonstrates simple code execution with tool access.
"""

import asyncio
from code_mode import CodeModeClient
from code_mode.code_mode_client import Tool


async def mock_calculator_add(args):
    """Mock calculator add function."""
    return {'result': args['a'] + args['b']}


async def mock_calculator_multiply(args):
    """Mock calculator multiply function."""
    return {'result': args['a'] * args['b']}


async def main():
    # Create client
    client = CodeModeClient.create()
    
    # Register mock tools
    add_tool = Tool(
        name='calculator.add',
        description='Adds two numbers',
        inputs={
            'type': 'object',
            'properties': {
                'a': {'type': 'number', 'description': 'First number'},
                'b': {'type': 'number', 'description': 'Second number'}
            },
            'required': ['a', 'b']
        },
        outputs={
            'type': 'object',
            'properties': {
                'result': {'type': 'number', 'description': 'Sum'}
            }
        },
        tags=['math'],
        tool_call_template={'call_template_type': 'mock'}
    )
    
    multiply_tool = Tool(
        name='calculator.multiply',
        description='Multiplies two numbers',
        inputs={
            'type': 'object',
            'properties': {
                'a': {'type': 'number', 'description': 'First number'},
                'b': {'type': 'number', 'description': 'Second number'}
            },
            'required': ['a', 'b']
        },
        outputs={
            'type': 'object',
            'properties': {
                'result': {'type': 'number', 'description': 'Product'}
            }
        },
        tags=['math'],
        tool_call_template={'call_template_type': 'mock'}
    )
    
    client.add_tool(add_tool, mock_calculator_add)
    client.add_tool(multiply_tool, mock_calculator_multiply)
    
    # Execute code that uses tools
    code = """
# Simple arithmetic using tools
a = await calculator.add(a=5, b=3)
b = await calculator.multiply(a=a['result'], b=2)

print(f"(5 + 3) * 2 = {b['result']}")

return {
    'addition_result': a['result'],
    'final_result': b['result']
}
"""
    
    response = await client.call_tool_chain(code)
    
    print("\n=== Execution Result ===")
    print(f"Result: {response['result']}")
    print(f"\n=== Console Logs ===")
    for log in response['logs']:
        print(log)
    
    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
