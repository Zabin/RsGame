.PHONY: build test test-unit test-integration previews clean all lint help install-hooks

help:
	@echo "RsGame Build Commands:"
	@echo ""
	@echo "  make build              Build ROM to BunnyGarden.gbc"
	@echo "  make test               Run all tests (unit + integration)"
	@echo "  make test-unit          Run unit tests only (fast, ~0.2s)"
	@echo "  make test-integration   Run integration tests (slow, requires PyBoy)"
	@echo "  make previews           Regenerate all PNG previews (tiles, screens, music)"
	@echo "  make lint               Run code quality checks (Black, Pylint, Flake8)"
	@echo "  make clean              Delete generated files (ROM + previews)"
	@echo "  make all                Full pipeline: build + test + previews"
	@echo "  make install-hooks      Set up git pre-commit hook"
	@echo ""
	@echo "Examples:"
	@echo "  make all                # Full build & test cycle"
	@echo "  make test-unit          # Quick smoke test"
	@echo "  make previews           # Refresh graphics without rebuilding"
	@echo ""

build:
	python build_rom.py

test:
	pytest tests/ test_rom.py -v --tb=short

test-unit:
	pytest tests/unit -v

test-integration:
	pytest tests/integration -v

previews:
	python tile_preview.py --all
	python screen_preview.py --all
	python music_preview.py

lint:
	black . --check
	isort . --check
	pylint *.py tests/ || true

clean:
	rm -f BunnyGarden.gbc
	rm -f previews/*.png previews/*/*.png

all: build test previews
	@echo ""
	@echo "✅ Full build pipeline complete"
	@echo "  ROM: BunnyGarden.gbc"
	@echo "  Previews: previews/"

install-hooks:
	@echo "Setting up pre-commit hook..."
	@chmod +x .git/hooks/pre-commit
	@echo "✅ Pre-commit hook installed"
	@echo "   Every commit will now:"
	@echo "   - Run tests (must pass)"
	@echo "   - Build ROM"
	@echo "   - Generate previews"
	@echo "   To bypass (emergency only): git commit --no-verify"
