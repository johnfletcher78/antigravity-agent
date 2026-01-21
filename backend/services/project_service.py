"""
Project Management Service
Handles storage and retrieval of project information
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import uuid

class ProjectService:
    def __init__(self, db_path: str = "db/projects.json"):
        self.db_path = db_path
        self.ensure_db_exists()
    
    def ensure_db_exists(self):
        """Create the database file if it doesn't exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        if not os.path.exists(self.db_path):
            self._save_data({"projects": []})
    
    def _load_data(self) -> dict:
        """Load data from the JSON database"""
        try:
            with open(self.db_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"projects": []}
    
    def _save_data(self, data: dict):
        """Save data to the JSON database"""
        with open(self.db_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def create_project(self, name: str, domain: str = "", description: str = "", 
                      industry: str = "", primary_objective: str = "", **kwargs) -> dict:
        """
        Create a new project
        
        Args:
            name: Project name
            domain: Primary domain/website
            description: Project description
            industry: Industry/sector
            primary_objective: Main goal/objective for this project
            **kwargs: Additional metadata
        
        Returns:
            Created project dict
        """
        data = self._load_data()
        
        project = {
            "id": str(uuid.uuid4()),
            "name": name,
            "domain": domain,
            "description": description,
            "industry": industry,
            "primary_objective": primary_objective,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "metadata": {
                "goals": kwargs.get("goals", []),
                "notes": kwargs.get("notes", []),
                "contacts": kwargs.get("contacts", []),
                **{k: v for k, v in kwargs.items() if k not in ["goals", "notes", "contacts"]}
            }
        }
        
        data["projects"].append(project)
        self._save_data(data)
        
        return project
    
    def get_project(self, project_id: str = None, name: str = None) -> Optional[dict]:
        """
        Get a project by ID or name
        
        Args:
            project_id: Project ID
            name: Project name (case-insensitive partial match)
        
        Returns:
            Project dict or None
        """
        data = self._load_data()
        
        for project in data["projects"]:
            if project_id and project["id"] == project_id:
                return project
            if name and name.lower() in project["name"].lower():
                return project
        
        return None
    
    def list_projects(self) -> List[dict]:
        """Get all projects"""
        data = self._load_data()
        return data["projects"]
    
    def update_project(self, project_id: str, **updates) -> Optional[dict]:
        """
        Update a project
        
        Args:
            project_id: Project ID
            **updates: Fields to update
        
        Returns:
            Updated project dict or None
        """
        data = self._load_data()
        
        for i, project in enumerate(data["projects"]):
            if project["id"] == project_id:
                # Update fields
                for key, value in updates.items():
                    if key in ["name", "domain", "description", "industry"]:
                        project[key] = value
                    elif key == "metadata":
                        project["metadata"].update(value)
                    else:
                        project["metadata"][key] = value
                
                project["updated_at"] = datetime.now().isoformat()
                data["projects"][i] = project
                self._save_data(data)
                return project
        
        return None
    
    def delete_project(self, project_id: str) -> bool:
        """
        Delete a project
        
        Args:
            project_id: Project ID
        
        Returns:
            True if deleted, False if not found
        """
        data = self._load_data()
        
        for i, project in enumerate(data["projects"]):
            if project["id"] == project_id:
                data["projects"].pop(i)
                self._save_data(data)
                return True
        
        return False
    
    def get_project_context(self, project_name: str = None) -> str:
        """
        Get formatted project context for LLM prompts
        
        Args:
            project_name: Optional project name to get specific project
        
        Returns:
            Formatted project context string
        """
        if project_name:
            project = self.get_project(name=project_name)
            if project:
                context = f"\n\n🎯 ACTIVE PROJECT: {project['name']}\n"
                if project['domain']:
                    context += f"Domain: {project['domain']}\n"
                if project['description']:
                    context += f"Description: {project['description']}\n"
                if project['industry']:
                    context += f"Industry: {project['industry']}\n"
                if project.get('primary_objective'):
                    context += f"\n🚀 PRIMARY OBJECTIVE: {project['primary_objective']}\n"
                    context += "→ Keep ALL recommendations aligned with this objective\n"
                return context
        
        # Return all projects summary
        projects = self.list_projects()
        if not projects:
            return ""
        
        context = "\n\nKnown Projects:\n"
        for project in projects[:5]:  # Limit to 5 most recent
            context += f"- {project['name']}"
            if project['domain']:
                context += f" ({project['domain']})"
            context += "\n"
        
        return context
