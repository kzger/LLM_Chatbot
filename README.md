# Llama Bot Project

This project is a modular bot built using Python that integrates with LINE, Slack, and a generic interface. The bot leverages Llama and Llava chat models to handle text and image messages.

## Project Structure

```
project/
|-- llama_bot.py
|-- app/
|   |-- __init__.py
|   |-- event_handlers.py
|   |-- message_handler.py
|   |-- utils.py
|-- services/
|   |-- __init__.py
|   |-- llama_service.py
|   |-- llava_service.py
|   |-- loading_animation.py
|   |-- prompt_service.py
|-- config/
|   |-- __init__.py
|   |-- settings.py
|-- model/
|   |-- __init__.py
|   |-- model_list.py
|-- README.md
|-- requirements.txt
```

## Requirements

### Python Packages

Make sure you have the following Python packages installed:

- line-bot-sdk
- slack_bolt
- slack_sdk
- flask
- requests
- python-dotenv

You can install these packages using the following command:

```bash
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the root directory of your project and add the following environment variables:

```
LINE_CHANNEL_ACCESS_TOKEN=your-line-channel-access-token
LINE_CHANNEL_SECRET=your-line-channel-secret
SLACK_BOT_TOKEN=your-slack-bot-token
SLACK_SIGNING_SECRET=your-slack-signing-secret
SLACK_APP_TOKEN=your-slack-app-token
LLAMA_API_URL=your-llama-api-url
LLAVA_API_URL=your-llava-api-url
```

## How to Run

### 1. Clone the repository:

```bash
git clone https://github.com/kzger/Slack_bolt.git
cd Slack_bolt
```

### 2. Set up your environment:

Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate   # On Windows use `venv\Scripts\activate`
```

Install the required packages:

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables:

Create a `.env` file in the project root directory with the necessary environment variables as mentioned above.

### 4. Run the application:

```bash
python llama_bot.py
```

## Integrating with LINE

To set up your bot with LINE, follow these steps:

1. Go to the LINE Developers Console.
2. Create a new provider and channel.
3. Note down your `LINE_CHANNEL_ACCESS_TOKEN` and `LINE_CHANNEL_SECRET`.
4. Add the callback endpoint in your LINE channel settings for the webhook URL.

## Integrating with Slack

### Slack Setup

Please refer to the Slack website to set up your bot: [Slack Bolt for Python](https://slack.dev/bolt-python/tutorial/getting-started)

1. Go to the [Slack API](https://api.slack.com/) and create a new app.
2. Enable the necessary permissions and event subscriptions.
3. Note down your `SLACK_BOT_TOKEN`, `SLACK_SIGNING_SECRET`, and `SLACK_APP_TOKEN`.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contact

For any questions or inquiries, please contact [rock1903jack@gmail.com].

---
