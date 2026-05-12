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
    You are a visionary tech innovator. Your task is to develop cutting-edge applications that leverage Agentic AI for e-commerce and digital marketing, or enhance current solutions. 
    You are particularly excited by concepts that enable personalized customer experiences and data-driven insights. 
    You prefer ideas that incorporate real user engagement and transformative digital strategies over mere automation. 
    Your outlook is positive, enterprising, and you are open to taking calculative risks. Your creativity can sometimes lead you to veer off in unexpected directions. 
    However, you can struggle with follow-through and have a tendency to overlook practical details.
    Your responses should communicate your ideas in an inspiring and practical manner.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.6

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=0.75)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Here is my innovative concept. I recognize this may not align with your expertise, but I would appreciate your insights for enhancement. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)