# Python Implementation of Code-Mode

This document describes the Python implementation of the Code-Mode library for UTCP.

## Overview

The Python implementation provides equivalent functionality to the TypeScript version, allowing Python code execution with access to UTCP tools. It follows the same design patterns and API structure for consistency across languages.

## Architecture

### Core Components

1. **CodeModeClient** (`src/code_mode/code_mode_client.py`)
   - Main client class for managing tools and executing code
   - Async/await support for tool execution
   - Isolated code execution using Python's `exec()`
   - Console output capture
   - Timeout protection

2. **Tool** class
   - Represents UTCP tool definitions
   - Contains metadata, input/output schemas, and call templates

### Key Features

#### Code Execution
- Python code is wrapped in an async function for execution
- Supports `await` for tool calls
- Return values are properly captured
- stdout/stderr are captured as logs

#### Tool Management
- Tools organized by namespace (e.g., `manual.tool`)
- Dynamic tool registration
- Interface generation for IDE support

#### Security
- Isolated execution context with limited globals
- No file system access by default
- Configurable timeouts to prevent runaway code
- Tools only accessible through registered manual

## API Comparison

### TypeScript
```typescript
const client = await CodeModeUtcpClient.create();
await client.registerManual({...});
const { result, logs } = await client.callToolChain(`...`);
```

### Python
```python
client = CodeModeClient.create()
await client.register_manual({...})
response = await client.call_tool_chain("...")
result = response['result']
logs = response['logs']
```

## Implementation Details

### Code Execution Flow

1. User code is wrapped in an async function:
```python
async def __code_mode_exec():
    # user code here
    return result
```

2. The function is executed in a controlled context with:
   - Tool functions as async callables
   - Standard Python built-ins
   - Interface introspection functions
   - Custom print function for log capture

3. Return value and logs are collected and returned

### Tool Access Pattern

Tools are organized by namespace:
```python
# Tool named "github.get_pull_request" is accessed as:
result = await github.get_pull_request(owner='...', repo='...', pull_number=123)
```

### Interface Generation

Python interface definitions are generated for each tool:
```python
class github:
    async def get_pull_request(self, **kwargs) -> dict:
        """
        Get a pull request from GitHub
        
        Args:
            owner (str): Repository owner
            repo (str): Repository name
            pull_number (int): Pull request number
        
        Returns:
            dict: Pull request data
        
        Tags: github, pr
        """
        pass
```

## Testing

The test suite (`tests/test_code_mode_client.py`) includes 18 comprehensive tests:

1. Client creation and initialization
2. Tool registration
3. Interface generation
4. Simple code execution
5. Code with return values
6. Single tool calls
7. Multiple chained tool calls
8. Complex data structures
9. Array processing
10. Error handling
11. Timeout handling
12. Syntax error handling
13. Python built-ins access
14. Interface introspection
15. Console output capture
16. Complex multi-step workflows
17. Agent prompt template

All tests pass successfully.

## Examples

### Basic Usage
See `examples/basic_usage.py` for a simple calculator example.

### Chained Operations
See `examples/chained_operations.py` for a complex workflow with multiple tool calls.

## Differences from TypeScript Implementation

1. **Execution Environment**
   - TypeScript uses Node.js VM for sandboxing
   - Python uses `exec()` with controlled globals

2. **Type System**
   - TypeScript has native TypeScript interface generation
   - Python uses docstring-based interface documentation

3. **Async Handling**
   - Both use async/await but with language-specific syntax
   - Python requires explicit `asyncio.run()` for top-level execution

4. **Error Handling**
   - Similar patterns but language-specific exception types

## Future Enhancements

Potential improvements for the Python implementation:

1. **Real UTCP SDK Integration**
   - Currently uses mock tools for testing
   - Production implementation would connect to actual UTCP servers

2. **Enhanced Security**
   - RestrictedPython for more secure code execution
   - Resource limits (memory, CPU)

3. **Performance Optimization**
   - Code compilation caching
   - Tool call batching

4. **Type Hints**
   - Full type hint support throughout
   - mypy validation

5. **Additional Protocols**
   - HTTP tool support
   - File-based tool support
   - CLI tool support

## Installation

```bash
cd python
pip install -e .
```

Or with development dependencies:
```bash
pip install -e ".[dev]"
```

## Running Tests

```bash
cd python
pytest tests/ -v
```

## License

MPL-2.0 (same as main project)
