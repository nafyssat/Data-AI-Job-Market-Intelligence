# Data-AI-Job-Market-Intelligence
End-to-end data platform for analyzing Data &amp; AI job market trends, combining Data Engineering, Analytics Engineering and AI Engineering.

# Data-AI-Job-Market-Intelligence 

Plateforme de données de bout en bout (End-to-End Data Platform) conçue pour analyser les tendances du marché de l'emploi sur les métiers de la **Data** et de l'**IA**, combinant les meilleures pratiques du **Data Engineering**, de l'**Analytics Engineering** et de l'**AI Engineering**.

---

## Objectif du Projet
Ce projet a été conçu pour répondre à une problématique concrète : *Comment capter, structurer et analyser en temps réel l'évolution des compétences, des technologies et des salaires demandés sur le marché des métiers de la Data et de l'IA (Data Engineer, AI Engineer, Data Scientist, etc.) ?*

Il démontre la maîtrise d'une stack moderne de type **Data Lakehouse** et l'automatisation de pipelines de données en production.

---

## Architecture & Flux de Données

Le pipeline repose sur une architecture en couches (Medallion Architecture revisitée) :

```mermaid
graph TD
    A1[API France Travail] -->|Ingestion Python| B[Stockage Bronze S3 / Brut]
    A2[Scraping LinkedIn / APEC] -->|Ingestion Python| B
    B --> C[Couche Silver: Nettoyage & Normalisation]
    C --> D[Couche Gold: Agrégations & Enrichissement IA]
    D --> E[Interface Analytics & LLM / Streamlit]