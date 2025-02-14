import os, sys
from transformers import DistilBertForSequenceClassification, DistilBertTokenizer
import torch
import onnx

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.utils.get_config import get_config

CONFIG_FILE = "./config/bert_config.yml"

model_path = get_config(CONFIG_FILE, "SAVE_MODEL")
onnx_path = get_config(CONFIG_FILE, "ONNX_MODEL")

# Load fine-tuned model
model = DistilBertForSequenceClassification.from_pretrained(model_path)
tokenizer = DistilBertTokenizer.from_pretrained(model_path)

# Dummy input for ONNX export
dummy_input = torch.randint(0, 30522, (1, 512))

# Export to ONNX format
torch.onnx.export(
    model,
    dummy_input,
    onnx_path,
    input_names=["input_ids"],
    output_names=["logits"],
    dynamic_axes={"input_ids": {0: "batch_size"}},  # Allow dynamic batching
)