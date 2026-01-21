"""
AI Conversation Memory System
Vector database for intelligent context retention and retrieval
Uses ChromaDB for local persistence
"""
import os
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class ConversationMemory:
    """
    Advanced Conversation Memory with Vector Search
    Stores and retrieves conversation history intelligently
    """
    
    def __init__(self, user_id: str, collection_name: str = "ysm_ai_memory"):
        """
        Initialize conversation memory
        
        Args:
            user_id: Unique user identifier
            collection_name: ChromaDB collection name
        """
        self.user_id = user_id
        self.collection_name = f"{collection_name}_{user_id}"
        self.client = None
        self.collection = None
        
        # Try to initialize ChromaDB
        try:
            import chromadb
            from chromadb.config import Settings
            
            # Setup persistent storage
            db_path = Path(__file__).parent.parent / '.ai_memory'
            db_path.mkdir(exist_ok=True)
            
            self.client = chromadb.PersistentClient(
                path=str(db_path),
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"user_id": user_id}
            )
            
            logger.info(f"✅ Memory Engine Active for user: {user_id}")
            
        except ImportError:
            logger.warning("ChromaDB not installed. Memory features disabled. Install: pip install chromadb")
        except Exception as e:
            logger.error(f"Memory initialization error: {e}")
    
    def add_interaction(
        self,
        question: str,
        answer: str,
        subject: str = "General",
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Store a conversation interaction
        
        Args:
            question: User's question
            answer: AI's response
            subject: Subject category
            metadata: Additional metadata
            
        Returns:
            Success status
        """
        if not self.collection:
            return False
        
        try:
            interaction_id = f"{self.user_id}_{datetime.now().timestamp()}"
            
            # Combine question + answer for better semantic search
            full_context = f"Q: {question}\nA: {answer}"
            
            # Metadata
            meta = {
                "question": question,
                "subject": subject,
                "timestamp": datetime.now().isoformat(),
                "user_id": self.user_id,
                **(metadata or {})
            }
            
            self.collection.add(
                documents=[full_context],
                metadatas=[meta],
                ids=[interaction_id]
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to store interaction: {e}")
            return False
    
    def search_memory(
        self,
        query: str,
        n_results: int = 3,
        subject_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Search conversation history using semantic similarity
        
        Args:
            query: Search query
            n_results: Number of results to return
            subject_filter: Filter by subject
            
        Returns:
            List of relevant past interactions
        """
        if not self.collection:
            return []
        
        try:
            # Build where clause for filtering
            where_clause = {"user_id": self.user_id}
            if subject_filter:
                where_clause["subject"] = subject_filter
            
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_clause if subject_filter else None
            )
            
            # Format results
            memories = []
            if results and results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    meta = results['metadatas'][0][i]
                    memories.append({
                        "context": doc,
                        "question": meta.get("question", ""),
                        "subject": meta.get("subject", "General"),
                        "timestamp": meta.get("timestamp", ""),
                        "relevance": 1.0 - results['distances'][0][i]  # Convert distance to similarity
                    })
            
            return memories
            
        except Exception as e:
            logger.error(f"Memory search error: {e}")
            return []
    
    def get_recent_conversations(self, limit: int = 5) -> List[Dict]:
        """
        Get recent conversations chronologically
        
        Args:
            limit: Number of recent interactions
            
        Returns:
            List of recent conversations
        """
        if not self.collection:
            return []
        
        try:
            # Get all, then sort by timestamp
            all_items = self.collection.get(
                where={"user_id": self.user_id},
                limit=limit * 2  # Get more to ensure we have enough after filtering
            )
            
            if not all_items or not all_items['metadatas']:
                return []
            
            # Sort by timestamp descending
            items_with_time = []
            for i, meta in enumerate(all_items['metadatas']):
                items_with_time.append({
                    "question": meta.get("question", ""),
                    "subject": meta.get("subject", "General"),
                    "timestamp": meta.get("timestamp", ""),
                    "context": all_items['documents'][i] if all_items['documents'] else ""
                })
            
            # Sort and limit
            items_with_time.sort(key=lambda x: x['timestamp'], reverse=True)
            return items_with_time[:limit]
            
        except Exception as e:
            logger.error(f"Recent conversations error: {e}")
            return []
    
    def clear_history(self) -> bool:
        """
        Clear all conversation history for this user
        
        Returns:
            Success status
        """
        if not self.collection:
            return False
        
        try:
            # Delete collection and recreate
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"user_id": self.user_id}
            )
            logger.info(f"Memory cleared for user: {self.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Clear history error: {e}")
            return False
    
    def get_context_for_query(self, query: str, max_context_length: int = 500) -> str:
        """
        Get relevant context from past conversations for current query
        
        Args:
            query: Current user query
            max_context_length: Max characters of context to return
            
        Returns:
            Formatted context string
        """
        memories = self.search_memory(query, n_results=2)
        
        if not memories:
            return ""
        
        context_parts = []
        total_length = 0
        
        for mem in memories:
            context_str = f"Previously discussed ({mem['subject']}): {mem['question']}"
            if total_length + len(context_str) < max_context_length:
                context_parts.append(context_str)
                total_length += len(context_str)
        
        if context_parts:
            return "Relevant past context:\n" + "\n".join(context_parts)
        return ""


# Cache memory instances per user
_memory_instances = {}

def get_conversation_memory(user_id: str) -> ConversationMemory:
    """
    Get or create conversation memory for user
    
    Args:
        user_id: User identifier
        
    Returns:
        ConversationMemory instance
    """
    if user_id not in _memory_instances:
        _memory_instances[user_id] = ConversationMemory(user_id)
    return _memory_instances[user_id]
