import os, sys
from fastapi import FastAPI
from transformers import DistilBertTokenizer
import uvicorn
from pydantic import BaseModel
import numpy as np
import onnxruntime as ort

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.utils.get_config import get_config

CONFIG_FILE = "./config/bert_config.yml"

model_path = get_config(CONFIG_FILE, "SAVE_MODEL")
onnx_path = get_config(CONFIG_FILE, "ONNX_MODEL")

tokenizer = DistilBertTokenizer.from_pretrained(model_path)
ort_session = ort.InferenceSession(onnx_path)

app = FastAPI()

class TextInput(BaseModel):
    text: str

@app.get("/")
def main():
    return {"health_check": "OK"}

@app.post("/predict/")
def predict(data: TextInput):
    metadata_prediction = {0: "neutral", 1: "hope", 2: "fear"}

    text = data.text
    inputs = tokenizer(text, return_tensors="np", padding="max_length", truncation=True, max_length=512)
    input_ids = inputs["input_ids"].astype(np.int64)  # Convert to NumPy array

    # Run inference with ONNX
    outputs = ort_session.run(None, {"input_ids": input_ids})
    predictions = np.argmax(outputs[0], axis=1).item()

    return {"text": text, "prediction": metadata_prediction[predictions]}

if __name__ == "__main__":
    uvicorn.run(app, host='127.0.0.1', port=8000)