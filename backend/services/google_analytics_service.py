"""
Google Analytics Service
Handles Google Analytics 4 Data API integration
"""

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
    RunRealtimeReportRequest
)
from services.google_oauth_service import GoogleOAuthService

class GoogleAnalyticsService:
    def __init__(self, credentials_file='credentials.json', token_file='token.json'):
        """Initialize Google Analytics service with unified OAuth"""
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.client = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Analytics Data API"""
        oauth = GoogleOAuthService(self.credentials_file, self.token_file)
        creds = oauth.get_credentials()
        self.client = BetaAnalyticsDataClient(credentials=creds)
    
    def get_analytics_overview(self, property_id: str, start_date: str = "30daysAgo", end_date: str = "today") -> dict:
        """
        Get analytics overview with key metrics
        
        Args:
            property_id: GA4 Property ID (e.g., "123456789")
            start_date: Start date (e.g., "30daysAgo", "2024-01-01")
            end_date: End date (e.g., "today", "2024-01-31")
        
        Returns:
            dict with sessions, users, pageviews, bounce rate, avg session duration
        """
        try:
            request = RunReportRequest(
                property=f"properties/{property_id}",
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                metrics=[
                    Metric(name="sessions"),
                    Metric(name="totalUsers"),
                    Metric(name="screenPageViews"),
                    Metric(name="bounceRate"),
                    Metric(name="averageSessionDuration")
                ]
            )
            
            response = self.client.run_report(request)
            
            if not response.rows:
                return {"success": False, "error": "No data available"}
            
            row = response.rows[0]
            return {
                "success": True,
                "data": {
                    "sessions": int(row.metric_values[0].value),
                    "users": int(row.metric_values[1].value),
                    "pageviews": int(row.metric_values[2].value),
                    "bounce_rate": f"{float(row.metric_values[3].value):.1f}%",
                    "avg_session_duration": f"{float(row.metric_values[4].value):.0f}s"
                },
                "date_range": f"{start_date} to {end_date}"
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_top_pages(self, property_id: str, start_date: str = "30daysAgo", end_date: str = "today", limit: int = 10) -> dict:
        """
        Get top performing pages
        
        Args:
            property_id: GA4 Property ID
            start_date: Start date
            end_date: End date
            limit: Number of pages to return
        
        Returns:
            dict with list of top pages and their metrics
        """
        try:
            request = RunReportRequest(
                property=f"properties/{property_id}",
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                dimensions=[Dimension(name="pageTitle"), Dimension(name="pagePath")],
                metrics=[
                    Metric(name="screenPageViews"),
                    Metric(name="averageSessionDuration"),
                    Metric(name="bounceRate")
                ],
                limit=limit,
                order_bys=[{"metric": {"metric_name": "screenPageViews"}, "desc": True}]
            )
            
            response = self.client.run_report(request)
            
            if not response.rows:
                return {"success": False, "error": "No data available"}
            
            pages = []
            for row in response.rows:
                pages.append({
                    "title": row.dimension_values[0].value,
                    "path": row.dimension_values[1].value,
                    "pageviews": int(row.metric_values[0].value),
                    "avg_time": f"{float(row.metric_values[1].value):.0f}s",
                    "bounce_rate": f"{float(row.metric_values[2].value):.1f}%"
                })
            
            return {
                "success": True,
                "pages": pages,
                "count": len(pages),
                "date_range": f"{start_date} to {end_date}"
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_traffic_sources(self, property_id: str, start_date: str = "30daysAgo", end_date: str = "today") -> dict:
        """
        Get traffic sources breakdown
        
        Args:
            property_id: GA4 Property ID
            start_date: Start date
            end_date: End date
        
        Returns:
            dict with traffic sources and their metrics
        """
        try:
            request = RunReportRequest(
                property=f"properties/{property_id}",
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                dimensions=[Dimension(name="sessionSource"), Dimension(name="sessionMedium")],
                metrics=[
                    Metric(name="sessions"),
                    Metric(name="totalUsers")
                ],
                limit=10,
                order_bys=[{"metric": {"metric_name": "sessions"}, "desc": True}]
            )
            
            response = self.client.run_report(request)
            
            if not response.rows:
                return {"success": False, "error": "No data available"}
            
            sources = []
            for row in response.rows:
                sources.append({
                    "source": row.dimension_values[0].value,
                    "medium": row.dimension_values[1].value,
                    "sessions": int(row.metric_values[0].value),
                    "users": int(row.metric_values[1].value)
                })
            
            return {
                "success": True,
                "sources": sources,
                "count": len(sources),
                "date_range": f"{start_date} to {end_date}"
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_realtime_data(self, property_id: str) -> dict:
        """
        Get real-time active users
        
        Args:
            property_id: GA4 Property ID
        
        Returns:
            dict with real-time metrics
        """
        try:
            request = RunRealtimeReportRequest(
                property=f"properties/{property_id}",
                metrics=[Metric(name="activeUsers")]
            )
            
            response = self.client.run_realtime_report(request)
            
            if not response.rows:
                return {
                    "success": True,
                    "active_users": 0
                }
            
            active_users = int(response.rows[0].metric_values[0].value)
            
            return {
                "success": True,
                "active_users": active_users
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
