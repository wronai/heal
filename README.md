# Heal

A Python package for fixing shell errors using LLM assistance.

## Installation

```bash
pip install heal
```

## Quick Start

### Basic Usage (with pipe)

```bash
# Fix errors by piping stderr to heal
make dev 2>&1 | heal fix

# Or from error file
heal fix < error.txt
```

### Automatic Mode (with shell hook)

```bash
# Install shell hook for automatic error capture
heal install

# Add to ~/.bashrc:
source ~/.heal/heal.bash

# Now you can run:
your_failing_command
heal fix
```

## Features

- **LLM-powered error analysis** - Uses GPT models to understand and fix shell errors
- **Automatic command capture** - Shell hook captures last command and output
- **Multiple input methods** - Works with stdin, files, or shell hooks
- **Configurable models** - Support for various LLM providers via litellm

## Commands

### `heal fix`
Fix shell errors using LLM. Reads from stdin or shell hook.

```bash
heal fix [--model MODEL] [--api-key KEY]
```

### `heal install`
Install shell hook for automatic error capture.

```bash
heal install
```

### `heal uninstall`
Remove shell hook and configuration.

```bash
heal uninstall
```

## Configuration

On first run, heal will prompt for:
- API key (for your LLM provider)
- Model name (e.g., `gpt-4o-mini`, `gpt-4.1`)

Configuration is stored in `~/.heal/.env`.

## Examples

### Fix a make error
```bash
make dev 2>&1 | heal fix
```

### Fix a Python error
```bash
python script.py 2>&1 | heal fix
```

### Fix from error log
```bash
heal fix < application.log
```

## Development

This package uses modern Python packaging with `pyproject.toml`.

### Install in development mode

```bash
pip install -e .
```

### Run tests

```bash
python -m pytest
```

## How it works

1. **Command capture**: Gets last command from bash history or shell hook
2. **Error collection**: Reads error output from stdin or captured file
3. **LLM analysis**: Sends command and error to LLM for analysis
4. **Solution proposal**: Returns concrete fix suggestions

## Limitations

- Shell processes cannot access previous process stderr without pipes
- Shell hook required for fully automatic operation
- Requires API key for LLM service

## License

Apache License 2.0 - see [LICENSE](LICENSE) for details.

## Author

Created by **Tom Sapletta** - [tom@sapletta.com](mailto:tom@sapletta.com)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.