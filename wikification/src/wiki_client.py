import wikipediaapi
import logging

logging.basicConfig(level=logging.INFO)

class WikiClient:
    def __init__(self, lang='tr'):
        self.wiki = wikipediaapi.Wikipedia(
            user_agent='StudentProject/1.0 (contact@example.com)',
            language=lang,
            extract_format=wikipediaapi.ExtractFormat.WIKI
        )
        self.cache = {} # Simple in-memory cache

    def get_page(self, title):
        """
        Retrieves a Wikipedia page. Uses cache if available.
        """
        if title in self.cache:
            return self.cache[title]

        page = self.wiki.page(title)

        # Cache the result object (or basic info to save memory)
        # Storing the page object directly is fine for small scale
        self.cache[title] = page
        return page

    def is_disambiguation(self, page):
        """
        Checks if a page is a disambiguation page.
        """
        # Wikipedia-API might have a property, or we check categories/text
        # Common pattern: "anlam ayrımı" in title or categories
        if "anlam ayrımı" in page.title.lower():
            return True
        # Check categories
        for cat in page.categories.keys():
            if "anlam ayrımı" in cat.lower():
                return True
        return False

    def get_summary(self, page):
        return page.summary

    def get_disambiguation_candidates(self, page, limit=5):
        """
        Fetches the first 'limit' links from a disambiguation page to be used as candidates.
        Returns a list of Page objects.
        """
        candidates = []
        # page.links returns a dictionary of all links on the page.
        # On a disambiguation page, these are the options.
        # Note: This might include irrelevant links (Help, Portal, etc.),
        # but for a simple project, taking the first few meaningful ones is okay.

        count = 0
        for title, link_page in page.links.items():
            # Filter out obvious non-article namespaces if possible, but title check is easier
            if ":" in title and title.split(":")[0] in ["Vikipedi", "Kategori", "Dosya", "Şablon", "Yardım"]:
                continue

            # Retrieve full page details (summary needed for TF-IDF)
            # This triggers an API call per candidate, so we must limit it.
            if count >= limit:
                break

            full_candidate = self.get_page(title)
            if full_candidate.exists():
                candidates.append(full_candidate)
                count += 1

        return candidates
