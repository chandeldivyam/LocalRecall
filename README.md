# LocalRecall

LocalRecall is a powerful, privacy-focused tool that enhances data processing and recall capabilities using local machine learning models. Inspired by Microsoft's Project Recall, this local spinoff leverages BYOM to provide flexible and secure data analysis. [Also, it support gemini for those who doesn't have enought VRAM]

## Key Features:

- **Data Privacy**: All image data is encrypted at rest, ensuring your information remains secure.
- **Flexible Model Options**: Choose between Google's Gemini or local models for processing.
- **Open Source**: Built with FastAPI and Ollama, LocalRecall is open for contributions and improvements.

**Note**: This is the first version of LocalRecall and may contain fundamental issues. We welcome contributions from the community to help improve and expand its capabilities.

## Prerequisites

Before you begin the setup, ensure you have the following installed on your Windows machine:

- Docker
- Ollama
- Conda
- Python 3.10

## Installation

### Step 1: Clone the Repository

Start by cloning the LocalRecall repository from GitHub:
```bash
git clone https://github.com/chandeldivyam/LocalRecall
```

### Step 2: Run the Florence-2 FastAPI Server

> **Note** You can skip the Step 2 and Step 3 if you want to use Gemini 

Navigate to the project directory and execute the following script to start the Florence-2 server. Note that it may take a few minutes for the server to become fully operational as it downloads the required model from Hugging Face.

```bash
./run_florence.sh
```

### Step 3: Launch Ollama
Ensure the Ollama server is running on the default port (11434) and has the `llama3` and `mxbai-embed-large` models loaded.

To check if the models are running properly, use the following:

```curl
curl --location 'http://localhost:11434/api/generate' \
--header 'Content-Type: application/json' \
--data '{
    "model": "llama3",
    "prompt": "What is the date today, can you give me python code for it?",
    "stream": false
}'
```
```curl
curl --location 'http://localhost:11434/api/embeddings' \
--header 'Content-Type: application/json' \
--data '{
  "model": "mxbai-embed-large",
  "prompt": "Hi, I hope you are doing well"
}'
```

### Step 4: Set Up the Conda Environment

Create and activate a new Conda environment, then install the necessary Python packages:

```bash
conda create --name localrecall python=3.10
conda activate localrecall
python -m pip install -r requirements.txt
```

### Step 5: Configure Environment Variables

Copy the `.env.example` file to `.env` and update it with your specific configurations:
```bash
cp .env.example .env
```

### Step 6: Run the Application

With the servers running and the environment set up, you can now launch the LocalRecall application with the following command:

```bash
python -m src.localrecall.main --process --track --api --vision-strategy local
```

For additional functionality such as image compression, you can use the following command:
```bash
python -m src.localrecall.main --process --track --compress --api --compress-quality 50 --resize-factor 0.5  --vision-strategy local
```

### Step 7: Run the Application

We can finally run the streamlit server, make sure to change the strategy accordingly for whatever you are using in `/src/chat_interface.py` either as `local` or `google_gemini` accordingly.

To run the streamlit frontend, use
```bash
python -m streamlit run src/chat_interface.py
```

## Usage

For more details on how to use different commands and modify parameters, please refer to the documentation in the `src/localrecall/main.py` file.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
