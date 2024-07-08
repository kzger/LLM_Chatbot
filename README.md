# Slack Bot Project

This project is a modular Slack Bot built using Python and the Slack Bolt framework. The bot integrates with the Llama and Llava chat models to handle text and image messages, update user conversations, and provide loading animations.

## Project Structure

```
project/
|-- slack_bot.py
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
### Slack bolt for python
Please refer to Slack website to set up your bot : https://slack.dev/bolt-python/tutorial/getting-started

### Python Packages

Make sure you have the following Python packages installed:

- slack_bolt
- slack_sdk
- flask
- requests
- python-dotenv

You can install these packages using the following command:

```bash
pip install slack_bolt slack_sdk flask requests python-dotenv 
```

### Environment Variables

Create a `.env` file in the root directory of your project and add the following environment variables:

```
SLACK_BOT_TOKEN=your-slack-bot-token
SLACK_SIGNING_SECRET=your-slack-signing-secret
SLACK_APP_TOKEN=your-slack-app-token 
LLAMA_API_URL = your-llama-api-url
LLAVA_API_URL = your-llava-api-url
```

## How to Run

1. **Clone the repository**:
    ```bash
    git clone https://github.com/kzger/Slack_bolt.git
    cd slack-bot-project
    ```

2. **Set up your environment**:
    - Create a virtual environment:
      ```bash
      python -m venv venv
      source venv/bin/activate   # On Windows use `venv\Scripts\activate`
      ```
    - Install the required packages:
      ```bash
      pip install -r requirements.txt
      ```

3. **Configure environment variables**:
    - Create a `.env` file in the project root directory with the necessary environment variables as mentioned above.

4. **Run the application**:
    ```bash
    python slack_bot.py
    ```


## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contact

For any questions or inquiries, please contact [rock1903jack@gmail.com].

---
