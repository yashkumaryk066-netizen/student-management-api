"""
AI Function/Tool Calling System
Enables AI to execute actions and use external tools
"""
import os
import json
import logging
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class AIToolRegistry:
    """
    Registry of tools/functions that AI can call
    Provides structured function calling capability
    """
    
    def __init__(self):
        """Initialize tool registry"""
        self.tools: Dict[str, Dict] = {}
        self._register_default_tools()
    
    def register_tool(
        self,
        name: str,
        function: Callable,
        description: str,
        parameters: Dict[str, Any]
    ):
        """
        Register a new tool
        
        Args:
            name: Tool name
            function: Actual function to call
            description: What the tool does
            parameters: JSON schema for parameters
        """
        self.tools[name] = {
            "function": function,
            "description": description,
            "parameters": parameters
        }
        logger.info(f"✅ Registered tool: {name}")
    
    def _register_default_tools(self):
        """Register default educational tools"""
        
        # Tool 1: Calculator
        def calculator(expression: str) -> str:
            """Safe calculator for mathematical expressions"""
            try:
                # Safe eval with limited scope
                allowed_names = {"__builtins__": {}}
                result = eval(expression, allowed_names)
                return str(result)
            except Exception as e:
                return f"Calculation error: {str(e)}"
        
        self.register_tool(
            name="calculator",
            function=calculator,
            description="Evaluate mathematical expressions. Supports +, -, *, /, **, (), etc.",
            parameters={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate, e.g., '2+2' or '(10*5)/2'"
                    }
                },
                "required": ["expression"]
            }
        )
        
        # Tool 2: Web Search (simulated - would connect to real API)
        def web_search(query: str, num_results: int = 3) -> str:
            """Simulated web search - would use real API in production"""
            return f"[Web search results for '{query}' would appear here. Integrate with Google Custom Search API or SerpAPI for real results.]"
        
        self.register_tool(
            name="web_search",
            function=web_search,
            description="Search the web for current information",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "num_results": {"type": "integer", "description": "Number of results (default: 3)"}
                },
                "required": ["query"]
            }
        )
        
        # Tool 3: Code Executor (Python sandbox)
        def execute_python(code: str) -> str:
            """Execute Python code in restricted environment"""
            try:
                # In production, use https://github.com/kmod/pysandbox or Docker container
                # For now, simple exec with limited builtins
                allowed_builtins = {
                    'print': print,
                    'len': len,
                    'range': range,
                    'sum': sum,
                    'max': max,
                    'min': min,
                    'abs': abs,
                    'round': round
                }
                
                exec_globals = {"__builtins__": allowed_builtins}
                exec_locals = {}
                
                exec(code, exec_globals, exec_locals)
                
                # Return last expression value if any
                return str(exec_locals) if exec_locals else "Code executed successfully"
                
            except Exception as e:
                return f"Execution error: {str(e)}"
        
        self.register_tool(
            name="python_executor",
            function=execute_python,
            description="Execute Python code safely (basic operations only)",
            parameters={
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Python code to execute"}
                },
                "required": ["code"]
            }
        )
        
        # Tool 4: Get Current Time/Date
        def get_current_time(format: str = "%Y-%m-%d %H:%M:%S") -> str:
            """Get current date/time"""
            return datetime.now().strftime(format)
        
        self.register_tool(
            name="get_time",
            function=get_current_time,
            description="Get current date and time",
            parameters={
                "type": "object",
                "properties": {
                    "format": {
                        "type": "string",
                        "description": "Time format string (default: YYYY-MM-DD HH:MM:SS)"
                    }
                }
            }
        )
        
        # Tool 5: Unit Converter
        def convert_units(value: float, from_unit: str, to_unit: str) -> str:
            """Convert between common units"""
            conversions = {
                # Length
                ("meters", "feet"): 3.28084,
                ("feet", "meters"): 0.3048,
                ("kilometers", "miles"): 0.621371,
                ("miles", "kilometers"): 1.60934,
                # Temperature
                ("celsius", "fahrenheit"): lambda c: c * 9/5 + 32,
                ("fahrenheit", "celsius"): lambda f: (f - 32) * 5/9,
                # Weight
                ("kilograms", "pounds"): 2.20462,
                ("pounds", "kilograms"): 0.453592,
            }
            
            key = (from_unit.lower(), to_unit.lower())
            if key in conversions:
                conversion = conversions[key]
                if callable(conversion):
                    result = conversion(value)
                else:
                    result = value * conversion
                return f"{value} {from_unit} = {result:.2f} {to_unit}"
            else:
                return f"Conversion from {from_unit} to {to_unit} not supported"
        
        self.register_tool(
            name="unit_converter",
            function=convert_units,
            description="Convert between different units (length, temperature, weight)",
            parameters={
                "type": "object",
                "properties": {
                    "value": {"type": "number", "description": "Value to convert"},
                    "from_unit": {"type": "string", "description": "Source unit"},
                    "to_unit": {"type": "string", "description": "Target unit"}
                },
                "required": ["value", "from_unit", "to_unit"]
            }
        )
    
    def get_tools_schema(self) -> List[Dict]:
        """
        Get all tools in OpenAI function calling format
        
        Returns:
            List of tool schemas
        """
        schemas = []
        for name, tool in self.tools.items():
            schemas.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": tool["description"],
                    "parameters": tool["parameters"]
                }
            })
        return schemas
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        Execute a registered tool
        
        Args:
            tool_name: Name of tool to execute
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        if tool_name not in self.tools:
            return f"Error: Tool '{tool_name}' not found"
        
        try:
            function = self.tools[tool_name]["function"]
            result = function(**arguments)
            return str(result)
        except Exception as e:
            logger.error(f"Tool execution error ({tool_name}): {e}")
            return f"Tool execution failed: {str(e)}"
    
    def list_tools(self) -> List[str]:
        """Get list of available tool names"""
        return list(self.tools.keys())


# Singleton registry
_tool_registry = None

def get_tool_registry() -> AIToolRegistry:
    """Get or create tool registry"""
    global _tool_registry
    if _tool_registry is None:
        _tool_registry = AIToolRegistry()
    return _tool_registry


class FunctionCallingAI:
    """
    AI wrapper with function calling capability
    Enables AI to use tools intelligently
    """
    
    def __init__(self, base_ai_service):
        """
        Initialize function calling wrapper
        
        Args:
            base_ai_service: Base AI service (ChatGPT, Gemini, etc.)
        """
        self.ai = base_ai_service
        self.registry = get_tool_registry()
    
    def chat_with_tools(
        self,
        user_message: str,
        available_tools: Optional[List[str]] = None
    ) -> str:
        """
        Chat with AI that can call tools
        
        Args:
            user_message: User's message
            available_tools: List of tool names to make available (None = all)
            
        Returns:
            AI response (may include tool execution results)
        """
        # Get tools schema
        if available_tools:
            tools_schema = [
                schema for schema in self.registry.get_tools_schema()
                if schema['function']['name'] in available_tools
            ]
        else:
            tools_schema = self.registry.get_tools_schema()
        
        # Add system message about tools
        system_message = f"""You have access to the following tools:

{json.dumps(tools_schema, indent=2)}

When you need to use a tool, respond with:
TOOL_CALL: {{"tool": "tool_name", "arguments": {{"arg1": "value1"}}}}

Then I will execute the tool and give you the result."""
        
        # Check if AI wants to call a tool
        initial_response = self.ai.custom_prompt(
            user_message,
            system_message=system_message
        ) if hasattr(self.ai, 'custom_prompt') else self.ai.ask_tutor(user_message)
        
        # Parse for tool calls
        if "TOOL_CALL:" in initial_response:
            try:
                # Extract tool call JSON
                tool_call_start = initial_response.index("TOOL_CALL:") + 10
                tool_call_json = initial_response[tool_call_start:].strip()
                
                # Find JSON object
                brace_count = 0
                json_end = 0
                for i, char in enumerate(tool_call_json):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            json_end = i + 1
                            break
                
                tool_call = json.loads(tool_call_json[:json_end])
                
                # Execute tool
                tool_name = tool_call.get("tool")
                arguments = tool_call.get("arguments", {})
                
                tool_result = self.registry.execute_tool(tool_name, arguments)
                
                # Get final response with tool result
                final_prompt = f"""The user asked: {user_message}

You decided to use the tool '{tool_name}' which returned:
{tool_result}

Now provide a final answer to the user incorporating this result."""
                
                final_response = self.ai.custom_prompt(final_prompt) if hasattr(self.ai, 'custom_prompt') else tool_result
                
                return final_response
                
            except Exception as e:
                logger.error(f"Tool calling error: {e}")
                return initial_response  # Return original response if tool calling fails
        
        return initial_response


# Helper function
def enable_function_calling(ai_service):
    """
    Wrap any AI service with function calling capability
    
    Args:
        ai_service: Any AI service instance
        
    Returns:
        FunctionCallingAI wrapper
    """
    return FunctionCallingAI(ai_service)
