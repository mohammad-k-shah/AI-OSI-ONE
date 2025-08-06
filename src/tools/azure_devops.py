"""
Azure DevOps Tool

Handles Azure DevOps API integration for tasks, work items, and pull requests.
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
from utils.logger import LoggerMixin


class WorkItem(BaseModel):
    """Represents an Azure DevOps work item."""
    id: int
    title: str
    type: str
    state: str
    assigned_to: Optional[str]
    created_date: datetime
    changed_date: datetime
    area_path: str
    iteration_path: str
    priority: Optional[int]
    effort: Optional[float]
    description: Optional[str]


class PullRequest(BaseModel):
    """Represents an Azure DevOps pull request."""
    id: int
    title: str
    description: Optional[str]
    status: str
    created_by: str
    created_date: datetime
    closed_date: Optional[datetime]
    source_branch: str
    target_branch: str
    repository: str
    reviewers: List[str]
    is_draft: bool


class AzureDevOpsTool(LoggerMixin):
    """Azure DevOps API integration tool."""
    
    def __init__(self, config):
        """Initialize Azure DevOps tool."""
        super().__init__()
        self.config = config
        self.ado_config = config.get_tool_config("azure_devops")
        self.base_url = None
        self.organization = None
        self.project = None
        self.pat_token = None
        self.session = None
        
        self.log_info("Azure DevOps tool initialized")
    
    async def setup(self, pat_token: str = None, organization: str = None, project: str = None):
        """Setup Azure DevOps connection."""
        # Get configuration from config manager
        if not pat_token:
            pat_token = self.config.get_azure_devops_token()
        if not organization:
            organization = self.config.get_azure_devops_organization()
        if not project:
            project = self.config.get_azure_devops_project()
        
        # Validate required configuration
        missing_configs = []
        if not pat_token:
            missing_configs.append("AZURE_DEVOPS_TOKEN")
        if not organization:
            missing_configs.append("AZURE_DEVOPS_ORGANIZATION")
        if not project:
            missing_configs.append("AZURE_DEVOPS_PROJECT")
        
        if missing_configs:
            error_msg = (
                f"🔧 **Azure DevOps Configuration Required**\n\n"
                f"I need the following configuration to connect to Azure DevOps:\n\n"
                f"**Missing Environment Variables:**\n"
                f"{chr(10).join(f'• {config}' for config in missing_configs)}\n\n"
                f"**Setup Instructions:**\n"
                f"1. Set these environment variables in your system:\n"
                f"   - `AZURE_DEVOPS_TOKEN`: Your Personal Access Token\n"
                f"   - `AZURE_DEVOPS_ORGANIZATION`: Your Azure DevOps organization name\n"
                f"   - `AZURE_DEVOPS_PROJECT`: Your Azure DevOps project name\n\n"
                f"2. Or add them to your config file: `config/app/app.yaml`\n\n"
                f"**Example:**\n"
                f"```bash\n"
                f"# Set environment variables\n"
                f"export AZURE_DEVOPS_TOKEN=your_pat_token_here\n"
                f"export AZURE_DEVOPS_ORGANIZATION=your_organization\n"
                f"export AZURE_DEVOPS_PROJECT=your_project\n"
                f"```\n\n"
                f"Once configured, I'll be able to fetch your tasks and pull requests!"
            )
            raise ValueError(error_msg)
        
        self.pat_token = pat_token
        self.organization = organization
        self.project = project
        self.base_url = f"https://dev.azure.com/{organization}/{project}"
        
        # Create aiohttp session with authentication
        auth = aiohttp.BasicAuth("", pat_token)
        self.session = aiohttp.ClientSession(auth=auth)
        
        self.log_info("Azure DevOps connection established", 
                     organization=organization, project=project)
    
    async def get_my_tasks(self, sprint: Optional[str] = None, status: Optional[str] = None) -> List[WorkItem]:
        """Get tasks assigned to the current user with optional filtering."""
        try:
            # Build WIQL query for assigned work items
            status_filter = ""
            if status:
                # Map common status terms to Azure DevOps states
                status_mapping = {
                    "active": "('Active', 'In Progress')",
                    "new": "('New', 'Assigned')",
                    "resolved": "('Resolved', 'Completed')",
                    "closed": "('Closed', 'Done')",
                    "blocked": "('Blocked', 'On Hold')"
                }
                
                if status in status_mapping:
                    status_filter = f"AND [System.State] IN {status_mapping[status]}"
                else:
                    # If specific status provided, use it directly
                    status_filter = f"AND [System.State] = '{status}'"
            else:
                # Default filter: exclude closed and removed
                status_filter = "AND [System.State] NOT IN ('Closed', 'Removed')"
            
            sprint_filter = f"AND [System.IterationPath] = '{sprint}'" if sprint else ""
            
            wiql_query = {
                "query": f"""
                SELECT [System.Id], [System.Title], [System.State], [System.AssignedTo], 
                       [System.CreatedDate], [System.ChangedDate], [System.AreaPath], 
                       [System.IterationPath], [Microsoft.VSTS.Common.Priority], 
                       [Microsoft.VSTS.Scheduling.Effort], [System.Description]
                FROM WorkItems 
                WHERE [System.AssignedTo] = @me 
                {status_filter}
                {sprint_filter}
                ORDER BY [System.ChangedDate] DESC
                """
            }
            
            # Execute WIQL query
            async with self.session.post(
                f"{self.base_url}/_apis/wit/wiql?api-version=6.0",
                json=wiql_query
            ) as response:
                if response.status != 200:
                    raise Exception(f"WIQL query failed: {response.status}")
                
                data = await response.json()
                work_item_ids = [item["id"] for item in data.get("workItems", [])]
            
            # Get detailed work item information
            work_items = []
            for batch in self._chunk_list(work_item_ids, 200):  # Azure DevOps batch limit
                batch_items = await self._get_work_items_batch(batch)
                work_items.extend(batch_items)
            
            self.log_info("Retrieved user tasks", count=len(work_items), status=status, sprint=sprint)
            return work_items
            
        except Exception as e:
            self.log_error("Failed to get user tasks", error=str(e))
            raise
    
    async def get_my_pull_requests(self, status: str = "active") -> List[PullRequest]:
        """Get pull requests created by the current user."""
        try:
            # Build query parameters
            params = {
                "api-version": "6.0",
                "searchCriteria.creatorId": "@me",
                "searchCriteria.status": status,
                "$top": 50
            }
            
            async with self.session.get(
                f"{self.base_url}/_apis/git/pullrequests",
                params=params
            ) as response:
                if response.status != 200:
                    raise Exception(f"Pull request query failed: {response.status}")
                
                data = await response.json()
                pull_requests = []
                
                for pr_data in data.get("value", []):
                    pr = PullRequest(
                        id=pr_data["pullRequestId"],
                        title=pr_data["title"],
                        description=pr_data.get("description"),
                        status=pr_data["status"],
                        created_by=pr_data["createdBy"]["displayName"],
                        created_date=datetime.fromisoformat(pr_data["creationDate"].replace("Z", "+00:00")),
                        closed_date=datetime.fromisoformat(pr_data["closedDate"].replace("Z", "+00:00")) if pr_data.get("closedDate") else None,
                        source_branch=pr_data["sourceRefName"],
                        target_branch=pr_data["targetRefName"],
                        repository=pr_data["repository"]["name"],
                        reviewers=[r["displayName"] for r in pr_data.get("reviewers", [])],
                        is_draft=pr_data.get("isDraft", False)
                    )
                    pull_requests.append(pr)
                
                self.log_info("Retrieved user pull requests", count=len(pull_requests))
                return pull_requests
                
        except Exception as e:
            self.log_error("Failed to get pull requests", error=str(e))
            raise
    
    async def get_sprint_work_items(self, sprint: str) -> List[WorkItem]:
        """Get all work items in a specific sprint."""
        try:
            wiql_query = {
                "query": f"""
                SELECT [System.Id], [System.Title], [System.State], [System.AssignedTo], 
                       [System.CreatedDate], [System.ChangedDate], [System.AreaPath], 
                       [System.IterationPath], [Microsoft.VSTS.Common.Priority], 
                       [Microsoft.VSTS.Scheduling.Effort], [System.Description]
                FROM WorkItems 
                WHERE [System.IterationPath] = '{sprint}'
                AND [System.State] NOT IN ('Removed')
                ORDER BY [System.ChangedDate] DESC
                """
            }
            
            async with self.session.post(
                f"{self.base_url}/_apis/wit/wiql?api-version=6.0",
                json=wiql_query
            ) as response:
                if response.status != 200:
                    raise Exception(f"WIQL query failed: {response.status}")
                
                data = await response.json()
                work_item_ids = [item["id"] for item in data.get("workItems", [])]
            
            # Get detailed work item information
            work_items = []
            for batch in self._chunk_list(work_item_ids, 200):
                batch_items = await self._get_work_items_batch(batch)
                work_items.extend(batch_items)
            
            self.log_info("Retrieved sprint work items", sprint=sprint, count=len(work_items))
            return work_items
            
        except Exception as e:
            self.log_error("Failed to get sprint work items", sprint=sprint, error=str(e))
            raise
    
    async def _get_work_items_batch(self, work_item_ids: List[int]) -> List[WorkItem]:
        """Get detailed work item information for a batch of IDs."""
        try:
            ids_param = ",".join(map(str, work_item_ids))
            params = {
                "api-version": "6.0",
                "ids": ids_param,
                "$expand": "all"
            }
            
            async with self.session.get(
                f"{self.base_url}/_apis/wit/workitems",
                params=params
            ) as response:
                if response.status != 200:
                    raise Exception(f"Work items query failed: {response.status}")
                
                data = await response.json()
                work_items = []
                
                for item_data in data.get("value", []):
                    fields = item_data["fields"]
                    work_item = WorkItem(
                        id=item_data["id"],
                        title=fields.get("System.Title", ""),
                        type=fields.get("System.WorkItemType", ""),
                        state=fields.get("System.State", ""),
                        assigned_to=fields.get("System.AssignedTo", {}).get("displayName") if fields.get("System.AssignedTo") else None,
                        created_date=datetime.fromisoformat(fields["System.CreatedDate"].replace("Z", "+00:00")),
                        changed_date=datetime.fromisoformat(fields["System.ChangedDate"].replace("Z", "+00:00")),
                        area_path=fields.get("System.AreaPath", ""),
                        iteration_path=fields.get("System.IterationPath", ""),
                        priority=fields.get("Microsoft.VSTS.Common.Priority"),
                        effort=fields.get("Microsoft.VSTS.Scheduling.Effort"),
                        description=fields.get("System.Description")
                    )
                    work_items.append(work_item)
                
                return work_items
                
        except Exception as e:
            self.log_error("Failed to get work items batch", error=str(e))
            raise
    
    def _chunk_list(self, lst: List, chunk_size: int) -> List[List]:
        """Split a list into chunks of specified size."""
        return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]
    
    async def format_tasks_response(self, tasks: List[WorkItem]) -> str:
        """Format tasks for user display."""
        if not tasks:
            return "No tasks found."
        
        response_lines = [f"I found {len(tasks)} tasks assigned to you:"]
        
        for i, task in enumerate(tasks, 1):
            priority_emoji = "🔴" if task.priority and task.priority <= 1 else "🟡" if task.priority and task.priority <= 2 else "🟢"
            state_emoji = "✅" if task.state == "Done" else "🔄" if task.state == "In Progress" else "📋"
            
            response_lines.append(f"\n{i}. {priority_emoji} [{task.type.upper()}-{task.id}] {task.title}")
            response_lines.append(f"   {state_emoji} Status: {task.state}")
            response_lines.append(f"   📍 Area: {task.area_path}")
            response_lines.append(f"   🏃 Sprint: {task.iteration_path}")
            
            if task.effort:
                response_lines.append(f"   ⏱️ Effort: {task.effort} hours")
        
        return "\n".join(response_lines)
    
    async def format_pull_requests_response(self, prs: List[PullRequest]) -> str:
        """Format pull requests for user display."""
        if not prs:
            return "No pull requests found."
        
        response_lines = [f"Your recent pull requests:"]
        
        for i, pr in enumerate(prs, 1):
            status_emoji = "✅" if pr.status == "completed" else "🔄" if pr.status == "active" else "📝"
            draft_emoji = "📝" if pr.is_draft else ""
            
            response_lines.append(f"\n{i}. {status_emoji} PR-{pr.id}: {pr.title} {draft_emoji}")
            response_lines.append(f"   📂 Repository: {pr.repository}")
            response_lines.append(f"   🌿 {pr.source_branch} → {pr.target_branch}")
            response_lines.append(f"   👤 Created by: {pr.created_by}")
            response_lines.append(f"   📅 Created: {pr.created_date.strftime('%Y-%m-%d %H:%M')}")
            
            if pr.reviewers:
                response_lines.append(f"   👥 Reviewers: {', '.join(pr.reviewers)}")
        
        return "\n".join(response_lines)
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Azure DevOps connection health."""
        try:
            if not self.session:
                return {"status": "not_configured", "error": "No session established"}
            
            # Test connection with a simple API call
            async with self.session.get(
                f"{self.base_url}/_apis/project?api-version=6.0"
            ) as response:
                if response.status == 200:
                    return {"status": "healthy", "organization": self.organization, "project": self.project}
                else:
                    return {"status": "unhealthy", "error": f"API returned status {response.status}"}
                    
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def close(self):
        """Close the Azure DevOps session."""
        if self.session:
            await self.session.close()
            self.log_info("Azure DevOps session closed") 

    async def update_work_item(self, work_item_id: int, field_updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update work item fields."""
        try:
            # First, get the work item details to determine its type for state validation
            work_item_type = None
            if "status" in field_updates:
                try:
                    async with self.session.get(
                        f"{self.base_url}/_apis/wit/workitems/{work_item_id}?api-version=6.0"
                    ) as response:
                        if response.status == 200:
                            work_item_data = await response.json()
                            work_item_type = work_item_data.get("fields", {}).get("System.WorkItemType", "").upper()
                            self.log_info("Retrieved work item type", work_item_id=work_item_id, type=work_item_type)
                        else:
                            self.log_warning("Could not retrieve work item type, using default validation", work_item_id=work_item_id)
                except Exception as e:
                    self.log_warning("Error retrieving work item type, using default validation", work_item_id=work_item_id, error=str(e))
            
            # Prepare the update operations
            operations = []
            for field_name, new_value in field_updates.items():
                # Map field names to Azure DevOps field paths
                field_mapping = {
                    "start_date": "Microsoft.VSTS.Scheduling.StartDate",
                    "finish_date": "Microsoft.VSTS.Scheduling.FinishDate",
                    "status": "System.State",
                    "priority": "Microsoft.VSTS.Common.Priority",
                    "title": "System.Title",
                    "description": "System.Description",
                    "assigned_to": "System.AssignedTo",
                    "remaining": "Microsoft.VSTS.Scheduling.RemainingWork",
                    "completed": "Microsoft.VSTS.Scheduling.CompletedWork",
                    "original_estimate": "Microsoft.VSTS.Scheduling.OriginalEstimate"
                }
                
                azure_field = field_mapping.get(field_name, field_name)
                
                # Map status values to Azure DevOps states based on work item type
                if field_name == "status":
                    # Define valid states based on work item type
                    valid_states_by_type = {
                        "TASK": ["New", "Active", "Closed", "Removed"],
                        "USER STORY": ["New", "Approved", "Active", "Resolved", "Closed", "Removed"]
                    }
                    
                    # Default mapping for common terms
                    status_mapping = {
                        "active": "Active",
                        "new": "New",
                        "approved": "Approved",
                        "resolved": "Resolved",
                        "closed": "Closed",
                        "removed": "Removed",
                        "blocked": "Active"  # Default fallback
                    }
                    
                    # Apply type-specific validation
                    if work_item_type and work_item_type in valid_states_by_type:
                        valid_states = valid_states_by_type[work_item_type]
                        mapped_value = status_mapping.get(new_value.lower(), new_value)
                        
                        # Check if the mapped value is valid for this work item type
                        if mapped_value not in valid_states:
                            # Find the best fallback based on the work item type
                            if work_item_type == "TASK":
                                # For TASK, prefer Active as fallback
                                fallback_mapping = {
                                    "resolved": "Active",
                                    "approved": "Active",
                                    "closed": "Active",
                                    "removed": "Active"
                                }
                                mapped_value = fallback_mapping.get(mapped_value.lower(), "Active")
                            elif work_item_type == "USER STORY":
                                # For USER STORY, prefer Active as fallback
                                fallback_mapping = {
                                    "removed": "Active"
                                }
                                mapped_value = fallback_mapping.get(mapped_value.lower(), "Active")
                        
                        new_value = mapped_value
                        self.log_info("Applied type-specific state mapping", 
                                    work_item_id=work_item_id, 
                                    work_item_type=work_item_type,
                                    original_value=new_value,
                                    mapped_value=mapped_value,
                                    valid_states=valid_states)
                    else:
                        # Fallback to simple mapping if work item type is unknown
                        new_value = status_mapping.get(new_value.lower(), new_value)
                        self.log_info("Applied default state mapping", 
                                    work_item_id=work_item_id,
                                    original_value=new_value)
                
                # Format date values
                if field_name in ["start_date", "finish_date"] and new_value:
                    # Convert MM/DD/YYYY to YYYY-MM-DD format
                    if "/" in str(new_value):
                        from datetime import datetime
                        try:
                            date_obj = datetime.strptime(new_value, "%m/%d/%Y")
                            new_value = date_obj.strftime("%Y-%m-%d")
                        except ValueError:
                            pass
                
                operations.append({
                    "op": "add",
                    "path": f"/fields/{azure_field}",
                    "value": new_value
                })
            
            # Execute the update
            async with self.session.patch(
                f"{self.base_url}/_apis/wit/workitems/{work_item_id}?api-version=6.0",
                json=operations,
                headers={"Content-Type": "application/json-patch+json"}
            ) as response:
                if response.status not in [200, 201]:
                    error_text = await response.text()
                    raise Exception(f"Work item update failed: {response.status} - {error_text}")
                
                result = await response.json()
                self.log_info("Work item updated successfully", work_item_id=work_item_id, fields=list(field_updates.keys()))
                return result
                
        except Exception as e:
            self.log_error("Failed to update work item", work_item_id=work_item_id, error=str(e))
            raise 