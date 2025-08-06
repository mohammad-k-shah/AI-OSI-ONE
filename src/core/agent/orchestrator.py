"""
Agent Orchestrator

Coordinates between NLP processing and tool execution.
"""

import asyncio
from typing import Dict, List, Any, Optional
from utils.logger import LoggerMixin
from core.nlp.processor import NLPProcessor


class AgentOrchestrator(LoggerMixin):
    """Orchestrates the agent workflow and tool execution."""
    
    def __init__(self, config, token_manager):
        """Initialize agent orchestrator."""
        super().__init__()
        self.config = config
        self.token_manager = token_manager
        self.nlp_processor = NLPProcessor(config)
        self.tools = {}  # Will be populated with available tools
        self.conversation_history = []
        
        # Initialize tools
        self._initialize_tools()
        
        self.log_info("Agent orchestrator initialized")
    
    async def process_query(self, user_input: str) -> Dict[str, Any]:
        """
        Process a user query through the complete pipeline.
        
        Args:
            user_input: User's natural language input
            
        Returns:
            Dictionary with response and metadata
        """
        try:
            self.log_info("Processing user query", input=user_input)
            
            # Step 1: NLP Processing
            nlp_result = await self.nlp_processor.process_query(user_input)
            
            # Step 2: Tool Selection
            selected_tool = self._select_tool(nlp_result)
            
            # Step 3: Tool Execution (placeholder for now)
            tool_result = await self._execute_tool(selected_tool, nlp_result)
            
            # Step 4: Response Generation
            response = self._generate_response(nlp_result, tool_result)
            
            # Step 5: Update conversation history
            self._update_conversation_history(user_input, nlp_result, response)
            
            self.log_info("Query processed successfully", 
                         intent=nlp_result["intent"], 
                         tool=selected_tool)
            
            return {
                "success": True,
                "response": response,
                "intent": nlp_result["intent"],
                "confidence": nlp_result["confidence"],
                "tool_used": selected_tool,
                "metadata": {
                    "processing_time": 0,  # TODO: Add timing
                    "entities": nlp_result["entities"]
                }
            }
            
        except Exception as e:
            self.log_error("Failed to process query", input=user_input, error=str(e))
            return {
                "success": False,
                "error": str(e),
                "response": "I'm sorry, I encountered an error processing your request. Please try again."
            }
    
    def _select_tool(self, nlp_result: Dict[str, Any]) -> str:
        """
        Select the appropriate tool based on intent.
        
        Args:
            nlp_result: NLP processing result
            
        Returns:
            Tool name to use
        """
        intent = nlp_result["intent"]
        
        # Tool mapping based on intent
        tool_mapping = {
            "timesheet": "osi_one",
            "tasks": "azure_devops",
            "task_update": "azure_devops",
            "pull_requests": "azure_devops",
            "meetings": "teams",
            "summary": "aggregator"  # Special tool for cross-platform aggregation
        }
        
        selected_tool = tool_mapping.get(intent, "azure_devops")
        self.log_info("Tool selected", intent=intent, tool=selected_tool)
        
        return selected_tool
    
    def _initialize_tools(self):
        """Initialize available tools."""
        try:
            # Initialize Azure DevOps tool
            from tools.azure_devops import AzureDevOpsTool
            self.tools["azure_devops"] = AzureDevOpsTool(self.config)
            
            self.log_info("Tools initialized", tools=list(self.tools.keys()))
            
        except Exception as e:
            self.log_error("Failed to initialize tools", error=str(e))
    
    async def _execute_tool(self, tool_name: str, nlp_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the selected tool.
        
        Args:
            tool_name: Name of the tool to execute
            nlp_result: NLP processing result
            
        Returns:
            Tool execution result
        """
        try:
            intent = nlp_result["intent"]
            entities = nlp_result["entities"]
            
            if tool_name == "azure_devops":
                return await self._execute_azure_devops(intent, entities)
            
            elif tool_name == "teams":
                return {
                    "success": True,
                    "message": f"Mock Teams tool execution for intent: {intent}",
                    "data": {"meetings": []}
                }
            
            elif tool_name == "osi_one":
                return {
                    "success": True,
                    "message": f"Mock OSI One tool execution for intent: {intent}",
                    "data": {"timesheet_entries": []}
                }
            
            elif tool_name == "aggregator":
                return {
                    "success": True,
                    "message": f"Mock data aggregation for intent: {intent}",
                    "data": {"summary": "No data available yet"}
                }
            
            else:
                return {
                    "success": False,
                    "message": f"Tool {tool_name} not implemented yet",
                    "data": {}
                }
                
        except Exception as e:
            self.log_error("Tool execution failed", tool=tool_name, error=str(e))
            return {
                "success": False,
                "message": str(e),
                "data": {}
            }
    
    async def _execute_azure_devops(self, intent: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Azure DevOps tool based on intent."""
        try:
            ado_tool = self.tools.get("azure_devops")
            if not ado_tool:
                return {
                    "success": False,
                    "message": "Azure DevOps tool is not available."
                }
            
            # Check if Azure DevOps is configured, if not try to setup
            if not ado_tool.session:
                try:
                    await ado_tool.setup()
                except ValueError as e:
                    return {
                        "success": False,
                        "message": str(e)
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "message": f"Failed to configure Azure DevOps: {str(e)}"
                    }
            
            if intent == "tasks":
                # Extract filters from entities
                sprint = entities.get("sprint")
                status = entities.get("status")
                
                # Get tasks for current user with filters
                tasks = await ado_tool.get_my_tasks(sprint=sprint, status=status)
                response = await ado_tool.format_tasks_response(tasks)
                
                # Add context about the filters used
                filter_info = []
                if status:
                    filter_info.append(f"status: {status}")
                if sprint:
                    filter_info.append(f"sprint: {sprint}")
                
                if filter_info:
                    response = f"📋 Filtered by: {', '.join(filter_info)}\n\n{response}"
                
                return {
                    "success": True,
                    "message": response,
                    "data": {"tasks": [task.dict() for task in tasks]}
                }
            
            elif intent == "pull_requests":
                # Get pull requests for current user
                status = entities.get("status", "active")
                prs = await ado_tool.get_my_pull_requests(status)
                response = await ado_tool.format_pull_requests_response(prs)
                
                return {
                    "success": True,
                    "message": response,
                    "data": {"pull_requests": [pr.dict() for pr in prs]}
                }
            
            elif intent == "task_update":
                # Check for batch updates first
                batch_updates = entities.get("batch_updates")
                batch_update_error = entities.get("batch_update_error", False)
                
                if batch_update_error:
                    return {
                        "success": False,
                        "message": "❌ **Invalid Batch Update Format!**\n\n"
                                  "Some tasks in your batch update have invalid or missing task IDs.\n\n"
                                  "**Please ensure all tasks have valid ID numbers:**\n"
                                  "• TASK 51311 -> Start Date -> 08/08/2025\n"
                                  "• TASK 51312 -> Start Date -> 08/11/2025\n"
                                  "• TASK 51310 -> Start Date -> 08/11/2025\n\n"
                                  "Please correct the task IDs and try again."
                    }
                
                if batch_updates:
                    return await self._handle_batch_updates(ado_tool, batch_updates)
                
                # Extract update information from entities (single task update)
                task_id = entities.get("task_id")
                field_names = entities.get("field_names", [entities.get("field_name")])  # Get list of field names
                date_values = entities.get("date_values", [])
                status_values = entities.get("status_values", [])
                remaining_values = entities.get("remaining_values", [])
                completed_values = entities.get("completed_values", [])
                original_estimate_values = entities.get("original_estimate_values", [])
                assignee_values = entities.get("assignee_values", [])
                status = entities.get("status")
                
                # CRITICAL SAFETY CHECK: Prevent bulk updates without specific work item ID
                if not task_id:
                    return {
                        "success": False,
                        "message": "❌ **Please provide the missing Work Item ID!**\n\n"
                                  "I need a specific TASK, USER STORY, or REQUIREMENT number "
                                  "to update individual work items.\n\n"
                                  "**Examples:**\n"
                                  "• Update TASK-12345 Start Date -> 08/11/2025\n"
                                  "• Update USER STORY-67890 Status -> Active\n"
                                  "• Update REQUIREMENT-11111 Finish Date -> 08/12/2025\n\n"
                                  "Please provide the specific work item ID and try again."
                    }
                
                # Additional validation: Ensure task_id is a valid format
                if not isinstance(task_id, str) or not task_id.isdigit():
                    return {
                        "success": False,
                        "message": "❌ **Invalid Work Item ID Format**\n\n"
                                  "The work item ID must be a valid number.\n\n"
                                  "**Examples:**\n"
                                  "• TASK-12345 (ID: 12345)\n"
                                  "• USER STORY-67890 (ID: 67890)\n"
                                  "• REQUIREMENT-11111 (ID: 11111)\n\n"
                                  f"Received: {task_id}\n\n"
                                  "Please provide a valid work item ID and try again."
                    }
                
                # Prepare field updates
                field_updates = {}
                
                if field_names and date_values:
                    # Handle multiple field updates
                    for i, field_name in enumerate(field_names):
                        if i < len(date_values):
                            field_updates[field_name] = date_values[i]
                
                # Handle status updates
                if "status" in field_names and status_values:
                    field_updates["status"] = status_values[0]
                elif status:
                    field_updates["status"] = status
                
                # Handle remaining field updates
                if "remaining" in field_names and remaining_values:
                    field_updates["remaining"] = int(remaining_values[0])
                
                # Handle completed field updates
                if "completed" in field_names and completed_values:
                    field_updates["completed"] = int(completed_values[0])
                
                # Handle original estimate field updates
                if "original_estimate" in field_names and original_estimate_values:
                    field_updates["original_estimate"] = int(original_estimate_values[0])
                
                # Handle assignee field updates
                if "assigned_to" in field_names and assignee_values:
                    field_updates["assigned_to"] = assignee_values[0]
                
                if not field_updates:
                    return {
                        "success": False,
                        "message": f"Missing field updates for task {task_id}. Please specify what fields to update."
                    }
                
                try:
                    # Update the work item
                    result = await ado_tool.update_work_item(int(task_id), field_updates)
                    
                    # Format the response
                    update_summary = []
                    for field, value in field_updates.items():
                        update_summary.append(f"{field}: {value}")
                    
                    return {
                        "success": True,
                        "message": f"✅ Task {task_id} updated successfully!\n\nUpdated fields:\n" + "\n".join(f"• {summary}" for summary in update_summary),
                        "data": {"updated_task": result}
                    }
                    
                except Exception as e:
                    return {
                        "success": False,
                        "message": f"Failed to update task {task_id}: {str(e)}"
                    }
            
            else:
                return {
                    "success": False,
                    "message": f"I don't know how to handle '{intent}' with Azure DevOps."
                }
                
        except Exception as e:
            self.log_error("Azure DevOps execution failed", intent=intent, error=str(e))
            return {
                "success": False,
                "message": f"I encountered an error while accessing Azure DevOps: {str(e)}"
            }
    
    def _generate_response(self, nlp_result: Dict[str, Any], tool_result: Dict[str, Any]) -> str:
        """
        Generate a user-friendly response.
        
        Args:
            nlp_result: NLP processing result
            tool_result: Tool execution result
            
        Returns:
            User-friendly response message
        """
        if not tool_result["success"]:
            return f"I'm sorry, I couldn't complete your request. {tool_result['message']}"
        
        # Return the tool's formatted message
        return tool_result["message"]
    
    def _update_conversation_history(self, user_input: str, nlp_result: Dict[str, Any], response: str) -> None:
        """Update conversation history."""
        history_entry = {
            "user_input": user_input,
            "intent": nlp_result["intent"],
            "confidence": nlp_result["confidence"],
            "entities": nlp_result["entities"],
            "response": response,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        self.conversation_history.append(history_entry)
        
        # Keep only recent history (last 10 interactions)
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
    
    def get_tools(self) -> List[str]:
        """Get list of available tools."""
        return ["azure_devops", "osi_one", "teams", "aggregator"]
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history."""
        return self.conversation_history.copy()
    
    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history.clear()
        self.log_info("Conversation history cleared")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of the agent."""
        try:
            # Check NLP processor
            test_result = await self.nlp_processor.process_query("test")
            
            # Check token manager
            token_services = self.token_manager.list_tokens()
            
            # Check Azure DevOps tool
            ado_health = {"status": "not_configured"}
            if "azure_devops" in self.tools:
                ado_tool = self.tools["azure_devops"]
                ado_health = await ado_tool.health_check()
            
            return {
                "status": "healthy",
                "nlp_processor": "ok",
                "token_manager": "ok",
                "azure_devops": ado_health,
                "available_tokens": token_services,
                "tools": self.get_tools()
            }
            
        except Exception as e:
            self.log_error("Health check failed", error=str(e))
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def _handle_batch_updates(self, ado_tool, batch_updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle batch updates for multiple tasks."""
        try:
            # Validate all task IDs first
            invalid_tasks = []
            for update in batch_updates:
                task_id = update.get("task_id")
                if not task_id or not str(task_id).isdigit():
                    invalid_tasks.append(task_id)
            
            if invalid_tasks:
                return {
                    "success": False,
                    "message": "❌ **Invalid Task IDs Found!**\n\n"
                              "Some tasks are missing valid ID numbers:\n"
                              f"Invalid IDs: {invalid_tasks}\n\n"
                              "**Please ensure all tasks have valid ID numbers:**\n"
                              "• TASK 51311 -> Start Date -> 08/08/2025\n"
                              "• TASK 51312 -> Start Date -> 08/11/2025\n"
                              "• TASK 51310 -> Start Date -> 08/11/2025\n\n"
                              "Please correct the task IDs and try again."
                }
            
            # Process all updates
            results = []
            failed_updates = []
            
            for update in batch_updates:
                task_id = update["task_id"]
                field_updates = update["field_updates"]
                
                try:
                    result = await ado_tool.update_work_item(int(task_id), field_updates)
                    results.append({
                        "task_id": task_id,
                        "success": True,
                        "result": result
                    })
                except Exception as e:
                    failed_updates.append({
                        "task_id": task_id,
                        "error": str(e)
                    })
            
            # Format response
            if failed_updates:
                # Some updates failed
                success_count = len(results)
                failed_count = len(failed_updates)
                
                message = f"⚠️ **Batch Update Partially Completed**\n\n"
                message += f"✅ Successfully updated {success_count} tasks\n"
                message += f"❌ Failed to update {failed_count} tasks\n\n"
                
                if results:
                    message += "**Successfully Updated:**\n"
                    for result in results:
                        task_id = result["task_id"]
                        message += f"• TASK-{task_id}\n"
                
                if failed_updates:
                    message += "\n**Failed Updates:**\n"
                    for failed in failed_updates:
                        task_id = failed["task_id"]
                        error = failed["error"]
                        message += f"• TASK-{task_id}: {error}\n"
                
                return {
                    "success": False,
                    "message": message,
                    "data": {
                        "successful_updates": results,
                        "failed_updates": failed_updates
                    }
                }
            else:
                # All updates succeeded
                message = f"✅ **Batch Update Completed Successfully!**\n\n"
                message += f"Updated {len(results)} tasks:\n"
                
                for result in results:
                    task_id = result["task_id"]
                    message += f"• TASK-{task_id}\n"
                
                return {
                    "success": True,
                    "message": message,
                    "data": {
                        "successful_updates": results,
                        "failed_updates": []
                    }
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ **Batch Update Failed**\n\nError: {str(e)}"
            } 