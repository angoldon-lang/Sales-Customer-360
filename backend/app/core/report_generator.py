from typing import List, Tuple
from datetime import datetime
from app.models.news import NewsItem
from app.models.cluster import Cluster


class ReportGenerator:
    """Generate email reports from news items."""

    @staticmethod
    def generate_report(
        cluster: Cluster,
        news_items: List[NewsItem],
        period_start: datetime,
        period_end: datetime,
    ) -> Tuple[str, str, str]:
        """
        Generate report.

        Returns:
            (subject, body_html, body_text)
        """
        subject = f"Customer Intelligence Report - {cluster.cluster_name} - {datetime.utcnow().strftime('%Y-%m-%d')}"

        # Filter news by min_relevance_score
        approved_news = [
            n for n in news_items
            if n.relevance_score >= cluster.min_relevance_score and n.status == "approved"
        ]

        # Text version
        body_text = ReportGenerator._generate_text_body(cluster, approved_news, period_start, period_end)

        # HTML version
        body_html = ReportGenerator._generate_html_body(cluster, approved_news, period_start, period_end)

        return subject, body_html, body_text

    @staticmethod
    def _generate_text_body(
        cluster: Cluster,
        news_items: List[NewsItem],
        period_start: datetime,
        period_end: datetime,
    ) -> str:
        """Generate text version of report."""
        lines = [
            f"Customer Intelligence Report - {cluster.cluster_name}",
            f"Period: {period_start.date()} to {period_end.date()}",
            "",
            f"Dear recipient,",
            "",
            f"Here is a summary of the most relevant news for cluster {cluster.cluster_name}.",
            "",
            "-" * 80,
            "",
        ]

        for i, news in enumerate(news_items, 1):
            lines.extend([
                f"{i}. Company: {news.company.company_name}",
                f"   Category: {news.category.value.replace('_', ' ').title()}",
                f"   Title: {news.title}",
                f"   Impact: {'High' if news.relevance_score >= 8 else 'Medium' if news.relevance_score >= 5 else 'Low'}",
                f"   Summary: {news.summary or 'N/A'}",
                f"   Source: {news.source}",
                f"   URL: {news.url}",
                "",
            ])

        lines.extend([
            "-" * 80,
            "",
            "Report generated automatically.",
            "---",
            f"Generated at: {datetime.utcnow().isoformat()}",
        ])

        return "\n".join(lines)

    @staticmethod
    def _generate_html_body(
        cluster: Cluster,
        news_items: List[NewsItem],
        period_start: datetime,
        period_end: datetime,
    ) -> str:
        """Generate HTML version of report."""
        news_html = ""

        for i, news in enumerate(news_items, 1):
            impact_level = "High" if news.relevance_score >= 8 else "Medium" if news.relevance_score >= 5 else "Low"
            impact_color = "#d32f2f" if impact_level == "High" else "#f57c00" if impact_level == "Medium" else "#1976d2"

            news_html += f"""
            <div style="border-left: 4px solid {impact_color}; padding: 12px; margin: 12px 0; background: #f5f5f5; border-radius: 4px;">
                <h3 style="margin: 0 0 8px 0; color: #333;">{i}. {news.company.company_name}</h3>
                <p style="margin: 4px 0; color: #666;">
                    <strong>Category:</strong> {news.category.value.replace('_', ' ').title()}<br/>
                    <strong>Impact:</strong> <span style="color: {impact_color}; font-weight: bold;">{impact_level}</span><br/>
                    <strong>Title:</strong> {news.title}<br/>
                    <strong>Source:</strong> {news.source}
                </p>
                <p style="margin: 8px 0; color: #555;">{news.summary or 'No summary available'}</p>
                <p style="margin: 8px 0;"><a href="{news.url}" style="color: #1976d2; text-decoration: none;">Read full article →</a></p>
            </div>
            """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: Arial, sans-serif; color: #333; background: #f9f9f9; }}
                .container {{ max-width: 800px; margin: 0 auto; padding: 20px; background: white; }}
                h1 {{ color: #1976d2; border-bottom: 2px solid #1976d2; padding-bottom: 10px; }}
                .header {{ margin-bottom: 20px; }}
                .news-item {{ border-left: 4px solid #ccc; padding: 12px; margin: 12px 0; background: #f5f5f5; }}
                .footer {{ margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd; color: #999; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Customer Intelligence Report</h1>
                    <p><strong>Cluster:</strong> {cluster.cluster_name}</p>
                    <p><strong>Period:</strong> {period_start.date()} to {period_end.date()}</p>
                </div>

                <p>Dear recipient,</p>
                <p>Here is a summary of the most relevant news for cluster <strong>{cluster.cluster_name}</strong>.</p>

                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">

                {news_html if news_items else '<p style="color: #999;">No news items for this period.</p>'}

                <div class="footer">
                    <p>Report generated automatically.</p>
                    <p>Generated at: {datetime.utcnow().isoformat()}</p>
                </div>
            </div>
        </body>
        </html>
        """

        return html
