import uuid
from typing import Dict, Any
from gigachain.llms.gigachat import GigaChat
from langchain.schema import HumanMessage, SystemMessage

from .base_agent import BaseAgent
from models.prompt_models import PromptAnalysis
from models.agent_models import AgentResult


class AnalyzerAgent(BaseAgent):
    """Агент для анализа промптов"""
    
    def _setup_llm(self):
        """Настройка LLM для анализа"""
        self.llm = GigaChat(
            model=self.config.model_name,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ промпта по метрикам качества"""
        prompt_content = input_data.get("prompt_content", "")
        prompt_id = input_data.get("prompt_id", "")
        context = input_data.get("context", "")
        
        # Формирование промпта для анализа
        analysis_prompt = self._build_analysis_prompt(prompt_content, context)
        
        # Анализ промпта
        messages = [
            SystemMessage(content=self.config.system_prompt),
            HumanMessage(content=analysis_prompt)
        ]
        
        response = await self.llm.ainvoke(messages)
        analysis_result = self._parse_analysis_response(response.content)
        
        # Создание объекта анализа
        analysis = PromptAnalysis(
            id=str(uuid.uuid4()),
            prompt_id=prompt_id,
            clarity_score=analysis_result["clarity_score"],
            relevance_score=analysis_result["relevance_score"],
            adaptability_score=analysis_result["adaptability_score"],
            overall_score=analysis_result["overall_score"],
            feedback=analysis_result["feedback"],
            suggestions=analysis_result["suggestions"]
        )
        
        return {
            "analysis": analysis.dict(),
            "analysis_metadata": {
                "prompt_id": prompt_id,
                "context": context,
                "analyzer_agent": self.agent_id
            }
        }
    
    def _build_analysis_prompt(self, prompt_content: str, context: str) -> str:
        """Построение промпта для анализа"""
        return f"""
Промпт для анализа:
{prompt_content}

Контекст: {context}

Проведи комплексный анализ промпта по следующим критериям:

1. ЯСНОСТЬ (0-1): Насколько четко и понятно сформулирована задача
2. РЕЛЕВАНТНОСТЬ (0-1): Насколько промпт соответствует поставленной задаче
3. АДАПТИВНОСТЬ (0-1): Насколько промпт может быть адаптирован к различным контекстам

Ответь в следующем формате:
CLARITY: [оценка 0-1]
RELEVANCE: [оценка 0-1]
ADAPTABILITY: [оценка 0-1]
OVERALL: [средняя оценка 0-1]
FEEDBACK: [подробная обратная связь]
SUGGESTIONS:
- [предложение 1]
- [предложение 2]
- [предложение 3]
"""
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Парсинг ответа анализа"""
        lines = response.strip().split('\n')
        result = {
            "clarity_score": 0.5,
            "relevance_score": 0.5,
            "adaptability_score": 0.5,
            "overall_score": 0.5,
            "feedback": "",
            "suggestions": []
        }
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if line.startswith("CLARITY:"):
                try:
                    result["clarity_score"] = float(line.split(":")[1].strip())
                except:
                    pass
            elif line.startswith("RELEVANCE:"):
                try:
                    result["relevance_score"] = float(line.split(":")[1].strip())
                except:
                    pass
            elif line.startswith("ADAPTABILITY:"):
                try:
                    result["adaptability_score"] = float(line.split(":")[1].strip())
                except:
                    pass
            elif line.startswith("OVERALL:"):
                try:
                    result["overall_score"] = float(line.split(":")[1].strip())
                except:
                    pass
            elif line.startswith("FEEDBACK:"):
                current_section = "feedback"
                result["feedback"] = line.split(":", 1)[1].strip() if ":" in line else ""
            elif line.startswith("SUGGESTIONS:"):
                current_section = "suggestions"
            elif line.startswith("-") and current_section == "suggestions":
                suggestion = line[1:].strip()
                if suggestion:
                    result["suggestions"].append(suggestion)
            elif current_section == "feedback" and line:
                result["feedback"] += " " + line
        
        # Пересчет общей оценки
        scores = [result["clarity_score"], result["relevance_score"], result["adaptability_score"]]
        result["overall_score"] = sum(scores) / len(scores)
        
        return result