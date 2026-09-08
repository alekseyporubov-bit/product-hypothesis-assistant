"""
Research Finder - Система поиска исследований в открытых источниках
для обогащения анализа гипотез данными из реальных исследований

Интегрирует:
- Google Scholar API (через SerpAPI)
- ArXiv API (для научных статей)
- Semantic Scholar API (для доступа к полнотекстовым статьям)
"""

import os
import json
from typing import List, Dict, Optional
import requests
from datetime import datetime


class ResearchResult:
    """Результат поиска исследования"""
    def __init__(self, title: str, authors: List[str], year: int, 
                 url: str, abstract: str, source: str, relevance_score: float = 0.8):
        self.title = title
        self.authors = authors
        self.year = year
        self.url = url
        self.abstract = abstract
        self.source = source  # "google_scholar", "arxiv", "semantic_scholar"
        self.relevance_score = relevance_score  # 0-1
    
    def to_dict(self):
        return {
            "title": self.title,
            "authors": self.authors,
            "year": self.year,
            "url": self.url,
            "abstract": self.abstract,
            "source": self.source,
            "relevance_score": self.relevance_score
        }


class ResearchFinder:
    """
    Система поиска исследований в открытых источниках
    
    Поддерживает:
    1. Google Scholar (через SerpAPI)
    2. ArXiv (научные статьи)
    3. Semantic Scholar (общественный API)
    """
    
    def __init__(self):
        # API ключи (можно подставить из переменных окружения)
        self.serpapi_key = os.getenv('SERPAPI_KEY')
        self.enable_remote = False  # По умолчанию отключаем реальные запросы
        
        # Кэш результатов для демо
        self.research_cache = {}
    
    def search_problem_severity(self, problem_statement: str, 
                                target_users: str) -> Dict:
        """
        Ищет исследования о серьёзности проблемы
        
        Использует Google Scholar для поиска релевантных исследований о:
        - Распространённости проблемы
        - Влиянии проблемы на целевую аудиторию
        - Статистике проблемы в разных регионах
        """
        
        # Формируем поисковый запрос
        search_query = f"{problem_statement} {target_users} problem severity"
        
        results = self._search_research(search_query, limit=5)
        
        # Анализируем результаты
        return {
            "query": search_query,
            "research_count": len(results),
            "research_sources": [r.to_dict() for r in results],
            "average_relevance": sum(r.relevance_score for r in results) / len(results) if results else 0,
            "recommendation": self._analyze_problem_severity(results)
        }
    
    def search_market_size(self, product_category: str, 
                          target_users: str) -> Dict:
        """
        Ищет исследования о размере рынка
        
        Использует поиск рыночных отчётов о:
        - Размере целевого рынка (TAM)
        - Темпе роста рынка
        - Прогнозах развития
        """
        
        search_query = f"{product_category} market size {target_users} TAM"
        results = self._search_research(search_query, limit=5)
        
        return {
            "query": search_query,
            "research_count": len(results),
            "research_sources": [r.to_dict() for r in results],
            "average_relevance": sum(r.relevance_score for r in results) / len(results) if results else 0
        }
    
    def search_competitive_landscape(self, product_description: str) -> Dict:
        """
        Ищет информацию о конкурентном ландшафте
        
        Находит:
        - Существующие конкурентные решения
        - Их особенности и слабости
        - Возможности для дифференциации
        """
        
        search_query = f"{product_description} competitive analysis alternatives"
        results = self._search_research(search_query, limit=5)
        
        return {
            "query": search_query,
            "research_count": len(results),
            "research_sources": [r.to_dict() for r in results],
            "average_relevance": sum(r.relevance_score for r in results) / len(results) if results else 0
        }
    
    def _search_research(self, query: str, limit: int = 5) -> List[ResearchResult]:
        """Выполняет поиск исследований по запросу"""
        
        # В демо режиме возвращаем заранее подготовленные данные
        if not self.enable_remote:
            return self._get_demo_results(query, limit)
        
        results = []
        
        # 1. Поиск в Google Scholar (через SerpAPI)
        if self.serpapi_key:
            results.extend(self._search_google_scholar(query, limit))
        
        # 2. Поиск в ArXiv
        results.extend(self._search_arxiv(query, limit))
        
        # 3. Поиск в Semantic Scholar
        results.extend(self._search_semantic_scholar(query, limit))
        
        # Сортируем по relevance_score и возвращаем лучшие
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:limit]
    
    def _search_google_scholar(self, query: str, limit: int = 5) -> List[ResearchResult]:
        """Поиск в Google Scholar через SerpAPI"""
        if not self.serpapi_key:
            return []
        
        try:
            url = "https://serpapi.com/search"
            params = {
                "q": query,
                "engine": "google_scholar",
                "api_key": self.serpapi_key,
                "num": limit
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code != 200:
                return []
            
            data = response.json()
            results = []
            
            for item in data.get("organic_results", [])[:limit]:
                result = ResearchResult(
                    title=item.get("title", ""),
                    authors=item.get("publication_info", {}).get("authors", []),
                    year=item.get("publication_info", {}).get("year", 0),
                    url=item.get("link", ""),
                    abstract=item.get("snippet", "")[:200],
                    source="google_scholar",
                    relevance_score=0.85
                )
                results.append(result)
            
            return results
        except Exception as e:
            print(f"Error searching Google Scholar: {e}")
            return []
    
    def _search_arxiv(self, query: str, limit: int = 5) -> List[ResearchResult]:
        """Поиск в ArXiv API"""
        try:
            import urllib.parse
            search_query = urllib.parse.quote(query)
            url = f"http://export.arxiv.org/api/query?search_query=all:{search_query}&start=0&max_results={limit}"
            
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                return []
            
            # Простой парсинг XML ответа (без lxml)
            results = []
            text = response.text
            
            # Извлекаем записи между <entry> и </entry>
            import re
            entries = re.findall(r'<entry>.*?</entry>', text, re.DOTALL)
            
            for entry in entries[:limit]:
                title_match = re.search(r'<title>(.+?)</title>', entry)
                authors_matches = re.findall(r'<name>(.+?)</name>', entry)
                published_match = re.search(r'<published>(\d{4})', entry)
                id_match = re.search(r'<id>http://arxiv.org/abs/(.+?)</id>', entry)
                summary_match = re.search(r'<summary>(.+?)</summary>', entry)
                
                if title_match:
                    result = ResearchResult(
                        title=title_match.group(1).strip(),
                        authors=authors_matches[:3],
                        year=int(published_match.group(1)) if published_match else 0,
                        url=f"https://arxiv.org/abs/{id_match.group(1)}" if id_match else "",
                        abstract=summary_match.group(1).strip()[:200] if summary_match else "",
                        source="arxiv",
                        relevance_score=0.8
                    )
                    results.append(result)
            
            return results
        except Exception as e:
            print(f"Error searching ArXiv: {e}")
            return []
    
    def _search_semantic_scholar(self, query: str, limit: int = 5) -> List[ResearchResult]:
        """Поиск в Semantic Scholar API (публичный, без ключа)"""
        try:
            url = "https://api.semanticscholar.org/graph/v1/paper/search"
            params = {
                "query": query,
                "limit": limit,
                "fields": "title,authors,year,url,abstract"
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code != 200:
                return []
            
            data = response.json()
            results = []
            
            for item in data.get("data", [])[:limit]:
                result = ResearchResult(
                    title=item.get("title", ""),
                    authors=[a.get("name", "") for a in item.get("authors", [])],
                    year=item.get("year", 0),
                    url=item.get("url", ""),
                    abstract=item.get("abstract", "")[:200],
                    source="semantic_scholar",
                    relevance_score=0.75
                )
                results.append(result)
            
            return results
        except Exception as e:
            print(f"Error searching Semantic Scholar: {e}")
            return []
    
    def _get_demo_results(self, query: str, limit: int) -> List[ResearchResult]:
        """
        Возвращает демо-результаты поиска для разработки
        (без реальных API запросов)
        """
        
        demo_data = {
            "problem severity": [
                ResearchResult(
                    title="User Experience Challenges in Mobile Applications: A Comprehensive Study",
                    authors=["Smith J.", "Johnson K.", "Williams M."],
                    year=2023,
                    url="https://scholar.google.com/...",
                    abstract="This study examines major UX challenges affecting 78% of mobile app users...",
                    source="google_scholar",
                    relevance_score=0.92
                ),
                ResearchResult(
                    title="Dark Mode Adoption and Eye Strain Reduction in Digital Interfaces",
                    authors=["Chen L.", "Park S."],
                    year=2023,
                    url="https://arxiv.org/abs/2301.12345",
                    abstract="Empirical research showing 65% reduction in eye strain with dark mode...",
                    source="arxiv",
                    relevance_score=0.88
                ),
                ResearchResult(
                    title="Night Usage Patterns and Visual Fatigue: Industry Report 2023",
                    authors=["Tech Insights Ltd."],
                    year=2023,
                    url="https://semantic.scholar.org/...",
                    abstract="Market analysis of 50,000+ users showing 40% evening/night usage...",
                    source="semantic_scholar",
                    relevance_score=0.85
                ),
            ],
            "market size": [
                ResearchResult(
                    title="Global Mobile App Personalization Market: Growth Trends and Forecasts",
                    authors=["Anderson R.", "Taylor B."],
                    year=2023,
                    url="https://scholar.google.com/...",
                    abstract="Market valued at $3.2B in 2023, expected to reach $8.5B by 2028...",
                    source="google_scholar",
                    relevance_score=0.90
                ),
            ],
            "competitive": [
                ResearchResult(
                    title="Dark Mode Implementation Across Popular Mobile Platforms",
                    authors=["Developer Research Institute"],
                    year=2023,
                    url="https://arxiv.org/abs/2303.54321",
                    abstract="Comparative analysis of dark mode features in iOS, Android, and web apps...",
                    source="arxiv",
                    relevance_score=0.87
                ),
            ]
        }
        
        # Ищем релевантные демо-результаты по ключевым словам из запроса
        results = []
        for category, papers in demo_data.items():
            if category.lower() in query.lower() or any(word in query.lower() for word in category.split()):
                results.extend(papers)
        
        # Если не нашли точного совпадения, возвращаем общие результаты
        if not results:
            results = [paper for papers in demo_data.values() for paper in papers]
        
        return results[:limit]
    
    def _analyze_problem_severity(self, research_results: List[ResearchResult]) -> str:
        """
        Использует LLM (или правила) для анализа результатов
        и выдачи экспертного заключения о серьёзности проблемы
        """
        
        if not research_results:
            return "⚠️ Недостаточно исследований для оценки серьёзности проблемы"
        
        avg_relevance = sum(r.relevance_score for r in research_results) / len(research_results)
        
        if avg_relevance > 0.85:
            return "✓ Множество высоконадёжных исследований подтверждают серьёзность проблемы"
        elif avg_relevance > 0.70:
            return "○ Умеренное количество исследований поддерживает наличие проблемы"
        else:
            return "✗ Ограниченные доказательства серьёзности проблемы в доступных исследованиях"


# Пример использования
if __name__ == "__main__":
    finder = ResearchFinder()
    
    # Поиск о серьёзности проблемы с тёмным режимом
    problem_analysis = finder.search_problem_severity(
        problem_statement="Eye strain from bright displays at night",
        target_users="mobile app users"
    )
    
    print("\n📊 АНАЛИЗ ПРОБЛЕМЫ (из открытых источников):")
    print(json.dumps(problem_analysis, indent=2, ensure_ascii=False))
