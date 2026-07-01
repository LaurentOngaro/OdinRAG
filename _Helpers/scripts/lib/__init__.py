"""Reusable modules shared by the scrapers.

Contains:
  - http_client : robust GET, URL normalisation, sitemap/RSS parsing
  - html2md     : HTML->Markdown conversion via BeautifulSoup + markdownify
  - text_clean  : string repair (mojibake, NBSP)
  - user_config : personal paths/credentials loader
"""
