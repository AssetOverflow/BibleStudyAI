from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
import json
import asyncio
from typing import Callable, Dict, Any, List


class AgentCommunicationBus:
    """Handles inter-agent communication via Kafka"""

    def __init__(self, bootstrap_servers: List[str]):
        self.bootstrap_servers = bootstrap_servers
        self.producer = None
        self.consumers = {}
        self.message_handlers = {}

    async def initialize(self):
        """Initialize Kafka producer and consumers"""
        self.producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            key_serializer=lambda k: k.encode("utf-8") if k else None,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            retries=3,
            max_in_flight_requests_per_connection=1,
            enable_idempotence=True,
            acks="all",
        )

    async def send_message(self, topic: str, message: Dict[str, Any], key: str = None):
        """Send message to specific agent or broadcast"""
        try:
            # Add metadata to message
            enhanced_message = {
                **message,
                "timestamp": datetime.now().isoformat(),
                "message_id": f"{datetime.now().timestamp()}_{key or 'broadcast'}",
            }

            future = self.producer.send(topic, value=enhanced_message, key=key)
            result = future.get(timeout=10)  # Wait up to 10 seconds
            return result
        except KafkaError as e:
            print(f"Failed to send message: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error sending message: {e}")
            return None

    async def subscribe_to_agent(
        self, agent_id: str, handler: Callable[[Dict[str, Any]], None]
    ):
        """Subscribe to messages for specific agent"""
        topic = f"agent_{agent_id}"

        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=f"agent_group_{agent_id}",
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            auto_offset_reset="latest",
            enable_auto_commit=True,
            consumer_timeout_ms=1000,
        )

        self.consumers[agent_id] = consumer
        self.message_handlers[agent_id] = handler

        # Start consuming messages in background
        asyncio.create_task(self._consume_messages(agent_id))

    async def _consume_messages(self, agent_id: str):
        """Consume messages for specific agent"""
        consumer = self.consumers.get(agent_id)
        handler = self.message_handlers.get(agent_id)

        if not consumer or not handler:
            print(f"Consumer or handler not found for agent {agent_id}")
            return

        try:
            for message in consumer:
                try:
                    # Process message
                    await handler(message.value)

                except Exception as e:
                    print(f"Error handling message: {e}")

        except Exception as e:
            print(f"Error in message consumption loop for agent {agent_id}: {e}")
        finally:
            consumer.close()

    async def broadcast_to_all_agents(self, message: Dict[str, Any]):
        """Broadcast message to all agents"""
        await self.send_message("agent_broadcast", message)

    async def send_to_specific_agent(self, target_agent: str, message: Dict[str, Any]):
        """Send message to specific agent"""
        topic = f"agent_{target_agent}"
        await self.send_message(topic, message, key=target_agent)
