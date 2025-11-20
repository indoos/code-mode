"""
Advanced example showing complex chained operations.
This demonstrates how to build workflows with multiple tool calls.
"""

import asyncio
from code_mode import CodeModeClient
from code_mode.code_mode_client import Tool


async def mock_data_fetch(args):
    """Mock data fetching function."""
    return {
        'data': [
            {'id': 1, 'value': 10},
            {'id': 2, 'value': 20},
            {'id': 3, 'value': 30}
        ]
    }


async def mock_data_transform(args):
    """Mock data transformation function."""
    data = args['data']
    operation = args.get('operation', 'sum')
    
    if operation == 'sum':
        total = sum(item['value'] for item in data)
    elif operation == 'average':
        total = sum(item['value'] for item in data) / len(data)
    else:
        total = 0
    
    return {
        'result': total,
        'operation': operation,
        'count': len(data)
    }


async def mock_format_report(args):
    """Mock report formatting function."""
    return {
        'report': f"Report: {args['title']}\nValue: {args['value']}\nStatus: Complete"
    }


async def main():
    # Create client
    client = CodeModeClient.create()
    
    # Register mock tools
    tools_config = [
        (Tool(
            name='data.fetch',
            description='Fetch data from source',
            inputs={'type': 'object', 'properties': {}},
            outputs={
                'type': 'object',
                'properties': {
                    'data': {'type': 'array', 'description': 'Fetched data'}
                }
            },
            tags=['data'],
            tool_call_template={'call_template_type': 'mock'}
        ), mock_data_fetch),
        
        (Tool(
            name='data.transform',
            description='Transform data',
            inputs={
                'type': 'object',
                'properties': {
                    'data': {'type': 'array', 'description': 'Input data'},
                    'operation': {'type': 'string', 'description': 'Operation to perform'}
                },
                'required': ['data']
            },
            outputs={
                'type': 'object',
                'properties': {
                    'result': {'type': 'number', 'description': 'Transformation result'},
                    'operation': {'type': 'string'},
                    'count': {'type': 'number'}
                }
            },
            tags=['data'],
            tool_call_template={'call_template_type': 'mock'}
        ), mock_data_transform),
        
        (Tool(
            name='report.format',
            description='Format a report',
            inputs={
                'type': 'object',
                'properties': {
                    'title': {'type': 'string', 'description': 'Report title'},
                    'value': {'type': 'number', 'description': 'Report value'}
                },
                'required': ['title', 'value']
            },
            outputs={
                'type': 'object',
                'properties': {
                    'report': {'type': 'string', 'description': 'Formatted report'}
                }
            },
            tags=['reporting'],
            tool_call_template={'call_template_type': 'mock'}
        ), mock_format_report)
    ]
    
    for tool, func in tools_config:
        client.add_tool(tool, func)
    
    # Execute complex chained operations
    code = """
print("Starting data processing workflow...")

# Step 1: Fetch data
print("Step 1: Fetching data...")
raw_data = await data.fetch()
print(f"Fetched {len(raw_data['data'])} items")

# Step 2: Transform data (calculate sum)
print("Step 2: Calculating sum...")
sum_result = await data.transform(
    data=raw_data['data'],
    operation='sum'
)
print(f"Sum: {sum_result['result']}")

# Step 3: Transform data (calculate average)
print("Step 3: Calculating average...")
avg_result = await data.transform(
    data=raw_data['data'],
    operation='average'
)
print(f"Average: {avg_result['result']}")

# Step 4: Generate report
print("Step 4: Generating report...")
final_report = await report.format(
    title='Data Analysis Summary',
    value=sum_result['result']
)

print("\\n=== Generated Report ===")
print(final_report['report'])

# Return comprehensive results
return {
    'raw_data_count': len(raw_data['data']),
    'sum': sum_result['result'],
    'average': avg_result['result'],
    'report': final_report['report']
}
"""
    
    response = await client.call_tool_chain(code, timeout=10)
    
    print("\n=== Final Result ===")
    print(f"Data Count: {response['result']['raw_data_count']}")
    print(f"Sum: {response['result']['sum']}")
    print(f"Average: {response['result']['average']}")
    
    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
