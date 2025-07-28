import uuid
import time
import os
from typing import Dict, Any, List
from langchain_gigachat import GigaChat
from langchain.schema import HumanMessage, SystemMessage

from .base_agent import BaseAgent
from models.prompt_models import PromptTest
from models.test_models import TestParameters, TestMetrics, TestResult
from models.agent_models import AgentResult


class TesterAgent(BaseAgent):
    """Агент для тестирования промптов"""
    
    def _setup_llm(self):
        """Настройка LLM для тестирования"""
        self.llm = GigaChat(
            credentials=os.getenv("GIGACHAT_CREDENTIALS"),
            scope=os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS"),
            model=self.config.model_name,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            verify_ssl_certs=os.getenv("GIGACHAT_VERIFY_SSL_CERTS", "false").lower() == "true"
        )
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Тестирование промпта с различными параметрами"""
        prompt_content = input_data.get("prompt_content", "")
        prompt_id = input_data.get("prompt_id", "")
        test_parameters = input_data.get("test_parameters", TestParameters())
        
        # Выполнение тестов
        test_cases = []
        all_results = []
        
        for temp in test_parameters.temperature:
            for max_tokens in test_parameters.max_tokens:
                for top_p in test_parameters.top_p:
                    for test_input in test_parameters.test_inputs:
                        test_result = await self._run_single_test(
                            prompt_content, test_input, temp, max_tokens, top_p
                        )
                        test_cases.append(test_result)
                        all_results.append(test_result)
        
        # Вычисление метрик
        metrics = self._calculate_metrics(all_results)
        
        # Создание результата тестирования
        test_result = TestResult(
            test_id=str(uuid.uuid4()),
            prompt_id=prompt_id,
            test_parameters=test_parameters,
            metrics=metrics,
            test_cases=test_cases,
            summary=self._generate_summary(metrics, test_cases),
            recommendations=self._generate_recommendations(metrics, test_cases)
        )
        
        return {
            "test_result": test_result.dict(),
            "test_metadata": {
                "prompt_id": prompt_id,
                "total_tests": len(test_cases),
                "tester_agent": self.agent_id
            }
        }
    
    async def _run_single_test(self, prompt_content: str, test_input: str, 
                              temperature: float, max_tokens: int, top_p: float) -> Dict[str, Any]:
        """Выполнение одного теста"""
        start_time = time.time()
        
        # Создание LLM с тестовыми параметрами
        test_llm = GigaChat(
            credentials=os.getenv("GIGACHAT_CREDENTIALS"),
            scope=os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS"),
            model=self.config.model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            verify_ssl_certs=os.getenv("GIGACHAT_VERIFY_SSL_CERTS", "false").lower() == "true"
        )
        
        # Формирование полного промпта
        full_prompt = f"{prompt_content}\n\nВходные данные: {test_input}"
        
        # Выполнение теста
        messages = [
            SystemMessage(content=self.config.system_prompt),
            HumanMessage(content=full_prompt)
        ]
        
        response = await test_llm.ainvoke(messages)
        execution_time = time.time() - start_time
        
        # Создание объекта теста
        prompt_test = PromptTest(
            id=str(uuid.uuid4()),
            prompt_id="",  # Будет заполнено позже
            test_parameters={
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": top_p
            },
            input_data=test_input,
            output_data=response.content,
            execution_time=execution_time,
            tokens_used=len(response.content.split()),  # Приблизительная оценка
            cost=0.0  # Будет рассчитано позже
        )
        
        return prompt_test.dict()
    
    def _calculate_metrics(self, test_results: List[Dict[str, Any]]) -> TestMetrics:
        """Вычисление метрик на основе результатов тестов"""
        if not test_results:
            return TestMetrics(
                accuracy=0.0,
                consistency=0.0,
                relevance=0.0,
                creativity=0.0,
                response_time=0.0,
                token_efficiency=0.0,
                cost_efficiency=0.0
            )
        
        # Вычисление средних значений
        execution_times = [r["execution_time"] for r in test_results]
        tokens_used = [r["tokens_used"] for r in test_results]
        
        # Простые метрики (в реальной системе здесь была бы более сложная логика)
        avg_response_time = sum(execution_times) / len(execution_times)
        avg_tokens = sum(tokens_used) / len(tokens_used)
        
        # Оценка качества ответов (упрощенная)
        quality_scores = []
        for result in test_results:
            output = result["output_data"]
            # Простая эвристика для оценки качества
            score = min(1.0, len(output) / 100)  # Чем длиннее ответ, тем лучше
            quality_scores.append(score)
        
        avg_quality = sum(quality_scores) / len(quality_scores)
        
        return TestMetrics(
            accuracy=avg_quality,
            consistency=0.8,  # Заглушка
            relevance=avg_quality,
            creativity=0.7,  # Заглушка
            response_time=avg_response_time,
            token_efficiency=1.0 / avg_tokens if avg_tokens > 0 else 0.0,
            cost_efficiency=0.8  # Заглушка
        )
    
    def _generate_summary(self, metrics: TestMetrics, test_cases: List[Dict[str, Any]]) -> str:
        """Генерация сводки результатов"""
        return f"""
Результаты тестирования:
- Точность: {metrics.accuracy:.2f}
- Релевантность: {metrics.relevance:.2f}
- Среднее время ответа: {metrics.response_time:.2f} сек
- Эффективность токенов: {metrics.token_efficiency:.2f}
- Всего тестов: {len(test_cases)}
        """.strip()
    
    def _generate_recommendations(self, metrics: TestMetrics, test_cases: List[Dict[str, Any]]) -> List[str]:
        """Генерация рекомендаций"""
        recommendations = []
        
        if metrics.accuracy < 0.7:
            recommendations.append("Улучшить точность промпта для более качественных ответов")
        
        if metrics.response_time > 5.0:
            recommendations.append("Оптимизировать промпт для уменьшения времени ответа")
        
        if metrics.token_efficiency < 0.5:
            recommendations.append("Сократить промпт для более эффективного использования токенов")
        
        if not recommendations:
            recommendations.append("Промпт показывает хорошие результаты, минимальные улучшения не требуются")
        
        return recommendations