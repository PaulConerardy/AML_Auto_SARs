# AML SAR Assistant

## À propos
Projet personnel.

J'ai créé cet assistant pour voir si l'on pouvait automatiser la rédaction des rapports d'activité suspecte (SAR), une tâche souvent longue et répétitive. L'idée est d'utiliser une architecture **RAG (Retrieval-Augmented Generation)** pour récupérer les preuves dans des documents et aider l'utilisateur à rédiger un rapport cohérent en quelques secondes.

## Ce que ça fait
*   **Analyse de documents** : Le système lit des transactions et des documents KYC.
*   **Rédaction assistée** : Il propose un brouillon de rapport structuré.
*   **Sécurité** : Une attention particulière a été portée à la protection des données sensibles (PII).
*   **Validation** : L'humain reste au centre de la décision, l'IA agit comme un assistant.

## Stack Technique
C'était l'occasion de manipuler plusieurs technos intéressantes :
*   **LlamaIndex & LangChain** pour l'orchestration et le RAG.
*   **ChromaDB** comme base de données vectorielle.
*   **GPT-4o / Claude 3.5** pour la génération de texte (ou modèles locaux via Ollama).
*   **Streamlit** pour une interface utilisateur rapide et propre.

## Comment l'essayer
Si vous voulez tester le code chez vous :

1.  **Installez les dépendances** :
    ```bash
    pip install -r requirements.txt
    ```

2.  **Préparez les données** (indexation) :
    ```bash
    python src/ingestion/indexer.py
    ```

3.  **Lancez l'interface** :
    ```bash
    streamlit run src/ui/app.py
    ```

*Note : Possible d'utiliser un modèle en local via local ou de fournir une clé API*
