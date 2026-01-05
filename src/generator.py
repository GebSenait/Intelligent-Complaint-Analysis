"""
Generator Module

Generates answers using LLM with retrieved context.
"""

from typing import Optional, Dict, Any
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch

from .prompt_template import PromptTemplate


class Generator:
    """Generates answers using LLM with RAG context."""
    
    def __init__(
        self, 
        model_name: str = "gpt2",
        use_local: bool = True,
        device: Optional[str] = None
    ):
        """
        Initialize the generator with an LLM.
        
        Args:
            model_name: HuggingFace model name or path
            use_local: Whether to use local model (True) or API (False)
            device: Device to use ('cuda', 'cpu', or None for auto)
        """
        self.model_name = model_name
        self.use_local = use_local
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        
        if use_local:
            self._load_local_model()
        else:
            # For API-based models (OpenAI, etc.) - implement as needed
            raise NotImplementedError("API-based models not implemented yet")
    
    def _load_local_model(self):
        """Load the local LLM model."""
        print(f"Loading generator model: {self.model_name} on {self.device}...")
        
        try:
            # Use a lightweight instruction-following model
            # For production, consider: microsoft/DialoGPT-medium, google/flan-t5-base
            # Using GPT-2 as a fallback (can be replaced with better models)
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            )
            
            # Set pad token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            self.model.to(self.device)
            self.model.eval()
            
            print(f"[OK] Generator model loaded successfully")
            
        except Exception as e:
            print(f"Warning: Could not load {self.model_name}: {e}")
            print("Falling back to simple text generation...")
            self.model = None
            self.tokenizer = None
    
    def generate(
        self, 
        prompt: str, 
        max_length: int = 500,
        temperature: float = 0.7,
        top_p: float = 0.9
    ) -> str:
        """
        Generate answer from prompt.
        
        Args:
            prompt: Complete prompt with context
            max_length: Maximum generation length
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
        
        Returns:
            Generated answer text
        """
        if self.model is None or self.tokenizer is None:
            # Fallback: return a simple response
            return self._fallback_generate(prompt)
        
        try:
            # Tokenize input
            inputs = self.tokenizer.encode(prompt, return_tensors="pt", max_length=1024, truncation=True)
            inputs = inputs.to(self.device)
            
            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=len(inputs[0]) + max_length,
                    temperature=temperature,
                    top_p=top_p,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.2
                )
            
            # Decode only the generated part
            generated = outputs[0][len(inputs[0]):]
            answer = self.tokenizer.decode(generated, skip_special_tokens=True)
            
            # Clean up the answer
            answer = answer.strip()
            
            return answer if answer else self._fallback_generate(prompt)
            
        except Exception as e:
            print(f"Error during generation: {e}")
            return self._fallback_generate(prompt)
    
    def _fallback_generate(self, prompt: str) -> str:
        """
        Fallback generation when model is not available.
        Provides a simple template-based response.
        """
        # Extract query from prompt
        if "## User Question:" in prompt:
            query_part = prompt.split("## User Question:")[1].split("## Relevant Complaint Evidence:")[0].strip()
        else:
            query_part = "the question"
        
        # Check if context is available
        if "No relevant complaints found" in prompt or len(prompt.split("## Relevant Complaint Evidence:")) < 2:
            return f"I cannot answer {query_part} based on the available complaint data. Please refine your query or check if relevant complaints exist in the database."
        
        # Simple extraction-based response
        if "[Complaint" in prompt:
            return f"Based on the retrieved complaint evidence, I can provide insights related to {query_part}. Please review the complaint narratives above for specific details. For a more detailed analysis, consider using a more advanced language model."
        
        return "I have retrieved relevant complaint information, but cannot generate a detailed analysis with the current setup. Please review the retrieved complaints above."

