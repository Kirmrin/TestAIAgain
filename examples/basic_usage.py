#!/usr/bin/env python3
"""
Пример базового использования многоагентной системы тестирования промптов
"""

import asyncio
import os
from dotenv import load_dotenv

from core.orchestrator import PromptLifecycleOrchestrator
from models.test_models import TestParameters

# Загрузка переменных окружения
load_dotenv()


async def main():
    """Основная функция примера"""
    print("🚀 Запуск многоагентной системы тестирования промптов")
    
    # Создание оркестратора
    orchestrator = PromptLifecycleOrchestrator()
    
    # Пример спецификации для промпта
    specification = """
    Создай промпт для анализа тональности текста. 
    Промпт должен:
    - Определять эмоциональную окраску текста
    - Классифицировать тональность как позитивную, негативную или нейтральную
    - Предоставлять краткое обоснование оценки
    - Работать с текстами на русском языке
    """
    
    # Параметры тестирования
    test_parameters = TestParameters(
        temperature=[0.1, 0.5, 0.9],
        max_tokens=[200, 500],
        top_p=[0.5, 0.9],
        test_inputs=[
            "Я очень рад, что сегодня прекрасная погода!",
            "Этот продукт ужасен, не рекомендую никому.",
            "Сегодня обычный день, ничего особенного не произошло."
        ],
        iterations=2
    )
    
    print(f"📝 Спецификация: {specification.strip()}")
    print("🔄 Запуск полного жизненного цикла...")
    
    try:
        # Запуск полного жизненного цикла
        result = await orchestrator.run_full_lifecycle(
            specification=specification,
            test_parameters=test_parameters,
            context="Анализ тональности для социальных сетей",
            requirements=[
                "Высокая точность классификации",
                "Быстрое выполнение",
                "Понятные результаты"
            ]
        )
        
        if result["success"]:
            print("✅ Жизненный цикл завершен успешно!")
            
            # Вывод результатов
            summary = result["summary"]
            print(f"\n📊 Результаты:")
            print(f"- Всего фаз: {summary['total_phases']}")
            print(f"- Успешных фаз: {summary['successful_phases']}")
            
            if summary["final_prompt"]:
                print(f"\n🎯 Финальный промпт:")
                print(summary["final_prompt"]["content"])
            
            if summary["key_metrics"]:
                print(f"\n📈 Ключевые метрики:")
                for metric, value in summary["key_metrics"].items():
                    print(f"- {metric}: {value:.2f}")
            
            # Детальные результаты по фазам
            phases = result["phases"]
            
            if "generation" in phases:
                print(f"\n🔧 Фаза генерации:")
                prompt = phases["generation"]["prompt"]
                print(f"- ID промпта: {prompt['id']}")
                print(f"- Статус: {prompt['status']}")
            
            if "analysis" in phases:
                print(f"\n📋 Фаза анализа:")
                analysis = phases["analysis"]["analysis"]
                print(f"- Ясность: {analysis['clarity_score']:.2f}")
                print(f"- Релевантность: {analysis['relevance_score']:.2f}")
                print(f"- Адаптивность: {analysis['adaptability_score']:.2f}")
                print(f"- Общая оценка: {analysis['overall_score']:.2f}")
            
            if "testing" in phases:
                print(f"\n🧪 Фаза тестирования:")
                test_result = phases["testing"]["test_result"]
                metrics = test_result["metrics"]
                print(f"- Точность: {metrics['accuracy']:.2f}")
                print(f"- Время ответа: {metrics['response_time']:.2f} сек")
                print(f"- Эффективность токенов: {metrics['token_efficiency']:.2f}")
                print(f"- Всего тестов: {len(test_result['test_cases'])}")
            
            if "editing" in phases:
                print(f"\n✏️ Фаза редактирования:")
                edit = phases["editing"]["prompt_edit"]
                print(f"- Причина редактирования: {edit['edit_reason']}")
                print(f"- Количество улучшений: {len(edit['improvements'])}")
        
        else:
            print(f"❌ Ошибка в жизненном цикле: {result.get('error', 'Неизвестная ошибка')}")
    
    except Exception as e:
        print(f"❌ Ошибка выполнения: {str(e)}")


async def comparative_example():
    """Пример сравнительного анализа"""
    print("\n🔄 Запуск сравнительного анализа...")
    
    orchestrator = PromptLifecycleOrchestrator()
    
    # Создание нескольких промптов для сравнения
    specifications = [
        "Создай промпт для анализа тональности текста",
        "Создай промпт для определения эмоций в тексте",
        "Создай промпт для классификации настроения текста"
    ]
    
    prompt_ids = []
    
    # Генерация промптов
    for spec in specifications:
        result = await orchestrator.run_full_lifecycle(
            specification=spec,
            context="Анализ эмоций в тексте"
        )
        if result["success"]:
            prompt_id = result["summary"]["final_prompt"]["id"]
            prompt_ids.append(prompt_id)
    
    if len(prompt_ids) >= 2:
        # Сравнительный анализ
        comparison = await orchestrator.run_comparative_analysis(prompt_ids)
        
        print(f"\n📊 Сравнительный анализ {len(prompt_ids)} промптов:")
        print(f"- Лучший промпт: {comparison['comparison']['best_prompt_id']}")
        print(f"- Ранжирование: {comparison['comparison']['ranking']}")
        
        # Детальное сравнение
        matrix = comparison['comparison']['comparison_matrix']
        for prompt_id, data in matrix.items():
            scores = data['scores']
            print(f"\nПромпт {prompt_id}:")
            print(f"- Анализ: {scores.get('analysis', 0):.2f}")
            print(f"- Тестирование: {scores.get('testing', 0):.2f}")


if __name__ == "__main__":
    # Проверка наличия API ключа
    if not os.getenv("GIGACHAT_CREDENTIALS"):
        print("⚠️  Внимание: GIGACHAT_CREDENTIALS не установлен!")
        print("Создайте файл .env на основе .env.example и добавьте ваши учетные данные GigaChat")
    else:
        # Запуск примеров
        asyncio.run(main())
        asyncio.run(comparative_example())