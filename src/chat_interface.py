import streamlit as st
import asyncio
import aiohttp
from PIL import Image
import io

async def call_chat_api(question, history=None, filters=None):
    url = "http://localhost:11011/chat"
    
    payload = {
        "question": question,
        "history": history or [],
        "filters": filters,
        "strategy": "local",
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "text/event-stream"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            async for line in response.content:
                if line.startswith(b'data: '):
                    chunk = line[6:].decode('utf-8').strip()
                    if chunk.startswith('list_'):
                        chunk = chunk[5:].strip('[]').replace("'", "").split(',')
                        for item in chunk:
                            yield {"type": "image", "content": item.strip()}
                    else:
                        yield {"type": "text", "content": f"{chunk} "}

def load_image(image_path):
    try:
        return Image.open(image_path)
    except Exception as e:
        st.error(f"Error loading image: {e}")
        return None

async def process_chunks(prompt, message_placeholder):
    full_response = ""
    async for chunk in call_chat_api(prompt, st.session_state.messages):
        if chunk["type"] == "text":
            full_response += chunk["content"]
            message_placeholder.markdown(full_response + "▌")
        elif chunk["type"] == "image":
            image = load_image(chunk["content"])
            if image:
                st.image(image)
            # st.session_state.messages.append({"role": "assistant", "type": "image", "content": chunk["content"]})
    message_placeholder.markdown(full_response)
    return full_response

def main():
    st.title("LocalRecall")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    print(st.session_state.messages)

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["type"] == "text":
                st.markdown(message["content"])
            elif message["type"] == "image":
                image = load_image(message["content"])
                if image:
                    st.image(image)

    if prompt := st.chat_input("What is your question?"):
        st.session_state.messages.append({"role": "user", "type": "text", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()

            # Run the asynchronous function
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            full_response = loop.run_until_complete(process_chunks(prompt, message_placeholder))
            
        st.session_state.messages.append({"role": "assistant", "type": "text", "content": full_response})

if __name__ == "__main__":
    main()
