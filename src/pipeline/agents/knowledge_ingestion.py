#!/usr/bin/env python3
"""
Knowledge Ingestion Script for Structural Engineering RAG Database

This script ingests IFC 4.3, Tekla Open API, and IS 800 documentation
into the Chroma vector database for LLM retrieval-augmented generation.
"""

import os
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any
import requests
from urllib.parse import urljoin

from .llm_orchestrator import LLMRAGStore


class StructuralKnowledgeIngester:
    """Ingests structural engineering knowledge sources into RAG database."""

    def __init__(self, rag_store: LLMRAGStore):
        self.rag_store = rag_store
        self.sources = {
            'ifc_4_3': {
                'name': 'IFC 4.3 Schema Documentation',
                'urls': [
                    'https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/',
                    'https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/concepts.htm'
                ],
                'local_files': [
                    'docs/ifc_4_3_reference.md',
                    'docs/ifc_structural_elements.md'
                ]
            },
            'tekla_api': {
                'name': 'Tekla Open API Documentation',
                'urls': [
                    'https://developer.tekla.com/tekla-structures/api',
                    'https://developer.tekla.com/tekla-structures/modeling-guide'
                ],
                'local_files': [
                    'docs/tekla_api_reference.md',
                    'docs/tekla_structural_modeling.md'
                ]
            },
            'is_800': {
                'name': 'IS 800:2007 Steel Design Code',
                'urls': [
                    'https://www.iitk.ac.in/nicee/wcee/article/17_vol2_1235.pdf',
                    'https://www.engineering.com/story/what-is-is-8002007'
                ],
                'local_files': [
                    'docs/is_800_steel_design.md',
                    'docs/indian_steel_codes.md'
                ]
            }
        }

    def ingest_all_sources(self) -> Dict[str, int]:
        """Ingest all configured knowledge sources."""
        results = {}
        for source_key, source_config in self.sources.items():
            print(f"Ingesting {source_config['name']}...")
            count = self._ingest_source(source_config)
            results[source_key] = count
            print(f"  → Ingested {count} chunks")
        return results

    def _ingest_source(self, source_config: Dict[str, Any]) -> int:
        """Ingest a single knowledge source."""
        total_chunks = 0

        # Ingest local files
        for file_path in source_config.get('local_files', []):
            if Path(file_path).exists():
                chunks = self._ingest_local_file(file_path, source_config['name'])
                total_chunks += len(chunks)

        # Ingest web content (if available)
        for url in source_config.get('urls', []):
            try:
                chunks = self._ingest_web_content(url, source_config['name'])
                total_chunks += len(chunks)
            except Exception as e:
                print(f"  Warning: Failed to ingest {url}: {e}")

        return total_chunks

    def _ingest_local_file(self, file_path: str, source_name: str) -> List[Dict[str, str]]:
        """Ingest content from a local file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Create chunks with source metadata
            chunks = []
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]

            for i, paragraph in enumerate(paragraphs):
                if len(paragraph) > 100:  # Skip very short paragraphs
                    chunks.append({
                        'source': f"{source_name} ({Path(file_path).name})",
                        'text': paragraph,
                        'chunk_id': f"{Path(file_path).stem}_{i}"
                    })

            return chunks

        except Exception as e:
            print(f"  Error reading {file_path}: {e}")
            return []

    def _ingest_web_content(self, url: str, source_name: str) -> List[Dict[str, str]]:
        """Ingest content from a web URL."""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            # Simple HTML text extraction (basic implementation)
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()

            text = soup.get_text()
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip() and len(p) > 100]

            chunks = []
            for i, paragraph in enumerate(paragraphs[:50]):  # Limit to first 50 paragraphs
                chunks.append({
                    'source': f"{source_name} ({url})",
                    'text': paragraph,
                    'chunk_id': f"{url.split('/')[-1]}_{i}"
                })

            return chunks

        except Exception as e:
            print(f"  Error fetching {url}: {e}")
            return []


def main():
    parser = argparse.ArgumentParser(description='Ingest structural engineering knowledge into RAG database')
    parser.add_argument('--index-path', type=str, help='Path to Chroma index directory')
    parser.add_argument('--force-rebuild', action='store_true', help='Force rebuild of existing index')
    args = parser.parse_args()

    # Initialize RAG store
    rag_store = LLMRAGStore(index_path=args.index_path)

    # Check if index exists and handle rebuild
    if hasattr(rag_store, 'collection') and rag_store.collection and not args.force_rebuild:
        try:
            count = rag_store.collection.count()
            if count > 0:
                print(f"Index already exists with {count} documents. Use --force-rebuild to rebuild.")
                return
        except:
            pass

    # Ingest knowledge
    ingester = StructuralKnowledgeIngester(rag_store)
    results = ingester.ingest_all_sources()

    print("\nIngestion Summary:")
    for source, count in results.items():
        print(f"  {source}: {count} chunks")

    total = sum(results.values())
    print(f"\nTotal chunks ingested: {total}")

    # Test query
    print("\nTesting RAG query...")
    test_results = rag_store.query("IFC structural elements", top_k=3)
    print(f"Found {len(test_results)} relevant chunks")
    for result in test_results[:2]:
        print(f"  Source: {result['source']}")
        print(f"  Text: {result['text'][:200]}...")


if __name__ == '__main__':
    main()