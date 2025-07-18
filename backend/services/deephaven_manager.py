import pydeephaven as dh
from pydeephaven import Session
from typing import Dict, List, Optional, Any
import asyncio
import json
from datetime import datetime

from models.data_models import AgentState


class DeephavenAgentManager:
    """Manages agent states using Deephaven tables"""

    def __init__(self, session: Any):
        self.session = session
        self.agents_table = None
        self.messages_table = None
        self.performance_table = None
        self._initialize_tables()

    def _initialize_tables(self):
        """Initialize Deephaven tables for agent management"""
        try:
            # Agents table schema
            agents_schema = {
                "agent_id": "string",
                "name": "string",
                "specialization": "string",
                "status": "string",
                "current_task": "string",
                "conversation_context": "string",  # JSON string
                "performance_metrics": "string",  # JSON string
                "last_updated": "string",
                "memory_usage": "int",
                "active_connections": "string",  # JSON array
            }

            # Messages table schema
            messages_schema = {
                "message_id": "string",
                "from_agent": "string",
                "to_agent": "string",
                "message_type": "string",
                "content": "string",
                "timestamp": "string",
                "status": "string",
            }

            # Performance table schema
            performance_schema = {
                "agent_id": "string",
                "metric_name": "string",
                "metric_value": "double",
                "timestamp": "string",
                "metadata": "string",
            }

            # Create tables using Deephaven's table creation methods
            self.agents_table = self.session.empty_table(0).update(
                [f"{col}=({dtype})null" for col, dtype in agents_schema.items()]
            )

            self.messages_table = self.session.empty_table(0).update(
                [f"{col}=({dtype})null" for col, dtype in messages_schema.items()]
            )

            self.performance_table = self.session.empty_table(0).update(
                [f"{col}=({dtype})null" for col, dtype in performance_schema.items()]
            )

        except Exception as e:
            print(f"Error initializing Deephaven tables: {e}")
            # Fallback to None if Deephaven is not available
            self.agents_table = None
            self.messages_table = None
            self.performance_table = None

    async def register_agent(self, agent_state: AgentState):
        """Register a new agent in the system"""
        if not self.agents_table:
            return  # Deephaven not available

        try:
            new_row = {
                "agent_id": agent_state.agent_id,
                "name": agent_state.name,
                "specialization": agent_state.specialization,
                "status": agent_state.status,
                "current_task": agent_state.current_task or "",
                "conversation_context": json.dumps(agent_state.conversation_context),
                "performance_metrics": json.dumps(agent_state.performance_metrics),
                "last_updated": agent_state.last_updated,
                "memory_usage": agent_state.memory_usage,
                "active_connections": json.dumps(agent_state.active_connections),
            }

            # Insert into Deephaven table
            # This is a simplified representation. The actual pydeephaven syntax might differ.
            # Assuming a method to add a new row from a dictionary.
            # For this example, we'll stick to the existing update logic representation.
            self.agents_table = self.agents_table.update(
                [
                    f"{k} = `{v}`" if isinstance(v, str) else f"{k} = {v}"
                    for k, v in new_row.items()
                ]
            )

        except Exception as e:
            print(f"Error registering agent: {e}")

    async def update_agent_state(self, agent_id: str, updates: Dict[str, Any]):
        """Update agent state in real-time"""
        if not self.agents_table:
            return  # Deephaven not available

        try:
            # Update the agents table with new state
            update_expressions = []
            for key, value in updates.items():
                if isinstance(value, (dict, list)):
                    value = json.dumps(value)
                update_expressions.append(
                    f"{key}=agent_id==`{agent_id}` ? `{value}` : {key}"
                )

            # Add timestamp update
            update_expressions.append(
                f"last_updated=agent_id==`{agent_id}` ? `{datetime.now().isoformat()}` : last_updated"
            )

            self.agents_table = self.agents_table.update(update_expressions)

        except Exception as e:
            print(f"Error updating agent state: {e}")

    async def get_agent_state(self, agent_id: str) -> Optional[AgentState]:
        """Retrieve current agent state"""
        if not self.agents_table:
            return None  # Deephaven not available

        try:
            filtered = self.agents_table.where(f"agent_id==`{agent_id}`")
            if filtered.size == 0:
                return None

            row = filtered.to_arrow().to_pylist()[0]
            return AgentState(
                agent_id=row["agent_id"],
                name=row["name"],
                specialization=row["specialization"],
                status=row["status"],
                current_task=row["current_task"] if row["current_task"] else None,
                conversation_context=(
                    json.loads(row["conversation_context"])
                    if row["conversation_context"]
                    else {}
                ),
                performance_metrics=(
                    json.loads(row["performance_metrics"])
                    if row["performance_metrics"]
                    else {}
                ),
                last_updated=row["last_updated"],
                memory_usage=row["memory_usage"],
                active_connections=(
                    json.loads(row["active_connections"])
                    if row["active_connections"]
                    else []
                ),
            )

        except Exception as e:
            print(f"Error getting agent state: {e}")
            return None

    async def log_message(self, message: Dict[str, Any]):
        """Log inter-agent communication"""
        if not self.messages_table:
            return  # Deephaven not available

        try:
            self.messages_table = self.messages_table.update(
                [
                    f"message_id=`{message['message_id']}`",
                    f"from_agent=`{message['from_agent']}`",
                    f"to_agent=`{message['to_agent']}`",
                    f"message_type=`{message['message_type']}`",
                    f"content=`{message['content']}`",
                    f"timestamp=`{message['timestamp']}`",
                    f"status=`{message['status']}`",
                ]
            )

        except Exception as e:
            print(f"Error logging message: {e}")

    async def log_performance_metric(
        self,
        agent_id: str,
        metric_name: str,
        metric_value: float,
        metadata: Dict[str, Any] = None,
    ):
        """Log performance metric for an agent"""
        if not self.performance_table:
            return  # Deephaven not available

        try:
            self.performance_table = self.performance_table.update(
                [
                    f"agent_id=`{agent_id}`",
                    f"metric_name=`{metric_name}`",
                    f"metric_value={metric_value}",
                    f"timestamp=`{datetime.now().isoformat()}`",
                    f"metadata=`{json.dumps(metadata or {})}`",
                ]
            )

        except Exception as e:
            print(f"Error logging performance metric: {e}")

    def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time system metrics"""
        if not self.agents_table:
            return {
                "active_agents": 0,
                "total_messages": 0,
                "status": "deephaven_unavailable",
            }

        try:
            active_agents = self.agents_table.where("status==`active`").size
            total_agents = self.agents_table.size

            # Get message statistics
            total_messages = self.messages_table.size if self.messages_table else 0

            # Get performance metrics
            avg_response_time = 0.0
            if self.performance_table:
                response_time_metrics = self.performance_table.where(
                    "metric_name==`response_time`"
                )
                if response_time_metrics.size > 0:
                    avg_response_time = (
                        response_time_metrics.view(
                            "avg_response_time=avg(metric_value)"
                        )
                        .to_arrow()
                        .to_pylist()[0]["avg_response_time"]
                    )

            return {
                "active_agents": active_agents,
                "total_agents": total_agents,
                "total_messages": total_messages,
                "avg_response_time": avg_response_time,
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            print(f"Error getting real-time metrics: {e}")
            return {
                "active_agents": 0,
                "total_messages": 0,
                "status": "error",
                "error": str(e),
            }

    async def get_agent_performance_history(
        self, agent_id: str, metric_name: str, hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Get performance history for an agent"""
        if not self.performance_table:
            return []

        try:
            # Calculate timestamp for N hours ago
            cutoff_time = datetime.now().timestamp() - (hours * 3600)

            # Query performance data
            performance_data = self.performance_table.where(
                f"agent_id==`{agent_id}` && metric_name==`{metric_name}` && timestamp >= `{cutoff_time}`"
            ).sort("timestamp")

            return performance_data.to_arrow().to_pylist()

        except Exception as e:
            print(f"Error getting performance history: {e}")
            return []

    async def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health metrics"""
        metrics = self.get_real_time_metrics()

        try:
            # Additional health checks
            health_status = {
                "deephaven_connection": (
                    "healthy" if self.agents_table else "unavailable"
                ),
                "agents_table_size": self.agents_table.size if self.agents_table else 0,
                "messages_table_size": (
                    self.messages_table.size if self.messages_table else 0
                ),
                "performance_table_size": (
                    self.performance_table.size if self.performance_table else 0
                ),
                **metrics,
            }

            return health_status

        except Exception as e:
            print(f"Error getting system health: {e}")
            return {"status": "error", "error": str(e)}
