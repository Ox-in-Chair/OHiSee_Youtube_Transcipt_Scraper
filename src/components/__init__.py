"""UI components for the YouTube Research Platform."""

# Phase 1: Foundation & Design System
from .wizard_rail import WizardRail
from .live_preview import LivePreview
from .onboarding import OnboardingWizard
from .template_card import TemplateCard, TemplateGrid

# Phase 2: Intelligence & Interaction
from .prompt_composer import PromptComposer
from .ai_transparency import AITransparencyPanel
from .query_transformation import QueryTransformationView
from .credentials_manager import CredentialsManager

# Phase 3: Results & Workflow
from .facets_bar import FacetsBar
from .results_slider import ResultsSlider
from .review_sheet import ReviewSheet
from .activity_log import ActivityLog
from .result_card import ResultCard, ResultCardGrid

# Phase 4: Polish & Accessibility
from .accessibility import (
    AccessibilityHelper,
    KeyboardNavigationManager,
    SkipNavigation,
    AccessibleButton,
    AccessibleEntry
)
from .empty_states import (
    EmptyState,
    NoResultsState,
    NoConfigState,
    NoTranscriptsState,
    NoAPIKeyState,
    LoadingState
)
from .error_states import (
    ErrorState,
    NetworkError,
    APIKeyError,
    SearchError,
    TranscriptError,
    QuotaExceededError,
    InlineErrorMessage
)
from .toast_notifications import Toast, ToastManager

# Phase 5: Advanced Features
from .offline_mode import OfflineCache, OfflineModePanel
from .data_portability import DataPortability, DataPortabilityPanel
from .learning_loop import LearningLoop, LearningInsightsPanel, FeedbackWidget
from .smart_suggestions import SmartSuggestions, SuggestionPanel
from .citation_generator import CitationGenerator, CitationPanel
from .export_formats import ExportFormats, ExportPanel

__all__ = [
    # Phase 1
    'WizardRail', 'LivePreview', 'OnboardingWizard', 'TemplateCard', 'TemplateGrid',
    # Phase 2
    'PromptComposer', 'AITransparencyPanel', 'QueryTransformationView', 'CredentialsManager',
    # Phase 3
    'FacetsBar', 'ResultsSlider', 'ReviewSheet', 'ActivityLog', 'ResultCard', 'ResultCardGrid',
    # Phase 4
    'AccessibilityHelper', 'KeyboardNavigationManager', 'SkipNavigation',
    'AccessibleButton', 'AccessibleEntry',
    'EmptyState', 'NoResultsState', 'NoConfigState', 'NoTranscriptsState',
    'NoAPIKeyState', 'LoadingState',
    'ErrorState', 'NetworkError', 'APIKeyError', 'SearchError',
    'TranscriptError', 'QuotaExceededError', 'InlineErrorMessage',
    'Toast', 'ToastManager',
    # Phase 5
    'OfflineCache', 'OfflineModePanel',
    'DataPortability', 'DataPortabilityPanel',
    'LearningLoop', 'LearningInsightsPanel', 'FeedbackWidget',
    'SmartSuggestions', 'SuggestionPanel',
    'CitationGenerator', 'CitationPanel',
    'ExportFormats', 'ExportPanel',
]
