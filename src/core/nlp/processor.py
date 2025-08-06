"""
NLP Processor

Handles natural language processing for intent classification and entity extraction.
"""

import asyncio
import os
import re
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import openai
from utils.logger import LoggerMixin


class Intent(BaseModel):
    """Represents a classified intent."""
    name: str
    confidence: float
    entities: Dict[str, Any] = {}


class NLPProcessor(LoggerMixin):
    """Handles natural language processing for the OSI ONE AGENT."""
    
    def __init__(self, config):
        """Initialize NLP processor."""
        super().__init__()
        self.config = config
        self.nlp_config = config.get_nlp_config()
        self._setup_openai()
        self._intent_examples = self._load_intent_examples()
    
    def _setup_openai(self) -> None:
        """Setup OpenAI client."""
        api_key = self.config.get_env_var("OPENAI_API_KEY")
        if not api_key:
            self.log_warning("OpenAI API key not found in environment variables")
            return
        
        openai.api_key = api_key
        self.log_info("OpenAI client configured")
    
    def _load_intent_examples(self) -> Dict[str, List[str]]:
        """Load intent classification examples."""
        return {
            "timesheet": [
                "Fill my timesheet",
                "Submit my timesheet",
                "Show my timesheet entries",
                "Fill my timesheet based on last week's PRs",
                "Auto-fill timesheet with DevOps data"
            ],
            "tasks": [
                "Show my tasks",
                "What are my assigned tasks",
                "Get my tasks for this sprint",
                "Show my work items",
                "List my current tasks",
                "Show tasks with Active status"
            ],
            "task_update": [
                "Update task TASK-12345",
                "Change the status of TASK-12345 to Active",
                "Modify the priority of TASK-12345",
                "Update Start Date of TASK-12345 to 08/06/2025",
                "Change Finish Date of TASK-12345 to 08/07/2025",
                "Update [Start Date] and [Finish Date] of [TASK-12345]",
                "Modify field values of TASK-12345",
                "Change task TASK-12345 status to Active"
            ],
            "meetings": [
                "Show my meetings",
                "What meetings do I have today",
                "Show my calendar",
                "Do I have meetings with John",
                "Get my schedule"
            ],
            "pull_requests": [
                "Show my pull requests",
                "Get my recent PRs",
                "List my code reviews",
                "Show my recent PRs"
            ],
            "summary": [
                "Summarize my activity",
                "Create a summary of my work",
                "Show my productivity metrics",
                "Generate a report"
            ]
        }
    
    async def classify_intent(self, user_input: str) -> Intent:
        """
        Classify user intent from natural language input.
        
        Args:
            user_input: User's natural language input
            
        Returns:
            Classified intent with confidence and entities
        """
        try:
            # Check for update scenarios first
            user_input_lower = user_input.lower()
            update_keywords = ["update", "modify", "change", "edit", "set"]
            task_id_patterns = [r"task-\d+", r"story-\d+", r"bug-\d+", r"epic-\d+", r"requirement-\d+", r"\[task-\d+\]", r"\[story-\d+\]", r"\[bug-\d+\]", r"\[epic-\d+\]", r"\[requirement-\d+\]"]
            
            has_update_keyword = any(keyword in user_input_lower for keyword in update_keywords)
            has_task_id = any(re.search(pattern, user_input_lower) for pattern in task_id_patterns)
            
            # If update keyword is present, use fallback classification (which has safety logic)
            if has_update_keyword:
                return self._fallback_intent_classification(user_input)
            
            # Create prompt for intent classification
            prompt = self._create_intent_prompt(user_input)
            
            # Call OpenAI API
            response = await self._call_openai(prompt)
            
            # Parse response
            intent = self._parse_intent_response(response, user_input)
            
            self.log_info("Intent classified", 
                         input=user_input, 
                         intent=intent.name, 
                         confidence=intent.confidence)
            
            return intent
            
        except Exception as e:
            self.log_error("Failed to classify intent", input=user_input, error=str(e))
            # Fallback to basic keyword matching
            return self._fallback_intent_classification(user_input)
    
    def _create_intent_prompt(self, user_input: str) -> str:
        """Create prompt for intent classification."""
        examples = []
        for intent, examples_list in self._intent_examples.items():
            for example in examples_list[:3]:  # Limit examples per intent
                examples.append(f"Input: {example}\nIntent: {intent}")
        
        examples_text = "\n".join(examples)
        
        return f"""
You are an intent classifier for an AI assistant that helps with:
- Timesheet management
- Task tracking and updates
- Meeting scheduling
- Pull request management
- Activity summarization

IMPORTANT: Distinguish between task QUERIES and task UPDATES:
- If the user wants to SEE/LIST/GET tasks → classify as "tasks"
- If the user wants to MODIFY/UPDATE/CHANGE task fields → classify as "task_update"

Classify the following user input into one of these intents:
- timesheet: Timesheet-related requests
- tasks: Task and work item queries (show, list, get, display tasks)
- task_update: Task and work item updates (modify, change, update fields, edit tasks)
- meetings: Calendar and meeting requests
- pull_requests: Pull request and code review requests
- summary: Summary and report requests

Examples:
{examples_text}

Input: {user_input}
Intent:"""
    
    async def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API."""
        try:
            from openai import OpenAI
            
            # Get API key from environment or config
            api_key = self.config.get_openai_api_key()
            
            if not api_key:
                error_msg = (
                    f"🔧 **OpenAI Configuration Required**\n\n"
                    f"I need an OpenAI API key to process your requests.\n\n"
                    f"**Setup Instructions:**\n"
                    f"1. Set the environment variable:\n"
                    f"   - `OPENAI_API_KEY`: Your OpenAI API key\n\n"
                    f"2. Or add it to your config file: `config/app/app.yaml`\n\n"
                    f"**Example:**\n"
                    f"```bash\n"
                    f"# Set environment variable\n"
                    f"export OPENAI_API_KEY=your_openai_api_key_here\n"
                    f"```\n\n"
                    f"Once configured, I'll be able to understand and process your requests!"
                )
                raise ValueError(error_msg)
            
            client = OpenAI(api_key=api_key)
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model=self.nlp_config.model,
                messages=[
                    {"role": "system", "content": "You are a helpful intent classifier."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.nlp_config.max_tokens,
                temperature=self.nlp_config.temperature
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.log_error("OpenAI API call failed", error=str(e))
            raise
    
    def _parse_intent_response(self, response: str, user_input: str) -> Intent:
        """Parse OpenAI response into Intent object."""
        # Extract intent name from response
        intent_name = response.lower().strip()
        
        # Map to known intents
        intent_mapping = {
            "timesheet": "timesheet",
            "task": "tasks",
            "task update": "task_update",
            "update": "task_update",
            "modify": "task_update",
            "change": "task_update",
            "meeting": "meetings",
            "calendar": "meetings",
            "pull request": "pull_requests",
            "pr": "pull_requests",
            "summary": "summary",
            "report": "summary"
        }
        
        # Find matching intent
        for keyword, intent in intent_mapping.items():
            if keyword in intent_name:
                return Intent(
                    name=intent,
                    confidence=0.8,  # Default confidence
                    entities=self._extract_entities(user_input, intent)
                )
        
        # Default to tasks if no match
        return Intent(
            name="tasks",
            confidence=0.5,
            entities=self._extract_entities(user_input, "tasks")
        )
    
    def _extract_entities(self, user_input: str, intent: str) -> Dict[str, Any]:
        """Extract entities from user input."""
        entities = {}
        user_input_lower = user_input.lower()
        
        # Extract time-related entities
        time_keywords = ["today", "tomorrow", "yesterday", "this week", "last week", "next week", "this sprint", "current sprint"]
        for keyword in time_keywords:
            if keyword in user_input_lower:
                entities["time_period"] = keyword
                break
        
        # Extract status filters
        status_keywords = {
            "active": ["active", "in progress", "in-progress", "working", "started"],
            "new": ["new", "created", "assigned"],
            "resolved": ["resolved", "completed", "done", "finished"],
            "closed": ["closed", "closed", "finished"],
            "blocked": ["blocked", "waiting", "on hold", "stuck"]
        }
        
        for status, keywords in status_keywords.items():
            if any(keyword in user_input_lower for keyword in keywords):
                entities["status"] = status
                break
        
        # Extract task ID patterns (case-insensitive)
        task_id_patterns = [
            r"task-(\d+)",
            r"story-(\d+)",
            r"bug-(\d+)",
            r"epic-(\d+)",
            r"requirement-(\d+)",
            r"\[task-(\d+)\]",
            r"\[story-(\d+)\]",
            r"\[bug-(\d+)\]",
            r"\[epic-(\d+)\]",
            r"\[requirement-(\d+)\]",
            # Add patterns for space-separated formats (case-insensitive)
            r"task\s+(\d+)",
            r"user\s+story\s+(\d+)",
            r"story\s+(\d+)",
            r"bug\s+(\d+)",
            r"epic\s+(\d+)",
            r"requirement\s+(\d+)"
        ]
        
        # Check for batch update patterns
        batch_update_pattern = r"update following individual tasks:"
        if re.search(batch_update_pattern, user_input_lower):
            # Extract multiple task updates
            batch_updates = self._extract_batch_updates(user_input)
            if batch_updates is not None:
                entities["batch_updates"] = batch_updates
                return entities
            else:
                # Invalid batch update - add error information
                entities["batch_update_error"] = True
                return entities
        
        # Single task ID extraction (case-insensitive)
        for pattern in task_id_patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                entities["task_id"] = match.group(1)
                break
        
        # Extract field names for updates
        field_patterns = {
            "start_date": [r"start date", r"startdate", r"start"],
            "finish_date": [r"finish date", r"finishdate", r"finish", r"end date", r"enddate"],
            "status": [r"status", r"state"],
            "priority": [r"priority"],
            "title": [r"title", r"name"],
            "description": [r"description", r"desc"],
            "assigned_to": [r"assigned to", r"assigned", r"assignee"],
            "remaining": [r"remaining"],
            "completed": [r"completed"],
            "original_estimate": [r"original estimate", r"originalestimate", r"estimate"]
        }
        
        # Extract all field names that match (not just the first one)
        field_names = []
        for field_name, patterns in field_patterns.items():
            for pattern in patterns:
                if re.search(pattern, user_input_lower):
                    field_names.append(field_name)
                    break
        
        if field_names:
            entities["field_names"] = field_names  # Store as list
            entities["field_name"] = field_names[0]  # Keep first for backward compatibility
        
        # Extract date values
        date_patterns = [
            r"(\d{1,2}/\d{1,2}/\d{4})",  # MM/DD/YYYY
            r"(\d{4}-\d{1,2}-\d{1,2})",  # YYYY-MM-DD
            r"(\d{1,2}-\d{1,2}-\d{4})"   # MM-DD-YYYY
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, user_input)
            if matches:
                entities["date_values"] = matches
                break
        
        # Extract numeric values for remaining, completed, and original estimate fields (case-insensitive)
        numeric_values = []
        remaining_values = []
        completed_values = []
        original_estimate_values = []
        
        # Patterns for remaining field
        remaining_patterns = [
            r"remaining\s+to\s+(\d+)",
            r"remaining\s+(\d+)"
        ]
        
        for pattern in remaining_patterns:
            matches = re.findall(pattern, user_input, re.IGNORECASE)
            if matches:
                remaining_values.extend(matches)
        
        # Patterns for completed field
        completed_patterns = [
            r"completed\s+to\s+(\d+)",
            r"completed\s+(\d+)"
        ]
        
        for pattern in completed_patterns:
            matches = re.findall(pattern, user_input, re.IGNORECASE)
            if matches:
                completed_values.extend(matches)
        
        # Patterns for original estimate field
        original_estimate_patterns = [
            r"original estimate\s+to\s+(\d+)",
            r"original estimate\s+(\d+)",
            r"original estimate\s*->\s*(\d+)",
            r"estimate\s+to\s+(\d+)",
            r"estimate\s+(\d+)",
            r"estimate\s*->\s*(\d+)",
            r"for original estimate\s+to\s+(\d+)",
            r"for original estimate\s+(\d+)",
            r"for original estimate\s*->\s*(\d+)"
        ]
        
        for pattern in original_estimate_patterns:
            matches = re.findall(pattern, user_input, re.IGNORECASE)
            if matches:
                original_estimate_values.extend(matches)
        
        if remaining_values:
            entities["remaining_values"] = remaining_values
        if completed_values:
            entities["completed_values"] = completed_values
        if original_estimate_values:
            entities["original_estimate_values"] = original_estimate_values
        
        # Extract assignee values for assignee updates
        assignee_values = []
        # Pattern to extract names in quotes or after assignee keywords
        assignee_patterns = [
            r"assignee\s*->\s*['\"]([^'\"]+)['\"]",
            r"assignee\s+to\s+['\"]([^'\"]+)['\"]",
            r"assigned\s+to\s+['\"]([^'\"]+)['\"]",
            r"assign\s+to\s+['\"]([^'\"]+)['\"]"
        ]
        
        for pattern in assignee_patterns:
            matches = re.findall(pattern, user_input, re.IGNORECASE)
            if matches:
                assignee_values.extend(matches)
        
        if assignee_values:
            entities["assignee_values"] = assignee_values
        
        # Extract status values for status updates
        status_values = []
        status_keywords = {
            "active": ["active", "in progress", "in-progress", "working", "started"],
            "new": ["new", "created", "assigned"],
            "resolved": ["resolved", "completed", "done", "finished"],
            "closed": ["closed", "closed", "finished"],
            "blocked": ["blocked", "waiting", "on hold", "stuck"]
        }
        
        # Look for status values in the input
        for status, keywords in status_keywords.items():
            if any(keyword in user_input_lower for keyword in keywords):
                status_values.append(status)
        
        if status_values:
            entities["status_values"] = status_values
        
        # Extract sprint information
        sprint_patterns = [
            r"sprint\s+(\d+)",
            r"sprint\s+(\w+)",
            r"current\s+sprint",
            r"this\s+sprint"
        ]
        
        for pattern in sprint_patterns:
            match = re.search(pattern, user_input_lower)
            if match:
                entities["sprint"] = match.group(1) if match.groups() else "current"
                break
        
        # Extract person names (simple pattern)
        person_pattern = r"(?:with|meeting with|call with)\s+([A-Z][a-z]+)"
        person_match = re.search(person_pattern, user_input, re.IGNORECASE)
        if person_match:
            entities["person"] = person_match.group(1)
        
        # Extract project/task keywords
        project_keywords = ["sprint", "project", "feature", "bug", "story", "task"]
        for keyword in project_keywords:
            if keyword in user_input_lower:
                entities["context"] = keyword
                break
        
        # Extract priority information
        priority_keywords = {
            "high": ["high priority", "urgent", "critical"],
            "medium": ["medium priority", "normal"],
            "low": ["low priority", "low"]
        }
        
        for priority, keywords in priority_keywords.items():
            if any(keyword in user_input_lower for keyword in keywords):
                entities["priority"] = priority
                break
        
        # Extract specific task types
        task_types = {
            "user_story": ["user story", "story", "feature"],
            "bug": ["bug", "defect", "issue"],
            "task": ["task", "work item"],
            "epic": ["epic", "large feature"]
        }
        
        for task_type, keywords in task_types.items():
            if any(keyword in user_input_lower for keyword in keywords):
                entities["task_type"] = task_type
                break
        
        return entities
    
    def _extract_batch_updates(self, user_input: str) -> List[Dict[str, Any]]:
        """Extract multiple task updates from batch update command."""
        updates = []
        invalid_lines = []
        lines = user_input.split('\n')
        
        # Skip the header line
        for i, line in enumerate(lines[1:], 1):
            line = line.strip()
            if not line:
                continue
                
            # Extract task ID and updates from each line
            # Pattern: TASK 51311 -> Start Date -> 08/08/2025 Finish Date -> 08/11/2025
            task_match = re.search(r'task\s+(\d+)\s*->', line, re.IGNORECASE)
            if not task_match:
                # If no task ID found, this is an invalid line
                invalid_lines.append(f"Line {i}: {line}")
                continue
                
            task_id = task_match.group(1)
            
            # Validate task ID is numeric
            if not task_id.isdigit():
                invalid_lines.append(f"Line {i}: Invalid task ID '{task_id}' in '{line}'")
                continue
            
            # Extract field updates
            field_updates = {}
            
            # Extract Start Date
            start_date_match = re.search(r'start date\s*->\s*(\d{1,2}/\d{1,2}/\d{4})', line, re.IGNORECASE)
            if start_date_match:
                field_updates["start_date"] = start_date_match.group(1)
            
            # Extract Finish Date
            finish_date_match = re.search(r'finish date\s*->\s*(\d{1,2}/\d{1,2}/\d{4})', line, re.IGNORECASE)
            if finish_date_match:
                field_updates["finish_date"] = finish_date_match.group(1)
            
            # Extract Status
            status_match = re.search(r'status\s*->\s*(\w+)', line, re.IGNORECASE)
            if status_match:
                field_updates["status"] = status_match.group(1).lower()
            
            if field_updates:
                updates.append({
                    "task_id": task_id,
                    "field_updates": field_updates
                })
            else:
                invalid_lines.append(f"Line {i}: No valid field updates found in '{line}'")
        
        # If there are any invalid lines, return None to indicate validation failure
        if invalid_lines:
            return None
        
        return updates
    
    def _fallback_intent_classification(self, user_input: str) -> Intent:
        """Fallback intent classification using keyword matching."""
        user_input_lower = user_input.lower()
        
        # Check for task update patterns first (higher priority)
        update_keywords = ["update", "modify", "change", "edit", "set"]
        task_id_patterns = [r"task-\d+", r"story-\d+", r"bug-\d+", r"epic-\d+", r"requirement-\d+", r"\[task-\d+\]", r"\[story-\d+\]", r"\[bug-\d+\]", r"\[epic-\d+\]", r"\[requirement-\d+\]"]
        
        has_update_keyword = any(keyword in user_input_lower for keyword in update_keywords)
        has_task_id = any(re.search(pattern, user_input_lower) for pattern in task_id_patterns)
        
        # CRITICAL SAFETY: Classify as task_update if update keyword is present (with or without task ID)
        # This allows the safety validation to block dangerous queries
        if has_update_keyword:
            if has_task_id:
                return Intent(name="task_update", confidence=0.8, entities=self._extract_entities(user_input, "task_update"))
            else:
                # If update keyword is present but no specific task ID, still classify as task_update
                # so that the safety validation can block it with the proper error message
                self.log_warning("Update keyword detected without specific task ID - classifying as task_update for safety validation", 
                               user_input=user_input)
                return Intent(name="task_update", confidence=0.6, entities=self._extract_entities(user_input, "task_update"))
        
        # Keyword-based classification
        if any(word in user_input_lower for word in ["timesheet", "time", "fill", "submit"]):
            return Intent(name="timesheet", confidence=0.6, entities={})
        
        elif any(word in user_input_lower for word in ["task", "work", "item", "sprint"]):
            return Intent(name="tasks", confidence=0.6, entities={})
        
        elif any(word in user_input_lower for word in ["meeting", "calendar", "schedule", "call"]):
            return Intent(name="meetings", confidence=0.6, entities={})
        
        elif any(word in user_input_lower for word in ["pull request", "pr", "review", "code"]):
            return Intent(name="pull_requests", confidence=0.6, entities={})
        
        elif any(word in user_input_lower for word in ["summary", "report", "activity"]):
            return Intent(name="summary", confidence=0.6, entities={})
        
        else:
            # Default to tasks
            return Intent(name="tasks", confidence=0.3, entities={})
    
    async def process_query(self, user_input: str) -> Dict[str, Any]:
        """
        Process a user query and return structured information.
        
        Args:
            user_input: User's natural language input
            
        Returns:
            Dictionary with intent, entities, and processed information
        """
        intent = await self.classify_intent(user_input)
        
        return {
            "intent": intent.name,
            "confidence": intent.confidence,
            "entities": intent.entities,
            "original_input": user_input,
            "processed": True
        } 