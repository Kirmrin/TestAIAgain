from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from loguru import logger

from core.orchestrator import PromptLifecycleOrchestrator
from core.agent_manager import AgentManager
from core.prompt_store import PromptStore
from models.test_models import TestParameters

router = APIRouter()
orchestrator = PromptLifecycleOrchestrator()
agent_manager = AgentManager()
prompt_store = PromptStore()


# Модели запросов
class LifecycleRequest(BaseModel):
    specification: str
    context: Optional[str] = ""
    requirements: Optional[List[str]] = []
    test_parameters: Optional[TestParameters] = None


class PromptRequest(BaseModel):
    content: str
    specification: str
    context: Optional[str] = ""
    requirements: Optional[List[str]] = []


class AnalysisRequest(BaseModel):
    prompt_id: str
    context: Optional[str] = ""


class TestRequest(BaseModel):
    prompt_id: str
    test_parameters: Optional[TestParameters] = None


class EditRequest(BaseModel):
    prompt_id: str
    feedback: Optional[str] = ""
    suggestions: Optional[List[str]] = []


class ComparativeAnalysisRequest(BaseModel):
    prompt_ids: List[str]


# Роуты для жизненного цикла
@router.post("/lifecycle/full")
async def run_full_lifecycle(request: LifecycleRequest):
    """Запуск полного жизненного цикла промпта"""
    try:
        result = await orchestrator.run_full_lifecycle(
            specification=request.specification,
            test_parameters=request.test_parameters,
            context=request.context,
            requirements=request.requirements
        )
        return result
    except Exception as e:
        logger.error(f"Ошибка в полном жизненном цикле: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/lifecycle/generate")
async def generate_prompt(request: PromptRequest):
    """Генерация промпта"""
    try:
        result = await orchestrator._generate_phase(
            specification=request.specification,
            context=request.context,
            requirements=request.requirements
        )
        return result
    except Exception as e:
        logger.error(f"Ошибка генерации промпта: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/lifecycle/analyze")
async def analyze_prompt(request: AnalysisRequest):
    """Анализ промпта"""
    try:
        prompt = prompt_store.get_prompt(request.prompt_id)
        if not prompt:
            raise HTTPException(status_code=404, detail="Промпт не найден")
        
        result = await orchestrator._analyze_phase(prompt)
        return result
    except Exception as e:
        logger.error(f"Ошибка анализа промпта: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/lifecycle/test")
async def test_prompt(request: TestRequest):
    """Тестирование промпта"""
    try:
        prompt = prompt_store.get_prompt(request.prompt_id)
        if not prompt:
            raise HTTPException(status_code=404, detail="Промпт не найден")
        
        result = await orchestrator._test_phase(prompt, request.test_parameters)
        return result
    except Exception as e:
        logger.error(f"Ошибка тестирования промпта: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/lifecycle/edit")
async def edit_prompt(request: EditRequest):
    """Редактирование промпта"""
    try:
        prompt = prompt_store.get_prompt(request.prompt_id)
        if not prompt:
            raise HTTPException(status_code=404, detail="Промпт не найден")
        
        # Получение анализа и результатов тестирования
        analysis = prompt_store.get_analysis(request.prompt_id)
        test_result = prompt_store.get_test_result(request.prompt_id)
        
        analysis_result = {"analysis": analysis} if analysis else None
        test_result_data = {"test_result": test_result} if test_result else None
        
        result = await orchestrator._edit_phase(prompt, analysis_result, test_result_data)
        return result
    except Exception as e:
        logger.error(f"Ошибка редактирования промпта: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Роуты для сравнительного анализа
@router.post("/comparative/analyze")
async def run_comparative_analysis(request: ComparativeAnalysisRequest):
    """Запуск сравнительного анализа промптов"""
    try:
        result = await orchestrator.run_comparative_analysis(request.prompt_ids)
        return result
    except Exception as e:
        logger.error(f"Ошибка сравнительного анализа: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Роуты для управления промптами
@router.get("/prompts")
async def list_prompts():
    """Список всех промптов"""
    try:
        prompts = prompt_store.list_prompts()
        return {"prompts": prompts, "count": len(prompts)}
    except Exception as e:
        logger.error(f"Ошибка получения списка промптов: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/prompts/{prompt_id}")
async def get_prompt(prompt_id: str):
    """Получение промпта по ID"""
    try:
        prompt = prompt_store.get_prompt(prompt_id)
        if not prompt:
            raise HTTPException(status_code=404, detail="Промпт не найден")
        return prompt
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения промпта: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/prompts/{prompt_id}/history")
async def get_prompt_history(prompt_id: str):
    """Получение полной истории промпта"""
    try:
        history = prompt_store.get_prompt_history(prompt_id)
        if not history["prompt"]:
            raise HTTPException(status_code=404, detail="Промпт не найден")
        return history
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения истории промпта: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/prompts/search/{query}")
async def search_prompts(query: str):
    """Поиск промптов"""
    try:
        results = prompt_store.search_prompts(query)
        return {"results": results, "count": len(results), "query": query}
    except Exception as e:
        logger.error(f"Ошибка поиска промптов: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/prompts/status/{status}")
async def get_prompts_by_status(status: str):
    """Получение промптов по статусу"""
    try:
        prompts = prompt_store.get_prompts_by_status(status)
        return {"prompts": prompts, "count": len(prompts), "status": status}
    except Exception as e:
        logger.error(f"Ошибка получения промптов по статусу: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/prompts/{prompt_id}")
async def delete_prompt(prompt_id: str):
    """Удаление промпта"""
    try:
        success = prompt_store.delete_prompt(prompt_id)
        if not success:
            raise HTTPException(status_code=404, detail="Промпт не найден")
        return {"message": "Промпт успешно удален", "prompt_id": prompt_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка удаления промпта: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Роуты для управления агентами
@router.get("/agents")
async def list_agents():
    """Список всех агентов"""
    try:
        agents = agent_manager.list_agents()
        return {"agents": agents}
    except Exception as e:
        logger.error(f"Ошибка получения списка агентов: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/status")
async def get_agent_status():
    """Статус всех агентов"""
    try:
        status = agent_manager.get_agent_status()
        return {"status": status}
    except Exception as e:
        logger.error(f"Ошибка получения статуса агентов: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agents/{agent_id}/enable")
async def enable_agent(agent_id: str):
    """Включение агента"""
    try:
        agent_manager.enable_agent(agent_id)
        return {"message": f"Агент {agent_id} включен"}
    except Exception as e:
        logger.error(f"Ошибка включения агента: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agents/{agent_id}/disable")
async def disable_agent(agent_id: str):
    """Отключение агента"""
    try:
        agent_manager.disable_agent(agent_id)
        return {"message": f"Агент {agent_id} отключен"}
    except Exception as e:
        logger.error(f"Ошибка отключения агента: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Роуты для статистики
@router.get("/stats/overview")
async def get_system_overview():
    """Общая статистика системы"""
    try:
        prompts = prompt_store.list_prompts()
        
        stats = {
            "total_prompts": len(prompts),
            "prompts_by_status": {},
            "recent_activity": {
                "last_24h": 0,
                "last_7_days": 0,
                "last_30_days": 0
            }
        }
        
        # Статистика по статусам
        for prompt in prompts:
            status = prompt.get("status", "unknown")
            stats["prompts_by_status"][status] = stats["prompts_by_status"].get(status, 0) + 1
        
        return stats
    except Exception as e:
        logger.error(f"Ошибка получения статистики: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))