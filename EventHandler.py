import asyncio
import BW
import time
import sounddevice
import PromptEngine
import threading
from concurrent.futures import ThreadPoolExecutor
from TextInputApp import app

class AudioHandler(BW.TranscriptResultStreamHandler):
    text = []
    last_time = 0
    sample_count = 0
    max_sample_counter = 4

    def __init__(self, transcript_result_stream: BW.TranscriptResultStream, bedrock_wrapper):
        super().__init__(transcript_result_stream)
        self.bedrock_wrapper = bedrock_wrapper

    async def handle_transcript_event(self, transcript_event: BW.TranscriptEvent):
        results = transcript_event.transcript.results
        if not self.bedrock_wrapper.is_speaking():
            ## 如果结果list非空，则处理文本
            if results: 
                for result in results:
                    AudioHandler.sample_count = 0
                    if not result.is_partial:
                        for alt in result.alternatives: # 神秘备选结果，从测试结果看下来就是一种备选
                            print(alt.transcript, flush=True, end=' ')
                            AudioHandler.text.append(alt.transcript)
            ## 否则累加计数，超过阈值之后启动bedrock响应
            else:
                AudioHandler.sample_count += 1
                if AudioHandler.sample_count == AudioHandler.max_sample_counter:
                    if len(AudioHandler.text) != 0:    
                        input_text = ' '.join(AudioHandler.text)
                        BW.printer(f'\n[INFO] User input: {input_text}', 'info')

                        executor = ThreadPoolExecutor(max_workers=1)
                        # 将bedrock委托给线程池来处理
                        loop.run_in_executor(
                            executor,
                            self.bedrock_wrapper.invoke_bedrock,
                            input_text
                        )

                    AudioHandler.text.clear()
                    AudioHandler.sample_count = 0


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
        ## 调用transcribe进行语音识别
        stream = await BW.transcribe_streaming.start_stream_transcription( 
            language_code="zh-CN",
            media_sample_rate_hz=16000,
            media_encoding="pcm",
        )

        ## 处理语音识别的结果
        handler = AudioHandler(stream.output_stream, BW.BedrockWrapper())
        await asyncio.gather(self.write_chunks(stream), handler.handle_events()) 

class TextHandler():
    text = ['你好.']## 最基础的提示词? FirstPrePrompt

    def __init__(self,bedrock_wrapper):
        self.bedrock_wrapper = bedrock_wrapper

    async def handle_text_event(self,loop):
        if not self.bedrock_wrapper.is_speaking():

            future = asyncio.Future()
            loop.call_soon_threadsafe(run_in_main_thread,future)
            input_text = await future
            TextHandler.text.append(input_text)

            if len(TextHandler.text) != 0:
                input_text = ' '.join(TextHandler.text) ## 这里前面就可以加载提示词了
                BW.printer(f'\n[INFO] User input: {input_text}', 'info')
                executor = ThreadPoolExecutor(max_workers=1)
                # 将bedrock委托给线程池来处理
                loop.run_in_executor(
                    executor,
                    self.bedrock_wrapper.invoke_bedrock,
                    input_text
                )
                TextHandler.text = [] 

async def text2text(loop):
    handler = TextHandler(BW.BedrockWrapper())
    while True:
        if not handler.bedrock_wrapper.is_speaking():
            future = asyncio.Future()
            loop.call_soon_threadsafe(run_in_main_thread,future)
            input_text = await future
            TextHandler.text.append(input_text)

            if len(TextHandler.text) != 0:
                input_text = ' '.join(TextHandler.text) ## 这里前面就可以加载提示词了
                BW.printer(f'\n[INFO] User input: {input_text}', 'info')
                executor = ThreadPoolExecutor(max_workers=1)
                # 将bedrock委托给线程池来处理
                loop.run_in_executor(
                    executor,
                    handler.bedrock_wrapper.invoke_bedrock,
                    input_text
                )
                TextHandler.text = []         

def run_in_main_thread(future:asyncio.Future):
    result = app.get_input()  # 调用需要在主线程中执行的函数
    future.set_result(result)  # 将结果设置到 Future 对象中

def run_asyncio_loop():
    time.sleep(1)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        # loop.run_until_complete(MicStream().basic_transcribe())
        loop.run_until_complete(text2text(loop))
    except (KeyboardInterrupt, Exception) as e:
        print("RuntimeError:",e.__class__.__name__,str(e))
    loop.close()

if __name__ == "__main__":
    BW.printInfo()
    thread = threading.Thread(target=run_asyncio_loop)
    thread.start()
    app.root.mainloop()
    thread.join()

def ScriptsLoader(scripts:list): # 脚本加载器，只需要设定依次执行的脚本即可~
    for script in scripts:
        if callable(scripts):
            yield script()

def ModeSelect_Script():
    app.put_output("[Mode Select]:选择展示的模块（输入数字选择）")
    app.put_output("1. 提示词工程")
    app.put_output("2. RAG")
    app.put_output("3. 上下文记忆")
    app.put_output("4. 多模态")
    app.put_output("5. 多语言") # 主要是为了语音部分
    mode = app.get_input()
    return mode

def Mode1_PromptEngine():
    