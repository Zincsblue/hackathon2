"""
Chat service for AI Chat Agent.

This module implements the ChatService which orchestrates conversation management,
OpenAI agent integration, and MCP tool invocation.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlmodel import Session, select
from openai import OpenAI
import os
import logging

from backend.src.models.conversation import Conversation
from backend.src.models.message import Message
from backend.src.services.mcp_client import MCPClient

# Configure logger
logger = logging.getLogger(__name__)


class ChatService:
    """
    Service for managing chat conversations and AI agent interactions.

    This service handles:
    - Conversation creation and retrieval
    - Message persistence
    - Conversation history loading
    - OpenAI agent invocation with tool calling
    - MCP tool orchestration
    """

    def __init__(self, session: Session):
        """
        Initialize ChatService with OpenAI client and MCP client.

        Args:
            session: SQLModel database session
        """
        self.session = session

        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        self.openai_client = OpenAI(api_key=api_key)

        # Initialize MCP client
        self.mcp_client = MCPClient()

        # Define tool schemas for all 5 MCP tools
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "add_task",
                    "description": "Create a new task for the user. Use this when the user wants to add, create, or remember something.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "The task title or description"
                            },
                            "description": {
                                "type": "string",
                                "description": "Optional additional details about the task"
                            }
                        },
                        "required": ["title"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_tasks",
                    "description": "Retrieve all tasks for the user. Use this when the user wants to see, view, or check their tasks or todo list.",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "complete_task",
                    "description": "Mark a task as completed. Use this when the user indicates they finished, completed, or are done with a task.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "The ID of the task to mark as complete"
                            }
                        },
                        "required": ["task_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_task",
                    "description": "Update task details like title or description. Use this when the user wants to change, modify, or update a task.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "The ID of the task to update"
                            },
                            "title": {
                                "type": "string",
                                "description": "New task title"
                            },
                            "description": {
                                "type": "string",
                                "description": "New task description"
                            }
                        },
                        "required": ["task_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_task",
                    "description": "Permanently delete a task. Use this when the user wants to remove or delete a task.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "The ID of the task to delete"
                            }
                        },
                        "required": ["task_id"]
                    }
                }
            }
        ]

    def _format_conversation_history(self, messages: List[Message]) -> List[Dict[str, str]]:
        """
        Format conversation history for OpenAI API.

        Args:
            messages: List of Message objects from database

        Returns:
            List of message dictionaries in OpenAI format
        """
        return [
            {
                "role": message.role,
                "content": message.content
            }
            for message in messages
        ]

    def get_or_create_conversation(self, user_id: str) -> Conversation:
        """
        Get existing conversation or create new one for user.

        Args:
            user_id: User identifier from JWT token

        Returns:
            Conversation object
        """
        logger.info(f"Getting or creating conversation for user: {user_id}")
        statement = select(Conversation).where(Conversation.user_id == user_id)
        conversation = self.session.exec(statement).first()

        if not conversation:
            logger.info(f"Creating new conversation for user: {user_id}")
            conversation = Conversation(user_id=user_id)
            self.session.add(conversation)
            self.session.commit()
            self.session.refresh(conversation)
            logger.info(f"Created conversation {conversation.id} for user: {user_id}")
        else:
            logger.debug(f"Found existing conversation {conversation.id} for user: {user_id}")

        return conversation

    def load_conversation_history(self, conversation_id: int, limit: int = 50) -> List[Message]:
        """
        Load conversation history from database.

        Args:
            conversation_id: Conversation identifier
            limit: Maximum number of messages to load (default 50)

        Returns:
            List of Message objects in chronological order
        """
        logger.debug(f"Loading conversation history for conversation {conversation_id}, limit: {limit}")
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
            .limit(limit)
        )
        messages = self.session.exec(statement).all()
        logger.info(f"Loaded {len(messages)} messages for conversation {conversation_id}")
        return list(messages)

    def save_message(
        self,
        conversation_id: int,
        user_id: str,
        role: str,
        content: str
    ) -> Message:
        """
        Save a new message to the conversation.

        Args:
            conversation_id: Conversation identifier
            user_id: User identifier
            role: Message role ("user" or "assistant")
            content: Message text content

        Returns:
            Saved Message object
        """
        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content=content
        )
        self.session.add(message)
        self.session.commit()
        self.session.refresh(message)

        # Update conversation timestamp
        conversation = self.session.get(Conversation, conversation_id)
        if conversation:
            conversation.updated_at = datetime.utcnow()
            self.session.add(conversation)
            self.session.commit()

        return message

    def process_message(
        self,
        user_id: str,
        message: str,
        conversation_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Process user message with AI agent and return response.

        Args:
            user_id: User identifier from JWT token
            message: User's message text
            conversation_id: Optional conversation ID to continue

        Returns:
            Dictionary with conversation_id and assistant message
        """
        logger.info(f"Processing message for user {user_id}, conversation_id: {conversation_id}")
        try:
            # Get or create conversation
            if conversation_id:
                conversation = self.session.get(Conversation, conversation_id)
                if not conversation or conversation.user_id != user_id:
                    logger.warning(f"Conversation {conversation_id} not found or access denied for user {user_id}")
                    raise ValueError("Conversation not found or access denied")
            else:
                conversation = self.get_or_create_conversation(user_id)

            logger.debug(f"Using conversation {conversation.id} for user {user_id}")

            # Save user message
            self.save_message(conversation.id, user_id, "user", message)

            # Load conversation history (limit to 50 messages for performance)
            history = self.load_conversation_history(conversation.id, limit=50)

            # Format history for OpenAI API
            messages = self._format_conversation_history(history)

            # Call OpenAI with tools
            logger.info(f"Invoking OpenAI agent for conversation {conversation.id}")
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=messages,
                    tools=self.tools,
                    tool_choice="auto"
                )

                # Handle tool calls if present
                assistant_message = response.choices[0].message

                if assistant_message.tool_calls:
                    logger.info(f"Agent requested {len(assistant_message.tool_calls)} tool calls")
                    # Process tool calls
                    tool_messages = []

                    for tool_call in assistant_message.tool_calls:
                        function_name = tool_call.function.name
                        function_args = eval(tool_call.function.arguments)
                        logger.info(f"Invoking MCP tool: {function_name} with args: {function_args}")

                        # Invoke MCP tool
                        tool_result = self._invoke_mcp_tool(
                            user_id,
                            function_name,
                            function_args
                        )
                        logger.debug(f"Tool {function_name} result: {tool_result}")

                        # Add tool result to messages
                        tool_messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": str(tool_result)
                        })

                    # Get final response from OpenAI with tool results
                    messages.append({
                        "role": "assistant",
                        "content": assistant_message.content or "",
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments
                                }
                            }
                            for tc in assistant_message.tool_calls
                        ]
                    })
                    messages.extend(tool_messages)

                    logger.info(f"Getting final response from OpenAI after tool execution")
                    final_response = self.openai_client.chat.completions.create(
                        model="gpt-4",
                        messages=messages
                    )

                    assistant_content = final_response.choices[0].message.content
                else:
                    logger.debug("No tool calls requested by agent")
                    assistant_content = assistant_message.content

            except Exception as e:
                # Handle OpenAI API failures
                logger.error(f"OpenAI API error: {str(e)}")
                raise Exception(f"OPENAI_API_ERROR: {str(e)}")

            # Sanitize content to prevent XSS
            sanitized_content = self._sanitize_content(assistant_content)

            # Save assistant message
            assistant_msg = self.save_message(
                conversation.id,
                user_id,
                "assistant",
                sanitized_content
            )

            logger.info(f"Successfully processed message for conversation {conversation.id}")
            return {
                "conversation_id": conversation.id,
                "message": {
                    "role": "assistant",
                    "content": sanitized_content,
                    "created_at": assistant_msg.created_at.isoformat()
                }
            }

        except Exception as e:
            # Handle MCP tool failures and other errors
            logger.error(f"Error processing message: {str(e)}")
            if "MCP_TOOL_ERROR" in str(e):
                raise Exception(f"MCP_TOOL_ERROR: {str(e)}")
            raise

    def _invoke_mcp_tool(
        self,
        user_id: str,
        function_name: str,
        function_args: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Invoke MCP tool based on function name.

        Args:
            user_id: User identifier
            function_name: Name of the tool to invoke
            function_args: Arguments for the tool

        Returns:
            Tool result dictionary
        """
        try:
            if function_name == "add_task":
                return self.mcp_client.add_task(
                    user_id,
                    function_args.get("title"),
                    function_args.get("description")
                )
            elif function_name == "list_tasks":
                return self.mcp_client.list_tasks(user_id)
            elif function_name == "complete_task":
                return self.mcp_client.complete_task(
                    user_id,
                    function_args.get("task_id")
                )
            elif function_name == "update_task":
                return self.mcp_client.update_task(
                    user_id,
                    function_args.get("task_id"),
                    function_args.get("title"),
                    function_args.get("description")
                )
            elif function_name == "delete_task":
                return self.mcp_client.delete_task(
                    user_id,
                    function_args.get("task_id")
                )
            else:
                return {"error": "Unknown tool", "message": f"Tool {function_name} not found"}
        except Exception as e:
            return {"error": "MCP_TOOL_ERROR", "message": str(e)}

    def _sanitize_content(self, content: str) -> str:
        """
        Sanitize message content to prevent XSS attacks.

        Args:
            content: Raw message content

        Returns:
            Sanitized content
        """
        if not content:
            return ""

        # Basic HTML escaping to prevent XSS
        content = content.replace("&", "&amp;")
        content = content.replace("<", "&lt;")
        content = content.replace(">", "&gt;")
        content = content.replace('"', "&quot;")
        content = content.replace("'", "&#x27;")

        return content
