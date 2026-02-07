from __future__ import annotations

from typing import Any, Optional

import torch
from transformers import AutoModelForVision2Seq, AutoProcessor

try:
    from qwen_vl_utils import process_vision_info
except Exception:  # pragma: no cover - optional dependency
    process_vision_info = None


class QwenVL:
    def __init__(
        self,
        model_name: str,
        device: Optional[str] = None,
        max_new_tokens: int = 512,
    ) -> None:
        if process_vision_info is None:
            raise RuntimeError(
                "qwen-vl-utils is required. Install with: pip install -r requirements-ml.txt"
            )

        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.max_new_tokens = max_new_tokens

        self.processor = AutoProcessor.from_pretrained(model_name, trust_remote_code=True)
        self.model = AutoModelForVision2Seq.from_pretrained(
            model_name, trust_remote_code=True, device_map="auto"
        )

    def generate(self, prompt: str, image_path: str) -> str:
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image", "image": image_path},
                ],
            }
        ]
        text = self.processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        image_inputs, video_inputs = process_vision_info(messages)
        inputs = self.processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            return_tensors="pt",
        )
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
        with torch.no_grad():
            output_ids = self.model.generate(**inputs, max_new_tokens=self.max_new_tokens)
        output = self.processor.batch_decode(output_ids, skip_special_tokens=True)[0]
        return output
