"""
Terminal UI

Rich terminal interface for the OSI ONE AGENT.
"""

import asyncio
from typing import Optional, List
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.layout import Layout
from rich.live import Live
from rich.align import Align
from rich.columns import Columns
from rich.rule import Rule
from rich.syntax import Syntax
from rich.markdown import Markdown
from utils.logger import LoggerMixin


class TerminalUI(LoggerMixin):
    """Rich terminal user interface for the OSI ONE AGENT."""
    
    def __init__(self, agent):
        """Initialize terminal UI."""
        super().__init__()
        self.agent = agent
        self.console = Console()
        self.running = False
        self.command_history: List[str] = []
        self.max_history = 100
        
        # OSI Branding colors
        self.primary_color = "bright_blue"
        self.secondary_color = "cyan"
        self.success_color = "green"
        self.warning_color = "yellow"
        self.error_color = "red"
        self.info_color = "white"
        
        self.log_info("Terminal UI initialized")
    
    async def run(self):
        """Run the terminal UI."""
        self.running = True
        
        # Display welcome message
        self._display_enhanced_welcome()
        
        # Main interaction loop
        while self.running:
            try:
                # Get user input
                user_input = await self._get_user_input()
                
                if not user_input.strip():
                    continue
                
                # Process the query
                result = await self._process_query(user_input)
                
                # Display result
                self._display_result(result)
                
            except KeyboardInterrupt:
                self._display_goodbye()
                break
            except Exception as e:
                self.log_error("UI error", error=str(e))
                self.console.print(f"[{self.error_color}]Error: {e}[/{self.error_color}]")
    
    def _display_enhanced_welcome(self):
        """Display enhanced welcome message with OSI branding."""
        # OSI Logo and branding
        osi_logo = Text()
        osi_logo.append("╔══════════════════════════════════════════════════════════════════════════════╗\n", style=f"bold {self.primary_color}")
        osi_logo.append("║                                                                              ║\n", style=f"bold {self.primary_color}")
        osi_logo.append("║                    🧠 OSI ONE AGENT 🧠                                      ║\n", style=f"bold {self.primary_color}")
        osi_logo.append("║                                                                              ║\n", style=f"bold {self.primary_color}")
        osi_logo.append("║              AI-Powered Desktop Assistant                                   ║\n", style=f"bold {self.primary_color}")
        osi_logo.append("║              for OSI Digital Engineers                                      ║\n", style=f"bold {self.primary_color}")
        osi_logo.append("║                                                                              ║\n", style=f"bold {self.primary_color}")
        osi_logo.append("╚══════════════════════════════════════════════════════════════════════════════╝", style=f"bold {self.primary_color}")
        
        # Welcome message
        welcome_text = Text()
        welcome_text.append("\n🎯 ", style=f"bold {self.success_color}")
        welcome_text.append("Welcome to your AI Assistant!", style=f"bold {self.info_color}")
        welcome_text.append("\n\n", style=self.info_color)
        welcome_text.append("💡 ", style=f"bold {self.secondary_color}")
        welcome_text.append("Try these example commands:", style=self.info_color)
        welcome_text.append("\n", style=self.info_color)
        
        # Example commands in a table
        examples = Table(show_header=False, box=None, padding=(0, 1))
        examples.add_column("Command", style=f"bold {self.success_color}")
        examples.add_column("Description", style=self.info_color)
        
        examples.add_row("📋 Show my tasks for this sprint", "Get current sprint tasks from Azure DevOps")
        examples.add_row("⏰ Fill my timesheet based on last week's PRs", "Automate timesheet entry from recent work")
        examples.add_row("📅 What meetings do I have today?", "Check today's calendar in Microsoft Teams")
        examples.add_row("🔍 Show my recent pull requests", "Display recent PRs from Azure DevOps")
        examples.add_row("📊 Get my work summary for this week", "Aggregate work data across platforms")
        
        # Status information
        status_text = Text()
        status_text.append("\n🔧 ", style=f"bold {self.warning_color}")
        status_text.append("Quick Commands:", style=f"bold {self.warning_color}")
        status_text.append("\n", style=self.info_color)
        status_text.append("   • ", style=self.info_color)
        status_text.append("help", style=f"bold {self.secondary_color}")
        status_text.append(" - Show all available commands", style=self.info_color)
        status_text.append("\n   • ", style=self.info_color)
        status_text.append("status", style=f"bold {self.secondary_color}")
        status_text.append(" - Check system status and connections", style=self.info_color)
        status_text.append("\n   • ", style=self.info_color)
        status_text.append("history", style=f"bold {self.secondary_color}")
        status_text.append(" - View conversation history", style=self.info_color)
        status_text.append("\n   • ", style=self.info_color)
        status_text.append("quit", style=f"bold {self.secondary_color}")
        status_text.append(" - Exit the application", style=self.info_color)
        
        # Multi-line input instructions
        multiline_text = Text()
        multiline_text.append("\n📝 ", style=f"bold {self.info_color}")
        multiline_text.append("Multi-line Input:", style=f"bold {self.info_color}")
        multiline_text.append("\n", style=self.info_color)
        multiline_text.append("   • ", style=self.info_color)
        multiline_text.append("Press Enter twice", style=f"bold {self.secondary_color}")
        multiline_text.append(" to submit multi-line commands", style=self.info_color)
        multiline_text.append("\n   • ", style=self.info_color)
        multiline_text.append("End with ';'", style=f"bold {self.secondary_color}")
        multiline_text.append(" or type 'done' to submit", style=self.info_color)
        multiline_text.append("\n   • ", style=self.info_color)
        multiline_text.append("Example:", style=f"bold {self.secondary_color}")
        multiline_text.append("\n", style=self.info_color)
        multiline_text.append("     Update TASK-123", style=self.info_color)
        multiline_text.append("\n", style=self.info_color)
        multiline_text.append("     Start Date -> 08/11/2025", style=self.info_color)
        multiline_text.append("\n", style=self.info_color)
        multiline_text.append("     Finish Date -> 08/12/2025", style=self.info_color)
        
        # Display everything
        self.console.print(Panel(osi_logo, border_style=self.primary_color, padding=(1, 2)))
        self.console.print(welcome_text)
        self.console.print(examples)
        self.console.print(status_text)
        self.console.print(multiline_text)
        self.console.print(Rule(style=self.primary_color))
        self.console.print()
    
    async def _get_user_input(self) -> str:
        """Get user input with multi-line support."""
        try:
            # Display prompt
            self.console.print(f"[{self.primary_color}]OSI Agent[/{self.primary_color}]", end=" ")
            
            # Collect multi-line input
            lines = []
            while True:
                try:
                    # Read a line
                    line = input()
                    
                    # If it's an empty line and we have content, end input
                    if not line.strip() and lines:
                        break
                    
                    # Add line to collection
                    lines.append(line)
                    
                    # If line ends with a semicolon or specific keywords, end input
                    if line.strip().endswith(';') or line.strip().lower() in ['done', 'end', 'submit']:
                        break
                        
                except EOFError:
                    break
                except KeyboardInterrupt:
                    raise
            
            # Join lines and clean up
            user_input = '\n'.join(lines).strip()
            
            # Add to history
            if user_input:
                self._add_to_history(user_input)
            
            return user_input
            
        except KeyboardInterrupt:
            raise
        except Exception as e:
            self.log_error("Failed to get user input", error=str(e))
            return ""
    
    def _add_to_history(self, command: str):
        """Add command to history."""
        if command not in self.command_history:
            self.command_history.append(command)
            
            # Keep only recent history
            if len(self.command_history) > self.max_history:
                self.command_history = self.command_history[-self.max_history:]
    
    async def _process_query(self, user_input: str) -> dict:
        """Process user query with progress indicator."""
        # Handle special commands
        if user_input.lower() in ['quit', 'exit', 'bye']:
            self.running = False
            return {"success": True, "response": "Goodbye!"}
        
        elif user_input.lower() == 'help':
            return self._get_help_response()
        
        elif user_input.lower() == 'status':
            return await self._get_status_response()
        
        elif user_input.lower() == 'history':
            return self._get_history_response()
        
        elif user_input.lower() == 'clear':
            self.console.clear()
            return {"success": True, "response": "Screen cleared."}
        
        # Process with agent
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True
        ) as progress:
            task = progress.add_task("Processing your request...", total=None)
            
            try:
                result = await self.agent.process_query(user_input)
                progress.update(task, completed=True)
                return result
                
            except Exception as e:
                self.log_error("Query processing failed", input=user_input, error=str(e))
                return {
                    "success": False,
                    "error": str(e),
                    "response": "I'm sorry, I encountered an error processing your request."
                }
    
    def _display_result(self, result: dict):
        """Display query result."""
        if result.get("success", False):
            # Success response with enhanced formatting
            response_text = Text()
            response_text.append("✅ ", style=f"bold {self.success_color}")
            response_text.append("Response Received", style=f"bold {self.success_color}")
            response_text.append("\n\n", style=self.info_color)
            response_text.append(result["response"], style=self.info_color)
            
            # Add tool information if available
            if "tool_used" in result:
                response_text.append("\n\n", style=self.info_color)
                response_text.append("🛠️ ", style=f"bold {self.warning_color}")
                response_text.append(f"Tool Used: {result['tool_used']}", style=f"bold {self.warning_color}")
            
            panel = Panel(
                response_text,
                title="🤖 AI Response",
                border_style=f"{self.success_color}",
                padding=(1, 2)
            )
            
            self.console.print(panel)
            
            # Display entities separately if available
            if "metadata" in result:
                metadata = result["metadata"]
                if "entities" in metadata and metadata["entities"]:
                    self.console.print()
                    self.console.print(f"🔍 [bold {self.secondary_color}]Detected Entities:[/bold {self.secondary_color}]")
                    
                    # Create a table for entities
                    entities_table = Table(show_header=False, box=None, padding=(0, 1))
                    entities_table.add_column("Entity", style=f"bold {self.success_color}")
                    entities_table.add_column("Value", style=self.info_color)
                    
                    for key, value in metadata["entities"].items():
                        entities_table.add_row(f"• {key}", str(value))
                    
                    self.console.print(entities_table)
            
        else:
            # Error response with enhanced formatting
            error_text = Text()
            error_text.append("❌ ", style=f"bold {self.error_color}")
            error_text.append("Error Occurred", style=f"bold {self.error_color}")
            error_text.append("\n\n", style=self.error_color)
            error_text.append(result.get("response", "An error occurred"), style=self.error_color)
            
            if "error" in result:
                error_text.append("\n\n", style=self.error_color)
                error_text.append("🔧 ", style=f"bold {self.warning_color}")
                error_text.append("Technical Details:", style=f"bold {self.warning_color}")
                error_text.append(f"\n{result['error']}", style=f"dim {self.error_color}")
            
            panel = Panel(
                error_text,
                title="⚠️ Error",
                border_style=f"{self.error_color}",
                padding=(1, 2)
            )
            
            self.console.print(panel)
        
        self.console.print()
    
    def _get_help_response(self) -> dict:
        """Get help response."""
        help_text = """
Available Commands:

[bold]Natural Language Queries:[/bold]
• "Show my tasks for this sprint"
• "Fill my timesheet based on last week's PRs"
• "What meetings do I have today?"
• "Show my recent pull requests"
• "Create a summary of my work"

[bold]System Commands:[/bold]
• help - Show this help message
• status - Show system status
• history - Show command history
• clear - Clear the screen
• quit/exit - Exit the application

[bold]Supported Intents:[/bold]
• timesheet - Timesheet management
• tasks - Task and work item queries
• meetings - Calendar and meeting queries
• pull_requests - Pull request queries
• summary - Activity summarization

Note: This is Milestone 1 - basic NLP and agent framework. 
Tool integrations will be available in later milestones.
"""
        
        return {
            "success": True,
            "response": help_text
        }
    
    async def _get_status_response(self) -> dict:
        """Get system status response."""
        try:
            health = await self.agent.health_check()
            
            if health["status"] == "healthy":
                status_text = f"""
System Status: [bold green]HEALTHY[/bold green]

Components:
• NLP Processor: [green]✓ OK[/green]
• Token Manager: [green]✓ OK[/green]
• Available Tools: {', '.join(health.get('tools', []))}
• Stored Tokens: {', '.join(health.get('available_tokens', []))}

Version: 1.0.0 (Milestone 1)
"""
            else:
                status_text = f"""
System Status: [bold red]UNHEALTHY[/bold red]

Error: {health.get('error', 'Unknown error')}
"""
            
            return {
                "success": True,
                "response": status_text
            }
            
        except Exception as e:
            return {
                "success": False,
                "response": f"Failed to get system status: {e}"
            }
    
    def _get_history_response(self) -> dict:
        """Get command history response."""
        if not self.command_history:
            return {
                "success": True,
                "response": "No command history available."
            }
        
        # Create history table
        table = Table(title="Command History")
        table.add_column("No.", style="cyan", no_wrap=True)
        table.add_column("Command", style="white")
        
        for i, command in enumerate(self.command_history[-10:], 1):
            table.add_row(str(i), command)
        
        # Convert table to string
        with self.console.capture() as capture:
            self.console.print(table)
        
        return {
            "success": True,
            "response": f"Recent commands:\n{capture.get()}"
        }
    
    def _display_goodbye(self):
        """Display goodbye message."""
        goodbye_text = Text()
        goodbye_text.append("👋 ", style=f"bold {self.primary_color}")
        goodbye_text.append("Thank you for using OSI ONE AGENT!", style=self.info_color)
        goodbye_text.append("\nGoodbye!", style=f"dim {self.primary_color}")
        
        panel = Panel(
            goodbye_text,
            title="Farewell",
            border_style=f"{self.primary_color}",
            padding=(1, 2)
        )
        
        self.console.print(panel)
    
    def display_error(self, message: str):
        """Display error message."""
        error_text = Text()
        error_text.append("❌ ", style=f"bold {self.error_color}")
        error_text.append(message, style=self.error_color)
        
        panel = Panel(
            error_text,
            title="Error",
            border_style=f"{self.error_color}",
            padding=(1, 2)
        )
        
        self.console.print(panel)
    
    def display_info(self, message: str):
        """Display info message."""
        info_text = Text()
        info_text.append("ℹ️ ", style=f"bold {self.primary_color}")
        info_text.append(message, style=self.info_color)
        
        panel = Panel(
            info_text,
            title="Info",
            border_style=f"{self.primary_color}",
            padding=(1, 2)
        )
        
        self.console.print(panel) 