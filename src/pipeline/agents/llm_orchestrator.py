import json
import logging
import os
import re
import subprocess
import textwrap
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests
from sklearn.feature_extraction.text import TfidfVectorizer

logger = logging.getLogger("llm_orchestrator")


class LLMRAGStore:
    """Chroma-backed structural knowledge retrieval with TF-IDF fallback."""

    def __init__(self, source_dirs: Optional[List[str]] = None, index_path: Optional[str] = None):
        self.source_dirs = source_dirs or [
            str(Path(__file__).parent.parent.parent / 'docs'),
            str(Path(__file__).parent.parent.parent / 'data')
        ]
        self.index_path = Path(index_path or Path(__file__).parent.parent.parent / 'data' / 'structural_rag')
        self.chunks: List[Dict[str, str]] = []
        self.use_chroma = False
        self.client = None
        self.collection = None
        self.embedding_function = None
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.doc_matrix = None
        self._build_index()

    def _discover_documents(self) -> List[str]:
        paths = []
        for source_dir in self.source_dirs:
            root = Path(source_dir)
            if not root.exists():
                continue
            for ext in ('*.md', '*.txt', '*.py', '*.json'):
                for file_path in root.rglob(ext):
                    if file_path.is_file():
                        paths.append(str(file_path))
        return sorted(paths)

    def _read_document(self, path: str) -> str:
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
                return fh.read()
        except Exception as exc:
            logger.warning('Unable to read doc %s: %s', path, exc)
            return ''

    def _chunk_text(self, content: str, source: str) -> List[Dict[str, str]]:
        paragraphs = [paragraph.strip() for paragraph in re.split(r'\n\s*\n', content) if paragraph.strip()]
        chunks: List[Dict[str, str]] = []
        buffer = ''
        for paragraph in paragraphs:
            if len(buffer) + len(paragraph) > 2000:
                if buffer:
                    chunks.append({'source': source, 'text': buffer})
                buffer = paragraph
            else:
                buffer = f"{buffer}\n\n{paragraph}" if buffer else paragraph
        if buffer:
            chunks.append({'source': source, 'text': buffer})
        return chunks

    def _init_chroma(self) -> bool:
        try:
            import chromadb
            from chromadb.config import Settings
            from chromadb.utils import embedding_functions

            self.index_path.mkdir(parents=True, exist_ok=True)
            self.client = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=str(self.index_path)
            ))
            self.embedding_function = embedding_functions.SentenceTransformersEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
            self.collection = self.client.get_or_create_collection(
                name="structural_knowledge",
                embedding_function=self.embedding_function,
            )
            self.use_chroma = True
            return True
        except Exception as exc:
            logger.warning('ChromaDB initialization failed: %s', exc)
            self.use_chroma = False
            return False

    def _build_chroma_index(self) -> None:
        if not self.collection:
            return

        try:
            if self.collection.count() > 0:
                logger.info('Chroma RAG collection already populated with %s documents', self.collection.count())
                return
        except Exception:
            pass

        documents = []
        metadatas = []
        ids = []
        for doc_path in self._discover_documents():
            content = self._read_document(doc_path)
            if not content:
                continue
            doc_chunks = self._chunk_text(content, doc_path)
            for idx, chunk in enumerate(doc_chunks):
                documents.append(chunk['text'])
                metadatas.append({'source': chunk['source']})
                ids.append(f"{Path(chunk['source']).stem}_{idx}")

        if not documents:
            logger.warning('Chroma RAG build found no documents')
            return

        try:
            self.collection.add(ids=ids, documents=documents, metadatas=metadatas)
            self.client.persist()
            logger.info('Chroma RAG index built with %d chunks', len(documents))
        except Exception as exc:
            logger.warning('Failed to add documents to Chroma collection: %s', exc)
            self.use_chroma = False

    def _build_index(self) -> None:
        if self._init_chroma():
            self._build_chroma_index()
            return

        documents = []
        for doc_path in self._discover_documents():
            content = self._read_document(doc_path)
            if not content:
                continue
            doc_chunks = self._chunk_text(content, doc_path)
            self.chunks.extend(doc_chunks)
            documents.extend([chunk['text'] for chunk in doc_chunks])

        if not documents:
            logger.warning('RAG store built with no documents')
            return

        try:
            self.vectorizer = TfidfVectorizer(max_features=5000, stop_words='english', ngram_range=(1, 2))
            self.doc_matrix = self.vectorizer.fit_transform(documents)
            logger.info('TF-IDF fallback RAG index built with %d chunks', len(documents))
        except Exception as exc:
            logger.warning('Failed to build TF-IDF RAG index: %s', exc)
            self.vectorizer = None
            self.doc_matrix = None

    def query(self, query: str, top_k: int = 3) -> List[Dict[str, str]]:
        if self.use_chroma and self.collection:
            try:
                results = self.collection.query(query_texts=[query], n_results=top_k)
                documents = results.get('documents', [[]])[0]
                metadatas = results.get('metadatas', [[]])[0]
                return [
                    {'source': metadata.get('source', 'unknown'), 'text': text}
                    for text, metadata in zip(documents, metadatas)
                    if text
                ]
            except Exception as exc:
                logger.warning('Chroma RAG query failed: %s', exc)

        if self.vectorizer is None or self.doc_matrix is None:
            return []
        try:
            query_vec = self.vectorizer.transform([query])
            scores = (self.doc_matrix * query_vec.T).toarray().ravel()
            selected = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
            return [self.chunks[idx] for idx in selected if scores[idx] > 0]
        except Exception as exc:
            logger.warning('TF-IDF RAG query failed: %s', exc)
            return []


class LLMFineTuner:
    """Orchestrates automated fine-tuning for the selected inference backend."""

    def __init__(self, training_file: str, backend: str = 'ollama', model_name: Optional[str] = None):
        self.training_file = training_file
        self.backend = backend
        self.model_name = model_name or os.getenv('OLLAMA_MODEL_NAME', 'llama-3-70b')
        self.fine_tune_cmd = os.getenv('OLLAMA_FINE_TUNE_CMD')

    def trigger(self) -> Dict[str, str]:
        if self.backend == 'ollama' and self.fine_tune_cmd:
            try:
                command = self.fine_tune_cmd.format(model=self.model_name, training_file=self.training_file)
                logger.info('Triggering Ollama fine-tune with command: %s', command)
                completed = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=3600)
                if completed.returncode != 0:
                    logger.error('Fine-tune failed: %s', completed.stderr)
                    return {'status': 'error', 'message': completed.stderr}
                logger.info('Fine-tune triggered successfully')
                return {'status': 'ok', 'message': completed.stdout}
            except Exception as exc:
                logger.error('Fine-tune command failed: %s', exc)
                return {'status': 'error', 'message': str(exc)}

        logger.info('No automated fine-tune command configured for backend %s', self.backend)
        return {'status': 'skipped', 'message': 'Fine tuning not configured'}


class LLMOrchestrator:
    """Handles 70B model inference and retrieval augmented generation."""

    def __init__(self):
        self.backend = os.getenv('LLM_BACKEND', 'vllm' if os.getenv('VLLM_HOST') else ('ollama' if os.getenv('OLLAMA_HOST') else 'llama_cpp'))
        self.model_name = os.getenv('OLLAMA_MODEL_NAME', 'llama-3-70b')
        self.model_path = os.getenv('LLAMA_MODEL_PATH')
        self.ollama_host = os.getenv('OLLAMA_HOST', 'http://127.0.0.1:11434')
        self.ollama_port = os.getenv('OLLAMA_PORT', '11434')
        self.vllm_host = os.getenv('VLLM_HOST', 'http://127.0.0.1')
        self.vllm_port = os.getenv('VLLM_PORT', '8000')
        self.api_url = self._build_api_url()
        self.model = None
        self.available = False
        self.rag_store = LLMRAGStore()
        self._connect_model()

    def _build_api_url(self) -> str:
        if self.backend == 'vllm':
            return f"{self.vllm_host}:{self.vllm_port}" if self.vllm_host.startswith('http') else f"http://{self.vllm_host}:{self.vllm_port}"
        return f"{self.ollama_host}:{self.ollama_port}" if self.ollama_host.startswith('http') else f"http://{self.ollama_host}:{self.ollama_port}"

    def _connect_model(self) -> None:
        if self.backend == 'ollama':
            logger.info('Configured Ollama backend for LLM orchestration (model=%s)', self.model_name)
            self.available = True
            return

        if self.backend == 'vllm':
            logger.info('Configured vLLM backend for LLM orchestration (host=%s:%s)', self.vllm_host, self.vllm_port)
            self.available = True
            return

        if self.backend == 'llama_cpp':
            if not self.model_path:
                logger.warning('LLAMA_MODEL_PATH not configured for llama_cpp backend')
                self.available = False
                return
            try:
                import llama_cpp
                self.model = llama_cpp.Llama(model_path=self.model_path)
                self.available = True
                logger.info('Loaded local Llama model from %s', self.model_path)
            except Exception as exc:
                logger.warning('Unable to initialize llama_cpp model: %s', exc)
                self.available = False
                self.model = None
                return

    def generate(self, prompt: str, max_tokens: int = 256, temperature: float = 0.2) -> str:
        if not self.available:
            return 'LLM backend unavailable; returning heuristic reasoning fallback.'

        if self.backend == 'ollama':
            return self._ollama_generate(prompt, max_tokens=max_tokens, temperature=temperature)
        if self.backend == 'vllm':
            return self._vllm_generate(prompt, max_tokens=max_tokens, temperature=temperature)
        if self.backend == 'llama_cpp' and self.model is not None:
            return self._llama_cpp_generate(prompt, max_tokens=max_tokens, temperature=temperature)

        return 'No available LLM backend for generation.'

    def _ollama_generate(self, prompt: str, max_tokens: int = 256, temperature: float = 0.2) -> str:
        try:
            payload = {
                'model': self.model_name,
                'prompt': prompt,
                'temperature': temperature,
                'max_tokens': max_tokens,
                'stream': False,
            }
            response = requests.post(f'{self.api_url}/v1/completions', json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            return data.get('choices', [{}])[0].get('message', {}).get('content', '') or data.get('choices', [{}])[0].get('text', '') or ''
        except Exception as exc:
            logger.warning('Ollama generation failed: %s', exc)
            return 'Ollama generation failed. Returning heuristic reasoning fallback.'

    def _vllm_generate(self, prompt: str, max_tokens: int = 256, temperature: float = 0.2) -> str:
        try:
            payload = {
                'model': self.model_name,
                'input': prompt,
                'temperature': temperature,
                'max_tokens': max_tokens,
            }
            response = requests.post(f'{self.api_url}/v1/completions', json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            return data.get('choices', [{}])[0].get('text', '') or data.get('choices', [{}])[0].get('message', {}).get('content', '') or ''
        except Exception as exc:
            logger.warning('vLLM generation failed: %s', exc)
            return 'vLLM generation failed. Returning heuristic reasoning fallback.'

    def _llama_cpp_generate(self, prompt: str, max_tokens: int = 256, temperature: float = 0.2) -> str:
        try:
            response = self.model.create(prompt=prompt, max_tokens=max_tokens, temperature=temperature)
            return str(response['choices'][0].get('text', '')).strip()
        except Exception as exc:
            logger.warning('llama_cpp generation failed: %s', exc)
            return 'llama_cpp generation failed. Returning heuristic reasoning fallback.'

    def query_knowledge(self, query: str, top_k: int = 3) -> List[Dict[str, str]]:
        return self.rag_store.query(query, top_k=top_k)

    def compose_audit_prompt(self, summary: Dict[str, any], knowledge_snippets: Optional[List[Dict[str, str]]] = None) -> str:
        knowledge_text = ''
        if knowledge_snippets:
            knowledge_text = '\n\n'.join([f"Source: {chunk['source']}\n{chunk['text']}" for chunk in knowledge_snippets])

        return textwrap.dedent(f"""
            You are a structural engineering AI assistant specialized in IFC 4.3, Tekla Open API, and IS 800 steel design for Pune/India.
            Review the validation summary below and provide:
            1) a clear confidence rationale for the score
            2) whether the model should be rescaled or globally corrected
            3) a high-level spatial correction strategy for the entire model
            4) the reason why the action is necessary

            VALIDATION SUMMARY:
            - unit_prediction: {summary.get('unit_prediction')}
            - scale_correction_needed: {summary.get('scale_correction_needed')}
            - disconnected_node_count: {summary.get('disconnected_node_count')}
            - semantic_mismatch_count: {summary.get('semantic_mismatch_count')}
            - advisory_text: {summary.get('advisory_text')}
            - recommendations: {summary.get('recommendations')}

            KNOWN REFERENCE MATERIALS:
            {knowledge_text}

            Answer in a short paragraph and include the phrase 'Confidence {summary.get('confidence_score')}' at the beginning.
        """).strip()

    def compose_repair_prompt(self, report: Dict[str, any], geometry_context: str) -> str:
        return textwrap.dedent(f"""
            You are a structural AI assistant executing a model correction.
            Based on the audit below, produce a single JSON object with keys:
            - 'strategy'
            - 'scale_factor'
            - 'apply_spatial_correction'
            - 'reasoning'

            AUDIT REPORT:
            {json.dumps(report, indent=2)}

            GEOMETRY CONTEXT:
            {geometry_context}

            Use the IF C 4.3 and Tekla Open API context to decide if a global 1000x scaling is required and whether a global shift is more appropriate than a local snap.
        """).strip()

    def explain(self, report: Dict[str, any], query: str) -> str:
        snippets = self.query_knowledge(query, top_k=2)
        prompt = self.compose_audit_prompt(report, knowledge_snippets=snippets)
        return self.generate(prompt, max_tokens=200)

    def plan_repair(self, report: Dict[str, any], geometry_context: str) -> Dict[str, any]:
        prompt = self.compose_repair_prompt(report, geometry_context)
        completion = self.generate(prompt, max_tokens=220)
        try:
            repair_plan = json.loads(completion)
            if isinstance(repair_plan, dict):
                return repair_plan
        except json.JSONDecodeError:
            pass
        return {
            'strategy': 'heuristic',
            'scale_factor': 1000.0 if report.get('scale_correction_needed') else 1.0,
            'apply_spatial_correction': report.get('disconnected_node_count', 0) > 0,
            'reasoning': completion
        }
