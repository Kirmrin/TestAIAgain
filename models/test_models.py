from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime


class TestParameters(BaseModel):
    """Параметры тестирования"""
    temperature: List[float] = Field(default=[0.1, 0.5, 0.9], description="Значения температуры")
    max_tokens: List[int] = Field(default=[100, 500, 1000], description="Максимальное количество токенов")
    top_p: List[float] = Field(default=[0.1, 0.5, 0.9], description="Значения top-p")
    frequency_penalty: List[float] = Field(default=[0.0, 0.5, 1.0], description="Штраф частоты")
    presence_penalty: List[float] = Field(default=[0.0, 0.5, 1.0], description="Штраф присутствия")
    test_inputs: List[str] = Field(default_factory=list, description="Тестовые входные данные")
    iterations: int = Field(default=3, description="Количество итераций для каждого параметра")


class TestMetrics(BaseModel):
    """Метрики тестирования"""
    accuracy: float = Field(..., description="Точность ответов")
    consistency: float = Field(..., description="Консистентность ответов")
    relevance: float = Field(..., description="Релевантность ответов")
    creativity: float = Field(..., description="Креативность ответов")
    response_time: float = Field(..., description="Среднее время ответа")
    token_efficiency: float = Field(..., description="Эффективность использования токенов")
    cost_efficiency: float = Field(..., description="Эффективность по стоимости")


class TestResult(BaseModel):
    """Результат тестирования"""
    test_id: str = Field(..., description="Уникальный идентификатор теста")
    prompt_id: str = Field(..., description="ID промпта")
    test_parameters: TestParameters = Field(..., description="Параметры теста")
    metrics: TestMetrics = Field(..., description="Метрики тестирования")
    test_cases: List[Dict[str, Any]] = Field(default_factory=list, description="Результаты тестовых случаев")
    summary: str = Field(..., description="Сводка результатов")
    recommendations: List[str] = Field(default_factory=list, description="Рекомендации по улучшению")
    created_at: datetime = Field(default_factory=datetime.now, description="Время создания теста")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ComparativeAnalysis(BaseModel):
    """Сравнительный анализ промптов"""
    analysis_id: str = Field(..., description="Уникальный идентификатор анализа")
    prompt_ids: List[str] = Field(..., description="ID промптов для сравнения")
    comparison_metrics: Dict[str, Dict[str, float]] = Field(..., description="Метрики сравнения")
    winner_prompt_id: str = Field(..., description="ID лучшего промпта")
    ranking: List[str] = Field(..., description="Ранжирование промптов")
    detailed_comparison: Dict[str, Any] = Field(..., description="Детальное сравнение")
    created_at: datetime = Field(default_factory=datetime.now, description="Время создания анализа")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }