"""Centralized state management for the YouTube Research Platform."""

from typing import Dict, Any, Callable, List
from datetime import datetime
import json
from pathlib import Path


class ObservableState:
    """Observable state container with change notifications."""

    def __init__(self):
        self._observers: List[Callable] = []
        self._state: Dict[str, Any] = self._get_default_state()

    def _get_default_state(self) -> Dict[str, Any]:
        """Get default application state."""
        return {
            # Step tracking
            "current_step": 0,  # 0=Define, 1=Refine, 2=Review, 3=Run, 4=Export
            "completed_steps": [],
            # Research configuration
            "template": None,
            "prompt_config": {},
            "filters": {"upload_date": None, "sort_by": "relevance", "max_results": 15},
            # API configuration
            "api_key": None,
            "use_ai_optimization": False,
            # Results
            "search_results": [],
            "transcripts": [],
            "selected_results": [],
            # Execution state
            "is_running": False,
            "progress": 0,
            "activity_log": [],
            # Learning & suggestions
            "learning_data": {},
            "suggestions": [],
            # Offline & cache
            "offline_cache": {},
            "cache_enabled": True,
        }

    def subscribe(self, observer: Callable):
        """Subscribe to state changes."""
        if observer not in self._observers:
            self._observers.append(observer)

    def unsubscribe(self, observer: Callable):
        """Unsubscribe from state changes."""
        if observer in self._observers:
            self._observers.remove(observer)

    def _notify(self, key: str, value: Any):
        """Notify all observers of state change."""
        for observer in self._observers:
            try:
                observer(key, value)
            except Exception as e:
                print(f"Observer notification error: {e}")

    def get(self, key: str, default=None) -> Any:
        """Get state value."""
        return self._state.get(key, default)

    def set(self, key: str, value: Any):
        """Set state value and notify observers."""
        old_value = self._state.get(key)
        self._state[key] = value

        if old_value != value:
            self._notify(key, value)

    def update(self, updates: Dict[str, Any]):
        """Batch update multiple state values."""
        for key, value in updates.items():
            self.set(key, value)

    def get_all(self) -> Dict[str, Any]:
        """Get complete state."""
        return self._state.copy()

    def reset(self):
        """Reset to default state."""
        self._state = self._get_default_state()
        self._notify("*", self._state)


class ConfigurationManager:
    """Manages configuration persistence."""

    def __init__(self, config_dir: str = None):
        self.config_dir = Path(config_dir or Path.home() / ".youtube_research_platform")
        self.config_dir.mkdir(exist_ok=True)
        self.config_file = self.config_dir / "config.json"

    def save_config(self, config: Dict[str, Any], name: str = "default"):
        """Save configuration to disk."""
        try:
            configs = self.load_all_configs()
            configs[name] = {"config": config, "saved_at": datetime.now().isoformat(), "name": name}

            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(configs, f, indent=2)

            return True
        except Exception as e:
            print(f"Config save error: {e}")
            return False

    def load_config(self, name: str = "default") -> Dict[str, Any]:
        """Load configuration from disk."""
        try:
            configs = self.load_all_configs()
            return configs.get(name, {}).get("config", {})
        except Exception as e:
            print(f"Config load error: {e}")
            return {}

    def load_all_configs(self) -> Dict[str, Any]:
        """Load all saved configurations."""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Configs load error: {e}")
            return {}

    def delete_config(self, name: str) -> bool:
        """Delete a saved configuration."""
        try:
            configs = self.load_all_configs()
            if name in configs:
                del configs[name]
                with open(self.config_file, "w", encoding="utf-8") as f:
                    json.dump(configs, f, indent=2)
                return True
            return False
        except Exception as e:
            print(f"Config delete error: {e}")
            return False


class ApplicationState:
    """Main application state manager."""

    def __init__(self):
        self.state = ObservableState()
        self.config_manager = ConfigurationManager()
        self._load_persistent_config()

    def _load_persistent_config(self):
        """Load persistent configuration on startup."""
        config = self.config_manager.load_config("last_session")
        if config:
            self.state.update(
                {
                    "api_key": config.get("api_key"),
                    "use_ai_optimization": config.get("use_ai_optimization", False),
                    "filters": config.get("filters", self.state.get("filters")),
                }
            )

    def save_session(self):
        """Save current session for persistence."""
        session_config = {
            "api_key": self.state.get("api_key"),
            "use_ai_optimization": self.state.get("use_ai_optimization"),
            "filters": self.state.get("filters"),
            "last_template": self.state.get("template"),
        }
        self.config_manager.save_config(session_config, "last_session")

    def export_current_config(self) -> Dict[str, Any]:
        """Export current configuration for sharing."""
        return {
            "template": self.state.get("template"),
            "prompt_config": self.state.get("prompt_config"),
            "filters": self.state.get("filters"),
            "use_ai_optimization": self.state.get("use_ai_optimization"),
        }

    def import_config(self, config: Dict[str, Any]):
        """Import configuration from external source."""
        self.state.update(
            {
                "template": config.get("template"),
                "prompt_config": config.get("prompt_config", {}),
                "filters": config.get("filters", {}),
                "use_ai_optimization": config.get("use_ai_optimization", False),
            }
        )

    def advance_step(self):
        """Advance to next wizard step."""
        current = self.state.get("current_step")
        if current < 4:  # Max step is 4 (Export)
            completed = self.state.get("completed_steps", [])
            if current not in completed:
                completed.append(current)
                self.state.set("completed_steps", completed)

            self.state.set("current_step", current + 1)

    def go_to_step(self, step: int):
        """Navigate to specific step."""
        if 0 <= step <= 4:
            self.state.set("current_step", step)

    def can_advance(self) -> bool:
        """Check if user can advance to next step."""
        current = self.state.get("current_step")

        # Step-specific validation
        if current == 0:  # Define
            return bool(self.state.get("prompt_config"))
        elif current == 1:  # Refine
            return True  # Always can advance from Refine
        elif current == 2:  # Review
            return True  # Always can advance from Review
        elif current == 3:  # Run
            return not self.state.get("is_running")

        return True
