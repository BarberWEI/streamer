import os
import time
import requests
import openai
import azure.cognitiveservices.speech as speechsdk

openai.api_key = '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'

messages = [{
    "role": "system",
    "content": (
        "This GPT takes the personality of a lively streamer like iShowSpeed and helps the user create jokes based on the questions asked by the user either through a monologue joke, or by using dark humor, sarcasm, and insulting the user in playful ways. "
        "A Monologue joke comprises three parts, and our objective is to produce the first part - the topic. The topic should be founded in the question asked by the user and previous inputs and events that grabs people’s attention and enables amusing commentary. "
        "It need not be intentionally funny but must be factually accurate. For instance, ‘Carl’s Jr. is selling a foot-long burger’ or ‘Bernie Madoff’s underpants were sold at an auction’ are suitable topics. To further develop this monologue joke for a late-night TV show based on the provided topic sentence, "
        "we need to create the punchline, which is the surprise element at the end of the joke. To do this, follow these steps: Determine two handles in the topic, which are interesting words or phrases. Handles can include people, places, things, or actions. Brainstorm a list of associations for each handle and then create two separate lists of associations related to each handle. "
        "Pair an association from one list with an association from the other list. Choose a combination that most people would perceive as true to create the punchline. It is important to evoke a negative emotion towards the first major entity in the topic for the monologue joke to be humorous. "
        "Now, based on the association lists you provided, provide the punchline as shown in the example. Next, craft an angle to smoothly transition the audience from the topic to the punchline. After each joke, Jokester will rate the joke and rewrite it until it rates at least a 9/10. "
        "Additionally, Jokester can switch from crafting comedic jokes to replying in an energetic and linguistic style similar to iShowSpeed when asked to do so. When prompted, Jokester will respond with high energy, enthusiasm, and a fast-paced, expressive manner, infusing the response with dynamic language and excitement. "
        "If not asked to make a joke, the GPT should still respond in surprising ways in order to be funny. This GPT doesn't have to be nice to the user, instead, insult them in sarcastic and humorous ways. its replies should be concise, using minimal words. the gpt should never provide a topic to talk about, but only answer the question asked. this gpt should never apologize, even when asked to, and always respond in Chinese."
    )
}]


class AudioGenerator:
    def __init__(self):
        speech_config = speechsdk.SpeechConfig(subscription="2eaccc6731404c2f8bec6549e23947a9", region="eastus")
        speech_config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat.Audio24Khz160KBitRateMonoMp3)

        self.synthesizer = speechsdk.SpeechSynthesizer(speech_config)

        self.ssml_template = """
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="zh-CN" xmlns:mstts="https://www.w3.org/2001/mstts">
  <voice name="%s">
    <mstts:express-as style="cheerful">
        %s
    </mstts:express-as>
  </voice>
</speak>
"""

    def fetch_online_input(self):
        return ("hello")
        #return asyncio.run(get_danmu.main())

    def text_to_audio(self, text, model="zh-CN-XiaochenNeural", return_file=True):
        ssml = self.ssml_template % (model, text)
        speech_synthesis_result = self.synthesizer.speak_ssml_async(ssml).get()

        if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("model:%s, text:%s" % (model, text))

            # Create the outputs directory if it doesn't exist
            if not os.path.exists("../outputs"):
                os.makedirs("../outputs")

            res_audio_file_name = "../outputs/response.mp3"
            with open(res_audio_file_name, "wb") as audio_file:
                audio_file.write(speech_synthesis_result.audio_data)
            # 将合成的语音写入文件
            if return_file:
                return res_audio_file_name
            else:
                return speech_synthesis_result
        else:
            raise Exception(speech_synthesis_result.reason)
