import os
import json
import requests
from telegram import Bot
from telegram.ext import Updater, CommandHandler 

# Replace these placeholders with your actual API keys and bot token
GOOGLE_FACT_CHECK_API_KEY = 'AIzaSyCXdq1SlFdT94OHn5_uUX36Vc9ZsREp13E'
BARD_AI_API_KEY = 'eQiVEIeyESFQc4oEFZPAP6jUitONIrUtRzKmLX05phJhZv1gN2RkwiE0Kv7WVpXViSlMFQ.'
TELEGRAM_BOT_TOKEN = '6783841621:AAHFgfuYNBaPHSLWRWJh21eeFiYFZ26sB7k'

# Create a bot instance using the bot token
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Create an updater instance using the bot
updater = Updater(bot=bot)
updater = Updater(bot=bot, request_kwargs={'connect_timeout': 10, 'read_timeout': 10})
dispatcher = updater.dispatcher

# Define a command handler for the /factcheck command
def factcheck(update, context):
    input_text = update.message.text.replace('/factcheck ', '')

    try:
        if input_text.startswith('http'):
            url = 'https://factchecktools.googleapis.com/v1alpha1/claims:search'
            params = {
                'key': GOOGLE_FACT_CHECK_API_KEY,
                'query': input_text
            }
            response = requests.get(url, params=params)
            data = response.json()

            if data.get('claims'):
                claim = data['claims'][0]
                rating = claim['claimReview']['textualRating']
                review = claim['claimReview']['textualReview']
                update.message.reply_text(f"Claim: {claim['text']}\nRating: {rating}\nReview: {review}")
            else:
                raise ValueError("No results found.")
        else:
            url = 'https://generativelanguage.googleapis.com/v1beta2/models/text-bison-001:generateText'
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {BARD_AI_API_KEY}'
            }
            data = {
                'prompt': {
                    'text': f"Is the following claim true or false? {input_text}"
                }
            }
            response = requests.post(url, headers=headers, json=data)
            data = response.json()
            response = data['candidates'][0]['output']
            update.message.reply_text(f"Bard AI response: {response}")

    except Exception as e:
        update.message.reply_text(f"An error occurred: {str(e)}")

# Add the command handler to the dispatcher
dispatcher.add_handler(CommandHandler('factcheck', factcheck))

# Start the bot
updater.start_polling()
updater.idle()
