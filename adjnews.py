# -*- coding: utf-8 -*-

import requests
from requests import Session
from typing import Optional, Dict, Any
import os 
from dotenv import load_dotenv
load_dotenv()


class AdjNewsError(Exception):
    """Custom exception for AdjNews API errors."""
    pass


class AdjNews:
    BASE_URL = "https://api.data.adj.news"

    def __init__(self, api_key: str = None):
        if not api_key:
            api_key = os.getenv("ADJ_NEWS_API_KEY", None)
            if not api_key:
                raise AdjNewsError(f"ADJ_NEWS_API_KEY Not Found.")

        self.api_key = api_key
        self.session = self._init_session()

    def _init_session(self) -> Session:
        session = requests.Session()
        session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        })
        return session

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise AdjNewsError(f"GET {url} failed: {e}")

    def semantic_search(
        self,
        query: str, 
        limit: int = 10, 
        include_context: bool = False
    ) -> Any:
        """
        This endpoint provides powerful semantic search capabilities that 
        go beyond simple keyword matching. It uses machine learning-based 
        vector embeddings to find markets that are conceptually related to 
        your search query, even if they don’t contain the exact words.

        :param query: Search query
        :param limit: Maximum number of results to return
        :param include_context: Whether to include relevance scores and match context
        :return: JSON response
        
        Example Output:
        {
            "data": [
                {
                    "market_id": "polymarket_will-us-inflation-exceed-3-percent-in-2025",
                    "platform": "polymarket",
                    "question": "Will US inflation exceed 3% in 2025?",
                    // ... other market fields
                }, 
                // ... more markets
            ],
            "meta": {
                "query": "future inflation rates",
                "score": 0.95  // Only included if include_context=true
            }
        }
        """
        endpoint = "/api/search/query"
        params = {"q": query, "limit": limit, "include_context": include_context}
        return self._get(endpoint, params)

    def list_markets(
        self,
        limit: int = 5,
        offset: int = 0,
        platform: Optional[str] = None,
        status: Optional[str] = None,
        category: Optional[str] = None,
        market_type: Optional[str] = None,
        keyword: Optional[str] = None,
        tag: Optional[str] = None,
        created_after: Optional[str] = None,
        created_before: Optional[str] = None,
        probability_min: Optional[float] = None,
        probability_max: Optional[float] = None,
        sort_by: str = "updated_at",
        sort_dir: str = "desc",
        include_closed: bool = False,
        include_resolved: bool = False
    ) -> Any:
        """
        This endpoint provides a comprehensive way to retrieve markets with 
        powerful filtering, sorting, and pagination capabilities. It’s perfect 
        for building market dashboards, search interfaces, and data visualizations.

        :param limit: Number of results to return (default: 5)
        :param offset: Number of results to skip for pagination (default: 0)
        :param platform: Filter by platform name (e.g., kalshi, polymarket)
        :param status: Filter by market status (e.g., active, resolved)
        :param category: Filter by market category
        :param market_type: Filter by type of market (e.g., binary, scalar)
        :param keyword: Search within question, description, and rules fields
        :param tag: Filter by tag
        :param created_after: Return markets created after this ISO timestamp
        :param created_before: Return markets created before this ISO timestamp
        :param probability_min: Filter markets with probability greater than or equal to this value
        :param probability_max: Filter markets with probability less than or equal to this value
        :param sort_by: Field to sort results by (default: updated_at)
                        Options: created_at, updated_at, end_date, probability, volume, liquidity
        :param sort_dir: Sort direction (default: desc). Options: asc, desc
        :param include_closed: Whether to include closed markets (default: False)
        :param include_resolved: Whether to include resolved markets (default: False)
        :return: JSON response
        
        Example Output:
        {
            "data": [
                {
                    "market_id": "kalshi_KXSECPRESSMENTION-25JUN30-HOAX",
                    "platform": "kalshi",
                    "question": "Will the White House Press Secretary say Hoax at her next press briefing?",
                    // ... other market fields
                },
                // ... more markets
            ],
            "meta": {
                "count": 1250,  // Total number of matching markets
                "limit": 100,   // Results per page
                "offset": 0,    // Current offset
                "hasMore": true // Whether there are more results
            }
        }
        """
        endpoint = "/api/markets"
        params = {
            "limit": limit,
            "offset": offset,
            "sort_by": sort_by,
            "sort_dir": sort_dir,
            "include_closed": str(include_closed).lower(),
            "include_resolved": str(include_resolved).lower()
        }
        optional_params = {
            "platform": platform,
            "status": status,
            "category": category,
            "market_type": market_type,
            "keyword": keyword,
            "tag": tag,
            "created_after": created_after,
            "created_before": created_before,
            "probability_min": probability_min,
            "probability_max": probability_max
        }
        for key, value in optional_params.items():
            if value is not None:
                params[key] = value
        return self._get(endpoint, params)

