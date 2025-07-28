import asyncio
from typing import Dict, Any, List, Optional
from loguru import logger

from models.prompt_models import Prompt, PromptStatus
from models.test_models import TestParameters
from models.agent_models import AgentResult
from .agent_manager import AgentManager
from .prompt_store import PromptStore


class PromptLifecycleOrchestrator:
    """Оркестратор жизненного цикла промптов"""
    
    def __init__(self):
        self.agent_manager = AgentManager()
        self.prompt_store = PromptStore()
        self.logger = logger
    
    async def run_full_lifecycle(self, specification: str, 
                                test_parameters: Optional[TestParameters] = None,
                                context: str = "", requirements: List[str] = None) -> Dict[str, Any]:
        """Запуск полного жизненного цикла промпта"""
        self.logger.info("Запуск полного жизненного цикла промпта")
        
        lifecycle_results = {
            "specification": specification,
            "context": context,
            "requirements": requirements or [],
            "phases": {}
        }
        
        try:
            # Фаза 1: Генерация
            self.logger.info("Фаза 1: Генерация промпта")
            generation_result = await self._generate_phase(specification, context, requirements)
            lifecycle_results["phases"]["generation"] = generation_result
            
            prompt = generation_result["prompt"]
            prompt_id = prompt["id"]
            
            # Фаза 2: Анализ
            self.logger.info("Фаза 2: Анализ промпта")
            analysis_result = await self._analyze_phase(prompt)
            lifecycle_results["phases"]["analysis"] = analysis_result
            
            # Фаза 3: Тестирование
            self.logger.info("Фаза 3: Тестирование промпта")
            test_result = await self._test_phase(prompt, test_parameters)
            lifecycle_results["phases"]["testing"] = test_result
            
            # Фаза 4: Редактирование
            self.logger.info("Фаза 4: Редактирование промпта")
            edit_result = await self._edit_phase(prompt, analysis_result, test_result)
            lifecycle_results["phases"]["editing"] = edit_result
            
            # Финальная сводка
            lifecycle_results["summary"] = self._generate_lifecycle_summary(lifecycle_results)
            lifecycle_results["success"] = True
            
            self.logger.info("Жизненный цикл промпта завершен успешно")
            
        except Exception as e:
            self.logger.error(f"Ошибка в жизненном цикле: {str(e)}")
            lifecycle_results["success"] = False
            lifecycle_results["error"] = str(e)
        
        return lifecycle_results
    
    async def _generate_phase(self, specification: str, context: str, 
                            requirements: List[str]) -> Dict[str, Any]:
        """Фаза генерации промпта"""
        generator_agent = self.agent_manager.get_agent("generator")
        
        input_data = {
            "specification": specification,
            "context": context,
            "requirements": requirements or []
        }
        
        result = await generator_agent.run(input_data)
        
        if result.success:
            prompt_data = result.result_data["prompt"]
            self.prompt_store.save_prompt(prompt_data)
            return {
                "success": True,
                "prompt": prompt_data,
                "agent_result": result.dict()
            }
        else:
            raise Exception(f"Ошибка генерации: {result.error_message}")
    
    async def _analyze_phase(self, prompt: Dict[str, Any]) -> Dict[str, Any]:
        """Фаза анализа промпта"""
        analyzer_agent = self.agent_manager.get_agent("analyzer")
        
        input_data = {
            "prompt_content": prompt["content"],
            "prompt_id": prompt["id"],
            "context": prompt.get("metadata", {}).get("context", "")
        }
        
        result = await analyzer_agent.run(input_data)
        
        if result.success:
            analysis_data = result.result_data["analysis"]
            self.prompt_store.save_analysis(analysis_data)
            return {
                "success": True,
                "analysis": analysis_data,
                "agent_result": result.dict()
            }
        else:
            raise Exception(f"Ошибка анализа: {result.error_message}")
    
    async def _test_phase(self, prompt: Dict[str, Any], 
                         test_parameters: Optional[TestParameters]) -> Dict[str, Any]:
        """Фаза тестирования промпта"""
        tester_agent = self.agent_manager.get_agent("tester")
        
        if test_parameters is None:
            test_parameters = TestParameters()
        
        input_data = {
            "prompt_content": prompt["content"],
            "prompt_id": prompt["id"],
            "test_parameters": test_parameters
        }
        
        result = await tester_agent.run(input_data)
        
        if result.success:
            test_data = result.result_data["test_result"]
            self.prompt_store.save_test_result(test_data)
            return {
                "success": True,
                "test_result": test_data,
                "agent_result": result.dict()
            }
        else:
            raise Exception(f"Ошибка тестирования: {result.error_message}")
    
    async def _edit_phase(self, prompt: Dict[str, Any], analysis_result: Dict[str, Any],
                         test_result: Dict[str, Any]) -> Dict[str, Any]:
        """Фаза редактирования промпта"""
        editor_agent = self.agent_manager.get_agent("editor")
        
        analysis = analysis_result["analysis"]
        test_data = test_result["test_result"]
        
        input_data = {
            "prompt_content": prompt["content"],
            "prompt_id": prompt["id"],
            "specification": prompt["specification"],
            "version": prompt["version"],
            "feedback": analysis["feedback"],
            "suggestions": analysis["suggestions"],
            "test_results": test_data
        }
        
        result = await editor_agent.run(input_data)
        
        if result.success:
            edit_data = result.result_data["prompt_edit"]
            updated_prompt = result.result_data["updated_prompt"]
            self.prompt_store.save_prompt_edit(edit_data)
            self.prompt_store.save_prompt(updated_prompt)
            return {
                "success": True,
                "prompt_edit": edit_data,
                "updated_prompt": updated_prompt,
                "agent_result": result.dict()
            }
        else:
            raise Exception(f"Ошибка редактирования: {result.error_message}")
    
    def _generate_lifecycle_summary(self, lifecycle_results: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация сводки жизненного цикла"""
        phases = lifecycle_results["phases"]
        
        summary = {
            "total_phases": len(phases),
            "successful_phases": sum(1 for phase in phases.values() if phase.get("success", False)),
            "final_prompt": None,
            "key_metrics": {}
        }
        
        # Получение финального промпта
        if "editing" in phases and phases["editing"]["success"]:
            summary["final_prompt"] = phases["editing"]["updated_prompt"]
        elif "generation" in phases and phases["generation"]["success"]:
            summary["final_prompt"] = phases["generation"]["prompt"]
        
        # Ключевые метрики
        if "analysis" in phases and phases["analysis"]["success"]:
            analysis = phases["analysis"]["analysis"]
            summary["key_metrics"]["clarity"] = analysis["clarity_score"]
            summary["key_metrics"]["relevance"] = analysis["relevance_score"]
            summary["key_metrics"]["adaptability"] = analysis["adaptability_score"]
            summary["key_metrics"]["overall"] = analysis["overall_score"]
        
        if "testing" in phases and phases["testing"]["success"]:
            test_data = phases["testing"]["test_result"]
            metrics = test_data["metrics"]
            summary["key_metrics"]["accuracy"] = metrics["accuracy"]
            summary["key_metrics"]["response_time"] = metrics["response_time"]
            summary["key_metrics"]["token_efficiency"] = metrics["token_efficiency"]
        
        return summary
    
    async def run_comparative_analysis(self, prompt_ids: List[str]) -> Dict[str, Any]:
        """Запуск сравнительного анализа нескольких промптов"""
        self.logger.info(f"Запуск сравнительного анализа для {len(prompt_ids)} промптов")
        
        prompts = []
        analyses = []
        test_results = []
        
        # Сбор данных по всем промптам
        for prompt_id in prompt_ids:
            prompt = self.prompt_store.get_prompt(prompt_id)
            if prompt:
                prompts.append(prompt)
                
                analysis = self.prompt_store.get_analysis(prompt_id)
                if analysis:
                    analyses.append(analysis)
                
                test_result = self.prompt_store.get_test_result(prompt_id)
                if test_result:
                    test_results.append(test_result)
        
        # Сравнительный анализ
        comparison = self._compare_prompts(prompts, analyses, test_results)
        
        return {
            "prompt_ids": prompt_ids,
            "prompts": prompts,
            "analyses": analyses,
            "test_results": test_results,
            "comparison": comparison
        }
    
    def _compare_prompts(self, prompts: List[Dict], analyses: List[Dict], 
                        test_results: List[Dict]) -> Dict[str, Any]:
        """Сравнение промптов"""
        if not prompts:
            return {"error": "Нет промптов для сравнения"}
        
        # Создание матрицы сравнения
        comparison_matrix = {}
        
        for i, prompt in enumerate(prompts):
            prompt_id = prompt["id"]
            comparison_matrix[prompt_id] = {
                "prompt": prompt,
                "analysis": analyses[i] if i < len(analyses) else None,
                "test_result": test_results[i] if i < len(test_results) else None,
                "scores": {}
            }
            
            # Вычисление общих оценок
            if analyses[i]:
                analysis = analyses[i]
                comparison_matrix[prompt_id]["scores"]["analysis"] = analysis["overall_score"]
            
            if test_results[i]:
                test_data = test_results[i]
                metrics = test_data["metrics"]
                comparison_matrix[prompt_id]["scores"]["testing"] = (
                    metrics["accuracy"] + metrics["relevance"] + metrics["token_efficiency"]
                ) / 3
        
        # Определение лучшего промпта
        best_prompt_id = max(
            comparison_matrix.keys(),
            key=lambda pid: comparison_matrix[pid]["scores"].get("analysis", 0) + 
                           comparison_matrix[pid]["scores"].get("testing", 0)
        )
        
        return {
            "comparison_matrix": comparison_matrix,
            "best_prompt_id": best_prompt_id,
            "ranking": sorted(
                comparison_matrix.keys(),
                key=lambda pid: comparison_matrix[pid]["scores"].get("analysis", 0) + 
                               comparison_matrix[pid]["scores"].get("testing", 0),
                reverse=True
            )
        }