from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from enum import Enum


class AgentType(str, Enum):
    GENERATOR = "generator"
    ANALYZER = "analyzer"
    TESTER = "tester"
    EDITOR = "editor"


class AgentConfig(BaseModel):
    """Конфигурация агента"""
    agent_type: AgentType = Field(..., description="Тип агента")
    name: str = Field(..., description="Название агента")
    description: str = Field(..., description="Описание агента")
    model_name: str = Field(..., description="Название модели LLM")
    temperature: float = Field(default=0.7, description="Температура генерации")
    max_tokens: int = Field(default=1000, description="Максимальное количество токенов")
    system_prompt: str = Field(..., description="Системный промпт агента")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Дополнительные параметры")
    enabled: bool = Field(default=True, description="Активен ли агент")


class AgentResult(BaseModel):
    """Результат работы агента"""
    agent_id: str = Field(..., description="ID агента")
    agent_type: AgentType = Field(..., description="Тип агента")
    success: bool = Field(..., description="Успешность выполнения")
    result_data: Dict[str, Any] = Field(..., description="Данные результата")
    error_message: Optional[str] = Field(None, description="Сообщение об ошибке")
    execution_time: float = Field(..., description="Время выполнения в секундах")
    tokens_used: int = Field(..., description="Количество использованных токенов")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Дополнительные метаданные")


class AgentRegistry(BaseModel):
    """Реестр агентов"""
    agents: Dict[str, AgentConfig] = Field(default_factory=dict, description="Зарегистрированные агенты")
    
    def register_agent(self, agent_id: str, config: AgentConfig):
        """Регистрация нового агента"""
        self.agents[agent_id] = config
    
    def get_agent(self, agent_id: str) -> Optional[AgentConfig]:
        """Получение конфигурации агента"""
        return self.agents.get(agent_id)
    
    def list_agents(self, agent_type: Optional[AgentType] = None) -> List[str]:
        """Список агентов по типу"""
        if agent_type:
            return [aid for aid, config in self.agents.items() if config.agent_type == agent_type]
        return list(self.agents.keys())