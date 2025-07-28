import uuid
from typing import Dict, Any
import os
from langchain_community.chat_models import GigaChat
from langchain.schema import HumanMessage, SystemMessage

from .base_agent import BaseAgent
from models.prompt_models import Prompt, PromptStatus
from models.agent_models import AgentResult


class GeneratorAgent(BaseAgent):
    """Агент для генерации промптов"""
    
    def _setup_llm(self):
        """Настройка LLM для генерации"""
        from os import getenv
        self.llm = GigaChat(
            model=self.config.model_name,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            credentials=getenv("GIGACHAT_TOKEN") or getenv("GIGACHAT_CREDENTIALS"),
            verify_ssl_certs=False,
        )
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация промпта на основе спецификации"""
        specification = input_data.get("specification", "")
        context = input_data.get("context", "")
        requirements = input_data.get("requirements", [])
        
        # Формирование промпта для генерации
        generation_prompt = self._build_generation_prompt(
            specification, context, requirements
        )
        
        # Генерация промпта
        messages = [
            SystemMessage(content=self.config.system_prompt),
            HumanMessage(content=generation_prompt)
        ]
        
        response = await self.llm.ainvoke(messages)
        generated_content = response.content
        
        # Создание объекта промпта
        prompt = Prompt(
            id=str(uuid.uuid4()),
            content=generated_content,
            specification=specification,
            status=PromptStatus.GENERATED,
            metadata={
                "context": context,
                "requirements": requirements,
                "generator_agent": self.agent_id
            }
        )
        
        return {
            "prompt": prompt.dict(),
            "generation_metadata": {
                "specification": specification,
                "context": context,
                "requirements": requirements
            }
        }
    
    def _build_generation_prompt(self, specification: str, context: str, requirements: list) -> str:
        """Построение промпта для генерации"""
        prompt_parts = [
            f"Спецификация: {specification}",
        ]
        
        if context:
            prompt_parts.append(f"Контекст: {context}")
        
        if requirements:
            requirements_text = "\n".join([f"- {req}" for req in requirements])
            prompt_parts.append(f"Требования:\n{requirements_text}")
        
        prompt_parts.append("\nСоздай высококачественный промпт, который:")
        prompt_parts.append("- Четко и ясно формулирует задачу")
        prompt_parts.append("- Учитывает все указанные требования")
        prompt_parts.append("- Оптимизирован для эффективного выполнения")
        prompt_parts.append("- Адаптивен к различным контекстам")
        
        return "\n\n".join(prompt_parts)