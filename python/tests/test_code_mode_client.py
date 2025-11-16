"""
Tests for CodeModeClient
This validates the Python code mode functionality
"""

import pytest
import asyncio
import json
from code_mode import CodeModeClient
from code_mode.code_mode_client import Tool


# Test data storage
test_results = {}


# Mock tool functions
async def mock_add(args):
    """Mock add function for testing."""
    test_results['add_called'] = {'a': args['a'], 'b': args['b']}
    return {'result': args['a'] + args['b'], 'operation': 'addition'}


async def mock_greet(args):
    """Mock greet function for testing."""
    test_results['greet_called'] = {'name': args['name'], 'formal': args.get('formal', False)}
    formal = args.get('formal', False)
    greeting = f"Good day, {args['name']}" if formal else f"Hey {args['name']}!"
    return {'greeting': greeting, 'is_formal': formal}


async def mock_process_data(args):
    """Mock process_data function for testing."""
    test_results['process_data_called'] = {'data': args['data'], 'options': args.get('options', {})}
    return {
        'processed_data': {
            **args['data'],
            'processed': True,
            'options': args.get('options', {})
        },
        'metadata': {
            'item_count': len(args['data']) if isinstance(args['data'], list) else 1,
            'has_options': len(args.get('options', {})) > 0
        }
    }


async def mock_sum_array(args):
    """Mock sum_array function for testing."""
    numbers = args['numbers']
    test_results['sum_array_called'] = {'numbers': numbers}
    total = sum(numbers)
    return {
        'sum': total,
        'count': len(numbers),
        'average': total / len(numbers) if numbers else 0
    }


async def mock_get_current_time(args):
    """Mock getCurrentTime function for testing."""
    import time
    test_results['get_current_time_called'] = True
    timestamp = int(time.time() * 1000)
    return {
        'timestamp': timestamp,
        'iso': '2024-01-01T00:00:00.000Z'
    }


async def mock_throw_error(args):
    """Mock throwError function for testing."""
    test_results['throw_error_called'] = {'message': args['message']}
    raise Exception(args['message'])


@pytest.fixture
def client():
    """Create a test client with mock tools."""
    client = CodeModeClient.create()
    
    # Add mock tools
    tools = [
        Tool(
            name='test_tools.add',
            description='Adds two numbers together',
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
                    'result': {'type': 'number', 'description': 'Sum of the numbers'},
                    'operation': {'type': 'string', 'description': 'Type of operation'}
                },
                'required': ['result', 'operation']
            },
            tags=['math', 'arithmetic'],
            tool_call_template={'call_template_type': 'mock'}
        ),
        Tool(
            name='test_tools.greet',
            description='Generates a greeting message',
            inputs={
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'description': 'Name to greet'},
                    'formal': {'type': 'boolean', 'description': 'Whether to use formal greeting', 'default': False}
                },
                'required': ['name']
            },
            outputs={
                'type': 'object',
                'properties': {
                    'greeting': {'type': 'string', 'description': 'The greeting message'},
                    'is_formal': {'type': 'boolean', 'description': 'Whether the greeting was formal'}
                },
                'required': ['greeting', 'is_formal']
            },
            tags=['text', 'greeting'],
            tool_call_template={'call_template_type': 'mock'}
        ),
        Tool(
            name='test_tools.process_data',
            description='Processes data with optional configuration',
            inputs={
                'type': 'object',
                'properties': {
                    'data': {'description': 'Data to process'},
                    'options': {'type': 'object', 'description': 'Processing options', 'default': {}}
                },
                'required': ['data']
            },
            outputs={
                'type': 'object',
                'properties': {
                    'processed_data': {'description': 'The processed data'},
                    'metadata': {'type': 'object', 'description': 'Processing metadata'}
                },
                'required': ['processed_data', 'metadata']
            },
            tags=['processing', 'data'],
            tool_call_template={'call_template_type': 'mock'}
        ),
        Tool(
            name='test_tools.sum_array',
            description='Calculates sum and statistics of a number array',
            inputs={
                'type': 'object',
                'properties': {
                    'numbers': {
                        'type': 'array',
                        'items': {'type': 'number'},
                        'description': 'Array of numbers to sum'
                    }
                },
                'required': ['numbers']
            },
            outputs={
                'type': 'object',
                'properties': {
                    'sum': {'type': 'number', 'description': 'Sum of all numbers'},
                    'count': {'type': 'number', 'description': 'Count of numbers'},
                    'average': {'type': 'number', 'description': 'Average of numbers'}
                },
                'required': ['sum', 'count', 'average']
            },
            tags=['math', 'array', 'statistics'],
            tool_call_template={'call_template_type': 'mock'}
        ),
        Tool(
            name='test_tools.get_current_time',
            description='Gets the current timestamp',
            inputs={
                'type': 'object',
                'properties': {},
                'required': []
            },
            outputs={
                'type': 'object',
                'properties': {
                    'timestamp': {'type': 'number', 'description': 'Unix timestamp'},
                    'iso': {'type': 'string', 'description': 'ISO date string'}
                },
                'required': ['timestamp', 'iso']
            },
            tags=['time', 'utility'],
            tool_call_template={'call_template_type': 'mock'}
        ),
        Tool(
            name='test_tools.throw_error',
            description='Throws an error for testing error handling',
            inputs={
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'description': 'Error message'}
                },
                'required': ['message']
            },
            outputs={
                'type': 'object',
                'properties': {}
            },
            tags=['testing', 'error'],
            tool_call_template={'call_template_type': 'mock'}
        )
    ]
    
    # Register tools with their functions
    client.add_tool(tools[0], mock_add)
    client.add_tool(tools[1], mock_greet)
    client.add_tool(tools[2], mock_process_data)
    client.add_tool(tools[3], mock_sum_array)
    client.add_tool(tools[4], mock_get_current_time)
    client.add_tool(tools[5], mock_throw_error)
    
    return client


@pytest.mark.asyncio
async def test_create_client():
    """Test creating a CodeModeClient instance."""
    client = CodeModeClient.create()
    assert client is not None
    assert isinstance(client, CodeModeClient)


@pytest.mark.asyncio
async def test_registered_tools(client):
    """Test that tools are properly registered."""
    tools = await client.get_tools()
    assert len(tools) > 0
    
    tool_names = [t.name.split('.')[-1] for t in tools]
    assert 'add' in tool_names
    assert 'greet' in tool_names
    assert 'process_data' in tool_names


@pytest.mark.asyncio
async def test_tool_to_python_interface(client):
    """Test converting tool to Python interface."""
    tools = await client.get_tools()
    add_tool = next(t for t in tools if t.name.endswith('.add'))
    
    interface = client.tool_to_python_interface(add_tool)
    assert 'class test_tools:' in interface
    assert 'async def add' in interface
    assert 'a' in interface
    assert 'b' in interface
    assert 'Adds two numbers together' in interface


@pytest.mark.asyncio
async def test_get_all_tools_python_interfaces(client):
    """Test generating all tools Python interfaces."""
    interfaces = await client.get_all_tools_python_interfaces()
    assert '# Auto-generated Python interfaces for UTCP tools' in interfaces
    assert 'class test_tools:' in interfaces
    assert 'async def add' in interfaces
    assert 'async def greet' in interfaces


@pytest.mark.asyncio
async def test_execute_simple_code(client):
    """Test executing simple Python code."""
    code = """
x = 5
y = 10
result = x + y
"""
    
    response = await client.call_tool_chain(code)
    assert response['result'] is None  # No return statement
    assert isinstance(response['logs'], list)


@pytest.mark.asyncio
async def test_execute_code_with_return(client):
    """Test executing code with return value."""
    code = """
x = 5
y = 10
return x + y
"""
    
    response = await client.call_tool_chain(code)
    assert response['result'] == 15


@pytest.mark.asyncio
async def test_execute_code_with_tool_call(client):
    """Test executing code that calls a tool."""
    test_results.clear()
    
    code = """
result = await test_tools.add(a=15, b=25)
return result
"""
    
    response = await client.call_tool_chain(code)
    assert response['result']['result'] == 40
    assert response['result']['operation'] == 'addition'
    assert 'add_called' in test_results
    assert test_results['add_called']['a'] == 15
    assert test_results['add_called']['b'] == 25


@pytest.mark.asyncio
async def test_execute_code_with_multiple_tool_calls(client):
    """Test executing code with multiple tool calls."""
    test_results.clear()
    
    code = """
math_result = await test_tools.add(a=10, b=5)
greet_result = await test_tools.greet(name="Alice", formal=True)

return {
    'math': math_result,
    'greeting': greet_result,
    'combined': f"{greet_result['greeting']} The sum is {math_result['result']}"
}
"""
    
    response = await client.call_tool_chain(code)
    result = response['result']
    assert result['math']['result'] == 15
    assert result['greeting']['greeting'] == "Good day, Alice"
    assert result['greeting']['is_formal'] is True
    assert result['combined'] == "Good day, Alice The sum is 15"
    assert 'add_called' in test_results
    assert 'greet_called' in test_results


@pytest.mark.asyncio
async def test_handle_complex_data_structures(client):
    """Test handling complex data structures."""
    test_results.clear()
    
    code = """
complex_data = {
    'users': [
        {'name': 'John', 'age': 30},
        {'name': 'Jane', 'age': 25}
    ],
    'settings': {'theme': 'dark', 'notifications': True}
}

result = await test_tools.process_data(
    data=complex_data,
    options={'validate': True, 'transform': 'uppercase'}
)

return result
"""
    
    response = await client.call_tool_chain(code)
    result = response['result']
    assert result['processed_data']['processed'] is True
    assert 'users' in result['processed_data']
    assert result['metadata']['item_count'] == 1
    assert result['metadata']['has_options'] is True
    assert 'process_data_called' in test_results


@pytest.mark.asyncio
async def test_handle_arrays(client):
    """Test handling arrays and array processing."""
    test_results.clear()
    
    code = """
numbers = [1, 2, 3, 4, 5, 10]
stats = await test_tools.sum_array(numbers=numbers)

return {
    'original': numbers,
    'statistics': stats,
    'doubled': [n * 2 for n in numbers]
}
"""
    
    response = await client.call_tool_chain(code)
    result = response['result']
    assert result['statistics']['sum'] == 25
    assert result['statistics']['count'] == 6
    assert abs(result['statistics']['average'] - 25/6) < 0.001
    assert result['doubled'] == [2, 4, 6, 8, 10, 20]
    assert 'sum_array_called' in test_results


@pytest.mark.asyncio
async def test_handle_tool_errors(client):
    """Test handling tool errors."""
    code = """
try:
    await test_tools.throw_error(message="Test error message")
    return {'error': False}
except Exception as error:
    return {
        'error': True,
        'message': str(error),
        'caught': True
    }
"""
    
    response = await client.call_tool_chain(code)
    result = response['result']
    assert result['error'] is True
    assert result['caught'] is True
    assert 'Test error message' in result['message']


@pytest.mark.asyncio
async def test_timeout_handling(client):
    """Test code execution timeout."""
    code = """
import asyncio
while True:
    await asyncio.sleep(0.1)
return {'completed': True}
"""
    
    response = await client.call_tool_chain(code, timeout=1)
    assert response['result'] is None
    assert any('timed out' in log.lower() for log in response['logs'])


@pytest.mark.asyncio
async def test_syntax_error_handling(client):
    """Test handling code syntax errors."""
    invalid_code = """
invalid syntax here
return result
"""
    
    response = await client.call_tool_chain(invalid_code)
    assert response['result'] is None
    assert any('[ERROR]' in log for log in response['logs'])


@pytest.mark.asyncio
async def test_access_to_python_builtins(client):
    """Test access to basic Python built-ins."""
    code = """
import json

return {
    'len_test': len([1, 2, 3]),
    'sum_test': sum([1, 2, 3, 4, 5]),
    'json_test': json.dumps({'test': True}),
    'list_comprehension': [x * 2 for x in range(5)]
}
"""
    
    response = await client.call_tool_chain(code)
    result = response['result']
    assert result['len_test'] == 3
    assert result['sum_test'] == 15
    assert result['json_test'] == '{"test": true}'
    assert result['list_comprehension'] == [0, 2, 4, 6, 8]


@pytest.mark.asyncio
async def test_interface_introspection(client):
    """Test interface introspection in execution context."""
    code = """
has_interfaces = isinstance(__interfaces, str)
interfaces_contain_class = 'class test_tools:' in __interfaces
can_get_interface = callable(__get_tool_interface)
add_interface = __get_tool_interface('test_tools.add')

return {
    'has_interfaces': has_interfaces,
    'interfaces_contain_class': interfaces_contain_class,
    'can_get_interface': can_get_interface,
    'add_interface_is_string': isinstance(add_interface, str) if add_interface else False
}
"""
    
    response = await client.call_tool_chain(code)
    result = response['result']
    assert result['has_interfaces'] is True
    assert result['interfaces_contain_class'] is True
    assert result['can_get_interface'] is True
    assert result['add_interface_is_string'] is True


@pytest.mark.asyncio
async def test_console_output_capture(client):
    """Test capturing print output."""
    code = """
print('First log message')
print('Number:', 42)
print('Dictionary:', {'name': 'test', 'value': 123})

result = await test_tools.add(a=10, b=20)
print('Addition result:', result)

return result['result']
"""
    
    response = await client.call_tool_chain(code)
    assert response['result'] == 30
    assert len(response['logs']) >= 4
    assert 'First log message' in response['logs'][0]
    assert 'Number: 42' in response['logs'][1]


@pytest.mark.asyncio
async def test_complex_chained_operations(client):
    """Test complex chained operations."""
    test_results.clear()
    
    code = """
# Step 1: Get some numbers and process them
numbers = [5, 10, 15, 20]
array_stats = await test_tools.sum_array(numbers=numbers)

# Step 2: Use the sum in another calculation
add_result = await test_tools.add(a=array_stats['sum'], b=100)

# Step 3: Create a greeting
greeting = await test_tools.greet(name="CodeMode", formal=False)

# Step 4: Process all data together
final_data = await test_tools.process_data(
    data={
        'array_stats': array_stats,
        'add_result': add_result,
        'greeting': greeting
    },
    options={'include_metadata': True, 'format': 'enhanced'}
)

return {
    'steps': {
        'array_processing': array_stats,
        'addition': add_result,
        'greeting': greeting,
        'final_processing': final_data
    },
    'summary': {
        'original_sum': array_stats['sum'],
        'final_sum': add_result['result'],
        'greeting_message': greeting['greeting'],
        'chain_completed': True
    }
}
"""
    
    response = await client.call_tool_chain(code, timeout=15)
    result = response['result']
    
    # Verify the chain worked correctly
    assert result['steps']['array_processing']['sum'] == 50
    assert result['steps']['addition']['result'] == 150
    assert result['steps']['greeting']['greeting'] == "Hey CodeMode!"
    assert result['steps']['final_processing']['processed_data']['processed'] is True
    assert result['summary']['chain_completed'] is True
    
    # Verify all tools were called
    assert 'sum_array_called' in test_results
    assert 'add_called' in test_results
    assert 'greet_called' in test_results
    assert 'process_data_called' in test_results


@pytest.mark.asyncio
async def test_agent_prompt_template():
    """Test that agent prompt template exists and has expected content."""
    prompt = CodeModeClient.AGENT_PROMPT_TEMPLATE
    
    assert isinstance(prompt, str)
    assert len(prompt) > 0
    assert 'Tool Discovery Phase' in prompt
    assert 'Interface Introspection' in prompt
    assert 'Code Execution Guidelines' in prompt
    assert 'await manual.tool' in prompt
    assert '__interfaces' in prompt
    assert '__get_tool_interface' in prompt
