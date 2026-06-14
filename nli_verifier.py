import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_NAME = "facebook/bart-large-mnli"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME).to(device)
model.eval()

LABELS = ["contradiction", "neutral", "entailment"]

def nli_classify(premise, hypothesis):
    inputs = tokenizer(
        premise, hypothesis,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=512
    ).to(device)

    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.softmax(outputs.logits, dim=1)[0]

    return {"scores": {LABELS[i]: probs[i].item() for i in range(3)}}
