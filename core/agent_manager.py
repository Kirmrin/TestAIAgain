from typing import Dict, Optional
from loguru import logger

from models.agent_models import AgentConfig, AgentType
from agents import GeneratorAgent, AnalyzerAgent, TesterAgent, EditorAgent


class AgentManager:
    """Менеджер агентов системы"""
    
    def __init__(self):
        self.agents: Dict[str, any] = {}
        self._initialize_default_agents()
    
    def _initialize_default_agents(self):
        """Инициализация агентов по умолчанию"""
        # Агент-генератор
        generator_config = AgentConfig(
            agent_type=AgentType.GENERATOR,
            name="Prompt Generator",
            description="Генерирует высококачественные промпты на основе спецификаций",
            model_name="GigaChat",
            temperature=0.7,
            max_tokens=1000,
            system_prompt="""Ты эксперт по созданию промптов для AI систем. 
Твоя задача - создавать четкие, эффективные и адаптивные промпты, 
которые обеспечивают высокое качество результатов."""
        )
        self.register_agent("generator", GeneratorAgent(generator_config))
        
        # Агент-анализатор
        analyzer_config = AgentConfig(
            agent_type=AgentType.ANALYZER,
            name="Prompt Analyzer",
            description="Анализирует качество промптов по различным метрикам",
            model_name="GigaChat",
            temperature=0.3,
            max_tokens=800,
            system_prompt="""Ты эксперт по анализу промптов. 
Твоя задача - объективно оценивать качество промптов по критериям 
ясности, релевантности и адаптивности."""
        )
        self.register_agent("analyzer", AnalyzerAgent(analyzer_config))
        
        # Агент-тестер
        tester_config = AgentConfig(
            agent_type=AgentType.TESTER,
            name="Prompt Tester",
            description="Тестирует промпты с различными параметрами",
            model_name="GigaChat",
            temperature=0.5,
            max_tokens=1200,
            system_prompt="""Ты эксперт по тестированию промптов. 
Твоя задача - проводить комплексное тестирование промптов 
с различными параметрами и оценивать их производительность."""
        )
        self.register_agent("tester", TesterAgent(tester_config))
        
        # Агент-редактор
        editor_config = AgentConfig(
            agent_type=AgentType.EDITOR,
            name="Prompt Editor",
            description="Редактирует и оптимизирует промпты на основе обратной связи",
            model_name="GigaChat",
            temperature=0.6,
            max_tokens=1000,
            system_prompt="""Ты эксперт по редактированию промптов. 
Твоя задача - улучшать промпты на основе обратной связи, 
сохраняя их основную суть и назначение."""
        )
        self.register_agent("editor", EditorAgent(editor_config))
        
        logger.info(f"Инициализировано {len(self.agents)} агентов")
    
    def register_agent(self, agent_id: str, agent: any):
        """Регистрация нового агента"""
        self.agents[agent_id] = agent
        logger.info(f"Зарегистрирован агент: {agent_id}")
    
    def get_agent(self, agent_id: str) -> Optional[any]:
        """Получение агента по ID"""
        agent = self.agents.get(agent_id)
        if agent is None:
            logger.warning(f"Агент {agent_id} не найден")
        return agent
    
    def get_agents_by_type(self, agent_type: AgentType) -> Dict[str, any]:
        """Получение всех агентов определенного типа"""
        return {
            agent_id: agent for agent_id, agent in self.agents.items()
            if agent.config.agent_type == agent_type
        }
    
    def list_agents(self) -> Dict[str, AgentConfig]:
        """Список всех агентов с их конфигурациями"""
        return {
            agent_id: agent.config for agent_id, agent in self.agents.items()
        }
    
    def update_agent_config(self, agent_id: str, config: AgentConfig):
        """Обновление конфигурации агента"""
        if agent_id in self.agents:
            # Создание нового агента с обновленной конфигурацией
            agent_class = type(self.agents[agent_id])
            self.agents[agent_id] = agent_class(config)
            logger.info(f"Обновлена конфигурация агента: {agent_id}")
        else:
            logger.warning(f"Агент {agent_id} не найден для обновления")
    
    def enable_agent(self, agent_id: str):
        """Включение агента"""
        if agent_id in self.agents:
            self.agents[agent_id].config.enabled = True
            logger.info(f"Агент {agent_id} включен")
        else:
            logger.warning(f"Агент {agent_id} не найден")
    
    def disable_agent(self, agent_id: str):
        """Отключение агента"""
        if agent_id in self.agents:
            self.agents[agent_id].config.enabled = False
            logger.info(f"Агент {agent_id} отключен")
        else:
            logger.warning(f"Агент {agent_id} не найден")
    
    def get_agent_status(self) -> Dict[str, Dict[str, any]]:
        """Получение статуса всех агентов"""
        status = {}
        for agent_id, agent in self.agents.items():
            status[agent_id] = {
                "enabled": agent.is_enabled(),
                "agent_type": agent.config.agent_type.value,
                "name": agent.config.name,
                "description": agent.config.description,
                "model_name": agent.config.model_name
            }
        return status