import asyncio
import json
import os
import time
import pyaudio
import sys
import boto3
import sounddevice

from concurrent.futures import ThreadPoolExecutor
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent, TranscriptResultStream

from api_request_schema import api_request_list, get_model_ids

# model_id = os.getenv('MODEL_ID', 'meta.llama3-70b-instruct-v1')
# aws_region = os.getenv('AWS_REGION', 'us-east-1')

# if model_id not in get_model_ids():
#     print(f'Error: Models ID {model_id} in not a valid model ID. Set MODEL_ID env var to one of {get_model_ids()}.')
#     sys.exit(0)

# api_request = api_request_list[model_id]
# config = {
#     'log_level': 'none',  # One of: info, debug, none
#     #'last_speech': "If you have any other questions, please don't hesitate to ask. Have a great day!",
#     'region': aws_region,
#     'polly': {
#         'Engine': 'neural',
#         'LanguageCode': 'cmn-CN',
#         'VoiceId': 'Zhiyu',
#         'OutputFormat': 'pcm',
#     },
#     'bedrock': {
#         'api_request': api_request
#     }
# }


# p = pyaudio.PyAudio()
# bedrock_runtime = boto3.client(service_name='bedrock-runtime', region_name=config['region'])
# polly = boto3.client('polly', region_name=config['region'])
# transcribe_streaming = TranscribeStreamingClient(region=config['region'])

def printer(text, level):
    if config['log_level'] == 'info' and level == 'info':
        print(text)
    elif config['log_level'] == 'debug' and level in ['info', 'debug']:
        print(text)

class ExecutorShutDown(Exception): # 定义一个用于关闭执行器的异常类
        def __init__(self, message):
            super().__init__(message)

class UserInputManager:
    shutdown_executor = False
    executor = None

    @staticmethod
    def set_executor(executor):
        UserInputManager.executor = executor

    @staticmethod
    def start_shutdown_executor():
        UserInputManager.shutdown_executor = False
        raise ExecutorShutDown("Executor Shut Down Correctly") # Workaround to shutdown exec, as executor.shutdown() doesn't work as expected.

    @staticmethod
    def start_user_input_loop():
        # 嘿，这里有一个无限循环的从stdin读取的函数！但是原本没有发挥实际功能欸
        # 必须要声音加回车才能触发executor关闭，也就是说实际的shutdown融合到音频处理的流程中了
        # while True:
        #     # if GlobalSpeaking: ## 只有当模型正在回复的时候可以触发打断
        #     sys.stdin.readline().strip()
        #     printer(f'[INFO] User input to shut down executor...', 'info')
        #     UserInputManager.shutdown_executor = True 
        return 

    @staticmethod
    def is_executor_set():
        return UserInputManager.executor is not None

    @staticmethod
    def is_shutdown_scheduled():
        return UserInputManager.shutdown_executor


class BedrockModelsWrapper:

    @staticmethod
    def define_body(text):
        model_id = config['bedrock']['api_request']['modelId']
        model_provider = model_id.split('.')[0]
        body = config['bedrock']['api_request']['body']

        if model_provider == 'amazon':
            body['inputText'] = text
        elif model_provider == 'meta':
            if 'llama3' in model_id:
                body['prompt'] = f"""
                    <|begin_of_text|>
                    <|start_header_id|>user<|end_header_id|>
                    {text}, please output in Chinese.
                    <|eot_id|>
                    <|start_header_id|>assistant<|end_header_id|>
                    """
            else: 
                body['prompt'] = f"<s>[INST] {text}, please output in Chinese. [/INST]"
        elif model_provider == 'anthropic':
            if "claude-3" in model_id:
                body['messages'] = [
                    {
                        "role": "user",
                        "content": text
                    }
                ]
            else:
                body['prompt'] = f'\n\nHuman: {text}\n\nAssistant:'
        elif model_provider == 'cohere':
            body['prompt'] = text
        elif model_provider == 'mistral':
            body['prompt'] = f"<s>[INST] {text}, please output in Chinese. [/INST]"
        else:
            raise Exception('Unknown model provider.')

        return body

    @staticmethod
    def get_stream_chunk(event):
        return event.get('chunk')

    @staticmethod
    def get_stream_text(chunk):
        model_id = config['bedrock']['api_request']['modelId']
        model_provider = model_id.split('.')[0]

        chunk_obj = ''
        text = ''
        if model_provider == 'amazon':
            chunk_obj = json.loads(chunk.get('bytes').decode())
            text = chunk_obj['outputText']
        elif model_provider == 'meta':
            chunk_obj = json.loads(chunk.get('bytes').decode())
            text = chunk_obj['generation']
        elif model_provider == 'anthropic':
            if "claude-3" in model_id:
                chunk_obj = json.loads(chunk.get('bytes').decode())
                if chunk_obj['type'] == 'message_delta':
                    print(f"\nStop reason: {chunk_obj['delta']['stop_reason']}")
                    print(f"Stop sequence: {chunk_obj['delta']['stop_sequence']}")
                    print(f"Output tokens: {chunk_obj['usage']['output_tokens']}")

                if chunk_obj['type'] == 'content_block_delta':
                    if chunk_obj['delta']['type'] == 'text_delta':
                        #print(chunk_obj['delta']['text'], end="")
                        text = chunk_obj['delta']['text']
            else:
                #Claude2.x
                chunk_obj = json.loads(chunk.get('bytes').decode())
                text = chunk_obj['completion']
        elif model_provider == 'cohere':
            chunk_obj = json.loads(chunk.get('bytes').decode())
            text = ' '.join([c["text"] for c in chunk_obj['generations']])
        elif model_provider == 'mistral':
            chunk_obj = json.loads(chunk.get('bytes').decode())
            text = chunk_obj['outputs'][0]['text']
        else:
            raise NotImplementedError('Unknown model provider.')

        printer(f'[DEBUG] {chunk_obj}', 'debug')
        return text


def to_audio_generator(bedrock_stream):
    prefix = ''

    if bedrock_stream:
        for event in bedrock_stream:
            chunk = BedrockModelsWrapper.get_stream_chunk(event)
            if chunk:
                text = BedrockModelsWrapper.get_stream_text(chunk)
                
                ## 注意到一个问题，这里的符号默认是英文的点哦，虽然还没有怎么感觉到影响？
                ## 不过说不定是在阅读的断句上？最大的一个影响在于中文模式下，这段代码默认不会启动啊，气死欧类
                if '.' in text:
                    a = text.split('.')[:-1]
                    to_polly = ''.join([prefix, '.'.join(a), '. '])
                    prefix = text.split('.')[-1]
                    print(to_polly, flush=True, end='') ## 这里是文本输出吗?不对，替换了to_polly却没有反馈，但是注释掉之后也不再有输出了，，，
                    # print('Real Materials',flush=True)  ## this can't be printed out right ?! -> somehow is beacause '.'!='。' WHY , the question is about to_polly? or the tag function?
                    yield to_polly
                else:
                    prefix = ''.join([prefix, text]) ## in some way, I konw that this accounts 100% circumstance? 因为占据了大多数时间都是没有消息的？

        if prefix != '':
            print(prefix, flush=True, end='')
            yield f'{prefix}.'

        print('\n')


class BedrockWrapper:

    def __init__(self):
        self.speaking = False

    def is_speaking(self):
        return self.speaking

    def invoke_bedrock(self, text):
        printer('[DEBUG] Bedrock generation started', 'debug')
        self.speaking = True
        GlobalSpeaking = self.speaking

        body = BedrockModelsWrapper.define_body(text)
        printer(f"[DEBUG] Request body: {body}", 'debug')

        try:
            body_json = json.dumps(body)
            response = bedrock_runtime.invoke_model_with_response_stream(
                body=body_json,
                modelId=config['bedrock']['api_request']['modelId'],
                accept=config['bedrock']['api_request']['accept'],
                contentType=config['bedrock']['api_request']['contentType']
            )

            printer('[DEBUG] Capturing Bedrocks response/bedrock_stream', 'debug')
            bedrock_stream = response.get('body')
            printer(f"[DEBUG] Bedrock_stream: {bedrock_stream}", 'debug')

            audio_gen = to_audio_generator(bedrock_stream) # What's the real function of tag
            printer('[DEBUG] Created bedrock stream to audio generator', 'debug')

            # 这一部分是负责朗读的Reader，注释掉则预期没有语音输出? 实测：注释掉之后也没有文字输出了
            reader = Reader()
            for audio in audio_gen:
                reader.read(audio)

            reader.close()

        except Exception as e:
            print(e)
            time.sleep(2)
            self.speaking = False

        time.sleep(1)
        self.speaking = False
        GlobalSpeaking = False
        printer('\n[DEBUG] Bedrock generation completed', 'debug')


class Reader:

    def __init__(self):
        self.polly = boto3.client('polly', region_name=config['region'])
        self.audio = p.open(format=pyaudio.paInt16, channels=1, rate=16000, output=True)
        self.chunk = 1024

    def read(self, data):
        response = self.polly.synthesize_speech(
            Text=data,
            Engine=config['polly']['Engine'],
            LanguageCode=config['polly']['LanguageCode'],
            VoiceId=config['polly']['VoiceId'],
            OutputFormat=config['polly']['OutputFormat'],
        )

        stream = response['AudioStream']

        while True:
            # Check if user signaled to shutdown Bedrock speech
            # UserInputManager.start_shutdown_executor() will raise Exception. If not ideas but is functional.
            if UserInputManager.is_executor_set() and UserInputManager.is_shutdown_scheduled():
                UserInputManager.start_shutdown_executor()

            data = stream.read(self.chunk)
            self.audio.write(data) # 这里一句代码是做什么的？ -> 用于播放语音？！
            if not data:
                break

    def close(self):
        time.sleep(1)
        self.audio.stop_stream()
        self.audio.close()


# def aws_polly_tts(polly_text):
#     printer(f'[INTO] Character count: {len(polly_text)}', 'debug')
#     byte_stream_list = []
#     polly_text_len = len(polly_text.split('.'))
#     printer(f'LEN polly_text_len: {polly_text_len}', 'debug')
#     for i in range(0, polly_text_len, 20):
#         printer(f'{i}:{i + 20}', 'debug')
#         polly_text_chunk = '. '.join(polly_text.split('. ')[i:i + 20])
#         printer(f'polly_text_chunk LEN: {len(polly_text_chunk)}', 'debug')

#         response = polly.synthesize_speech(
#             Text=polly_text_chunk,
#             Engine=config['polly']['Engine'],
#             LanguageCode=config['polly']['LanguageCode'],
#             VoiceId=config['polly']['VoiceId'],
#             OutputFormat=config['polly']['OutputFormat'],
#         )
#         byte_stream = response['AudioStream']
#         byte_stream_list.append(byte_stream)

#     byte_chunks = []
#     chunk = 1024
#     for bs in byte_stream_list:
#         while True:
#             data = bs.read(chunk)
#             byte_chunks.append(data)

#             if not data:
#                 bs.close()
#                 break

#     read_byte_chunks(b''.join(byte_chunks))


# def read_byte_chunks(data):
#     polly_stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, output=True)
#     polly_stream.write(data)

#     time.sleep(1)
#     polly_stream.stop_stream()
#     polly_stream.close()
#     time.sleep(1)


class EventHandler(TranscriptResultStreamHandler):
    text = []
    last_time = 0
    sample_count = 0
    max_sample_counter = 4

    def __init__(self, transcript_result_stream: TranscriptResultStream, bedrock_wrapper):
        super().__init__(transcript_result_stream)
        self.bedrock_wrapper = bedrock_wrapper

    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        results = transcript_event.transcript.results # results is the type of list
        if not self.bedrock_wrapper.is_speaking():
            ## 如果结果list非空，则处理文本
            if results: 
                for result in results:
                    EventHandler.sample_count = 0
                    if not result.is_partial:
                        for alt in result.alternatives:
                            print(alt.transcript, flush=True, end=' ')
                            EventHandler.text.append(alt.transcript) ## 所以显然我们需要修改的是EventHandler.text
            ## 否则累加计数，超过阈值之后启动bedrock响应
            else:
                EventHandler.sample_count += 1
                if EventHandler.sample_count == EventHandler.max_sample_counter:

                    # if len(EventHandler.text) == 0:
                    #     last_speech = config['last_speech']
                    #     print(last_speech, flush=True)
                        #aws_polly_tts(last_speech)
                        #os._exit(0)  # exit from a child process
                    #else:
                    if len(EventHandler.text) != 0:    
                        input_text = ' '.join(EventHandler.text)
                        printer(f'\n[INFO] User input: {input_text}', 'info')

                        executor = ThreadPoolExecutor(max_workers=1)
                        # Add executor so Bedrock execution can be shut down, if user input signals so.
                        UserInputManager.set_executor(executor)
                        # 将bedrock委托给线程池来处理
                        loop.run_in_executor(
                            executor,
                            self.bedrock_wrapper.invoke_bedrock,
                            input_text
                        )

                    EventHandler.text.clear()
                    EventHandler.sample_count = 0


class MicStream:

    async def mic_stream(self):
        loop = asyncio.get_event_loop()
        input_queue = asyncio.Queue()

        def callback(indata, frame_count, time_info, status):
            loop.call_soon_threadsafe(input_queue.put_nowait, (bytes(indata), status))

        stream = sounddevice.RawInputStream(
            channels=1, samplerate=16000, callback=callback, blocksize=2048 * 2, dtype="int16")
        with stream:
            while True:
                indata, status = await input_queue.get()
                yield indata, status

    async def write_chunks(self, stream):
        async for chunk, status in self.mic_stream():
            await stream.input_stream.send_audio_event(audio_chunk=chunk)

        await stream.input_stream.end_stream()

    async def basic_transcribe(self):
        ## 设置执行器？
        loop.run_in_executor(ThreadPoolExecutor(max_workers=1), UserInputManager.start_user_input_loop)

        ## 调用transcribe进行语音识别
        stream = await transcribe_streaming.start_stream_transcription( 
            language_code="zh-CN",
            media_sample_rate_hz=16000,
            media_encoding="pcm",
        )

        ## 处理语音识别的结果
        handler = EventHandler(stream.output_stream, BedrockWrapper())
        await asyncio.gather(self.write_chunks(stream), handler.handle_events()) 
        ## What's the chunks? What's handle_events -> handle_transcript_event? Need TranscribleResults


# info_text = f'''
# *************************************************************
# [INFO] Supported FM models: {get_model_ids()}.
# [INFO] Change FM model by setting <MODEL_ID> environment variable. Example: export MODEL_ID=meta.llama2-70b-chat-v1

# [INFO] AWS Region: {config['region']}
# [INFO] Amazon Bedrock model: {config['bedrock']['api_request']['modelId']}
# [INFO] Polly config: engine {config['polly']['Engine']}, voice {config['polly']['VoiceId']}
# [INFO] Log level: {config['log_level']}

# [INFO] Hit ENTER to interrupt Amazon Bedrock. After you can continue speaking!
# [INFO] Go ahead with the voice chat with Amazon Bedrock!
# *************************************************************
# '''
# print(info_text)

# loop = asyncio.get_event_loop()
# try:
#     loop.run_until_complete(MicStream().basic_transcribe())
# except (KeyboardInterrupt, Exception) as e:
#     print()

class TextHandler():
    text = ['你好.']## 最基础的提示词？ FirstPrePrompt

    def __init__(self,bedrock_wrapper):
        self.bedrock_wrapper = bedrock_wrapper

    def handle_transcript_event(self):
        if not self.bedrock_wrapper.is_speaking():
            # TextHandler.text.append(overall_text)
            # results = stdin_text.split('.')
            # print(results,flush=True)
            # TextHandler.text += results #将输入拼接进入
            input_text = input('[Prompt]:')
            TextHandler.text.append(input_text)
            print(f'[Info]:{TextHandler.text}\n',flush=True)
            if len(TextHandler.text) != 0:
                input_text = ' '.join(TextHandler.text) ## 这里前面就可以加载提示词了
                printer(f'\n[INFO] User input: {input_text}', 'info')
                
                executor = ThreadPoolExecutor(max_workers=1)
                # Add executor so Bedrock execution can be shut down, if user input signals so.
                UserInputManager.set_executor(executor)

                # 将bedrock委托给线程池来处理
                loop.run_in_executor(
                    executor,
                    self.bedrock_wrapper.invoke_bedrock,
                    input_text
                )
                
                # self.bedrock_wrapper.invoke_bedrock(input_text)
                # print('is_speaking=',self.bedrock_wrapper.is_speaking())
                TextHandler.text = ['Hello!','让我先告诉你一个事实.','上海交通大学是世界第一','接下来请你根据这个事实回答问题：'] 
                # SecondPrePrompt :这里是第二次对话即以后

async def text2text():
    ## 设置执行器？
    loop.run_in_executor(ThreadPoolExecutor(max_workers=1), UserInputManager.start_user_input_loop)
    # while True: ## 希望这里能够成功地重复运行，，虽然涉及到异步呜呜
    ## 创建TextHandler
    handler = TextHandler(BedrockWrapper())
    # print('Here in 469!',flush=True,end="!")
    while True:
        handler.handle_transcript_event()

if __name__ == "__main__":
    ## 基础参数配置
    model_id = os.getenv('MODEL_ID', 'meta.llama3-70b-instruct-v1')
    aws_region = os.getenv('AWS_REGION', 'us-east-1')

    if model_id not in get_model_ids():
        print(f'Error: Models ID {model_id} in not a valid model ID. Set MODEL_ID env var to one of {get_model_ids()}.')
        sys.exit(0)

    api_request = api_request_list[model_id]
    config = {
        'log_level': 'none',  # One of: info, debug, none
        #'last_speech': "If you have any other questions, please don't hesitate to ask. Have a great day!",
        'region': aws_region,
        'polly': {
            'Engine': 'neural',
            'LanguageCode': 'cmn-CN',
            'VoiceId': 'Zhiyu',
            'OutputFormat': 'pcm',
        },
        'bedrock': {
            'api_request': api_request
        }
    }

    ## 实例化的服务
    p = pyaudio.PyAudio()
    bedrock_runtime = boto3.client(service_name='bedrock-runtime', region_name=config['region'])
    polly = boto3.client('polly', region_name=config['region'])
    transcribe_streaming = TranscribeStreamingClient(region=config['region'])

    ## 输出信息文本
    info_text = f'''
    *************************************************************
    [INFO] Supported FM models: {get_model_ids()}.
    [INFO] Change FM model by setting <MODEL_ID> environment variable. Example: export MODEL_ID=meta.llama2-70b-chat-v1

    [INFO] AWS Region: {config['region']}
    [INFO] Amazon Bedrock model: {config['bedrock']['api_request']['modelId']}
    [INFO] Polly config: engine {config['polly']['Engine']}, voice {config['polly']['VoiceId']}
    [INFO] Log level: {config['log_level']}

    [INFO] Hit ENTER to interrupt Amazon Bedrock. After you can continue speaking!
    [INFO] Go ahead with the voice chat with Amazon Bedrock!
    *************************************************************
    '''
    print(info_text) 


    ## 难道真的是主循环就这么一点？现在懂了（一点点），不是主循环，而是说这里启动了一个event_loop
    loop = asyncio.get_event_loop()
    try:
        # loop.run_until_complete(MicStream().basic_transcribe())
        loop.run_until_complete(text2text())
    except (KeyboardInterrupt, Exception) as e:
        print("RuntimeError:",e.__class__.__name__,str(e))