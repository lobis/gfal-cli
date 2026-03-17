# gfal-cli

A pip-installable Python rewrite of the [gfal2-util](https://github.com/lobis/gfal2-util) CLI tools, built on [fsspec](https://filesystem-spec.readthedocs.io/). Supports **HTTP/HTTPS** and **XRootD** only (via [fsspec-xrootd](https://github.com/scikit-hep/fsspec-xrootd)).

The original gfal2-util implementation lives in `gfal2-util/` (gitignored, clone separately for reference) and is the reference for CLI compatibility.

## Installation

```bash
pip install -e .
```

This registers all `gfal-*` executables as console scripts. Reinstall after changes to `pyproject.toml` (new entry points). Source edits in `src/` are picked up immediately without reinstalling.

## Project layout

```
src/gfal_cli/
  shell.py      Entry point + dispatcher (all executables share this)
  base.py       CommandBase class, @arg decorator, surl() type, common args
  fs.py         fsspec integration: url_to_fs(), StatInfo wrapper, helpers
  commands.py   mkdir, save, cat, stat, rename, chmod, sum, xattr
  ls.py         gfal-ls (CommandLs)
  copy.py       gfal-cp / gfal-copy (CommandCopy)
  rm.py         gfal-rm (CommandRm)
  utils.py      file_type_str(), file_mode_str() — pure helpers, no fsspec
  progress.py   Terminal progress bar for copy operations
```

## How dispatch works

Every `gfal-*` executable calls the same `shell.main()`. It reads `sys.argv[0]`, strips the `gfal-` prefix, resolves any aliases (`cp` → `copy`), then finds the `CommandBase` subclass that has an `execute_<cmd>` method. That method is decorated with `@arg(...)` to declare its argparse arguments.

To add a new command:
1. Add an `execute_<name>(self)` method to an existing or new `CommandBase` subclass.
2. Add a `gfal-<name> = "gfal_cli.shell:main"` entry point in `pyproject.toml` and reinstall.
3. Import the module in `shell.py` so the subclass is registered.

## fsspec integration (`fs.py`)

- `url_to_fs(url, storage_options)` — normalises URLs (bare paths → `file://`, `dav://` → `http://`), returns `(AbstractFileSystem, path)`.
- `StatInfo(info_dict)` — wraps an fsspec `info()` dict into a POSIX stat-like object. Synthesises `st_mode` when the filesystem doesn't provide one (e.g. HTTP returns no mode, uid, gid).
- `build_storage_options(params)` — extracts `client_cert`/`client_key` from parsed CLI params for HTTP auth. XRootD auth is handled via `X509_USER_*` environment variables (set in `base.py:execute()`).

### Known fsspec quirks

- `LocalFileSystem.mkdir(path)` raises `FileExistsError` unconditionally if the path exists, even when `create_parents=True`. Use `makedirs(path, exist_ok=True)` for the `-p` flag — already handled in `execute_mkdir`.
- HTTP `info()` always returns `type='file'` — it cannot distinguish files from directories (just does a HEAD request). `gfal-ls` therefore always calls `fso.ls()` directly and infers type from the result rather than relying on `info()['type']`.
- HTTP `info()` returns very few fields (no mode, uid, gid, timestamps). `StatInfo` fills in sensible defaults so the rest of the code doesn't need to guard every access.
- For XRootD the `info()` dict contains a `mode` integer; rely on that rather than synthesising it.
- XRootD via `fsspec.filesystem("root")` fails — use `fsspec.url_to_fs(url)` instead so fsspec extracts the `hostid` from the URL and passes it to `XRootDFileSystem.__init__()`.

### HTTP error messages

fsspec/aiohttp raise `ClientResponseError` (not an `OSError`) for HTTP errors. `CommandBase._format_error()` maps HTTP status codes to POSIX-style descriptions (403 → "Permission denied", 404 → "No such file or directory") and also handles fsspec-style `FileNotFoundError` instances that carry no `strerror`.

### EOS HTTPS endpoint (eospublic.cern.ch:8444)

- File stat/cat/copy works via HTTPS.
- Directory listing returns **403 Forbidden** — EOS does not support HTTP directory listing. Use XRootD (`root://`) for directory operations.
- The server uses the CERN Root CA 2 certificate. Without it installed locally, all HTTPS requests fail with `SSLCertVerificationError`. Use `--no-verify` to skip, or install the CA:
  ```bash
  # macOS
  curl -O https://cafiles.cern.ch/cafiles/certificates/CERN%20Root%20Certification%20Authority%202.crt
  openssl x509 -inform DER -in "CERN Root Certification Authority 2.crt" -out /tmp/cern-root-ca-2.pem
  sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain /tmp/cern-root-ca-2.pem
  ```

### XRootD on macOS (pip-installed)

The `xrootd` pip package installs security plugins (`libXrdSecgsi-5.so`, `libXrdSeckrb5-5.so`, etc.) inside the `pyxrootd` package directory. On macOS the dynamic linker does not look there, so GSI auth fails with "Could not load authentication handler". Fix by setting `DYLD_LIBRARY_PATH`:

```bash
export DYLD_LIBRARY_PATH="$(python3 -c 'import pyxrootd,os; print(os.path.dirname(pyxrootd.__file__))'):$DYLD_LIBRARY_PATH"
export X509_USER_PROXY=/tmp/x509up_u<uid>
gfal-ls "root://eospublic.cern.ch//eos/opendata/atlas/rucio/data16_13TeV/"
```

This is a macOS-only issue; on Linux the `.so` files are installed system-wide and are found automatically.

## Common args (every command)

`-v / --verbose`, `-t / --timeout`, `-E / --cert`, `--key`, `--log-file`

These are added automatically by `CommandBase.parse()`. Do not re-declare them in individual commands.

## Error handling

`CommandBase._executor()` catches all exceptions in the worker thread and maps them to exit codes. The exception's `errno` attribute is used when present; otherwise exit 1. Broken pipe (EPIPE) is silently swallowed. Tracebacks are never printed to the user.

`CommandBase._format_error(e)` converts exceptions to user-friendly strings. It handles three cases: real OS errors (already have `strerror` in `str(e)`), fsspec-style `OSError` subclasses with no `strerror` (appends POSIX description from the type), and aiohttp `ClientResponseError` with an HTTP `status` code (maps to POSIX description).

## Intentionally omitted

- Tape commands: `gfal-bringonline`, `gfal-archivepoll`, `gfal-evict`
- `gfal-token`
- Legacy LFC commands (`gfal-legacy-*`)
- gfal2-specific flags: `-D`/`--definition`, `-C`/`--client-info`, `-4`/`-6`
- GridFTP-specific copy options: `--nbstreams`, `--tcp-buffersize`, `--spacetoken`, `--copy-mode`, etc.

## Testing

pytest test suite lives in `tests/`. Run with:

```bash
pytest tests/                                    # all unit tests
pytest tests/ -m integration                     # integration tests (need network)
pytest tests/test_integration_eospublic.py       # EOS public endpoint tests
```

Manual smoke tests against local files:

```bash
echo "hello" > /tmp/test.txt

gfal-stat /tmp/test.txt
gfal-ls -l /tmp/
gfal-cp /tmp/test.txt /tmp/test_copy.txt
gfal-sum /tmp/test.txt ADLER32
gfal-cat /tmp/test.txt
gfal-mkdir /tmp/test_dir
gfal-cp -r /tmp/test_dir /tmp/test_dir2   # recursive copy
gfal-rm -r /tmp/test_dir /tmp/test_dir2
gfal-rm /tmp/test_copy.txt
rm /tmp/test.txt
```

For XRootD and HTTP, substitute `root://` and `https://` URLs respectively. XRootD auth uses the proxy at `$X509_USER_PROXY` or cert/key via `-E`/`--key`.
