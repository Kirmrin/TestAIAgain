from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


class PromptStatus(str, Enum):
    GENERATED = "generated"
    ANALYZED = "analyzed"
    TESTED = "tested"
    EDITED = "edited"
    FINALIZED = "finalized"


class Prompt(BaseModel):
    """Модель промпта"""
    id: str = Field(..., description="Уникальный идентификатор промпта")
    content: str = Field(..., description="Содержимое промпта")
    specification: str = Field(..., description="Исходная спецификация")
    version: int = Field(default=1, description="Версия промпта")
    status: PromptStatus = Field(default=PromptStatus.GENERATED, description="Статус промпта")
    created_at: datetime = Field(default_factory=datetime.now, description="Время создания")
    updated_at: datetime = Field(default_factory=datetime.now, description="Время последнего обновления")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Дополнительные метаданные")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PromptTest(BaseModel):
    """Модель теста промпта"""
    id: str = Field(..., description="Уникальный идентификатор теста")
    prompt_id: str = Field(..., description="ID промпта")
    test_parameters: Dict[str, Any] = Field(..., description="Параметры теста")
    input_data: str = Field(..., description="Входные данные для теста")
    output_data: str = Field(..., description="Выходные данные теста")
    execution_time: float = Field(..., description="Время выполнения в секундах")
    tokens_used: int = Field(..., description="Количество использованных токенов")
    cost: float = Field(..., description="Стоимость выполнения")
    created_at: datetime = Field(default_factory=datetime.now, description="Время создания теста")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PromptAnalysis(BaseModel):
    """Модель анализа промпта"""
    id: str = Field(..., description="Уникальный идентификатор анализа")
    prompt_id: str = Field(..., description="ID промпта")
    clarity_score: float = Field(..., description="Оценка ясности (0-1)")
    relevance_score: float = Field(..., description="Оценка релевантности (0-1)")
    adaptability_score: float = Field(..., description="Оценка адаптивности (0-1)")
    overall_score: float = Field(..., description="Общая оценка (0-1)")
    feedback: str = Field(..., description="Обратная связь по промпту")
    suggestions: List[str] = Field(default_factory=list, description="Предложения по улучшению")
    created_at: datetime = Field(default_factory=datetime.now, description="Время создания анализа")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PromptEdit(BaseModel):
    """Модель редактирования промпта"""
    id: str = Field(..., description="Уникальный идентификатор редактирования")
    prompt_id: str = Field(..., description="ID исходного промпта")
    original_content: str = Field(..., description="Исходное содержимое")
    edited_content: str = Field(..., description="Отредактированное содержимое")
    edit_reason: str = Field(..., description="Причина редактирования")
    improvements: List[str] = Field(default_factory=list, description="Внесенные улучшения")
    created_at: datetime = Field(default_factory=datetime.now, description="Время создания редактирования")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }