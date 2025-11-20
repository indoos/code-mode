"""
CodeModeClient - Python implementation for executing Python code with UTCP tool access.
"""

import asyncio
import io
import json
import re
import sys
from contextlib import redirect_stdout, redirect_stderr
from typing import Any, Dict, List, Optional, Callable
from collections.abc import Coroutine


class Tool:
    """Represents a UTCP tool definition."""
    
    def __init__(self, name: str, description: str, inputs: Dict, outputs: Dict, tags: List[str], tool_call_template: Dict):
        self.name = name
        self.description = description
        self.inputs = inputs
        self.outputs = outputs
        self.tags = tags
        self.tool_call_template = tool_call_template


class CodeModeClient:
    """
    CodeModeClient provides Python code execution capabilities with UTCP tool access.
    This allows executing Python code that can directly call registered tools as functions.
    """
    
    AGENT_PROMPT_TEMPLATE = """
## UTCP CodeMode Tool Usage Guide (Python)

You have access to a CodeModeClient that allows you to execute Python code with access to registered tools. Follow this workflow:

### 1. Tool Discovery Phase
**Always start by discovering available tools:**
- Tools are organized by manual namespace (e.g., `manual_name.tool_name`)
- Use hierarchical access patterns: `await manual.tool(param=value)`
- Multiple manuals can contain tools with the same name - namespaces prevent conflicts

### 2. Interface Introspection
**Understand tool contracts before using them:**
- Access `__interfaces` to see all available Python interface definitions
- Use `__get_tool_interface('manual.tool')` to get specific tool interfaces
- Interfaces show required inputs, expected outputs, and descriptions
- Look for "Access as: manual.tool(args)" comments for usage patterns

### 3. Code Execution Guidelines
**When writing code for `call_tool_chain`:**
- Use `await manual.tool(param=value)` syntax for all tool calls
- Tools are async functions that return dictionaries
- You have access to standard Python built-ins: `print`, `json`, `math`, `datetime`, etc.
- All print output is automatically captured and returned
- Build properly structured input objects based on interface definitions
- Handle errors appropriately with try/except blocks
- Chain tool calls by using results from previous calls

### 4. Best Practices
- **Discover first, code second**: Always explore available tools before writing execution code
- **Respect namespaces**: Use full `manual.tool` names to avoid conflicts
- **Parse interfaces**: Use interface information to construct proper input objects
- **Error handling**: Wrap tool calls in try/except for robustness
- **Data flow**: Chain tools by passing outputs as inputs to subsequent tools

### 5. Available Runtime Context
- `__interfaces`: String containing all Python interface definitions
- `__get_tool_interface(tool_name)`: Function to get specific tool interface
- All registered tools as `manual.tool` functions
- Standard Python built-ins for data processing

Remember: Always discover and understand available tools before attempting to use them in code execution.
""".strip()
    
    def __init__(self):
        """Initialize the CodeModeClient."""
        self._tools: List[Tool] = []
        self._tool_functions: Dict[str, Callable] = {}
        self._tool_interface_cache: Dict[str, str] = {}
    
    @classmethod
    def create(cls, config: Optional[Dict] = None) -> "CodeModeClient":
        """
        Create a new CodeModeClient instance.
        
        Args:
            config: Optional configuration dictionary
            
        Returns:
            A new CodeModeClient instance
        """
        client = cls()
        # In a real implementation, this would initialize UTCP SDK connection
        # For now, we provide the structure
        return client
    
    def register_manual(self, manual_config: Dict) -> Dict[str, Any]:
        """
        Register a UTCP manual with tools.
        
        Args:
            manual_config: Manual configuration dictionary
            
        Returns:
            Registration result with success status
        """
        # In a real implementation, this would register with UTCP SDK
        # For now, we provide the structure
        return {"success": True, "errors": []}
    
    def add_tool(self, tool: Tool, tool_function: Callable):
        """
        Add a tool to the client.
        
        Args:
            tool: Tool definition
            tool_function: Async function to call for this tool
        """
        self._tools.append(tool)
        self._tool_functions[tool.name] = tool_function
    
    async def get_tools(self) -> List[Tool]:
        """Get all registered tools."""
        return self._tools
    
    async def call_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """
        Call a registered tool by name.
        
        Args:
            tool_name: Name of the tool to call
            args: Arguments to pass to the tool
            
        Returns:
            Tool execution result
        """
        if tool_name not in self._tool_functions:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        tool_func = self._tool_functions[tool_name]
        return await tool_func(args)
    
    @staticmethod
    def _sanitize_identifier(name: str) -> str:
        """
        Sanitize an identifier to be a valid Python identifier.
        
        Args:
            name: The name to sanitize
            
        Returns:
            Sanitized identifier
        """
        # Replace non-alphanumeric characters with underscore
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        # Ensure first character is not a number
        if sanitized and sanitized[0].isdigit():
            sanitized = '_' + sanitized
        return sanitized
    
    def tool_to_python_interface(self, tool: Tool) -> str:
        """
        Convert a Tool object into a Python interface string.
        
        Args:
            tool: The Tool object to convert
            
        Returns:
            Python interface as a string
        """
        if tool.name in self._tool_interface_cache:
            return self._tool_interface_cache[tool.name]
        
        # Generate hierarchical interface structure
        if '.' in tool.name:
            parts = tool.name.split('.')
            manual_name = self._sanitize_identifier(parts[0])
            tool_name = '_'.join(self._sanitize_identifier(p) for p in parts[1:])
            access_pattern = f"{manual_name}.{tool_name}"
            
            # Generate interface content
            input_interface = self._json_schema_to_python_docstring(tool.inputs, "Args")
            output_interface = self._json_schema_to_python_docstring(tool.outputs, "Returns")
            
            interface_content = f"""
class {manual_name}:
    async def {tool_name}(self, **kwargs) -> dict:
        \"\"\"
        {tool.description}
        
        {input_interface}
        
        {output_interface}
        
        Tags: {', '.join(tool.tags)}
        \"\"\"
        pass
"""
        else:
            # No manual namespace
            sanitized_tool_name = self._sanitize_identifier(tool.name)
            access_pattern = sanitized_tool_name
            input_interface = self._json_schema_to_python_docstring(tool.inputs, "Args")
            output_interface = self._json_schema_to_python_docstring(tool.outputs, "Returns")
            
            interface_content = f"""
async def {sanitized_tool_name}(**kwargs) -> dict:
    \"\"\"
    {tool.description}
    
    {input_interface}
    
    {output_interface}
    
    Tags: {', '.join(tool.tags)}
    \"\"\"
    pass
"""
        
        interface_string = f"{interface_content}\n# Access as: {access_pattern}(**kwargs)"
        self._tool_interface_cache[tool.name] = interface_string
        return interface_string
    
    def _json_schema_to_python_docstring(self, schema: Dict, section_name: str) -> str:
        """
        Convert JSON Schema to Python docstring format.
        
        Args:
            schema: JSON Schema dictionary
            section_name: Section name (e.g., "Args", "Returns")
            
        Returns:
            Docstring section as string
        """
        if not schema or schema.get('type') != 'object':
            return f"{section_name}:\n            Any"
        
        properties = schema.get('properties', {})
        required = schema.get('required', [])
        
        if not properties:
            return f"{section_name}:\n            dict: Any dictionary"
        
        lines = [f"{section_name}:"]
        for prop_name, prop_schema in properties.items():
            is_required = prop_name in required
            description = prop_schema.get('description', '')
            py_type = self._json_type_to_python(prop_schema)
            
            required_marker = '' if is_required else ' (optional)'
            lines.append(f"            {prop_name} ({py_type}){required_marker}: {description}")
        
        return '\n'.join(lines)
    
    def _json_type_to_python(self, schema: Dict) -> str:
        """Convert JSON Schema type to Python type hint."""
        schema_type = schema.get('type')
        
        if schema.get('enum'):
            return 'str'  # Simplified
        
        type_map = {
            'string': 'str',
            'number': 'float',
            'integer': 'int',
            'boolean': 'bool',
            'array': 'list',
            'object': 'dict',
            'null': 'None'
        }
        
        if isinstance(schema_type, list):
            return ' | '.join(type_map.get(t, 'Any') for t in schema_type)
        
        return type_map.get(schema_type, 'Any')
    
    async def get_all_tools_python_interfaces(self) -> str:
        """
        Convert all registered tools to Python interface definitions.
        
        Returns:
            Complete Python interface definition string
        """
        tools = await self.get_tools()
        interfaces = [self.tool_to_python_interface(tool) for tool in tools]
        
        header = "# Auto-generated Python interfaces for UTCP tools\n"
        return header + '\n\n'.join(interfaces)
    
    async def call_tool_chain(self, code: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Execute Python code with access to registered tools and capture output.
        
        Args:
            code: Python code to execute
            timeout: Optional timeout in seconds (default: 30)
            
        Returns:
            Dictionary containing 'result' and 'logs' keys
        """
        tools = await self.get_tools()
        
        # Create execution context
        logs = []
        context = await self._create_execution_context(tools, logs)
        
        try:
            # Execute with timeout
            result = await asyncio.wait_for(
                self._run_code(code, context, logs),
                timeout=timeout
            )
            return {"result": result, "logs": logs}
        except asyncio.TimeoutError:
            error_msg = f"Code execution timed out after {timeout}s"
            return {"result": None, "logs": logs + [f"[ERROR] {error_msg}"]}
        except Exception as error:
            error_msg = f"Code execution failed: {str(error)}"
            return {"result": None, "logs": logs + [f"[ERROR] {error_msg}"]}
    
    async def _run_code(self, code: str, context: Dict[str, Any], logs: List[str]) -> Any:
        """
        Run Python code in the execution context.
        
        Args:
            code: Python code to execute
            context: Execution context dictionary
            logs: List to append logs to
            
        Returns:
            Execution result
        """
        # Capture stdout and stderr
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        # Prepare the code for execution
        # Wrap in async function to support await
        wrapped_code = f"""
async def __code_mode_exec():
{self._indent_code(code, 4)}

"""
        
        try:
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                # Execute the wrapped async function definition
                exec(wrapped_code, context)
                
                # Now call and await the function
                result = await context['__code_mode_exec']()
                context['__result'] = result
                
            # Capture any print output
            stdout_content = stdout_capture.getvalue()
            if stdout_content:
                logs.extend(stdout_content.rstrip().split('\n'))
            
            stderr_content = stderr_capture.getvalue()
            if stderr_content:
                logs.extend(['[ERROR] ' + line for line in stderr_content.rstrip().split('\n')])
            
            return context.get('__result')
            
        except Exception as e:
            # Capture error in stderr
            stderr_content = stderr_capture.getvalue()
            if stderr_content:
                logs.extend(['[ERROR] ' + line for line in stderr_content.rstrip().split('\n')])
            raise
    
    def _indent_code(self, code: str, spaces: int) -> str:
        """Indent code by specified number of spaces."""
        indent = ' ' * spaces
        return '\n'.join(indent + line if line.strip() else line 
                        for line in code.split('\n'))
    
    async def _create_execution_context(self, tools: List[Tool], logs: List[str]) -> Dict[str, Any]:
        """
        Create the execution context for running Python code.
        
        Args:
            tools: Array of tools to make available
            logs: List to capture console output
            
        Returns:
            Execution context dictionary
        """
        # Custom print function that captures output
        def captured_print(*args, **kwargs):
            output = io.StringIO()
            kwargs['file'] = output
            print(*args, **kwargs)
            log_line = output.getvalue().rstrip()
            if log_line:
                logs.append(log_line)
        
        # Build context with basic Python utilities
        context = {
            # Built-ins
            'print': captured_print,
            'len': len,
            'range': range,
            'enumerate': enumerate,
            'zip': zip,
            'map': map,
            'filter': filter,
            'sum': sum,
            'min': min,
            'max': max,
            'abs': abs,
            'round': round,
            'sorted': sorted,
            'reversed': reversed,
            'list': list,
            'dict': dict,
            'set': set,
            'tuple': tuple,
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            
            # Modules
            'json': json,
            'asyncio': asyncio,
            
            # Interface introspection
            '__interfaces': await self.get_all_tools_python_interfaces(),
            '__get_tool_interface': lambda tool_name: next(
                (self.tool_to_python_interface(t) for t in tools if t.name == tool_name),
                None
            ),
        }
        
        # Add tool functions organized by manual name
        for tool in tools:
            if '.' in tool.name:
                parts = tool.name.split('.')
                manual_name = self._sanitize_identifier(parts[0])
                tool_name = '_'.join(self._sanitize_identifier(p) for p in parts[1:])
                
                # Create manual namespace object if it doesn't exist
                if manual_name not in context:
                    # Create a simple class to hold tool methods
                    context[manual_name] = type(manual_name, (), {})()
                
                # Create the tool function
                async def make_tool_func(t_name=tool.name):
                    async def tool_func(**kwargs):
                        try:
                            return await self.call_tool(t_name, kwargs)
                        except Exception as error:
                            raise RuntimeError(f"Error calling tool '{t_name}': {str(error)}")
                    return tool_func
                
                # Add tool method to namespace
                setattr(context[manual_name], tool_name, await make_tool_func())
            else:
                # No namespace, add directly to context
                sanitized_tool_name = self._sanitize_identifier(tool.name)
                
                async def make_tool_func(t_name=tool.name):
                    async def tool_func(**kwargs):
                        try:
                            return await self.call_tool(t_name, kwargs)
                        except Exception as error:
                            raise RuntimeError(f"Error calling tool '{t_name}': {str(error)}")
                    return tool_func
                
                context[sanitized_tool_name] = await make_tool_func()
        
        return context
    
    async def close(self):
        """Close the client and cleanup resources."""
        # In a real implementation, this would close UTCP SDK connections
        self._tools.clear()
        self._tool_functions.clear()
        self._tool_interface_cache.clear()
