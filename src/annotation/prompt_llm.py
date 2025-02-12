import os, sys
from dotenv import load_dotenv
import google.generativeai as genai
from typing import Dict, Tuple
import yaml
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.utils.logger import get_logger
from src.exceptions.ResponseFormatException import ResponseFormatException

class PromptLLM:
    LLM_CONFIG_FILE = "./config/llm_config.yml"
    ENV_FILE = "./config/.env"
    PROMPT_FILES_DIR = "./src/annotation/resources/"

    def __init__(self):
        self.logger = get_logger(__name__)

    def load_api(self) -> str:
        try:
            load_dotenv(PromptLLM.ENV_FILE)
            API_KEY = os.getenv("LLM_API_KEY")
            return API_KEY
        except Exception as e:
            self.logger.error(f"Problem occured while reading from {PromptLLM.ENV_FILE} file: {e}")

    def load_config(self) -> Dict:
        if not os.path.exists(PromptLLM.LLM_CONFIG_FILE):
            raise FileNotFoundError(f"Prompt file not found at {PromptLLM.LLM_CONFIG_FILE}")
        try:
            with open(PromptLLM.LLM_CONFIG_FILE, 'r') as file:
                config = yaml.safe_load(file)
            return config
        except Exception as e:
            self.logger.error(f"Problem while reading the config file {PromptLLM.LLM_CONFIG_FILE}: {e}")

    def load_prompt(self, is_post: bool) -> str:
        PROMPT_FILE = PromptLLM.PROMPT_FILES_DIR + (int(is_post)) * "base_post_prompt.txt" + (1-int(is_post)) * "base_comment_prompt.txt"
        if not os.path.exists(PROMPT_FILE):
            raise FileNotFoundError(f"Prompt file not found at {PROMPT_FILE}")
        try:
            with open(PROMPT_FILE, 'r') as file:
                return file.read()
        except Exception as e:
            self.logger.error(f"Problem occured while reading the prompt file {PROMPT_FILE}: {e}")

    @staticmethod
    def process_text(text) -> Dict:
        start_idx, end_idx = None, None
        for idx in range(len(text)):
            if start_idx is not None and end_idx is not None:
                break

            if text[idx] == '{' and start_idx is None:
                start_idx = idx
            if text[len(text)-1-idx] == '}' and end_idx is None:
                end_idx = len(text) - idx - 1

        if start_idx is not None and end_idx is not None:
            try:
                data = json.loads(text[start_idx: end_idx+1])
                return data     # Dictionnary
            except Exception as e:
                raise ValueError(f"Problem occurred while transforming the text into a dictionary: {e}")
        else:
            raise ResponseFormatException("Invalid curly brackets found in the text.")

    def annotate_post(self, post_text: str) -> Dict:
        input_text = f"Text to Analyze:\n{post_text}"
        try:
            genai.configure(api_key=self.load_api())
            model = genai.GenerativeModel(self.load_config()["model"])
            prompt = self.load_prompt(is_post=True) + input_text
            response = model.generate_content(prompt)
            
            data = PromptLLM.process_text(response.text)
            annotated_data = {
                "text": post_text,
                "classification": data["classification"],
                "confidence": data["confidence"]
            }
            return annotated_data
        except Exception as e:
            self.logger.error(f"Problem occured while prompting the LLM: {e}")

    def annotate_comment(self, post_text: str, comment_text) -> Dict:
        input_text = f"Post Text:\n{post_text}\n\nComment Text:\n{comment_text}"
        try:
            genai.configure(api_key=self.load_api())
            model = genai.GenerativeModel(self.load_config()["model"])
            prompt = self.load_prompt(is_post=False) + input_text
            response = model.generate_content(prompt)
            
            data = PromptLLM.process_text(response.text)
            annotated_data = {
                "text": comment_text,
                "classification": data["classification"],
                "confidence": data["confidence"]
            }
            return annotated_data
        except Exception as e:
            self.logger.error(f"Problem occured while prompting the LLM: {e}")