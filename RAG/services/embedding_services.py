from openai import OpenAI
from typing import List
from app.utils.logging_config import get_logger
from RAG.config.settings import get_settings
from RAG.services.caching_service import CachingService

logger = get_logger(__name__)

class EmbeddingService:
    def __init__(self):
        settings = get_settings()
        self.model = settings.openai.embedding_model
        self.client = OpenAI(api_key=settings.openai.api_key)
        self.caching_service = CachingService()

    async def batch_create_embedding(self, texts: List[str], use_cache: bool = True) -> List[List[float]]:
        """Create embeddings for multiple texts with optional caching"""
        if not use_cache:
            # No caching, generate all embeddings
            logger.info("Caching disabled, generating all embeddings")
            return await self._generate_embeddings(texts)
            
        try:
            # Results array will match original texts order
            result_embeddings = [None] * len(texts)
            
            # Keep track of which texts need API calls
            uncached_texts = []
            uncached_indices = []
            
            # First, check cache for each text
            for idx, text in enumerate(texts):
                cached_embedding = await self.caching_service.get_cached_embedding(text)
                if cached_embedding:
                    logger.debug(f"Cache hit for text: {text[:30]}...")
                    result_embeddings[idx] = cached_embedding
                else:
                    uncached_texts.append(text)
                    uncached_indices.append(idx)
            
            # If everything was cached, we're done!
            if not uncached_texts:
                logger.info(f"Using cached embeddings for all {len(texts)} texts")
                return result_embeddings
                
            # Generate embeddings for uncached texts
            logger.info(f"Generating embeddings for {len(uncached_texts)} uncached texts out of {len(texts)} total")
            new_embeddings = await self._generate_embeddings(uncached_texts)
            
            # Cache the new embeddings and place them in results
            for i, embedding in enumerate(new_embeddings):
                orig_idx = uncached_indices[i]
                text = texts[orig_idx]
                
                # Update cache with new embedding
                await self.caching_service.cache_embedding(text, embedding)
                
                # Place in result at original position
                result_embeddings[orig_idx] = embedding
                
            return result_embeddings
        except Exception as e:
            logger.error(f"Error in cached batch embeddings: {e}")
            raise

    async def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Internal method to generate embeddings from OpenAI API"""
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            
            embeddings = [data.embedding for data in response.data]
            logger.info("Finish created embedding")
            return embeddings
        except Exception as e:
            if "insufficient_quota" in str(e):
                logger.error("OpenAI quota exceeded. Please check your billing and usage limits.")
                raise Exception("OpenAI API quota exceeded. Please check your account billing.")
            else:
                logger.error(f"Error generating embeddings from OpenAI: {e}")
                raise

    async def create_embedding(self, text: str, use_cache: bool = True) -> List[float]:
        """Create a single embedding with optional caching"""
        if not use_cache:
            # No caching, generate embedding directly
            embeddings = await self._generate_embeddings([text])
            return embeddings[0]
            
        try:
            # First check cache
            cached_embedding = await self.caching_service.get_cached_embedding(text)
            if cached_embedding:
                logger.debug(f"Using cached embedding for: {text[:30]}...")
                return cached_embedding
                
            # Generate new embedding if not cached
            embeddings = await self._generate_embeddings([text])
            logger.info("Finsihed generate embedding")
            embedding = embeddings[0]
            
            # Cache the new embedding
            await self.caching_service.cache_embedding(text, embedding)
            
            return embedding
        except Exception as e:
            logger.error(f"Error creating cached embedding: {e}")
            raise

    async def create_embedding_no_cache(self, text: str) -> List[float]:
        """Create a single embedding without using cache"""
        return await self.create_embedding(text, use_cache=False)

    async def batch_create_embedding_no_cache(self, texts: List[str]) -> List[List[float]]:
        """Create multiple embeddings without using cache"""
        return await self.batch_create_embedding(texts, use_cache=False)