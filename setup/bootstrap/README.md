# Bootstrap Scripts

One-command setup for fresh clone.

## Usage

**Windows:**
```powershell
.\bootstrap.ps1 --full
```

**macOS/Linux:**
```bash
chmod +x bootstrap.sh
./bootstrap.sh --full
```

**Cross-platform:**
```bash
python bootstrap.py --full
```

## Modes

- `--full` - Full setup (recommended)
- `--minimal` - Core only
- `--auto` - Auto mode (no prompts)

## What It Does

1. Checks Python 3.10+
2. Creates virtual environment
3. Installs dependencies
4. Sets up pre-commit hooks
5. Creates .env file
6. Runs verification

## See Also

- [BOOTSTRAP_GUIDE.md](BOOTSTRAP_GUIDE.md) - Detailed guide
- [../docs/QUICK_START.md](../docs/QUICK_START.md) - After bootstrap
