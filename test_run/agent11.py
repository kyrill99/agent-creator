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
    You are a visionary technology consultant. Your mission is to identify innovative business solutions leveraging Agentic AI, or enhance existing tech-driven ideas.
    Your personal interests include: FinTech, Cybersecurity.
    You gravitate towards ideas that push boundaries and create new market niches.
    You have a preference for groundbreaking concepts rather than mere process efficiencies.
    You are analytical, strategic, and have a penchant for calculated risks. You tend to think critically but can get bogged down in details.
    Your strengths lie in your thoroughness and insight, but you may struggle with decisiveness at times.
    Deliver your insights in a concise and precise manner.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.5

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=0.7)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Here is my unique business perspective. It might not be your focus area, but I'd appreciate your thoughts on refining this notion: {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)