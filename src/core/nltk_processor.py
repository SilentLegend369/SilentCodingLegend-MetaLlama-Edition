"""
NLTK Text Processing Enhancement Module
Advanced natural language processing capabilities for SilentCodingLegend AI Agent
"""
import re
import nltk
import logging
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import asyncio
from concurrent.futures import ThreadPoolExecutor
from ..utils.logging import get_logger

logger = get_logger(__name__)

class TextComplexity(Enum):
    """Text complexity levels"""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"

@dataclass
class TextAnalysis:
    """Comprehensive text analysis results"""
    text: str
    word_count: int
    sentence_count: int
    complexity: TextComplexity
    sentiment_score: float
    key_terms: List[str]
    named_entities: List[Tuple[str, str]]
    readability_score: float
    technical_terms: List[str]
    reasoning_indicators: List[str]
    confidence_factors: Dict[str, float]

class NLTKProcessor:
    """
    Advanced NLTK-based text processing for enhanced AI reasoning
    """
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=2)
        self._download_required_data()
        self._initialize_components()
        logger.info("NLTK Processor initialized successfully")
    
    def _download_required_data(self):
        """Download required NLTK data packages"""
        required_packages = [
            'punkt',
            'stopwords', 
            'wordnet',
            'averaged_perceptron_tagger',
            'vader_lexicon',
            'omw-1.4',
            'maxent_ne_chunker',
            'words'
        ]
        
        for package in required_packages:
            try:
                nltk.data.find(f'tokenizers/{package}')
            except LookupError:
                try:
                    nltk.download(package, quiet=True)
                    logger.info(f"Downloaded NLTK package: {package}")
                except Exception as e:
                    logger.warning(f"Failed to download {package}: {e}")
    
    def _initialize_components(self):
        """Initialize NLTK components"""
        try:
            from nltk.sentiment import SentimentIntensityAnalyzer
            from nltk.tokenize import word_tokenize, sent_tokenize
            from nltk.corpus import stopwords
            from nltk.stem import WordNetLemmatizer
            from nltk.tag import pos_tag
            from nltk.chunk import ne_chunk
            
            self.sentiment_analyzer = SentimentIntensityAnalyzer()
            self.lemmatizer = WordNetLemmatizer()
            self.stop_words = set(stopwords.words('english'))
            
            # Technical and reasoning indicators
            self.technical_terms = {
                'programming', 'algorithm', 'function', 'variable', 'class', 'method',
                'database', 'api', 'framework', 'library', 'module', 'package',
                'debugging', 'testing', 'deployment', 'architecture', 'design',
                'optimization', 'performance', 'scalability', 'security'
            }
            
            self.reasoning_indicators = {
                'because', 'therefore', 'thus', 'consequently', 'as a result',
                'this means', 'we can conclude', 'it follows that', 'given that',
                'furthermore', 'moreover', 'however', 'nevertheless', 'alternatively',
                'first', 'second', 'third', 'next', 'then', 'finally', 'in conclusion'
            }
            
            logger.info("NLTK components initialized")
            
        except ImportError as e:
            logger.error(f"Failed to initialize NLTK components: {e}")
            raise
    
    async def analyze_text(self, text: str) -> TextAnalysis:
        """
        Comprehensive text analysis using NLTK
        
        Args:
            text (str): Text to analyze
            
        Returns:
            TextAnalysis: Comprehensive analysis results
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self._analyze_text_sync, text)
    
    def _analyze_text_sync(self, text: str) -> TextAnalysis:
        """Synchronous text analysis"""
        try:
            # Basic tokenization
            sentences = nltk.sent_tokenize(text)
            words = nltk.word_tokenize(text.lower())
            
            # Filter out punctuation and stopwords for analysis
            filtered_words = [word for word in words if word.isalpha() and word not in self.stop_words]
            
            # Sentiment analysis
            sentiment_scores = self.sentiment_analyzer.polarity_scores(text)
            sentiment_score = sentiment_scores['compound']
            
            # Extract key terms (lemmatized, non-stop words)
            key_terms = list(set([self.lemmatizer.lemmatize(word) for word in filtered_words]))
            
            # Named entity recognition
            named_entities = self._extract_named_entities(text)
            
            # Technical terms detection
            technical_terms = [word for word in filtered_words if word in self.technical_terms]
            
            # Reasoning indicators
            reasoning_indicators = [indicator for indicator in self.reasoning_indicators 
                                 if indicator in text.lower()]
            
            # Complexity assessment
            complexity = self._assess_complexity(words, sentences, technical_terms)
            
            # Readability score (simplified)
            readability_score = self._calculate_readability(words, sentences)
            
            # Confidence factors for reasoning quality
            confidence_factors = self._calculate_confidence_factors(
                text, words, sentences, reasoning_indicators, technical_terms
            )
            
            return TextAnalysis(
                text=text,
                word_count=len(words),
                sentence_count=len(sentences),
                complexity=complexity,
                sentiment_score=sentiment_score,
                key_terms=key_terms[:20],  # Top 20 key terms
                named_entities=named_entities,
                readability_score=readability_score,
                technical_terms=technical_terms,
                reasoning_indicators=reasoning_indicators,
                confidence_factors=confidence_factors
            )
            
        except Exception as e:
            logger.error(f"Text analysis failed: {e}")
            # Return basic analysis as fallback
            return TextAnalysis(
                text=text,
                word_count=len(text.split()),
                sentence_count=text.count('.') + text.count('!') + text.count('?'),
                complexity=TextComplexity.MODERATE,
                sentiment_score=0.0,
                key_terms=[],
                named_entities=[],
                readability_score=0.5,
                technical_terms=[],
                reasoning_indicators=[],
                confidence_factors={}
            )
    
    def _extract_named_entities(self, text: str) -> List[Tuple[str, str]]:
        """Extract named entities from text"""
        try:
            words = nltk.word_tokenize(text)
            pos_tags = nltk.pos_tag(words)
            chunks = nltk.ne_chunk(pos_tags, binary=False)
            
            entities = []
            for chunk in chunks:
                if hasattr(chunk, 'label'):
                    entity_text = ' '.join([c[0] for c in chunk])
                    entity_type = chunk.label()
                    entities.append((entity_text, entity_type))
            
            return entities
            
        except Exception as e:
            logger.warning(f"Named entity recognition failed: {e}")
            return []
    
    def _assess_complexity(self, words: List[str], sentences: List[str], technical_terms: List[str]) -> TextComplexity:
        """Assess text complexity"""
        if not words:
            return TextComplexity.SIMPLE
        
        avg_sentence_length = len(words) / max(len(sentences), 1)
        unique_words_ratio = len(set(words)) / len(words)
        technical_ratio = len(technical_terms) / len(words)
        
        complexity_score = (
            (avg_sentence_length / 20) * 0.4 +  # Sentence length factor
            unique_words_ratio * 0.3 +          # Vocabulary diversity
            technical_ratio * 10 * 0.3          # Technical content
        )
        
        if complexity_score < 0.3:
            return TextComplexity.SIMPLE
        elif complexity_score < 0.6:
            return TextComplexity.MODERATE
        elif complexity_score < 0.9:
            return TextComplexity.COMPLEX
        else:
            return TextComplexity.VERY_COMPLEX
    
    def _calculate_readability(self, words: List[str], sentences: List[str]) -> float:
        """Calculate simplified readability score"""
        if not words or not sentences:
            return 0.5
        
        avg_sentence_length = len(words) / len(sentences)
        
        # Simplified readability (inverse of sentence length)
        readability = 1.0 / (1.0 + avg_sentence_length / 15)
        return min(max(readability, 0.0), 1.0)
    
    def _calculate_confidence_factors(
        self, 
        text: str, 
        words: List[str], 
        sentences: List[str],
        reasoning_indicators: List[str],
        technical_terms: List[str]
    ) -> Dict[str, float]:
        """Calculate various confidence factors for reasoning quality"""
        
        factors = {}
        
        # Reasoning structure factor
        factors['reasoning_structure'] = min(len(reasoning_indicators) / 3.0, 1.0)
        
        # Technical depth factor
        factors['technical_depth'] = min(len(technical_terms) / 5.0, 1.0)
        
        # Text length factor (optimal around 100-500 words)
        word_count = len(words)
        if 50 <= word_count <= 200:
            factors['length_factor'] = 1.0
        elif 200 < word_count <= 500:
            factors['length_factor'] = 0.8
        elif word_count > 500:
            factors['length_factor'] = 0.6
        else:
            factors['length_factor'] = 0.4
        
        # Sentence structure factor
        avg_sentence_length = len(words) / max(len(sentences), 1)
        if 10 <= avg_sentence_length <= 20:
            factors['sentence_structure'] = 1.0
        else:
            factors['sentence_structure'] = 0.7
        
        # Vocabulary diversity factor
        unique_words = len(set(words))
        factors['vocabulary_diversity'] = min(unique_words / max(len(words), 1), 1.0)
        
        return factors
    
    def enhance_reasoning_confidence(self, text: str, base_confidence: float) -> float:
        """
        Enhance reasoning confidence using NLTK analysis
        
        Args:
            text (str): Text to analyze
            base_confidence (float): Base confidence from existing system
            
        Returns:
            float: Enhanced confidence score
        """
        try:
            # Quick analysis for confidence enhancement
            words = nltk.word_tokenize(text.lower())
            sentences = nltk.sent_tokenize(text)
            
            # Count reasoning indicators
            reasoning_count = sum(1 for indicator in self.reasoning_indicators 
                                if indicator in text.lower())
            
            # Count technical terms
            technical_count = sum(1 for word in words if word in self.technical_terms)
            
            # Calculate enhancement factors
            reasoning_boost = min(reasoning_count / 3.0, 0.2)  # Max 0.2 boost
            technical_boost = min(technical_count / 5.0, 0.1)  # Max 0.1 boost
            
            # Sentence structure penalty for very short/long sentences
            avg_sentence_length = len(words) / max(len(sentences), 1)
            structure_factor = 1.0
            if avg_sentence_length < 5 or avg_sentence_length > 30:
                structure_factor = 0.9
            
            enhanced_confidence = (base_confidence + reasoning_boost + technical_boost) * structure_factor
            return min(max(enhanced_confidence, 0.0), 1.0)
            
        except Exception as e:
            logger.warning(f"Confidence enhancement failed: {e}")
            return base_confidence
    
    def extract_key_concepts(self, text: str, top_n: int = 10) -> List[str]:
        """
        Extract key concepts from text using NLTK
        
        Args:
            text (str): Text to analyze
            top_n (int): Number of top concepts to return
            
        Returns:
            List[str]: Key concepts
        """
        try:
            # Tokenize and filter
            words = nltk.word_tokenize(text.lower())
            filtered_words = [
                self.lemmatizer.lemmatize(word) 
                for word in words 
                if word.isalpha() and word not in self.stop_words and len(word) > 3
            ]
            
            # Count frequency
            word_freq = {}
            for word in filtered_words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # Sort by frequency and return top N
            sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            return [word for word, freq in sorted_words[:top_n]]
            
        except Exception as e:
            logger.warning(f"Key concept extraction failed: {e}")
            return []
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess text for better analysis
        
        Args:
            text (str): Raw text
            
        Returns:
            str: Preprocessed text
        """
        try:
            # Basic cleaning
            text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
            text = text.strip()
            
            # Tokenize and lemmatize
            words = nltk.word_tokenize(text)
            lemmatized_words = []
            
            for word in words:
                if word.isalpha():
                    lemmatized_words.append(self.lemmatizer.lemmatize(word.lower()))
                else:
                    lemmatized_words.append(word)
            
            return ' '.join(lemmatized_words)
            
        except Exception as e:
            logger.warning(f"Text preprocessing failed: {e}")
            return text
    
    def detect_question_type(self, text: str) -> str:
        """
        Detect the type of question or request
        
        Args:
            text (str): Question text
            
        Returns:
            str: Question type
        """
        text_lower = text.lower()
        
        # Question word detection
        if any(word in text_lower for word in ['how', 'tutorial', 'guide', 'steps']):
            return 'procedural'
        elif any(word in text_lower for word in ['why', 'explain', 'reason']):
            return 'explanatory'
        elif any(word in text_lower for word in ['what', 'define', 'describe']):
            return 'definitional'
        elif any(word in text_lower for word in ['debug', 'fix', 'error', 'problem']):
            return 'troubleshooting'
        elif any(word in text_lower for word in ['design', 'architecture', 'build']):
            return 'design'
        elif any(word in text_lower for word in ['compare', 'difference', 'versus']):
            return 'comparative'
        else:
            return 'general'
    
    def cleanup(self):
        """Cleanup resources"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=True)
