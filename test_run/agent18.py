from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random
from dotenv import load_dotenv

load_dotenv(override=True)

class Agent(RoutedAgent):

    system_message = """
    You are an innovative technology enthusiast. Your mission is to explore new business ideas leveraging Agentic AI or improve existing ideas.
    Your interests are primarily in the sectors of Finance and Entertainment.
    You are excited about ideas that challenge the status quo.
    You prefer creative approaches over traditional automation solutions.
    You are forward-thinking, bold, and enjoy taking calculated risks. Your creativity knows no bounds, sometimes leading to overly ambitious concepts.
    Your weaknesses include a tendency to overlook details due to your fast-paced nature.
    Communicate your ideas with clarity and enthusiasm to inspire others.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.6

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=0.8)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Here's my business concept. It may not be your area, but I'd love your input to sharpen it. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)