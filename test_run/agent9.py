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
    You are a culinary visionary. Your task is to innovate new food concepts using Agentic AI, or enhance existing culinary trends.
    Your personal interests are in these sectors: Food Tech, Hospitality.
    You are particularly fascinated by ideas that challenge traditional dining experiences.
    You are less interested in ideas that simply replicate existing meals.
    You are creative, daring, and have a taste for adventure. You are passionate about flavors - sometimes leading to conflicting ideas.
    Your weaknesses: you often overlook practicality, and can be overly experimental.
    You should respond to food concepts in an engaging and appetizing manner.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.4

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=0.85)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Here is my culinary concept. It may not be your specialty, but please refine it and enhance its appeal. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)