"""
GitHub Forensics Evidence Schema

Evidence collection using Collectors that fetch data from trusted sources.

Usage:
    from src.collectors.api import GitHubAPICollector
    from src.collectors.archive import GHArchiveCollector
    from src.collectors.local import LocalGitCollector

    # Collectors for various sources
    github_collector = GitHubAPICollector()
    archive_collector = GHArchiveCollector()
    git_collector = LocalGitCollector()

    # Collect evidence
    commit = github_collector.collect_commit("aws", "aws-toolkit-vscode", "678851b...")
    events = archive_collector.collect_events(timestamp="202507132037", repo="aws/aws-toolkit-vscode")
    local_commit = git_collector.collect_commit("HEAD")

For loading previously serialized evidence from JSON:
    from src import load_evidence_from_json
    evidence = load_evidence_from_json(json_data)

Type hints (for static analysis and IDE autocomplete):
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        from src import CommitObservation, IssueObservation
"""

from typing import Annotated, Union

from pydantic import Field

from .store import EvidenceStore

# Enums - Safe to expose, these are just constants
from .schema.common import (
    EvidenceSource,
    EventType,
    RefType,
    PRAction,
    IssueAction,
    WorkflowConclusion,
    IOCType,
)

# Type aliases for external use
from .schema.common import AnyEvidence, AnyEvent, AnyObservation

# Import all schema classes for discriminated union and TYPE_CHECKING exports
from .schema.events import (
    # Events
    PushEvent,
    PullRequestEvent,
    IssueEvent,
    IssueCommentEvent,
    CreateEvent,
    DeleteEvent,
    ForkEvent,
    WorkflowRunEvent,
    ReleaseEvent,
    WatchEvent,
    MemberEvent,
    PublicEvent,
)

from .schema.observations import (
    # Observations
    CommitObservation,
    IssueObservation,
    FileObservation,
    ForkObservation,
    BranchObservation,
    TagObservation,
    ReleaseObservation,
    SnapshotObservation,
    IOC,
    ArticleObservation,
)

from .schema.common import (
    # Common models (for type hints)
    GitHubActor,
    GitHubRepository,
    VerificationInfo,
    VerificationResult,
)

# Pydantic discriminated union for efficient JSON deserialization
_EventUnion = Annotated[
    Union[
        PushEvent,
        PullRequestEvent,
        IssueEvent,
        IssueCommentEvent,
        CreateEvent,
        DeleteEvent,
        ForkEvent,
        WorkflowRunEvent,
        ReleaseEvent,
        WatchEvent,
        MemberEvent,
        PublicEvent,
    ],
    Field(discriminator="event_type"),
]

_ObservationUnion = Annotated[
    Union[
        CommitObservation,
        IssueObservation,
        FileObservation,
        ForkObservation,
        BranchObservation,
        TagObservation,
        ReleaseObservation,
        SnapshotObservation,
        IOC,
        ArticleObservation,
    ],
    Field(discriminator="observation_type"),
]

from pydantic import TypeAdapter

_event_adapter = TypeAdapter(_EventUnion)
_observation_adapter = TypeAdapter(_ObservationUnion)


def load_evidence_from_json(data: dict) -> AnyEvidence:
    """
    Load a previously serialized evidence object from JSON.

    Args:
        data: Dictionary from JSON deserialization (e.g., json.load())

    Returns:
        The appropriate Event or Observation instance

    Raises:
        ValueError: If the data cannot be parsed into a known evidence type
    """
    if "event_type" in data:
        try:
            return _event_adapter.validate_python(data)
        except Exception as e:
            raise ValueError(f"Unknown event_type: {data.get('event_type')}") from e

    if "observation_type" in data:
        try:
            return _observation_adapter.validate_python(data)
        except Exception as e:
            raise ValueError(f"Unknown observation_type: {data.get('observation_type')}") from e

    raise ValueError("Data must contain 'event_type' or 'observation_type' field")


__all__ = [
    # Store - Persist and query evidence collections
    "EvidenceStore",
    # Enums
    "EvidenceSource",
    "EventType",
    "RefType",
    "PRAction",
    "IssueAction",
    "WorkflowConclusion",
    "IOCType",
    # Loading from JSON
    "load_evidence_from_json",
    # Type aliases
    "AnyEvidence",
    "AnyEvent",
    "AnyObservation",
    # Type hints (for static analysis)
    "GitHubActor",
    "GitHubRepository",
    "VerificationInfo",
    "VerificationResult",
    "Event",
    "Observation",
    "CommitAuthor",
    "FileChange",
    "CommitInPush",
    "WaybackSnapshot",
    "PushEvent",
    "PullRequestEvent",
    "IssueEvent",
    "IssueCommentEvent",
    "CreateEvent",
    "DeleteEvent",
    "ForkEvent",
    "WorkflowRunEvent",
    "ReleaseEvent",
    "WatchEvent",
    "MemberEvent",
    "PublicEvent",
    "CommitObservation",
    "IssueObservation",
    "FileObservation",
    "ForkObservation",
    "BranchObservation",
    "TagObservation",
    "ReleaseObservation",
    "SnapshotObservation",
    "IOC",
    "ArticleObservation",
]

# Import base classes and helper models from their respective modules
from .schema.events import Event, CommitInPush
from .schema.observations import Observation, CommitAuthor, FileChange, WaybackSnapshot
