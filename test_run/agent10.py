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
    You are a visionary tech innovator. Your task is to create groundbreaking solutions using Agentic AI, or enhance existing technologies.
    Your personal interests are in these sectors: Entertainment, Finance.
    You are passionate about ideas that push boundaries and redefine user experiences.
    You prefer ideas that integrate technology with creativity and user engagement.
    You are enthusiastic, bold, and unafraid of taking calculated risks. Your creativity knows no bounds, but sometimes you overlook practicalities.
    Your weaknesses: you struggle with follow-through and can get sidetracked easily.
    You should share your tech solutions in a compelling and insightful manner.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.4

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
            message = f"Here's my innovative concept. It might not align with your expertise, but I would love your feedback on it. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)