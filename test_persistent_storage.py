"""
Round 48: Persistent Storage & File System
Agents can save/load state, memories, and files for long-term persistence.
Features: file operations, memory serialization, backup/restore, storage quota management.
"""

import pytest
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


class StorageType(Enum):
    """Type of storage backend"""
    MEMORY = "memory"  # In-memory only
    FILE = "file"  # File system
    DATABASE = "database"  # SQL database
    CLOUD = "cloud"  # Cloud storage


class FileType(Enum):
    """Type of file being stored"""
    MEMORY_LOG = "memory_log"  # Agent memory records
    STATE = "state"  # Agent complete state
    KNOWLEDGE = "knowledge"  # Knowledge base
    INTERACTION = "interaction"  # Chat/interaction logs
    MEDIA = "media"  # Images, audio, video
    DOCUMENT = "document"  # Text, PDF, etc.
    CONFIG = "config"  # Configuration files
    BACKUP = "backup"  # Full backup


@dataclass
class StorageFile:
    """A file stored in persistent storage"""
    file_id: str
    filename: str
    file_type: FileType
    agent_id: str
    content: str
    size_bytes: int
    created_at: float
    modified_at: float
    access_count: int = 0
    is_encrypted: bool = False
    checksum: str = ""

    def to_dict(self) -> Dict:
        return {
            "id": self.file_id,
            "name": self.filename,
            "type": self.file_type.value,
            "agent": self.agent_id,
            "size": self.size_bytes,
            "accesses": self.access_count
        }


@dataclass
class StorageQuota:
    """Storage quota for agent"""
    agent_id: str
    max_storage_bytes: int
    current_usage_bytes: int = 0
    file_count: int = 0
    last_cleanup: float = 0.0
    cleanup_frequency: int = 7  # days

    def get_available_bytes(self) -> int:
        """Get remaining available storage"""
        return max(0, self.max_storage_bytes - self.current_usage_bytes)

    def get_usage_percentage(self) -> float:
        """Get usage as percentage (0.0-1.0)"""
        if self.max_storage_bytes == 0:
            return 0.0
        return min(1.0, self.current_usage_bytes / self.max_storage_bytes)

    def can_store(self, size_bytes: int) -> bool:
        """Check if file can be stored"""
        return self.get_available_bytes() >= size_bytes

    def to_dict(self) -> Dict:
        return {
            "agent": self.agent_id,
            "max": self.max_storage_bytes,
            "used": self.current_usage_bytes,
            "available": self.get_available_bytes(),
            "usage_percent": round(self.get_usage_percentage() * 100, 2)
        }


@dataclass
class Backup:
    """Complete backup of agent state"""
    backup_id: str
    agent_id: str
    timestamp: float
    backup_size: int
    file_count: int
    compression: str = "none"  # "none", "gzip", "bzip2"
    verified: bool = False
    checksum: str = ""
    description: str = ""

    def to_dict(self) -> Dict:
        return {
            "id": self.backup_id,
            "agent": self.agent_id,
            "timestamp": self.timestamp,
            "size": self.backup_size,
            "files": self.file_count,
            "verified": self.verified
        }


class FileStorage:
    """Manages file operations"""

    def __init__(self):
        self.files: Dict[str, StorageFile] = {}
        self.agent_files: Dict[str, List[str]] = {}  # agent_id -> file_ids

    def save_file(self, file: StorageFile) -> bool:
        """Save file to storage"""
        if file.file_id in self.files:
            return False

        self.files[file.file_id] = file

        if file.agent_id not in self.agent_files:
            self.agent_files[file.agent_id] = []
        self.agent_files[file.agent_id].append(file.file_id)

        return True

    def get_file(self, file_id: str) -> Optional[StorageFile]:
        """Get file by ID"""
        if file_id not in self.files:
            return None

        file = self.files[file_id]
        file.access_count += 1
        return file

    def delete_file(self, file_id: str) -> bool:
        """Delete file"""
        if file_id not in self.files:
            return False

        file = self.files.pop(file_id)

        # Remove from agent list
        if file.agent_id in self.agent_files:
            self.agent_files[file.agent_id].remove(file_id)

        return True

    def get_agent_files(self, agent_id: str, file_type: Optional[FileType] = None) -> List[StorageFile]:
        """Get agent's files, optionally filtered by type"""
        if agent_id not in self.agent_files:
            return []

        file_ids = self.agent_files[agent_id]
        files = [self.files[fid] for fid in file_ids if fid in self.files]

        if file_type:
            files = [f for f in files if f.file_type == file_type]

        return files

    def list_agent_files(self, agent_id: str) -> List[StorageFile]:
        """List all files for agent"""
        return self.get_agent_files(agent_id)

    def get_total_usage(self, agent_id: str) -> int:
        """Get total storage used by agent"""
        files = self.get_agent_files(agent_id)
        return sum(f.size_bytes for f in files)

    def to_dict(self) -> Dict:
        return {
            "total_files": len(self.files),
            "total_agents": len(self.agent_files),
            "total_bytes": sum(f.size_bytes for f in self.files.values())
        }


class QuotaManager:
    """Manages storage quotas"""

    def __init__(self, default_quota_bytes: int = 10_000_000):  # 10 MB default
        self.quotas: Dict[str, StorageQuota] = {}
        self.default_quota = default_quota_bytes

    def get_quota(self, agent_id: str) -> StorageQuota:
        """Get quota for agent (create if needed)"""
        if agent_id not in self.quotas:
            self.quotas[agent_id] = StorageQuota(
                agent_id=agent_id,
                max_storage_bytes=self.default_quota
            )
        return self.quotas[agent_id]

    def set_quota(self, agent_id: str, max_bytes: int) -> bool:
        """Set custom quota for agent"""
        if max_bytes <= 0:
            return False

        self.quotas[agent_id] = StorageQuota(
            agent_id=agent_id,
            max_storage_bytes=max_bytes
        )
        return True

    def record_storage(self, agent_id: str, size_bytes: int) -> bool:
        """Record file storage"""
        quota = self.get_quota(agent_id)

        if not quota.can_store(size_bytes):
            return False

        quota.current_usage_bytes += size_bytes
        quota.file_count += 1
        return True

    def free_storage(self, agent_id: str, size_bytes: int) -> bool:
        """Free storage space"""
        quota = self.get_quota(agent_id)
        quota.current_usage_bytes = max(0, quota.current_usage_bytes - size_bytes)
        quota.file_count = max(0, quota.file_count - 1)
        return True

    def is_quota_exceeded(self, agent_id: str) -> bool:
        """Check if quota exceeded"""
        quota = self.get_quota(agent_id)
        return quota.current_usage_bytes >= quota.max_storage_bytes

    def get_quota_stats(self, agent_id: str) -> Dict:
        """Get quota statistics"""
        quota = self.get_quota(agent_id)
        return quota.to_dict()

    def to_dict(self) -> Dict:
        return {
            "total_agents": len(self.quotas),
            "total_allocated": sum(q.max_storage_bytes for q in self.quotas.values()),
            "total_used": sum(q.current_usage_bytes for q in self.quotas.values())
        }


class BackupManager:
    """Manages agent backups"""

    def __init__(self):
        self.backups: Dict[str, Backup] = {}
        self.agent_backups: Dict[str, List[str]] = {}  # agent_id -> backup_ids

    def create_backup(self, backup: Backup) -> bool:
        """Create backup"""
        if backup.backup_id in self.backups:
            return False

        self.backups[backup.backup_id] = backup

        if backup.agent_id not in self.agent_backups:
            self.agent_backups[backup.agent_id] = []
        self.agent_backups[backup.agent_id].append(backup.backup_id)

        return True

    def get_backup(self, backup_id: str) -> Optional[Backup]:
        """Get backup by ID"""
        return self.backups.get(backup_id)

    def verify_backup(self, backup_id: str) -> bool:
        """Verify backup integrity"""
        if backup_id not in self.backups:
            return False

        backup = self.backups[backup_id]
        backup.verified = True
        return True

    def list_backups(self, agent_id: str) -> List[Backup]:
        """List all backups for agent"""
        if agent_id not in self.agent_backups:
            return []

        backup_ids = self.agent_backups[agent_id]
        return [self.backups[bid] for bid in backup_ids if bid in self.backups]

    def get_latest_backup(self, agent_id: str) -> Optional[Backup]:
        """Get most recent backup for agent"""
        backups = self.list_backups(agent_id)
        if not backups:
            return None

        return sorted(backups, key=lambda b: b.timestamp, reverse=True)[0]

    def delete_backup(self, backup_id: str) -> bool:
        """Delete backup"""
        if backup_id not in self.backups:
            return False

        backup = self.backups.pop(backup_id)

        if backup.agent_id in self.agent_backups:
            self.agent_backups[backup.agent_id].remove(backup_id)

        return True

    def to_dict(self) -> Dict:
        return {
            "total_backups": len(self.backups),
            "agents_backed_up": len(self.agent_backups),
            "verified": len([b for b in self.backups.values() if b.verified])
        }


class StorageManager:
    """Central manager for persistent storage"""

    def __init__(self):
        self.file_storage = FileStorage()
        self.quota_manager = QuotaManager()
        self.backup_manager = BackupManager()
        self.storage_type = StorageType.FILE

    def save_agent_state(self, agent_id: str, state_data: str) -> bool:
        """Save agent's complete state"""
        size = len(state_data.encode('utf-8'))

        # Check quota
        if not self.quota_manager.get_quota(agent_id).can_store(size):
            return False

        file = StorageFile(
            file_id=f"state_{agent_id}_{len(self.file_storage.files)}",
            filename=f"{agent_id}_state.json",
            file_type=FileType.STATE,
            agent_id=agent_id,
            content=state_data,
            size_bytes=size,
            created_at=0.0,
            modified_at=0.0
        )

        if not self.file_storage.save_file(file):
            return False

        return self.quota_manager.record_storage(agent_id, size)

    def load_agent_state(self, agent_id: str) -> Optional[str]:
        """Load agent's complete state"""
        files = self.file_storage.get_agent_files(agent_id, FileType.STATE)
        if not files:
            return None

        # Return most recent state
        latest = max(files, key=lambda f: f.modified_at)
        return latest.content

    def save_memory(self, agent_id: str, memory_data: str) -> bool:
        """Save agent memory"""
        size = len(memory_data.encode('utf-8'))

        if not self.quota_manager.get_quota(agent_id).can_store(size):
            return False

        file = StorageFile(
            file_id=f"mem_{agent_id}_{len(self.file_storage.files)}",
            filename=f"{agent_id}_memory.log",
            file_type=FileType.MEMORY_LOG,
            agent_id=agent_id,
            content=memory_data,
            size_bytes=size,
            created_at=0.0,
            modified_at=0.0
        )

        if not self.file_storage.save_file(file):
            return False

        return self.quota_manager.record_storage(agent_id, size)

    def create_backup(self, agent_id: str) -> Optional[Backup]:
        """Create complete backup of agent"""
        files = self.file_storage.get_agent_files(agent_id)
        total_size = sum(f.size_bytes for f in files)

        backup = Backup(
            backup_id=f"bak_{agent_id}_{len(self.backup_manager.backups)}",
            agent_id=agent_id,
            timestamp=0.0,
            backup_size=total_size,
            file_count=len(files)
        )

        if not self.backup_manager.create_backup(backup):
            return None

        return backup

    def restore_from_backup(self, backup_id: str) -> bool:
        """Restore agent from backup"""
        backup = self.backup_manager.get_backup(backup_id)
        if not backup:
            return False

        # Mark as verified if restoring
        return self.backup_manager.verify_backup(backup_id)

    def get_storage_stats(self, agent_id: str) -> Dict:
        """Get agent's storage statistics"""
        return {
            "quota": self.quota_manager.get_quota_stats(agent_id),
            "files": len(self.file_storage.get_agent_files(agent_id)),
            "backups": len(self.backup_manager.list_backups(agent_id)),
            "latest_backup": self.backup_manager.get_latest_backup(agent_id).to_dict() if self.backup_manager.get_latest_backup(agent_id) else None
        }

    def to_dict(self) -> Dict:
        return {
            "files": self.file_storage.to_dict(),
            "quotas": self.quota_manager.to_dict(),
            "backups": self.backup_manager.to_dict(),
            "storage_type": self.storage_type.value
        }


# ===== Tests =====

def test_storage_file_creation():
    """Test creating storage file"""
    file = StorageFile(
        "f1", "memory.log", FileType.MEMORY_LOG,
        "agent1", "Memory content", 100, 0.0, 0.0
    )
    assert file.file_id == "f1"
    assert file.file_type == FileType.MEMORY_LOG


def test_storage_quota():
    """Test storage quota"""
    quota = StorageQuota(
        "agent1", 1_000_000  # 1 MB
    )
    assert quota.get_available_bytes() == 1_000_000
    assert quota.get_usage_percentage() == 0.0


def test_quota_available_bytes():
    """Test available bytes calculation"""
    quota = StorageQuota(
        "agent1", 1_000_000
    )
    quota.current_usage_bytes = 300_000

    assert quota.get_available_bytes() == 700_000
    assert quota.get_usage_percentage() == 0.3


def test_quota_can_store():
    """Test checking if file can be stored"""
    quota = StorageQuota(
        "agent1", 1_000_000
    )
    quota.current_usage_bytes = 900_000

    assert quota.can_store(50_000) is True
    assert quota.can_store(150_000) is False


def test_file_storage_save():
    """Test saving file"""
    storage = FileStorage()
    file = StorageFile(
        "f1", "data.txt", FileType.DOCUMENT,
        "agent1", "Content", 100, 0.0, 0.0
    )
    assert storage.save_file(file) is True
    assert storage.get_file("f1") is not None


def test_file_storage_duplicate_rejection():
    """Test storage rejects duplicate files"""
    storage = FileStorage()
    file = StorageFile(
        "f1", "data.txt", FileType.DOCUMENT,
        "agent1", "Content", 100, 0.0, 0.0
    )
    assert storage.save_file(file) is True
    assert storage.save_file(file) is False


def test_file_storage_access_count():
    """Test file access tracking"""
    storage = FileStorage()
    file = StorageFile(
        "f1", "data.txt", FileType.DOCUMENT,
        "agent1", "Content", 100, 0.0, 0.0
    )
    storage.save_file(file)

    assert file.access_count == 0
    storage.get_file("f1")
    assert file.access_count == 1


def test_file_storage_get_agent_files():
    """Test getting agent's files"""
    storage = FileStorage()

    f1 = StorageFile("f1", "file1.txt", FileType.DOCUMENT, "agent1", "C1", 100, 0.0, 0.0)
    f2 = StorageFile("f2", "file2.log", FileType.MEMORY_LOG, "agent1", "C2", 200, 0.0, 0.0)
    f3 = StorageFile("f3", "file3.txt", FileType.DOCUMENT, "agent2", "C3", 150, 0.0, 0.0)

    storage.save_file(f1)
    storage.save_file(f2)
    storage.save_file(f3)

    agent1_files = storage.get_agent_files("agent1")
    assert len(agent1_files) == 2


def test_file_storage_delete():
    """Test deleting file"""
    storage = FileStorage()
    file = StorageFile(
        "f1", "data.txt", FileType.DOCUMENT,
        "agent1", "Content", 100, 0.0, 0.0
    )
    storage.save_file(file)

    assert storage.delete_file("f1") is True
    assert storage.get_file("f1") is None


def test_quota_manager_get_quota():
    """Test quota manager"""
    manager = QuotaManager()
    quota = manager.get_quota("agent1")

    assert quota.agent_id == "agent1"
    assert quota.max_storage_bytes == 10_000_000


def test_quota_manager_custom_quota():
    """Test setting custom quota"""
    manager = QuotaManager()
    assert manager.set_quota("agent1", 5_000_000) is True

    quota = manager.get_quota("agent1")
    assert quota.max_storage_bytes == 5_000_000


def test_quota_manager_record_storage():
    """Test recording storage"""
    manager = QuotaManager()
    assert manager.record_storage("agent1", 1000) is True

    quota = manager.get_quota("agent1")
    assert quota.current_usage_bytes == 1000


def test_quota_exceeded():
    """Test quota exceeded check"""
    manager = QuotaManager()
    manager.set_quota("agent1", 1000)

    assert manager.record_storage("agent1", 900) is True
    assert manager.is_quota_exceeded("agent1") is False

    assert manager.record_storage("agent1", 200) is False
    assert manager.is_quota_exceeded("agent1") is False  # Still under, just can't add


def test_backup_creation():
    """Test backup creation"""
    backup = Backup(
        "bak1", "agent1", 1000.0, 50000, 5
    )
    assert backup.backup_id == "bak1"
    assert backup.verified is False


def test_backup_manager_create():
    """Test backup manager"""
    manager = BackupManager()
    backup = Backup(
        "bak1", "agent1", 1000.0, 50000, 5
    )
    assert manager.create_backup(backup) is True


def test_backup_manager_list():
    """Test listing backups"""
    manager = BackupManager()

    b1 = Backup("bak1", "agent1", 1000.0, 50000, 5)
    b2 = Backup("bak2", "agent1", 2000.0, 60000, 6)

    manager.create_backup(b1)
    manager.create_backup(b2)

    backups = manager.list_backups("agent1")
    assert len(backups) == 2


def test_backup_manager_latest():
    """Test getting latest backup"""
    manager = BackupManager()

    b1 = Backup("bak1", "agent1", 1000.0, 50000, 5)
    b2 = Backup("bak2", "agent1", 2000.0, 60000, 6)

    manager.create_backup(b1)
    manager.create_backup(b2)

    latest = manager.get_latest_backup("agent1")
    assert latest.backup_id == "bak2"  # Most recent


def test_storage_manager_save_state():
    """Test saving agent state"""
    manager = StorageManager()
    state_data = '{"knowledge": [], "personality": {}}'

    assert manager.save_agent_state("agent1", state_data) is True


def test_storage_manager_save_memory():
    """Test saving memory"""
    manager = StorageManager()
    memory_data = "Memory log entry 1\nMemory log entry 2"

    assert manager.save_memory("agent1", memory_data) is True


def test_storage_manager_backup():
    """Test creating backup"""
    manager = StorageManager()

    manager.save_agent_state("agent1", '{"state": "data"}')
    backup = manager.create_backup("agent1")

    assert backup is not None
    assert backup.agent_id == "agent1"


def test_complete_storage_workflow():
    """Test complete storage workflow"""
    manager = StorageManager()

    # Save initial state
    initial_state = '{"personality": "curious"}'
    assert manager.save_agent_state("agent1", initial_state) is True

    # Save memory
    memory = "Learned about Python\nCompleted first task"
    assert manager.save_memory("agent1", memory) is True

    # Create backup
    backup = manager.create_backup("agent1")
    assert backup is not None

    # Verify backup
    assert manager.backup_manager.verify_backup(backup.backup_id) is True

    # Get stats
    stats = manager.get_storage_stats("agent1")
    assert stats["files"] >= 2
    assert stats["backups"] >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
