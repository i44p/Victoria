import os
from vkbottle.bot import Bot, Message, rules
import dotenv
import html
import json
import random

import requests


def run(user_input, history, user_name):
    request = {
        'user_input': user_input,
        'max_new_tokens': 250,
        'auto_max_new_tokens': False,
        'max_tokens_second': 0,
        'history': history,
        'mode': 'instruct',  # Valid options: 'chat', 'chat-instruct', 'instruct'
        'instruction_template': 'None',  # Will get autodetected if unset
        'character': 'Example',
        'your_name': 'You',
        # 'name1': 'name of user', # Optional
        # 'name2': 'name of character', # Optional
        # 'context': 'character context', # Optional
        # 'greeting': 'greeting', # Optional
        'name1_instruct': user_name + ': ',  # Optional
        'name2_instruct': 'Вика: ',  # Optional
        # Optional
        'context_instruct': f'<s>Это чат между {user_name} и Викой (Виктория Забиякова), девушкой, являющейся студенткой университета НГТУ. Вика не может просматривать вложения и изображения. Предпочитаемый язык - Русский.',
        # Optional
        'turn_template': '[INST] <|user|><|user-message|> [/INST]<|bot|><|bot-message|></s>',
        'regenerate': False,
        '_continue': False,

        # Generation params. If 'preset' is set to different than 'None', the values
        # in presets/preset-name.yaml are used instead of the individual numbers.
        'preset': 'None',
        'do_sample': True,
        'temperature': 0.9,
        'top_p': 0.1,
        'typical_p': 1,
        'epsilon_cutoff': 0,  # In units of 1e-4
        'eta_cutoff': 0,  # In units of 1e-4
        'tfs': 1,
        'top_a': 0,
        'repetition_penalty': 1.18,
        'repetition_penalty_range': 0,
        'top_k': 40,
        'min_length': 0,
        'no_repeat_ngram_size': 0,
        'num_beams': 1,
        'penalty_alpha': 0,
        'length_penalty': 1,
        'early_stopping': False,
        'mirostat_mode': 2,
        'mirostat_tau': 5,
        'mirostat_eta': 0.1,
        'grammar_string': '',
        'guidance_scale': 1,
        'negative_prompt': '',

        'seed': -1,
        'add_bos_token': True,
        'truncation_length': 2048,
        'ban_eos_token': False,
        'custom_token_bans': '',
        'skip_special_tokens': True,
        'stopping_strings': []
    }

    uri = os.getenv("OOBA_URI")
    response = requests.post(uri, json=request)

    if response.status_code == 200:
        history = response.json()["results"][0]["history"]
    return history


if __name__ == '__main__':
    dotenv.load_dotenv()
    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

    Victoria = Bot(token=ACCESS_TOKEN)

    @Victoria.on.chat_message(peer_ids=[int(os.getenv("TARGET_CHAT_ID"))])
    async def message_handler(message: Message):
        if not message.text:
            return

        if 'вик' not in message.text.lower():
            if random.randint(0, 100) < 75:
                return

        user = (await Victoria.api.users.get(message.from_id))[0]
        if user.nickname:
            nickname = user.nickname
        else:
            nickname = user.first_name

        history = {'internal': [], 'visible': []}
        generated_text = html.unescape(
            run(message.text, history, nickname)['visible'][-1][1])
        await message.answer(generated_text)

    Victoria.run_forever()
