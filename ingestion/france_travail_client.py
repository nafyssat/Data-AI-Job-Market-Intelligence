"""Client de l'API Offres d'emploi v2 de France Travail (https://francetravail.io).

Authentification OAuth2 « client credentials », puis recherche paginée via le
paramètre ``range`` (150 offres max par appel, index max 3149).
"""

import time
from collections.abc import Iterator
from typing import Any

import requests

TOKEN_URL = "https://entreprise.francetravail.fr/connexion/oauth2/access_token"
SEARCH_URL = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search"
SCOPE = "api_offresdemploiv2 o2dsoffre"
PAGE_SIZE = 150
MAX_INDEX = 3149


class FranceTravailClient:
    def __init__(self, client_id: str, client_secret: str, timeout: float = 30.0) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._timeout = timeout
        self._session = requests.Session()
        self._token: str | None = None
        self._token_expires_at = 0.0

    def _get_token(self) -> str:
        if self._token and time.time() < self._token_expires_at - 60:
            return self._token
        response = self._session.post(
            TOKEN_URL,
            params={"realm": "/partenaire"},
            data={
                "grant_type": "client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "scope": SCOPE,
            },
            timeout=self._timeout,
        )
        response.raise_for_status()
        body = response.json()
        self._token = body["access_token"]
        self._token_expires_at = time.time() + int(body.get("expires_in", 1499))
        return self._token

    def search_offers(self, **params: Any) -> Iterator[dict[str, Any]]:
        """Itère sur toutes les offres correspondant aux critères (ex. ``motsCles="data"``)."""
        start = 0
        while start <= MAX_INDEX:
            end = min(start + PAGE_SIZE - 1, MAX_INDEX)
            response = self._session.get(
                SEARCH_URL,
                params={**params, "range": f"{start}-{end}"},
                headers={"Authorization": f"Bearer {self._get_token()}"},
                timeout=self._timeout,
            )
            if response.status_code == 204:  # aucun résultat
                return
            response.raise_for_status()
            offers = response.json().get("resultats", [])
            yield from offers
            if len(offers) < PAGE_SIZE:
                return
            start += PAGE_SIZE
