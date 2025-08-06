"""
Unit tests for NLP processing.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.core.nlp.processor import NLPProcessor, Intent


class TestNLPProcessor:
    """Test NLP processor functionality."""
    
    @pytest.fixture
    def mock_config(self):
        """Mock configuration for testing."""
        config = Mock()
        config.get_nlp_config.return_value = Mock(
            provider="openai",
            model="gpt-4",
            max_tokens=1000,
            temperature=0.1,
            timeout=30
        )
        config.get_env_var.return_value = "test-api-key"
        return config
    
    @pytest.fixture
    def nlp_processor(self, mock_config):
        """Create NLP processor instance for testing."""
        return NLPProcessor(mock_config)
    
    def test_nlp_processor_initialization(self, nlp_processor):
        """Test NLP processor initialization."""
        assert nlp_processor is not None
        assert nlp_processor.config is not None
        assert nlp_processor.nlp_config is not None
        assert nlp_processor._intent_examples is not None
    
    def test_load_intent_examples(self, nlp_processor):
        """Test intent examples loading."""
        examples = nlp_processor._intent_examples
        
        assert "timesheet" in examples
        assert "tasks" in examples
        assert "meetings" in examples
        assert "pull_requests" in examples
        assert "summary" in examples
        
        # Check that each intent has examples
        for intent, intent_examples in examples.items():
            assert isinstance(intent_examples, list)
            assert len(intent_examples) > 0
    
    def test_extract_entities(self, nlp_processor):
        """Test entity extraction."""
        # Test time period extraction
        entities = nlp_processor._extract_entities("Show my tasks today", "tasks")
        assert entities.get("time_period") == "today"
        
        # Test person extraction
        entities = nlp_processor._extract_entities("Meeting with John tomorrow", "meetings")
        assert entities.get("person") == "John"
        assert entities.get("time_period") == "tomorrow"
        
        # Test context extraction
        entities = nlp_processor._extract_entities("Show sprint tasks", "tasks")
        assert entities.get("context") == "sprint"
    
    def test_fallback_intent_classification(self, nlp_processor):
        """Test fallback intent classification."""
        # Test timesheet intent
        intent = nlp_processor._fallback_intent_classification("Fill my timesheet")
        assert intent.name == "timesheet"
        assert intent.confidence == 0.6
        
        # Test tasks intent
        intent = nlp_processor._fallback_intent_classification("Show my tasks")
        assert intent.name == "tasks"
        assert intent.confidence == 0.6
        
        # Test meetings intent
        intent = nlp_processor._fallback_intent_classification("Show my meetings")
        assert intent.name == "meetings"
        assert intent.confidence == 0.6
        
        # Test pull requests intent
        intent = nlp_processor._fallback_intent_classification("Show my pull requests")
        assert intent.name == "pull_requests"
        assert intent.confidence == 0.6
        
        # Test summary intent
        intent = nlp_processor._fallback_intent_classification("Create a summary")
        assert intent.name == "summary"
        assert intent.confidence == 0.6
        
        # Test default case
        intent = nlp_processor._fallback_intent_classification("Random text")
        assert intent.name == "tasks"
        assert intent.confidence == 0.3
    
    def test_parse_intent_response(self, nlp_processor):
        """Test parsing OpenAI response into Intent object."""
        # Test timesheet intent
        intent = nlp_processor._parse_intent_response("timesheet", "Fill my timesheet")
        assert intent.name == "timesheet"
        assert intent.confidence == 0.8
        
        # Test tasks intent
        intent = nlp_processor._parse_intent_response("task", "Show my tasks")
        assert intent.name == "tasks"
        assert intent.confidence == 0.8
        
        # Test meetings intent
        intent = nlp_processor._parse_intent_response("meeting", "Show my meetings")
        assert intent.name == "meetings"
        assert intent.confidence == 0.8
        
        # Test default case
        intent = nlp_processor._parse_intent_response("unknown", "Random text")
        assert intent.name == "tasks"
        assert intent.confidence == 0.5
    
    @pytest.mark.asyncio
    async def test_process_query_success(self, nlp_processor):
        """Test successful query processing."""
        with patch.object(nlp_processor, '_call_openai', new_callable=AsyncMock) as mock_openai:
            mock_openai.return_value = "timesheet"
            
            result = await nlp_processor.process_query("Fill my timesheet")
            
            assert result["processed"] is True
            assert result["intent"] == "timesheet"
            assert result["confidence"] == 0.8
            assert "entities" in result
    
    @pytest.mark.asyncio
    async def test_process_query_fallback(self, nlp_processor):
        """Test query processing with fallback."""
        with patch.object(nlp_processor, '_call_openai', side_effect=Exception("API Error")):
            result = await nlp_processor.process_query("Fill my timesheet")
            
            assert result["processed"] is True
            assert result["intent"] == "timesheet"
            assert result["confidence"] == 0.6
    
    @pytest.mark.asyncio
    async def test_call_openai_success(self, nlp_processor):
        """Test successful OpenAI API call."""
        with patch('openai.ChatCompletion.create') as mock_create:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "timesheet"
            mock_create.return_value = mock_response
            
            result = await nlp_processor._call_openai("test prompt")
            assert result == "timesheet"
    
    @pytest.mark.asyncio
    async def test_call_openai_failure(self, nlp_processor):
        """Test OpenAI API call failure."""
        with patch('openai.ChatCompletion.create', side_effect=Exception("API Error")):
            with pytest.raises(Exception):
                await nlp_processor._call_openai("test prompt")


class TestIntent:
    """Test Intent model."""
    
    def test_intent_creation(self):
        """Test Intent object creation."""
        intent = Intent(
            name="timesheet",
            confidence=0.8,
            entities={"time_period": "today"}
        )
        
        assert intent.name == "timesheet"
        assert intent.confidence == 0.8
        assert intent.entities["time_period"] == "today"
    
    def test_intent_defaults(self):
        """Test Intent object with defaults."""
        intent = Intent(name="tasks", confidence=0.9)
        
        assert intent.name == "tasks"
        assert intent.confidence == 0.9
        assert intent.entities == {}
    
    def test_intent_validation(self):
        """Test Intent object validation."""
        # Should not raise validation errors
        intent = Intent(
            name="meetings",
            confidence=1.0,
            entities={"person": "John", "time_period": "tomorrow"}
        )
        
        assert intent.name == "meetings"
        assert intent.confidence == 1.0
        assert len(intent.entities) == 2 