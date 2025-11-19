"""
MemoryModule: Manages embeddings and learning history for all agents.
Uses sentence-transformers for semantic embeddings and stores memory patterns.
"""

import os
import json
import pickle
import sqlite3
import numpy as np
import threading
from typing import Dict, List, Any, Optional
from datetime import datetime
from sentence_transformers import SentenceTransformer

# Optional FAISS import - used only when available and requested
try:
    import faiss
    _HAS_FAISS = True
except Exception:
    faiss = None
    _HAS_FAISS = False


class MemoryModule:
    """
    Central memory system that stores embeddings and learning history.
    Enables agents to recall past interactions and learn from feedback.
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        model: Optional[Any] = None,
        persist: bool = False,
        db_path: Optional[str] = None,
        use_faiss: bool = False,
    ):
        """
        Initialize the MemoryModule with a sentence transformer model.

        Args:
            model_name: HuggingFace model for embeddings
            model: Optional pre-instantiated model (useful for testing/mocking)
        """
        # Allow injecting a pre-created model (useful for tests/mocks)
        if model is not None:
            self.model = model
        else:
            self.model = SentenceTransformer(model_name)

        # Lock to make the memory module safe for concurrent access
        self.lock = threading.RLock()

        # Persistence options
        self.persist = bool(persist)
        self.db_path = db_path or os.path.join(os.getcwd(), "memory_store.db")

        # FAISS option (only active if requested and available)
        self.use_faiss = bool(use_faiss) and _HAS_FAISS
        self._faiss_indices: Dict[str, Any] = {}
        self._embedding_dim: Optional[int] = None

        self.memories: Dict[str, List[Dict[str, Any]]] = {
            "story_context": [],
            "character_descriptions": [],
            "scene_settings": [],
            "music_metadata": [],
            "feedback_history": [],
        }
        self.embeddings: Dict[str, List[np.ndarray]] = {
            key: [] for key in self.memories.keys()
        }
        self.learning_patterns: Dict[str, List[float]] = {
            "story_coherence": [],
            "character_consistency": [],
            "scene_vividness": [],
            "music_relevance": [],
            "user_satisfaction": [],
        }

        # If persistence is enabled, initialize DB and load stored memories
        if self.persist:
            self._init_db()
            self._load_from_db()

        # If FAISS enabled and there are already embeddings, build indices lazily
        if self.use_faiss:
            # actual index creation happens on first store or load
            pass

    # --- Persistence / FAISS helper methods ---
    def _init_db(self) -> None:
        """Initialize SQLite database and tables for persistence."""
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        c = self._conn.cursor()
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT,
                timestamp TEXT,
                embedding BLOB
            )
            """
        )
        self._conn.commit()

    def _db_insert_memory(self, category: str, memory_entry: Dict[str, Any], embedding: np.ndarray) -> None:
        """Insert memory entry into SQLite DB."""
        c = self._conn.cursor()
        c.execute(
            "INSERT INTO memories (category, content, metadata, timestamp, embedding) VALUES (?, ?, ?, ?, ?)",
            (
                category,
                memory_entry["content"],
                json.dumps(memory_entry.get("metadata", {})),
                memory_entry.get("timestamp"),
                pickle.dumps(embedding),
            ),
        )
        self._conn.commit()

    def _load_from_db(self) -> None:
        """Load stored memories from DB into in-memory structures and build FAISS indices if requested."""
        c = self._conn.cursor()
        c.execute("SELECT id, category, content, metadata, timestamp, embedding FROM memories ORDER BY id ASC")
        rows = c.fetchall()
        for idx, category, content, metadata_json, timestamp, emb_blob in rows:
            try:
                metadata = json.loads(metadata_json) if metadata_json else {}
            except Exception:
                metadata = {}
            try:
                embedding = pickle.loads(emb_blob) if emb_blob is not None else None
                if embedding is not None:
                    embedding = np.asarray(embedding, dtype=float)
            except Exception:
                embedding = None

            if category not in self.memories:
                self.memories[category] = []
                self.embeddings[category] = []

            mem = {"content": content, "timestamp": timestamp, "metadata": metadata}
            self.memories[category].append(mem)
            if embedding is not None:
                # ensure normalization
                norm = np.linalg.norm(embedding)
                if norm > 0:
                    embedding = embedding / norm
                self.embeddings[category].append(embedding)

        # After loading embeddings, if FAISS is requested, build indices
        if self.use_faiss and _HAS_FAISS:
            for category, embs in self.embeddings.items():
                if embs:
                    arr = np.vstack(embs).astype(np.float32)
                    dim = arr.shape[1]
                    index = faiss.IndexFlatIP(dim)
                    index.add(arr)
                    # map faiss's position to memory index (identity mapping)
                    idx_to_pos = {i: i for i in range(arr.shape[0])}
                    self._faiss_indices[category] = (index, idx_to_pos)

    def _faiss_add(self, category: str, embedding: np.ndarray) -> None:
        """Add a single normalized embedding to the FAISS index for a category."""
        if not _HAS_FAISS or not self.use_faiss:
            return

        # Ensure embedding dim
        dim = int(embedding.shape[0])
        if self._embedding_dim is None:
            self._embedding_dim = dim

        if category not in self._faiss_indices or self._faiss_indices.get(category) is None:
            # create index
            index = faiss.IndexFlatIP(self._embedding_dim)
            idx_to_pos: Dict[int, int] = {}
            self._faiss_indices[category] = (index, idx_to_pos)

        index, idx_to_pos = self._faiss_indices[category]

        # faiss requires float32
        vec = np.asarray(embedding, dtype=np.float32).reshape(1, -1)
        index.add(vec)
        pos = int(index.ntotal) - 1
        # the memory index is the last appended memory for this category
        mem_idx = len(self.memories[category]) - 1
        idx_to_pos[pos] = mem_idx

    def close(self) -> None:
        """Close any open resources (DB connection)."""
        try:
            if getattr(self, "_conn", None) is not None:
                self._conn.close()
        except Exception:
            pass

    def store_memory(
        self,
        category: str,
        content: str,
        metadata: Dict[str, Any] = None,
    ) -> None:
        """
        Store a memory entry with its embedding.

        Args:
            category: Memory category (story_context, character_descriptions, etc.)
            content: Text content to store
            metadata: Additional metadata (agent_name, timestamp, etc.)
        """
        with self.lock:
            if category not in self.memories:
                self.memories[category] = []
                self.embeddings[category] = []

            # Generate embedding
            embedding = self.model.encode(content, convert_to_numpy=True)

            # Ensure numpy array and normalize to unit length for fast cosine similarity
            embedding = np.asarray(embedding, dtype=float)
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm

            # Set embedding dim if unknown
            if self._embedding_dim is None:
                self._embedding_dim = embedding.shape[0]

            # Store memory entry
            memory_entry = {
                "content": content,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {},
            }
            self.memories[category].append(memory_entry)
            self.embeddings[category].append(embedding)

            # If persistence enabled, save to DB
            if self.persist:
                try:
                    self._db_insert_memory(category, memory_entry, embedding)
                except Exception:
                    # persistence should not break runtime; log/ignore
                    pass

            # If FAISS enabled, add to index
            if self.use_faiss:
                self._faiss_add(category, embedding)

    def recall_similar(
        self, category: str, query: str, top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Retrieve similar memories using semantic similarity.

        Args:
            category: Memory category to search in
            query: Query text
            top_k: Number of top results to return

        Returns:
            List of similar memory entries with similarity scores
        """
        with self.lock:
            if category not in self.memories or not self.embeddings[category]:
                return []

            query_embedding = self.model.encode(query, convert_to_numpy=True)
            query_embedding = np.asarray(query_embedding, dtype=float)
            q_norm = np.linalg.norm(query_embedding)
            if q_norm > 0:
                query_embedding = query_embedding / q_norm

            # If FAISS is enabled and an index exists for this category, use it
            if self.use_faiss and category in self._faiss_indices and self._faiss_indices[category] is not None:
                index, idx_to_pos = self._faiss_indices[category]
                # search expects shape (n, dim)
                D, I = index.search(np.expand_dims(query_embedding.astype(np.float32), axis=0), top_k)
                results = []
                for dist, pos in zip(D[0], I[0]):
                    if pos < 0:
                        continue
                    mem_idx = idx_to_pos.get(int(pos))
                    if mem_idx is None:
                        continue
                    results.append({**self.memories[category][mem_idx], "similarity": float(dist)})
                return results

            # Fallback: numpy dot product over normalized embeddings
            category_embeddings = np.vstack(self.embeddings[category])
            similarities = np.dot(category_embeddings, query_embedding)
            top_indices = np.argsort(similarities)[::-1][:top_k]
            results = []
            for idx in top_indices:
                results.append({**self.memories[category][idx], "similarity": float(similarities[idx])})
            return results

    def record_feedback(
        self, agent_name: str, quality_score: float, feedback_text: str = ""
    ) -> None:
        """
        Record feedback for an agent's performance.

        Args:
            agent_name: Name of the agent
            quality_score: Quality score (0-1)
            feedback_text: Optional feedback text
        """
        with self.lock:
            feedback_entry = {
                "agent": agent_name,
                "score": quality_score,
                "feedback": feedback_text,
                "timestamp": datetime.now().isoformat(),
            }
            # Ensure feedback_history exists
            if "feedback_history" not in self.memories:
                self.memories["feedback_history"] = []
                self.embeddings["feedback_history"] = []

            self.memories["feedback_history"].append(feedback_entry)

            # Store embedding of feedback (normalized)
            text_to_embed = f"{agent_name}: {feedback_text}"
            embedding = self.model.encode(text_to_embed, convert_to_numpy=True)
            embedding = np.asarray(embedding, dtype=float)
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
            self.embeddings["feedback_history"].append(embedding)

            if self.persist:
                try:
                    self._db_insert_memory("feedback_history", feedback_entry, embedding)
                except Exception:
                    pass

            if self.use_faiss:
                self._faiss_add("feedback_history", embedding)

    def update_learning_pattern(
        self, pattern_type: str, value: float
    ) -> None:
        """
        Update a learning pattern metric.

        Args:
            pattern_type: Type of learning pattern
            value: Numeric value to record
        """
        with self.lock:
            if pattern_type in self.learning_patterns:
                self.learning_patterns[pattern_type].append(value)

    def get_learning_stats(self) -> Dict[str, Dict[str, float]]:
        """
        Get statistics on learning patterns.

        Returns:
            Dictionary with statistics for each pattern
        """
        with self.lock:
            stats = {}
            for pattern_type, values in self.learning_patterns.items():
                if values:
                    stats[pattern_type] = {
                        "mean": float(np.mean(values)),
                        "std": float(np.std(values)),
                        "max": float(np.max(values)),
                        "min": float(np.min(values)),
                        "count": len(values),
                    }
                else:
                    stats[pattern_type] = {
                        "mean": 0.0,
                        "std": 0.0,
                        "max": 0.0,
                        "min": 0.0,
                        "count": 0,
                    }
            return stats

    def get_memory_summary(self) -> Dict[str, int]:
        """
        Get a summary of stored memories.

        Returns:
            Dictionary with count of memories in each category
        """
        with self.lock:
            return {category: len(entries) for category, entries in self.memories.items()}

    def clear_memory(self, category: str = None) -> None:
        """
        Clear memories from a specific category or all categories.

        Args:
            category: Specific category to clear, or None to clear all
        """
        with self.lock:
            if category:
                if category in self.memories:
                    self.memories[category] = []
                    self.embeddings[category] = []
            else:
                for key in list(self.memories.keys()):
                    self.memories[key] = []
                    self.embeddings[key] = []

