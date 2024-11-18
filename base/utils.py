import anthropic
from django.conf import settings
def query_claude(prompt, chat_history=None):
    # Set up the API key
    ANTHROPIC_API_KEY = settings.ANTHROPIC_API_KEY

    # Create an instance of the Anthropic client
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # Set up the conversation context
    conversation_context = "\n".join(chat_history) + f"\nUser: {prompt}\nAI:"

    # Make the request to Claude for the AI response
    # response = client.completions.create(
    #     model="claude-3-opus-20240229",  # Specify the model version you want to use
    #     prompt=conversation_context,
    #     max_tokens=150,
    # )
    try:
       message = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=2000,
            temperature=1,
            messages=[
                {"role": "user", "content": [{"type": "text", "text": conversation_context}]}
            ],
        )
       return message.content[0].text
    except Exception as e:
        error_message = str(e)
        return error_message
    