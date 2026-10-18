-- Gold : volume d'offres publiées par jour et type de contrat.
select
    cast(created_at as date) as publication_date,
    contract_type,
    count(*)                 as offers_count
from {{ ref('stg_france_travail__job_offers') }}
group by all
