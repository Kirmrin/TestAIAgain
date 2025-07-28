import uuid
import os
from typing import Dict, Any, List
from langchain_gigachat import GigaChat
from langchain.schema import HumanMessage, SystemMessage

from .base_agent import BaseAgent
from models.prompt_models import PromptEdit, Prompt, PromptStatus
from models.agent_models import AgentResult


class EditorAgent(BaseAgent):
    """Агент для редактирования промптов"""
    
    def _setup_llm(self):
        """Настройка LLM для редактирования"""
        self.llm = GigaChat(
            credentials=os.getenv("GIGACHAT_CREDENTIALS"),
            scope=os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS"),
            model=self.config.model_name,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            verify_ssl_certs=os.getenv("GIGACHAT_VERIFY_SSL_CERTS", "false").lower() == "true"
        )
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Редактирование промпта на основе обратной связи"""
        prompt_content = input_data.get("prompt_content", "")
        prompt_id = input_data.get("prompt_id", "")
        feedback = input_data.get("feedback", "")
        suggestions = input_data.get("suggestions", [])
        test_results = input_data.get("test_results", {})
        
        # Формирование промпта для редактирования
        edit_prompt = self._build_edit_prompt(
            prompt_content, feedback, suggestions, test_results
        )
        
        # Редактирование промпта
        messages = [
            SystemMessage(content=self.config.system_prompt),
            HumanMessage(content=edit_prompt)
        ]
        
        response = await self.llm.ainvoke(messages)
        edited_content = response.content
        
        # Извлечение улучшений из ответа
        improvements = self._extract_improvements(response.content)
        
        # Создание объекта редактирования
        prompt_edit = PromptEdit(
            id=str(uuid.uuid4()),
            prompt_id=prompt_id,
            original_content=prompt_content,
            edited_content=edited_content,
            edit_reason=self._generate_edit_reason(feedback, suggestions),
            improvements=improvements
        )
        
        # Создание обновленного промпта
        updated_prompt = Prompt(
            id=prompt_id,
            content=edited_content,
            specification=input_data.get("specification", ""),
            version=input_data.get("version", 1) + 1,
            status=PromptStatus.EDITED,
            metadata={
                "original_prompt_id": prompt_id,
                "editor_agent": self.agent_id,
                "improvements": improvements
            }
        )
        
        return {
            "prompt_edit": prompt_edit.dict(),
            "updated_prompt": updated_prompt.dict(),
            "edit_metadata": {
                "prompt_id": prompt_id,
                "feedback": feedback,
                "suggestions": suggestions,
                "editor_agent": self.agent_id
            }
        }
    
    def _build_edit_prompt(self, prompt_content: str, feedback: str, 
                          suggestions: List[str], test_results: Dict[str, Any]) -> str:
        """Построение промпта для редактирования"""
        prompt_parts = [
            f"Исходный промпт:\n{prompt_content}",
            f"\nОбратная связь:\n{feedback}"
        ]
        
        if suggestions:
            suggestions_text = "\n".join([f"- {suggestion}" for suggestion in suggestions])
            prompt_parts.append(f"\nПредложения по улучшению:\n{suggestions_text}")
        
        if test_results:
            metrics = test_results.get("metrics", {})
            prompt_parts.append(f"\nРезультаты тестирования:")
            prompt_parts.append(f"- Точность: {metrics.get('accuracy', 0):.2f}")
            prompt_parts.append(f"- Релевантность: {metrics.get('relevance', 0):.2f}")
            prompt_parts.append(f"- Время ответа: {metrics.get('response_time', 0):.2f} сек")
        
        prompt_parts.append("\nЗадача: Улучши промпт, учитывая обратную связь и предложения.")
        prompt_parts.append("Требования к улучшенному промпту:")
        prompt_parts.append("- Сохрани основную суть и назначение")
        prompt_parts.append("- Улучши ясность и точность формулировок")
        prompt_parts.append("- Оптимизируй для лучшей производительности")
        prompt_parts.append("- Учти все предложения по улучшению")
        
        return "\n".join(prompt_parts)
    
    def _extract_improvements(self, edited_content: str) -> List[str]:
        """Извлечение списка улучшений из отредактированного контента"""
        improvements = []
        
        # Простая эвристика для извлечения улучшений
        lines = edited_content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('-') or line.startswith('•'):
                improvement = line[1:].strip()
                if improvement:
                    improvements.append(improvement)
        
        # Если не удалось извлечь, добавляем общее улучшение
        if not improvements:
            improvements.append("Улучшена общая структура и ясность промпта")
        
        return improvements
    
    def _generate_edit_reason(self, feedback: str, suggestions: List[str]) -> str:
        """Генерация причины редактирования"""
        reasons = []
        
        if feedback:
            reasons.append("Обратная связь по качеству")
        
        if suggestions:
            reasons.append(f"Учет {len(suggestions)} предложений по улучшению")
        
        if not reasons:
            reasons.append("Общая оптимизация промпта")
        
        return "; ".join(reasons)