"""Extraction des compétences des offres (Silver) vers ai.job_offer_skills.

Première version à base de dictionnaire ; elle sera remplacée ou complétée par un LLM.

Usage (depuis la racine du dépôt) : ``python -m ai.extractor``
"""

import os
import re

import duckdb

SKILLS: dict[str, list[str]] = {
    "python": [r"python"],
    "sql": [r"sql"],
    "spark": [r"spark", r"pyspark"],
    "dbt": [r"dbt"],
    "airflow": [r"airflow"],
    "kafka": [r"kafka"],
    "docker": [r"docker"],
    "kubernetes": [r"kubernetes", r"k8s"],
    "aws": [r"aws", r"amazon web services"],
    "azure": [r"azure"],
    "gcp": [r"gcp", r"google cloud"],
    "power bi": [r"power ?bi"],
    "tableau": [r"tableau"],
    "machine learning": [r"machine learning", r"apprentissage automatique"],
    "deep learning": [r"deep learning"],
    "llm": [r"llms?", r"genai", r"ia générative"],
}
_PATTERNS = {
    skill: re.compile(r"\b(?:" + "|".join(aliases) + r")\b", re.IGNORECASE)
    for skill, aliases in SKILLS.items()
}


def extract_skills(text: str | None) -> list[str]:
    if not text:
        return []
    return [skill for skill, pattern in _PATTERNS.items() if pattern.search(text)]


def main() -> None:
    db_path = os.environ.get("DUCKDB_PATH", "data/job_market.duckdb")
    with duckdb.connect(db_path) as con:
        offers = con.execute(
            "SELECT job_offer_id, title, description FROM silver.stg_france_travail__job_offers"
        ).fetchall()
        rows = [
            (offer_id, skill)
            for offer_id, title, description in offers
            for skill in extract_skills(f"{title or ''} {description or ''}")
        ]
        con.execute("CREATE SCHEMA IF NOT EXISTS ai")
        con.execute(
            "CREATE OR REPLACE TABLE ai.job_offer_skills (job_offer_id VARCHAR, skill VARCHAR)"
        )
        if rows:
            con.executemany("INSERT INTO ai.job_offer_skills VALUES (?, ?)", rows)
    print(f"{len(rows)} compétences extraites sur {len(offers)} offres")


if __name__ == "__main__":
    main()
