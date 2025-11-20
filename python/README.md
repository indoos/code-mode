# Code-Mode Python Implementation

Python implementation of the Code-Mode library for UTCP (Universal Tool Calling Protocol).

## Installation

```bash
pip install code-mode
```

## Quick Start

```python
from code_mode import CodeModeClient

# Initialize the client
client = CodeModeClient.create()

# Register tools (example with mock manual)
await client.register_manual({
    'name': 'github',
    'call_template_type': 'http',
    'config': {
        'base_url': 'https://api.github.com'
    }
})

# Execute Python code with tool access
result = await client.call_tool_chain("""
# Call tools and process data
pr = await github.get_pull_request(owner='microsoft', repo='vscode', pull_number=1234)
comments = await github.get_pull_request_comments(owner='microsoft', repo='vscode', pull_number=1234)

# Return processed result
return {
    'title': pr['title'],
    'comment_count': len(comments)
}
""")

print(result['result'])  # Access the execution result
print(result['logs'])     # Access console output
```

## Features

- **Python Code Execution**: Execute Python code with access to registered UTCP tools
- **Tool Integration**: Seamlessly call tools as Python functions
- **Console Logging**: Automatic capture of print statements and logging
- **Timeout Protection**: Configurable execution timeouts
- **Type Hints**: Full type hint support for better IDE integration

## API Reference

### CodeModeClient

#### `CodeModeClient.create(config=None)`
Create a new CodeModeClient instance.

#### `await client.register_manual(config)`
Register a UTCP manual with tools.

#### `await client.call_tool_chain(code, timeout=30)`
Execute Python code with tool access. Returns dict with 'result' and 'logs'.

#### `await client.get_all_tools_python_interfaces()`
Get Python interface definitions for all registered tools.

## License

MPL-2.0
