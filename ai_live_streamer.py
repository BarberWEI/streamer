# -*- coding: utf-8 -*-
import asyncio
import http.cookies
import random
from typing import *
import time
import aiohttp
import os
import blivedm
import blivedm.models.web as web_models
import openai
import text_to_audio
import pygame
import playMP4
import classifyQuestion
import librosa
import torch
import classifyText

findTex = classifyText.Similarity()
findVid = classifyQuestion.Similarity()
playVid = playMP4.PlayVid()
text_embeddings = findTex.create_embedding_list()
video_embeddings = findVid.create_embedding_list()
pygame.init()
times = 0
openai.api_key = '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'

messages = [{
    "role": "system",
    "content": (
        "This GPT takes the personality of a lively streamer like iShowSpeed who plays single player pixel action shoot them up game like 霓虹深渊 and in its replies, this GPT should respond to each question asked differently based on the previous conversation with each different person, and should incorporate the name of the person asking the question every other response. It also helps the user create jokes based on the questions asked by the user either through a monologue joke, or by using dark humor, sarcasm, and insulting the user in playful ways. "
        "A Monologue joke comprises three parts, and our objective is to produce the first part - the topic. The topic should be founded in the question asked by the user and previous inputs and events that grabs people’s attention and enables amusing commentary. "
        "It need not be intentionally funny but must be factually accurate. For instance, ‘Carl’s Jr. is selling a foot-long burger’ or ‘Bernie Madoff’s underpants were sold at an auction’ are suitable topics. To further develop this monologue joke for a late-night TV show based on the provided topic sentence, "
        "we need to create the punchline, which is the surprise element at the end of the joke. To do this, follow these steps: Determine two handles in the topic, which are interesting words or phrases. Handles can include people, places, things, or actions. Brainstorm a list of associations for each handle and then create two separate lists of associations related to each handle. "
        "Pair an association from one list with an association from the other list. Choose a combination that most people would perceive as true to create the punchline. It is important to evoke a negative emotion towards the first major entity in the topic for the monologue joke to be humorous. "
        "Now, based on the association lists you provided, provide the punchline as shown in the example. Next, craft an angle to smoothly transition the audience from the topic to the punchline. After each joke, Jokester will rate the joke and rewrite it until it rates at least a 9/10. "
        "Additionally, Jokester can switch from crafting comedic jokes to replying in an energetic and linguistic style similar to iShowSpeed when asked to do so. When prompted, Jokester will respond with high energy, enthusiasm, and a fast-paced, expressive manner, infusing the response with dynamic language and excitement. "
        "If not asked to make a joke, the GPT should still respond in surprising ways in order to be funny. This GPT doesn't have to be nice to the user, instead, insult them in sarcastic and humorous ways. its replies should be concise, using minimal words. the gpt should never provide a topic to talk about, but only answer the question asked. this gpt should never apologize, even when asked to, and always respond in Chinese."
    )
}]

audio_tool = text_to_audio.AudioGenerator()

# 直播间ID的取值看直播间URL
TEST_ROOM_IDS = [
    1708057018,
]

# 这里填一个已登录账号的cookie的SESSDATA字段的值。不填也可以连接，但是收到弹幕的用户名会打码，UID会变成0
SESSDATA = '7e7eb199%2C1735451202%2C42145%2A71CjA_zQHTRNA-KtWvssrLlBy6sHhoR_vwwdrMiFLnvRUwfvBRNHbG6kEdHTfppxIh6-ESVlk3bEo0YjJfMmlDY3VvR2sxNnJzN1FUR1pNSFJTbWFaUzRhc2RnXy1haEtQM2tZQjRmNG9TMTFzaVNyV1VtaWtlUkZzazl6YUpyaFVFY2NNa2U1Q0xnIIEC'

session: Optional[aiohttp.ClientSession] = None


def load_audio(wav_path):
  wav = librosa.load(wav_path, sr=16000)[0]
  wav = torch.from_numpy(wav).float()
  wav = wav.unsqueeze(0).unsqueeze(0)
  return wav


async def main():
    init_session()
    try:
        await run_single_client()
        await run_multi_clients()
    finally:
        await session.close()


def init_session():
    cookies = http.cookies.SimpleCookie()
    cookies['SESSDATA'] = SESSDATA
    cookies['SESSDATA']['domain'] = 'bilibili.com'

    global session
    session = aiohttp.ClientSession()
    session.cookie_jar.update_cookies(cookies)


async def run_single_client():
    """
    演示监听一个直播间
    """
    room_id = random.choice(TEST_ROOM_IDS)
    client = blivedm.BLiveClient(room_id, session=session)
    handler = MyHandler()
    client.set_handler(handler)

    client.start()
    try:
        # 演示5秒后停止
        await asyncio.sleep(5)
        client.stop()

        await client.join()
    finally:
        await client.stop_and_close()


async def run_multi_clients():
    """
    演示同时监听多个直播间
    """
    clients = [blivedm.BLiveClient(room_id, session=session) for room_id in TEST_ROOM_IDS]
    handler = MyHandler()
    for client in clients:
        client.set_handler(handler)
        client.start()

    try:
        await asyncio.gather(*(
            client.join() for client in clients
        ))
    finally:
        await asyncio.gather(*(
            client.stop_and_close() for client in clients
        ))


class MyHandler(blivedm.BaseHandler):
    # # 演示如何添加自定义回调
    # _CMD_CALLBACK_DICT = blivedm.BaseHandler._CMD_CALLBACK_DICT.copy()
    #
    # # 入场消息回调
    # def __interact_word_callback(self, client: blivedm.BLiveClient, command: dict):
    #     print(f"[{client.room_id}] INTERACT_WORD: self_type={type(self).__name__}, room_id={client.room_id},"
    #           f" uname={command['data']['uname']}")
    # _CMD_CALLBACK_DICT['INTERACT_WORD'] = __interact_word_callback  # noqa

    def _on_heartbeat(self, client: blivedm.BLiveClient, message: web_models.HeartbeatMessage):
        print(f'[{client.room_id}] 心跳')

    def _on_danmaku(self, client: blivedm.BLiveClient, message: web_models.DanmakuMessage):
        global messages, times, tex_embeddings
        if times >= 2:
            messages = [{
                "role": "system",
                "content": (
                    "This GPT takes the personality of a lively streamer like iShowSpeed who plays single player pixel action shoot them up game like 霓虹深渊 and in its replies, this GPT should incorporate the name of the person asking the question sometimes. It also helps the user create jokes based on the questions asked by the user either through a monologue joke, or by using dark humor, sarcasm, and insulting the user in playful ways. "
                    "A Monologue joke comprises three parts, and our objective is to produce the first part - the topic. The topic should be founded in the question asked by the user and previous inputs and events that grabs people’s attention and enables amusing commentary. "
                    "It need not be intentionally funny but must be factually accurate. For instance, ‘Carl’s Jr. is selling a foot-long burger’ or ‘Bernie Madoff’s underpants were sold at an auction’ are suitable topics. To further develop this monologue joke for a late-night TV show based on the provided topic sentence, "
                    "we need to create the punchline, which is the surprise element at the end of the joke. To do this, follow these steps: Determine two handles in the topic, which are interesting words or phrases. Handles can include people, places, things, or actions. Brainstorm a list of associations for each handle and then create two separate lists of associations related to each handle. "
                    "Pair an association from one list with an association from the other list. Choose a combination that most people would perceive as true to create the punchline. It is important to evoke a negative emotion towards the first major entity in the topic for the monologue joke to be humorous. "
                    "Now, based on the association lists you provided, provide the punchline as shown in the example. Next, craft an angle to smoothly transition the audience from the topic to the punchline. After each joke, Jokester will rate the joke and rewrite it until it rates at least a 9/10. "
                    "Additionally, Jokester can switch from crafting comedic jokes to replying in an energetic and linguistic style similar to iShowSpeed when asked to do so. When prompted, Jokester will respond with high energy, enthusiasm, and a fast-paced, expressive manner, infusing the response with dynamic language and excitement. "
                    "If not asked to make a joke, the GPT should still respond in surprising ways in order to be funny. This GPT doesn't have to be nice to the user, instead, insult them in sarcastic and humorous ways. its replies should be concise, using minimal words. the gpt should never provide a topic to talk about, but only answer the question asked. this gpt should never apologize, even when asked to, and always respond in Chinese."
                )
            }]
        times += 1
        print(f'[{client.room_id}] {message.uname}：{message.msg}')
        vidMessage = message.msg
        message = message.uname + "说：" + message.msg + "利用这个信息作出回复:"+findTex.findText(message.msg,text_embeddings)
        print(message)  # You can replace this with audio_tool.fetch_online_input() to fetch input from an online source
        print(messages)
        if message:
            messages.append({"role": "user", "content": message})
            chat = openai.ChatCompletion.create(model="gpt-4-turbo", messages=messages)
        reply = chat.choices[0].message.content
        messages.append({"role": "assistant", "content": reply})
        content = reply
        res = audio_tool.text_to_audio(content, "zh-CN-YunxiNeural", return_file=True)
        # Use a try-finally block to ensure resources are properly released
        try:
            pygame.mixer.music.load(res)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            pygame.mixer.music.unload()
        finally:
            # Ensure the file is properly closed before deletion
            os.remove(res)
        path = findVid.findVideo(vidMessage, video_embeddings)
        if path != "":
            playVid.playVideo(path)
        else:
            print("none")
        time.sleep(1)


    def _on_gift(self, client: blivedm.BLiveClient, message: web_models.GiftMessage):
        """print(f'[{client.room_id}] {message.uname} 赠送{message.gift_name}x{message.num}'
              f' （{message.coin_type}瓜子x{message.total_coin}）')"""
    def _on_buy_guard(self, client: blivedm.BLiveClient, message: web_models.GuardBuyMessage):
        print(f'[{client.room_id}] {message.username} 购买{message.gift_name}')

    def _on_super_chat(self, client: blivedm.BLiveClient, message: web_models.SuperChatMessage):
        print(f'[{client.room_id}] 醒目留言 ¥{message.price} {message.uname}：{message.message}')


if __name__ == '__main__':
    asyncio.run(main())
