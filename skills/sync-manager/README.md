# Sync Manager

Data synchronization manager with retry mechanism, multi-target support, resume capability and integrity verification.

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

1. Copy `config/sync.conf.example` to `config/sync.conf`
2. Edit configuration file with your credentials

## Usage

### CLI Commands

```bash
# Full synchronization
python sync_manager.py sync-all

# Sync specific target
python sync_manager.py sync --target notion
python sync_manager.py sync --target github
python sync_manager.py sync --target local

# Check status
python sync_manager.py status

# Clean checkpoint
python sync_manager.py clean
```

### Python API

```python
from sync_manager import SyncManager

manager = SyncManager()
manager.sync_all()
```

## Features

- Auto-retry (3 attempts with exponential backoff)
- Multi-target sync (Notion + GitHub + Local)
- Resume from checkpoint
- Integrity verification after sync
