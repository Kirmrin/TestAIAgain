#!/usr/bin/env python3
"""
Тесты для оркестратора системы
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from core.orchestrator import PromptLifecycleOrchestrator
from models.test_models import TestParameters
from models.prompt_models import PromptStatus


class TestPromptLifecycleOrchestrator:
    """Тесты для оркестратора жизненного цикла промптов"""
    
    @pytest.fixture
    def orchestrator(self):
        """Создание экземпляра оркестратора для тестов"""
        return PromptLifecycleOrchestrator()
    
    @pytest.fixture
    def mock_agent_manager(self):
        """Мок менеджера агентов"""
        mock = Mock()
        
        # Мок агента-генератора
        generator_agent = Mock()
        generator_result = Mock()
        generator_result.success = True
        generator_result.result_data = {
            "prompt": {
                "id": "test-prompt-1",
                "content": "Тестовый промпт",
                "specification": "Тестовая спецификация",
                "status": PromptStatus.GENERATED
            }
        }
        generator_agent.run = AsyncMock(return_value=generator_result)
        mock.get_agent.return_value = generator_agent
        
        # Мок агента-анализатора
        analyzer_agent = Mock()
        analyzer_result = Mock()
        analyzer_result.success = True
        analyzer_result.result_data = {
            "analysis": {
                "id": "test-analysis-1",
                "prompt_id": "test-prompt-1",
                "clarity_score": 0.8,
                "relevance_score": 0.9,
                "adaptability_score": 0.7,
                "overall_score": 0.8,
                "feedback": "Хороший промпт",
                "suggestions": ["Улучшить ясность"]
            }
        }
        analyzer_agent.run = AsyncMock(return_value=analyzer_result)
        
        # Мок агента-тестера
        tester_agent = Mock()
        tester_result = Mock()
        tester_result.success = True
        tester_result.result_data = {
            "test_result": {
                "test_id": "test-test-1",
                "prompt_id": "test-prompt-1",
                "metrics": {
                    "accuracy": 0.85,
                    "response_time": 2.5,
                    "token_efficiency": 0.7
                },
                "test_cases": [],
                "summary": "Тест завершен успешно",
                "recommendations": ["Оптимизировать время ответа"]
            }
        }
        tester_agent.run = AsyncMock(return_value=tester_result)
        
        # Мок агента-редактора
        editor_agent = Mock()
        editor_result = Mock()
        editor_result.success = True
        editor_result.result_data = {
            "prompt_edit": {
                "id": "test-edit-1",
                "prompt_id": "test-prompt-1",
                "original_content": "Тестовый промпт",
                "edited_content": "Улучшенный тестовый промпт",
                "edit_reason": "Улучшение ясности",
                "improvements": ["Улучшена ясность"]
            },
            "updated_prompt": {
                "id": "test-prompt-1",
                "content": "Улучшенный тестовый промпт",
                "specification": "Тестовая спецификация",
                "status": PromptStatus.EDITED
            }
        }
        editor_agent.run = AsyncMock(return_value=editor_result)
        
        return mock
    
    @pytest.fixture
    def mock_prompt_store(self):
        """Мок хранилища промптов"""
        mock = Mock()
        mock.save_prompt = Mock()
        mock.save_analysis = Mock()
        mock.save_test_result = Mock()
        mock.save_prompt_edit = Mock()
        return mock
    
    @pytest.mark.asyncio
    async def test_run_full_lifecycle_success(self, orchestrator, mock_agent_manager, mock_prompt_store):
        """Тест успешного выполнения полного жизненного цикла"""
        # Подмена зависимостей
        orchestrator.agent_manager = mock_agent_manager
        orchestrator.prompt_store = mock_prompt_store
        
        specification = "Тестовая спецификация"
        test_parameters = TestParameters()
        
        result = await orchestrator.run_full_lifecycle(
            specification=specification,
            test_parameters=test_parameters
        )
        
        assert result["success"] is True
        assert "phases" in result
        assert "summary" in result
        assert result["specification"] == specification
        
        # Проверка фаз
        phases = result["phases"]
        assert "generation" in phases
        assert "analysis" in phases
        assert "testing" in phases
        assert "editing" in phases
        
        # Проверка вызовов агентов
        mock_agent_manager.get_agent.assert_called()
    
    @pytest.mark.asyncio
    async def test_run_full_lifecycle_generation_failure(self, orchestrator, mock_agent_manager, mock_prompt_store):
        """Тест обработки ошибки в фазе генерации"""
        # Настройка мока для ошибки генерации
        generator_agent = Mock()
        generator_result = Mock()
        generator_result.success = False
        generator_result.error_message = "Ошибка генерации"
        generator_agent.run = AsyncMock(return_value=generator_result)
        mock_agent_manager.get_agent.return_value = generator_agent
        
        orchestrator.agent_manager = mock_agent_manager
        orchestrator.prompt_store = mock_prompt_store
        
        result = await orchestrator.run_full_lifecycle(
            specification="Тестовая спецификация"
        )
        
        assert result["success"] is False
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_generate_lifecycle_summary(self, orchestrator):
        """Тест генерации сводки жизненного цикла"""
        lifecycle_results = {
            "phases": {
                "generation": {
                    "success": True,
                    "prompt": {"id": "test-1", "content": "Тест"}
                },
                "analysis": {
                    "success": True,
                    "analysis": {
                        "clarity_score": 0.8,
                        "relevance_score": 0.9,
                        "adaptability_score": 0.7,
                        "overall_score": 0.8
                    }
                },
                "testing": {
                    "success": True,
                    "test_result": {
                        "metrics": {
                            "accuracy": 0.85,
                            "response_time": 2.5,
                            "token_efficiency": 0.7
                        }
                    }
                },
                "editing": {
                    "success": True,
                    "updated_prompt": {"id": "test-1", "content": "Обновленный тест"}
                }
            }
        }
        
        summary = orchestrator._generate_lifecycle_summary(lifecycle_results)
        
        assert summary["total_phases"] == 4
        assert summary["successful_phases"] == 4
        assert summary["final_prompt"] is not None
        assert "key_metrics" in summary
        
        metrics = summary["key_metrics"]
        assert "clarity" in metrics
        assert "relevance" in metrics
        assert "accuracy" in metrics
    
    @pytest.mark.asyncio
    async def test_compare_prompts(self, orchestrator):
        """Тест сравнения промптов"""
        prompts = [
            {"id": "prompt-1", "content": "Промпт 1"},
            {"id": "prompt-2", "content": "Промпт 2"}
        ]
        
        analyses = [
            {"prompt_id": "prompt-1", "overall_score": 0.8},
            {"prompt_id": "prompt-2", "overall_score": 0.9}
        ]
        
        test_results = [
            {
                "prompt_id": "prompt-1",
                "metrics": {"accuracy": 0.8, "relevance": 0.8, "token_efficiency": 0.8}
            },
            {
                "prompt_id": "prompt-2",
                "metrics": {"accuracy": 0.9, "relevance": 0.9, "token_efficiency": 0.9}
            }
        ]
        
        comparison = orchestrator._compare_prompts(prompts, analyses, test_results)
        
        assert "comparison_matrix" in comparison
        assert "best_prompt_id" in comparison
        assert "ranking" in comparison
        assert len(comparison["ranking"]) == 2
        assert comparison["best_prompt_id"] == "prompt-2"  # Лучший по оценкам
    
    @pytest.mark.asyncio
    async def test_compare_prompts_empty(self, orchestrator):
        """Тест сравнения пустого списка промптов"""
        comparison = orchestrator._compare_prompts([], [], [])
        
        assert "error" in comparison
        assert comparison["error"] == "Нет промптов для сравнения"


if __name__ == "__main__":
    pytest.main([__file__])