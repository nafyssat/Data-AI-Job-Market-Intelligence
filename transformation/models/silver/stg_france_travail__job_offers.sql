-- Silver : dernière version connue de chaque offre France Travail, champs typés.
with latest as (
    select *
    from {{ source('raw', 'job_offers') }}
    where source = 'france_travail'
    qualify row_number() over (partition by source_record_id order by ingested_at desc) = 1
)

select
    source_record_id                                    as job_offer_id,
    payload ->> 'intitule'                              as title,
    payload ->> 'description'                           as description,
    payload ->> '$.entreprise.nom'                      as company_name,
    payload ->> '$.lieuTravail.libelle'                 as location,
    payload ->> '$.lieuTravail.codePostal'              as postal_code,
    payload ->> 'typeContrat'                           as contract_type,
    payload ->> 'experienceExige'                       as experience_required,
    payload ->> 'romeCode'                              as rome_code,
    payload ->> '$.salaire.libelle'                     as salary_label,
    cast(payload ->> 'dateCreation' as timestamptz)     as created_at,
    cast(payload ->> 'dateActualisation' as timestamptz) as updated_at,
    ingested_at
from latest
