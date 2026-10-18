"""Collecte les offres France Travail et les charge dans la zone Bronze DuckDB (raw.job_offers).

Le payload source est conservé intact ; un hash SHA-256 du payload canonique sert à la
déduplication technique et à l'historisation des versions d'une même offre.

Usage (depuis la racine du dépôt) : ``python -m ingestion.main_ingest --keywords data ia``
"""

import argparse
import hashlib
import json
import os
import uuid
from datetime import UTC, datetime
from typing import Any

import duckdb

from ingestion.france_travail_client import FranceTravailClient

SOURCE = "france_travail"
DEFAULT_KEYWORDS = ["data engineer", "data scientist", "data analyst", "machine learning"]

DDL = """
CREATE SCHEMA IF NOT EXISTS raw;
CREATE TABLE IF NOT EXISTS raw.job_offers (
    source            VARCHAR     NOT NULL,
    source_record_id  VARCHAR     NOT NULL,
    ingestion_run_id  VARCHAR     NOT NULL,
    ingested_at       TIMESTAMPTZ NOT NULL,
    payload_hash      VARCHAR     NOT NULL,
    payload           JSON        NOT NULL,
    PRIMARY KEY (source, source_record_id, payload_hash)
);
"""


def compute_payload_hash(payload: dict[str, Any]) -> str:
    """SHA-256 stable d'un payload, indépendant de l'ordre des clés."""
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def load_offers(con: duckdb.DuckDBPyConnection, offers: list[dict[str, Any]]) -> int:
    """Insère les offres ; une version déjà connue (même hash) est ignorée."""
    run_id = uuid.uuid4().hex
    ingested_at = datetime.now(UTC)
    # Dédoublonnage intra-lot : une offre peut remonter pour plusieurs mots-clés.
    rows = {(str(o["id"]), compute_payload_hash(o)): o for o in offers}
    before = con.execute("SELECT count(*) FROM raw.job_offers").fetchone()[0]
    con.executemany(
        "INSERT INTO raw.job_offers VALUES (?, ?, ?, ?, ?, ?) ON CONFLICT DO NOTHING",
        [
            (SOURCE, offer_id, run_id, ingested_at, payload_hash, json.dumps(o, ensure_ascii=False))
            for (offer_id, payload_hash), o in rows.items()
        ],
    )
    return con.execute("SELECT count(*) FROM raw.job_offers").fetchone()[0] - before


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--keywords", nargs="+", default=DEFAULT_KEYWORDS)
    args = parser.parse_args()

    client = FranceTravailClient(
        client_id=os.environ["FRANCE_TRAVAIL_CLIENT_ID"],
        client_secret=os.environ["FRANCE_TRAVAIL_CLIENT_SECRET"],
    )
    offers = [o for kw in args.keywords for o in client.search_offers(motsCles=kw)]

    db_path = os.environ.get("DUCKDB_PATH", "data/job_market.duckdb")
    with duckdb.connect(db_path) as con:
        con.execute(DDL)
        inserted = load_offers(con, offers)
    print(f"{len(offers)} offres collectées, {inserted} nouvelles versions chargées dans {db_path}")


if __name__ == "__main__":
    main()
