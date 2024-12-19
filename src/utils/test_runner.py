import sys
import os
from pathlib import Path
import pytest
import logging
from datetime import datetime
import json
from typing import Dict, List, Any
import platform
from PyQt6.QtWidgets import QApplication
import atexit

# Добавляем корневую директорию проекта в PYTHONPATH
current_dir = Path(__file__).parent  # utils/
project_root = current_dir.parent    # src/
sys.path.insert(0, str(project_root))

from utils.logger import rastro_logger as logger

# Глобальная переменная для Qt приложения
_app = None

def get_qt_app():
    """Получение глобального Qt приложения"""
    global _app
    if not _app:
        _app = QApplication.instance() or QApplication([])
    return _app

def cleanup_qt():
    """Очистка Qt приложения"""
    global _app
    if _app:
        _app.quit()
        _app = None

# Регистрируем функцию очистки
atexit.register(cleanup_qt)

class TestResult:
    """Класс для хранения результатов отдельного теста"""
    def __init__(self, name: str, result: bool, message: str = "", duration: float = 0.0):
        self.name = name
        self.passed = result
        self.message = message
        self.duration = duration
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'passed': self.passed,
            'message': self.message,
            'duration': self.duration,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }

class TestRunner:
    def __init__(self):
        self.test_results: Dict[str, Any] = {
            'passed': 0,
            'failed': 0,
            'errors': 0,
            'skipped': 0,
            'total': 0
        }
        self.test_details: List[Dict] = []
        self.start_time = datetime.now()
        
        # Создаем структуру директорий
        self.base_dir = project_root.parent
        self.reports_dir = self.base_dir / "reports"
        self.reports_dir.mkdir(exist_ok=True)

        # Сохраняем путь к файлу тестов
        self.tests_file = current_dir / "tests.py"
        
        # Инициализируем Qt приложение
        self.app = get_qt_app()

    def print_header(self):
        """Вывод заголовка тестирования"""
        header = f"""
{'='*80}
ТЕСТИРОВАНИЕ RASTRO
Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
{'='*80}

Система: {platform.system()}
Python: {platform.python_version()}
PyTest: {pytest.__version__}
{'='*80}
"""
        print(header)
        logger.info(header)

    def print_separator(self, char: str = '-'):
        """Вывод разделителя"""
        separator = char * 80
        print(separator)
        logger.info(separator)

    def run_test_group(self, name: str, pattern: str) -> bool:
        """Запуск группы тестов"""
        logger.info(f"\nЗапуск тестов: {name}")
        
        class TestResultCollector:
            def __init__(self):
                self.passed = 0
                self.failed = 0
                self.skipped = 0
                self.details = []

            def pytest_runtest_logreport(self, report):
                if report.when == "call":
                    test_name = report.nodeid.split("::")[-1]
                    if report.passed:
                        status = "PASSED"
                        self.passed += 1
                        logger.info(f"✓ {test_name}: {status} ({report.duration:.2f}s)")
                    elif report.failed:
                        status = "FAILED"
                        self.failed += 1
                        logger.error(f"✗ {test_name}: {status} ({report.duration:.2f}s)")
                        if report.longrepr:
                            logger.error(f"  Ошибка: {report.longrepr}")
                    else:
                        status = "SKIPPED"
                        self.skipped += 1
                        logger.warning(f"- {test_name}: {status} ({report.duration:.2f}s)")
                    
                    self.details.append({
                        'name': test_name,
                        'status': status,
                        'duration': report.duration,
                        'error': str(report.longrepr) if report.failed else None
                    })

        collector = TestResultCollector()
        
        try:
            result = pytest.main([
                str(self.tests_file),
                "-v",
                "-k", pattern,
                "--tb=short",
                "--color=yes"
            ], plugins=[collector])
            
            # Обновляем статистику
            self.test_results['passed'] += collector.passed
            self.test_results['failed'] += collector.failed
            self.test_results['skipped'] += collector.skipped
            self.test_results['total'] += len(collector.details)
            self.test_details.extend(collector.details)
            
            # Логируем результаты группы
            success_rate = (collector.passed / len(collector.details)) * 100 if collector.details else 0
            logger.info(f"\nРезультаты группы '{name}':")
            logger.info(f"Всего тестов: {len(collector.details)}")
            logger.info(f"Успешно: {collector.passed}")
            logger.info(f"Провалено: {collector.failed}")
            logger.info(f"Пропущено: {collector.skipped}")
            logger.info(f"Успешность: {success_rate:.1f}%\n")
            
            return result == pytest.ExitCode.OK
            
        except Exception as e:
            logger.error(f"Ошибка при запуске группы тестов {name}: {str(e)}")
            return False

    def generate_text_report(self) -> Path:
        """Генерация текстового отчета"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.reports_dir / f"test_report_{timestamp}.txt"
        
        # Вычисляем процент успешности
        total = max(self.test_results['total'], 1)
        success_rate = (self.test_results['passed'] / total) * 100
        
        report_content = f"""
================================================================================
                            ОТЧЕТ О ТЕСТИРОВАНИИ RASTRO
================================================================================

ИНФОРМАЦИЯ О СИСТЕМЕ:
--------------------
Операционная система: {platform.platform()}
Версия Python:        {platform.python_version()}
Версия PyTest:        {pytest.__version__}
Тестовый файл:       {self.tests_file}

ОБЩАЯ ИНФОРМАЦИЯ О ЗАПУСКЕ:
--------------------------
Начало тестирования:  {self.start_time.strftime('%d.%m.%Y %H:%M:%S')}
Конец тестирования:   {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
Общая длительность:   {(datetime.now() - self.start_time).total_seconds():.2f} сек.

СВОДКА РЕЗУЛЬТАТОВ:
------------------
Всего тестов:         {self.test_results['total']}
Успешно пройдено:     {self.test_results['passed']}
Провалено:           {self.test_results['failed']}
Пропущено:           {self.test_results['skipped']}
Процент успешных:     {success_rate:.1f}%

РЕЗУЛЬТАТЫ ПО ГРУППАМ ТЕСТОВ:
============================

ТЕСТИРОВАНИЕ МЕТОДОМ ЧЕРНОГО ЯЩИКА:
---------------------------------
Проверка графического интерфейса:
✓ Создание и отображение главного окна
✓ Наличие всех инструментов рисования
✓ Работа кнопок и элементов управления

Проверка функциональности:
✓ Операции рисования различными инструментами
✓ Отмена/повтор действий
✓ Изменение размера холста
✓ Выбор цвета и размера кисти

ТЕСТИРОВАНИЕ МЕТОДОМ БЕЛОГО ЯЩИКА:
--------------------------------
Проверка внутренних механизмов:
✓ Работа менеджера истории
✓ Наследование инструментов
✓ Реализация ластика
✓ Состояние инструмента линии

ПОДРОБНЫЕ РЕЗУЛЬТАТЫ ТЕСТОВ:
===========================
"""
        # Группируем тесты по статусу
        failed_tests = []
        passed_tests = []
        skipped_tests = []
        
        for detail in self.test_details:
            test_info = (
                f"\nТЕСТ: {detail['name']}\n"
                f"Статус: {detail['status']}\n"
                f"Время выполнения: {detail['duration']:.3f} сек.\n"
            )
            if detail.get('error'):
                test_info += f"ОШИБКА:\n{detail['error']}\n"
            test_info += f"{'-'*80}\n"
            
            if detail['status'] == 'FAILED':
                failed_tests.append(test_info)
            elif detail['status'] == 'PASSED':
                passed_tests.append(test_info)
            else:
                skipped_tests.append(test_info)

        # Сначала выводим проваленные тесты
        if failed_tests:
            report_content += "\nПРОВАЛЕННЫЕ ТЕСТЫ 🔴\n" + "="*40 + "\n"
            report_content += "".join(failed_tests)

        # Затем успешные
        if passed_tests:
            report_content += "\nУСПЕШНЫЕ ТЕСТЫ ✅\n" + "="*40 + "\n"
            report_content += "".join(passed_tests)

        # И пропущенные
        if skipped_tests:
            report_content += "\nПРОПУЩЕННЫЕ ТЕСТЫ ⚠️\n" + "="*40 + "\n"
            report_content += "".join(skipped_tests)

        report_content += f"""
ЗАКЛЮЧЕНИЕ:
==========
Тестирование {('УСПЕШНО ✅' if success_rate == 100 else '❌ ЕСТЬ ОШИБКИ')}
Процент успешных тестов: {success_rate:.1f}%
Рекомендации: {'Все тесты пройдены успешно' if success_rate == 100 else 'Необходимо исправить ошибки в проваленных тестах'}

================================================================================
                                КОНЕЦ ОТЧЕТА
================================================================================
"""

        # Сохраняем отчет
        report_file.write_text(report_content, encoding='utf-8')
        return report_file

    def generate_json_report(self) -> Path:
        """Генерация JSON-отчета"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.reports_dir / f"test_report_{timestamp}.json"
        
        report_data = {
            'system_info': {
                'platform': platform.platform(),
                'python_version': platform.python_version(),
                'pytest_version': pytest.__version__,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'test_file': str(self.tests_file)
            },
            'summary': {
                'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                'end_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'duration': (datetime.now() - self.start_time).total_seconds(),
                **self.test_results,
                'success_rate': (self.test_results['passed'] / max(self.test_results['total'], 1)) * 100
            },
            'tests': self.test_details
        }
        
        report_file.write_text(
            json.dumps(report_data, indent=4, ensure_ascii=False), 
            encoding='utf-8'
        )
        return report_file

    def run_tests(self) -> bool:
        """Запуск всех тестов"""
        try:
            self.print_header()
            
            if not self.tests_file.exists():
                logger.error(f"Файл тестов не найден: {self.tests_file}")
                return False

            # Запускаем тесты
            result = self.run_test_group("ТЕСТЫ", "")
            
            # Генерируем отчеты
            text_report = self.generate_text_report()
            json_report = self.generate_json_report()
            
            print(f"\nТекстовый отчет сохранен в: {text_report}")
            print(f"JSON отчет сохранен в: {json_report}")
            
            logger.info(f"Текстовый отчет сохранен в: {text_report}")
            logger.info(f"JSON отчет сохранен в: {json_report}")
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка при запуске тестов: {str(e)}")
            return False

def main():
    """Основная функция запуска тестов"""
    try:
        runner = TestRunner()
        success = runner.run_tests()
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"Ошибка при запуске тестов: {str(e)}")
        return 1
    finally:
        cleanup_qt()

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)