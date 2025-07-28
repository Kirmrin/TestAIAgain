import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger


class PromptStore:
    """Хранилище промптов и связанных данных"""
    
    def __init__(self, storage_dir: str = "data"):
        self.storage_dir = storage_dir
        self._ensure_storage_dirs()
    
    def _ensure_storage_dirs(self):
        """Создание директорий для хранения данных"""
        dirs = [
            self.storage_dir,
            f"{self.storage_dir}/prompts",
            f"{self.storage_dir}/analyses",
            f"{self.storage_dir}/tests",
            f"{self.storage_dir}/edits"
        ]
        
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
    
    def save_prompt(self, prompt_data: Dict[str, Any]):
        """Сохранение промпта"""
        prompt_id = prompt_data["id"]
        file_path = f"{self.storage_dir}/prompts/{prompt_id}.json"
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(prompt_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Промпт сохранен: {prompt_id}")
        except Exception as e:
            logger.error(f"Ошибка сохранения промпта {prompt_id}: {str(e)}")
    
    def get_prompt(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """Получение промпта по ID"""
        file_path = f"{self.storage_dir}/prompts/{prompt_id}.json"
        
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning(f"Промпт не найден: {prompt_id}")
                return None
        except Exception as e:
            logger.error(f"Ошибка чтения промпта {prompt_id}: {str(e)}")
            return None
    
    def list_prompts(self) -> List[Dict[str, Any]]:
        """Список всех промптов"""
        prompts = []
        prompts_dir = f"{self.storage_dir}/prompts"
        
        try:
            for filename in os.listdir(prompts_dir):
                if filename.endswith('.json'):
                    prompt_id = filename[:-5]  # Убираем .json
                    prompt = self.get_prompt(prompt_id)
                    if prompt:
                        prompts.append(prompt)
        except Exception as e:
            logger.error(f"Ошибка получения списка промптов: {str(e)}")
        
        return prompts
    
    def save_analysis(self, analysis_data: Dict[str, Any]):
        """Сохранение анализа промпта"""
        analysis_id = analysis_data["id"]
        file_path = f"{self.storage_dir}/analyses/{analysis_id}.json"
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Анализ сохранен: {analysis_id}")
        except Exception as e:
            logger.error(f"Ошибка сохранения анализа {analysis_id}: {str(e)}")
    
    def get_analysis(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """Получение анализа по ID промпта"""
        analyses_dir = f"{self.storage_dir}/analyses"
        
        try:
            for filename in os.listdir(analyses_dir):
                if filename.endswith('.json'):
                    file_path = f"{analyses_dir}/{filename}"
                    with open(file_path, 'r', encoding='utf-8') as f:
                        analysis = json.load(f)
                        if analysis.get("prompt_id") == prompt_id:
                            return analysis
        except Exception as e:
            logger.error(f"Ошибка поиска анализа для промпта {prompt_id}: {str(e)}")
        
        return None
    
    def save_test_result(self, test_data: Dict[str, Any]):
        """Сохранение результата тестирования"""
        test_id = test_data["test_id"]
        file_path = f"{self.storage_dir}/tests/{test_id}.json"
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(test_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Результат тестирования сохранен: {test_id}")
        except Exception as e:
            logger.error(f"Ошибка сохранения результата тестирования {test_id}: {str(e)}")
    
    def get_test_result(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """Получение результата тестирования по ID промпта"""
        tests_dir = f"{self.storage_dir}/tests"
        
        try:
            for filename in os.listdir(tests_dir):
                if filename.endswith('.json'):
                    file_path = f"{tests_dir}/{filename}"
                    with open(file_path, 'r', encoding='utf-8') as f:
                        test_result = json.load(f)
                        if test_result.get("prompt_id") == prompt_id:
                            return test_result
        except Exception as e:
            logger.error(f"Ошибка поиска результата тестирования для промпта {prompt_id}: {str(e)}")
        
        return None
    
    def save_prompt_edit(self, edit_data: Dict[str, Any]):
        """Сохранение редактирования промпта"""
        edit_id = edit_data["id"]
        file_path = f"{self.storage_dir}/edits/{edit_id}.json"
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(edit_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Редактирование сохранено: {edit_id}")
        except Exception as e:
            logger.error(f"Ошибка сохранения редактирования {edit_id}: {str(e)}")
    
    def get_prompt_edits(self, prompt_id: str) -> List[Dict[str, Any]]:
        """Получение всех редактирований промпта"""
        edits = []
        edits_dir = f"{self.storage_dir}/edits"
        
        try:
            for filename in os.listdir(edits_dir):
                if filename.endswith('.json'):
                    file_path = f"{edits_dir}/{filename}"
                    with open(file_path, 'r', encoding='utf-8') as f:
                        edit = json.load(f)
                        if edit.get("prompt_id") == prompt_id:
                            edits.append(edit)
        except Exception as e:
            logger.error(f"Ошибка поиска редактирований для промпта {prompt_id}: {str(e)}")
        
        return edits
    
    def get_prompt_history(self, prompt_id: str) -> Dict[str, Any]:
        """Получение полной истории промпта"""
        history = {
            "prompt": None,
            "analyses": [],
            "test_results": [],
            "edits": []
        }
        
        # Основной промпт
        history["prompt"] = self.get_prompt(prompt_id)
        
        # Анализы
        analysis = self.get_analysis(prompt_id)
        if analysis:
            history["analyses"].append(analysis)
        
        # Результаты тестирования
        test_result = self.get_test_result(prompt_id)
        if test_result:
            history["test_results"].append(test_result)
        
        # Редактирования
        history["edits"] = self.get_prompt_edits(prompt_id)
        
        return history
    
    def search_prompts(self, query: str) -> List[Dict[str, Any]]:
        """Поиск промптов по содержимому"""
        results = []
        prompts = self.list_prompts()
        
        query_lower = query.lower()
        
        for prompt in prompts:
            content = prompt.get("content", "").lower()
            specification = prompt.get("specification", "").lower()
            
            if query_lower in content or query_lower in specification:
                results.append(prompt)
        
        return results
    
    def get_prompts_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Получение промптов по статусу"""
        results = []
        prompts = self.list_prompts()
        
        for prompt in prompts:
            if prompt.get("status") == status:
                results.append(prompt)
        
        return results
    
    def delete_prompt(self, prompt_id: str) -> bool:
        """Удаление промпта и всех связанных данных"""
        try:
            # Удаление основного промпта
            prompt_file = f"{self.storage_dir}/prompts/{prompt_id}.json"
            if os.path.exists(prompt_file):
                os.remove(prompt_file)
            
            # Удаление связанных данных
            self._delete_related_data(prompt_id)
            
            logger.info(f"Промпт удален: {prompt_id}")
            return True
        except Exception as e:
            logger.error(f"Ошибка удаления промпта {prompt_id}: {str(e)}")
            return False
    
    def _delete_related_data(self, prompt_id: str):
        """Удаление связанных данных промпта"""
        # Удаление анализов
        analyses_dir = f"{self.storage_dir}/analyses"
        for filename in os.listdir(analyses_dir):
            file_path = f"{analyses_dir}/{filename}"
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    analysis = json.load(f)
                    if analysis.get("prompt_id") == prompt_id:
                        os.remove(file_path)
            except:
                pass
        
        # Удаление результатов тестирования
        tests_dir = f"{self.storage_dir}/tests"
        for filename in os.listdir(tests_dir):
            file_path = f"{tests_dir}/{filename}"
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    test_result = json.load(f)
                    if test_result.get("prompt_id") == prompt_id:
                        os.remove(file_path)
            except:
                pass
        
        # Удаление редактирований
        edits_dir = f"{self.storage_dir}/edits"
        for filename in os.listdir(edits_dir):
            file_path = f"{edits_dir}/{filename}"
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    edit = json.load(f)
                    if edit.get("prompt_id") == prompt_id:
                        os.remove(file_path)
            except:
                pass