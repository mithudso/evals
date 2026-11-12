# Workflow log archives

`scripts/rotate_workflow_logs.py` keeps recent versioned sections in oversized
`memory.md` and `prompts.md` logs. It moves each complete original file here before
publishing a shorter root log. Archives preserve the original inode and text,
including writes through an already-open append handle.

The rotation tool refuses to proceed while an editor swap file for either log is
present. Close the editor or resolve its recovery state before trying again.
Do not delete another session's swap file or active work to make rotation pass.

Publication refuses to overwrite a source path recreated by another writer. The
error names the complete archived original. If rotation is interrupted after the
archive move, inspect that snapshot and the current root log before restoring or
combining them. Do not overwrite an active log to recover an archive.
