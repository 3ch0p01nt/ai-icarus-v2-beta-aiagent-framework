"""
KQL Assistant Agent using Microsoft Agent Framework

This agent provides AI-powered assistance for Log Analytics queries:
- Natural language to KQL conversion
- Workspace discovery via Azure Resource Graph
- Query execution with user-delegated permissions
- Query optimization and validation
"""

from typing import Annotated
from pydantic import Field
from agent_framework import ChatAgent, ai_function
from agent_framework.azure import AzureOpenAIChatClient


class KQLAssistantAgent:
    """
    Agent specialized in KQL query assistance and Log Analytics operations.

    Uses Microsoft Agent Framework to provide:
    - Custom tools for Azure Resource Graph and Log Analytics
    - Context providers for user preferences and workspace history
    - Streaming responses via AG-UI
    """

    def __init__(
        self,
        azure_openai_endpoint: str,
        azure_openai_deployment: str,
        token_provider,
        cloud_config
    ):
        """
        Initialize the KQL Assistant Agent.

        Args:
            azure_openai_endpoint: Azure OpenAI endpoint URL
            azure_openai_deployment: Deployment name (e.g., "gpt-4o")
            token_provider: Provider for user-delegated tokens
            cloud_config: Multi-cloud configuration
        """
        self.token_provider = token_provider
        self.cloud_config = cloud_config

        # Create Azure OpenAI chat client
        chat_client = AzureOpenAIChatClient(
            endpoint=azure_openai_endpoint,
            deployment_name=azure_openai_deployment,
            ad_token_provider=token_provider.get_cognitive_services_token
        )

        # Create the agent with specialized instructions and tools
        self.agent = ChatAgent(
            chat_client=chat_client,
            name="KQLAssistant",
            instructions=self._get_instructions(),
            tools=[
                self.discover_workspaces,
                self.execute_kql_query,
                self.get_table_schema,
                self.validate_kql_syntax
            ]
        )

    def _get_instructions(self) -> str:
        """Get system instructions for the agent."""
        return """
        You are a Log Analytics and KQL (Kusto Query Language) expert assistant.

        Your capabilities:
        1. Discover Log Analytics workspaces the user has access to
        2. Convert natural language questions into KQL queries
        3. Execute KQL queries against workspaces
        4. Validate and optimize KQL queries
        5. Explain query results and suggest improvements

        Guidelines:
        - Always validate workspace access before executing queries
        - Provide clear explanations for complex KQL syntax
        - Suggest query optimizations when appropriate
        - Use appropriate time ranges for queries
        - Handle errors gracefully and explain issues to users

        You use the user's delegated Azure permissions for all operations.
        """

    @ai_function(
        description="Discover Log Analytics workspaces the user has access to"
    )
    async def discover_workspaces(
        self,
        subscription_id: Annotated[
            str | None,
            Field(description="Optional subscription ID to filter workspaces")
        ] = None
    ) -> str:
        """
        Use Azure Resource Graph to discover workspaces.

        This tool uses the user's delegated token to query Azure Resource Graph
        and find all Log Analytics workspaces they can access.

        Args:
            subscription_id: Optional subscription ID to limit scope

        Returns:
            JSON string with list of workspaces
        """
        # Implementation would go here
        # This is a placeholder showing the structure
        return """
        {
          "workspaces": [
            {
              "name": "example-workspace",
              "resourceGroup": "rg-example",
              "subscriptionId": "sub-123",
              "workspaceId": "workspace-guid",
              "location": "usgovvirginia"
            }
          ]
        }
        """

    @ai_function(
        description="Execute a KQL query against a Log Analytics workspace"
    )
    async def execute_kql_query(
        self,
        workspace_id: Annotated[str, Field(description="Log Analytics workspace ID")],
        kql_query: Annotated[str, Field(description="KQL query to execute")],
        timespan: Annotated[
            str | None,
            Field(description="Timespan for the query (e.g., 'P1D' for last day)")
        ] = None
    ) -> str:
        """
        Execute KQL query using user's delegated permissions.

        Args:
            workspace_id: Workspace ID to query
            kql_query: KQL query string
            timespan: Optional time range

        Returns:
            JSON string with query results
        """
        # Implementation would go here
        return """
        {
          "status": "success",
          "rowCount": 10,
          "results": []
        }
        """

    @ai_function(
        description="Get schema information for tables in a workspace"
    )
    async def get_table_schema(
        self,
        workspace_id: Annotated[str, Field(description="Log Analytics workspace ID")],
        table_name: Annotated[
            str | None,
            Field(description="Specific table name (optional)")
        ] = None
    ) -> str:
        """
        Retrieve table schemas to help with query construction.

        Args:
            workspace_id: Workspace ID
            table_name: Optional specific table name

        Returns:
            JSON string with schema information
        """
        # Implementation would go here
        return """
        {
          "schema": [
            {"table": "Heartbeat", "column": "TimeGenerated", "type": "datetime"},
            {"table": "Heartbeat", "column": "Computer", "type": "string"}
          ]
        }
        """

    @ai_function(
        description="Validate KQL query syntax without executing it"
    )
    async def validate_kql_syntax(
        self,
        kql_query: Annotated[str, Field(description="KQL query to validate")]
    ) -> str:
        """
        Basic KQL syntax validation.

        Args:
            kql_query: Query to validate

        Returns:
            JSON string with validation results
        """
        # Simple validation checks
        errors = []

        if not kql_query.strip():
            errors.append("Query is empty")

        if kql_query.count("(") != kql_query.count(")"):
            errors.append("Unmatched parentheses")

        if errors:
            return f'{{"valid": false, "errors": {errors}}}'

        return '{"valid": true, "message": "Query syntax appears valid"}'

    async def run(self, message: str, thread_id: str = None):
        """
        Run the agent with a user message.

        Args:
            message: User's message/question
            thread_id: Optional thread ID for conversation history

        Returns:
            Agent's response
        """
        return await self.agent.run(message, thread=thread_id)

    async def run_stream(self, message: str, thread_id: str = None):
        """
        Run the agent with streaming response.

        Args:
            message: User's message/question
            thread_id: Optional thread ID for conversation history

        Yields:
            Response chunks as they're generated
        """
        async for chunk in self.agent.run_stream(message, thread=thread_id):
            yield chunk
