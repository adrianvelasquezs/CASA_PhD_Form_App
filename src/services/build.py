"""
Build helper for creating standalone executables with PyInstaller.

Cross-platform strategy
-----------------------
PyInstaller cannot cross-compile: a Windows .exe must be produced on a
Windows host and a macOS binary must be produced on a macOS host.  True
cross-platform builds are handled automatically by the GitHub Actions
workflow at .github/workflows/build.yml, which spins up a native runner
for each OS in parallel.

This script is the single build entry-point used both locally and by CI:
  - Run it on macOS  → produces  <root>/casa_phd_form.app
  - Run it on Windows → produces <root>/casa_phd_form.exe

Local usage:
    python src/services/build.py
    python src/services/build.py --name my_app
    python src/services/build.py --dry-run
    python src/services/build.py --no-clean
"""

from __future__ import annotations

import argparse
import platform
import shutil
import subprocess
import sys
from pathlib import Path

def _detect_platform() -> str:
    if sys.platform.startswith('win'):
        return 'windows'
    if sys.platform == 'darwin':
        return 'macos'
    raise RuntimeError(
        f'Unsupported host platform: {sys.platform}. '
        'Use the GitHub Actions workflow for automated cross-platform builds.'
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            'Build CASA PhD executable with PyInstaller. '
            'Always produces the binary for the current host OS. '
            'For cross-platform builds use the GitHub Actions workflow.'
        )
    )
    parser.add_argument(
        '--name',
        default='casa_phd_form',
        help='Executable name without extension (default: casa_phd_form).',
    )
    parser.add_argument(
        '--no-clean',
        action='store_true',
        help='Keep previous build cache and dist artifacts.',
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Print the PyInstaller command without executing it.',
    )
    return parser.parse_args()


def _remove_if_exists(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def _clean_artifacts(root_dir: Path, app_name: str) -> None:
    _remove_if_exists(root_dir / '.pyinstaller')
    _remove_if_exists(root_dir / app_name)
    _remove_if_exists(root_dir / f'{app_name}.app')
    _remove_if_exists(root_dir / f'{app_name}.exe')


def _output_path(root_dir: Path, app_name: str, host_platform: str) -> Path:
    if host_platform == 'windows':
        return root_dir / f'{app_name}.exe'
    return root_dir / f'{app_name}.app'


def _build_command(root_dir: Path, app_name: str, clean_build: bool, host_platform: str) -> list[str]:
    entrypoint = root_dir / 'src' / 'main.py'
    if not entrypoint.exists():
        raise FileNotFoundError(f'Entrypoint not found: {entrypoint}')

    src_dir  = root_dir / 'src'
    work_dir = root_dir / '.pyinstaller' / 'work'
    spec_dir = root_dir / '.pyinstaller' / 'spec'

    command = [
        sys.executable, '-m', 'PyInstaller',
        '--noconfirm',
        '--windowed',
        '--name', app_name,
        # output the finished binary directly into the project root
        '--distpath', str(root_dir),
        '--workpath', str(work_dir),
        '--specpath', str(spec_dir),
        # make src/ importable so services/utils, ui/gui, public/styles resolve
        '--paths', str(src_dir),
        # hidden imports for pandas/openpyxl engine that PyInstaller may miss
        '--hidden-import', 'openpyxl',
        '--hidden-import', 'pandas',
        str(entrypoint),
    ]

    if host_platform == 'windows':
        command.insert(4, '--onefile')
    else:
        command.extend([
            '--osx-bundle-identifier', 'co.uniandes.casa.phdform',
        ])

    if clean_build:
        command.insert(3, '--clean')

    return command


def main() -> int:
    args = _parse_args()

    try:
        host_platform = _detect_platform()
    except RuntimeError as exc:
        print(f'Error: {exc}')
        return 1

    root_dir    = Path(__file__).resolve().parents[2]
    clean_build = not args.no_clean

    output_file = _output_path(root_dir=root_dir, app_name=args.name, host_platform=host_platform)

    print(f'Host OS      : {platform.system()} ({host_platform})')
    print(f'Project root : {root_dir}')
    print(f'Output file  : {output_file}')

    if clean_build:
        print('Cleaning previous artifacts...')
        _clean_artifacts(root_dir=root_dir, app_name=args.name)

    command = _build_command(
        root_dir=root_dir,
        app_name=args.name,
        clean_build=clean_build,
        host_platform=host_platform,
    )

    print('\nPyInstaller command:')
    print(' '.join(command))

    if args.dry_run:
        print('\nDry run — no files were generated.')
        return 0

    print()
    subprocess.run(command, check=True)
    print(f'\nBuild complete -> {output_file}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

