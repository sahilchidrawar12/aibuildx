#!/usr/bin/env python3
"""
Knowledge Ingestion Runner for Structural Engineering RAG
Ingests IFC, Tekla, and IS 800 documentation into ChromaDB
"""

import sys
import os
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pipeline.agents.knowledge_ingestion import StructuralKnowledgeIngester

def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    logger = logging.getLogger(__name__)

    # Configuration
    chroma_path = os.getenv("CHROMA_DB_PATH", "./data/chroma_db")
    docs_dir = Path("./docs")

    # Ensure docs directory exists
    if not docs_dir.exists():
        logger.error(f"Documentation directory not found: {docs_dir}")
        return 1

    # Initialize ingester
    try:
        ingester = StructuralKnowledgeIngester(chroma_path=chroma_path)
        logger.info("Initialized ChromaDB ingester")
    except Exception as e:
        logger.error(f"Failed to initialize ingester: {e}")
        return 1

    # Define knowledge sources
    sources = [
        {
            "name": "IFC 4.3 Structural Steel Schemas",
            "urls": [
                "https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/",
                "https://ifc43-docs.standards.buildingsmart.org/"
            ],
            "local_files": [
                docs_dir / "ifc_standards.md",
                docs_dir / "ifc_structural_schemas.md"
            ]
        },
        {
            "name": "Tekla Open API Documentation",
            "urls": [
                "https://developer.tekla.com/tekla-structures/api",
                "https://developer.tekla.com/tekla-structures/programming-guide"
            ],
            "local_files": [
                docs_dir / "tekla_api_docs.md",
                docs_dir / "tekla_programming_guide.md"
            ]
        },
        {
            "name": "IS 800:2007 Steel Construction Standards",
            "urls": [
                "https://www.iitk.ac.in/nicee/wcee/article/17_vol2-S08-041.pdf",
                "https://law.resource.org/pub/in/bis/S03/is.800.2007.pdf"
            ],
            "local_files": [
                docs_dir / "is_800_2007.md",
                docs_dir / "indian_steel_standards.md"
            ]
        }
    ]

    # Ingest all sources
    total_ingested = 0
    for source in sources:
        logger.info(f"Ingesting: {source['name']}")

        try:
            # Ingest from URLs
            for url in source["urls"]:
                count = ingester.ingest_from_url(url, source["name"])
                total_ingested += count
                logger.info(f"  Ingested {count} chunks from URL: {url}")

            # Ingest from local files
            for file_path in source["local_files"]:
                if file_path.exists():
                    count = ingester.ingest_local_file(str(file_path), source["name"])
                    total_ingested += count
                    logger.info(f"  Ingested {count} chunks from file: {file_path}")
                else:
                    logger.warning(f"  Local file not found: {file_path}")

        except Exception as e:
            logger.error(f"Failed to ingest {source['name']}: {e}")
            continue

    logger.info(f"Knowledge ingestion complete! Total chunks ingested: {total_ingested}")

    # Test retrieval
    logger.info("Testing knowledge retrieval...")
    test_queries = [
        "What are the requirements for steel beam connections in IS 800?",
        "How to create a structural model in Tekla API?",
        "What IFC entities are used for structural steel elements?"
    ]

    for query in test_queries:
        results = ingester.search(query, n_results=3)
        logger.info(f"Query: {query}")
        logger.info(f"Results: {len(results)} found")
        if results:
            logger.info(f"Top result: {results[0]['document'][:200]}...")

    return 0

if __name__ == "__main__":
    sys.exit(main())