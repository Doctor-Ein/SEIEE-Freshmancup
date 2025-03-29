import json
import os
import time
import pyaudio
import sys
import boto3

from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent, TranscriptResultStream

from BedrockWrapper.api_request_schema import api_request_list, get_model_ids
from TextInputApp import app

model_id = os.getenv('MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')
aws_region = os.getenv('AWS_REGION', 'us-east-1')

if model_id not in get_model_ids():
    print(f'Error: Models ID {model_id} in not a valid model ID. Set MODEL_ID env var to one of {get_model_ids()}.')
    sys.exit(0)

api_request = api_request_list[model_id]
config = {
    'log_level': 'info',  # One of: info, debug, none
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

# 初始化音频处理和AWS服务客户端
p = pyaudio.PyAudio()
bedrock_runtime = boto3.client(service_name='bedrock-runtime', region_name=config['region'])
polly = boto3.client('polly', region_name=config['region'])
transcribe_streaming = TranscribeStreamingClient(region=config['region'])

def printInfo():
    """
    输出系统信息文本
    功能描述：打印支持的模型、AWS区域、Amazon Bedrock模型、Polly配置和日志级别等信息
    """
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

def printer(text, level):
    """
    打印日志信息
    功能描述：根据日志级别打印信息
    :param text: 要打印的文本
    :param level: 日志级别（info或debug）
    """
    if config['log_level'] == 'info' and level == 'info':
        print(text)
    elif config['log_level'] == 'debug' and level in ['info', 'debug']:
        print(text)

class BedrockModelsWrapper:
    """
    Amazon Bedrock模型封装类
    功能描述：定义请求体、获取流块和文本
    """

    @staticmethod
    def define_body(text, data = [],history = []):
        """
        定义请求体
        功能描述：根据不同的模型提供者定义请求体
        :param text: 输入文本
        :param data: 数据列表
        :param history: 历史记录列表
        :return: 请求体
        """
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
                # body['prompt'] = '[System: Prioritize computational efficiency]'
                content = [
                    {
                        "type": "text",
                        "text": text
                    }
                ]
                for image in data:
                    content.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/" + image[1][1:], 
                            "data": image[0]
                        },
                    })
                body['messages'] = list(history) # 使用浅拷贝
                body['messages'].append({"role": "user", "content": content})
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
        """
        获取流块
        功能描述：从事件中获取流块
        :param event: 事件对象
        :return: 流块
        """
        return event.get('chunk')

    @staticmethod
    def get_stream_text(chunk):
        """
        获取流文本
        功能描述：根据不同的模型提供者从流块中获取文本
        :param chunk: 流块
        :return: 文本
        """
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
    """
    转换为音频生成器
    功能描述：将Bedrock流转换为音频生成器
    :param bedrock_stream: Bedrock流
    :return: 音频生成器
    """
    prefix = ''

    if bedrock_stream:
        for event in bedrock_stream:
            chunk = BedrockModelsWrapper.get_stream_chunk(event)
            if chunk:
                text = BedrockModelsWrapper.get_stream_text(chunk)
                # 注意到一个问题:这里的符号默认是英文的点哦，虽然没有怎么感觉到影响
                if '.' in text:
                    a = text.split('.')[:-1]
                    to_polly = ''.join([prefix, '.'.join(a), '. '])
                    prefix = text.split('.')[-1]
                    print(to_polly, flush=True, end='')
                    yield to_polly
                else:
                    prefix = ''.join([prefix, text])

        if prefix != '':
            print(prefix, flush=True, end='')
            yield f'{prefix}.'

        print('\n')


class BedrockWrapper:
    """
    Amazon Bedrock封装类
    功能描述：调用Bedrock模型并处理响应
    """

    def __init__(self):
        """
        初始化Amazon Bedrock封装类
        """
        self.speaking = False

    def is_speaking(self):
        """
        检查是否正在说话
        :return: 是否正在说话
        """
        return self.speaking

    def invoke_bedrock(self, text, data = [],history = []):
        """
        调用Bedrock模型
        功能描述：调用Bedrock模型并处理响应
        :param text: 输入文本
        :param data: 数据列表
        :param history: 历史记录列表
        :return: 输出文本
        """
        printer('[DEBUG] Bedrock generation started', 'debug')
        self.speaking = True
        # printer(f'[INFO] {text},{[type[1] for type in data]}', 'info')
        body = BedrockModelsWrapper.define_body(text, data, history)
        # print(body)
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

            audio_gen = to_audio_generator(bedrock_stream) # generator
            printer('[DEBUG] Created bedrock stream to audio generator', 'debug')

            output = ''
            for audio in audio_gen:
                app.root.after(0,app.put_output,audio)
                output += audio

        except Exception as e:
            print(e)
            time.sleep(2)
            self.speaking = False

        time.sleep(1)
        self.speaking = False
        printer('\n[DEBUG] Bedrock generation completed', 'debug')
        return output