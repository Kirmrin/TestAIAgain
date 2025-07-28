from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import asyncio
import time
from loguru import logger

from models.agent_models import AgentConfig, AgentResult, AgentType


class BaseAgent(ABC):
    """Базовый класс для всех агентов"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.agent_id = f"{config.agent_type.value}_{config.name.lower().replace(' ', '_')}"
        self.llm = None
        self._setup_llm()
    
    @abstractmethod
    def _setup_llm(self):
        """Настройка LLM для агента"""
        pass
    
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Выполнение основной логики агента"""
        pass
    
    async def run(self, input_data: Dict[str, Any]) -> AgentResult:
        """Запуск агента с обработкой ошибок и метрик"""
        start_time = time.time()
        tokens_used = 0
        
        try:
            logger.info(f"Запуск агента {self.agent_id}")
            
            # Выполнение основной логики
            result = await self.execute(input_data)
            
            execution_time = time.time() - start_time
            
            return AgentResult(
                agent_id=self.agent_id,
                agent_type=self.config.agent_type,
                success=True,
                result_data=result,
                execution_time=execution_time,
                tokens_used=tokens_used,
                metadata={"agent_name": self.config.name}
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Ошибка в агенте {self.agent_id}: {str(e)}")
            
            return AgentResult(
                agent_id=self.agent_id,
                agent_type=self.config.agent_type,
                success=False,
                result_data={},
                error_message=str(e),
                execution_time=execution_time,
                tokens_used=tokens_used,
                metadata={"agent_name": self.config.name}
            )
    
    def get_system_prompt(self) -> str:
        """Получение системного промпта агента"""
        return self.config.system_prompt
    
    def is_enabled(self) -> bool:
        """Проверка активности агента"""
        return self.config.enabled
    
    def get_config(self) -> AgentConfig:
        """Получение конфигурации агента"""
        return self.config