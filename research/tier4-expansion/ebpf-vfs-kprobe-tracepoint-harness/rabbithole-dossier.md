# Rabbithole Dossier: eBPF VFS Kprobe and Tracepoint Harness

## 1. Deep Mathematical Mechanics & In-Kernel C Logic

Let $\mathcal{I}_{\text{tripwire}} \subset \mathbb{N} \times \mathbb{N}$ be the set of monitored canary file identifiers $(dev, ino)$.

The eBPF verification engine executes the following in-kernel filter on the `vfs_write` entry hook:

```c
#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

struct canary_key_t {
    __u32 dev;
    __u64 ino;
};

struct event_t {
    __u32 pid;
    __u32 dev;
    __u64 ino;
    char comm[16];
    __u32 op_type;
};

struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 1024);
    __type(key, struct canary_key_t);
    __type(value, __u32);
} canary_map SEC(".maps");

struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024);
} ringbuf SEC(".maps");

SEC("kprobe/vfs_write")
int BPF_KPROBE(trace_vfs_write, struct file *file) {
    struct inode *inode = BPF_CORE_READ(file, f_inode);
    if (!inode)
        return 0;

    struct canary_key_t key = {};
    key.dev = BPF_CORE_READ(inode, i_sb, s_dev);
    key.ino = BPF_CORE_READ(inode, i_ino);

    __u32 *policy = bpf_map_lookup_elem(&canary_map, &key);
    if (policy) {
        // Canary breach detected!
        struct event_t *event = bpf_ringbuf_reserve(&ringbuf, sizeof(*event), 0);
        if (event) {
            event->pid = bpf_get_current_pid_tgid() >> 32;
            event->dev = key.dev;
            event->ino = key.ino;
            event->op_type = 1; // WRITE
            bpf_get_current_comm(&event->comm, sizeof(event->comm));
            bpf_ringbuf_submit(event, 0);
        }
        // Terminate offending process immediately
        bpf_send_signal(9); // SIGKILL
    }
    return 0;
}

char LICENSE[] SEC("license") = "GPL";
```

---

## 2. Python User-Space Test Harness Integration

```python
import os
import sys
import ctypes
from pathlib import Path
from typing import Dict, List, Optional

class EBPFTripwireMonitor:
    def __init__(self, canary_files: List[Path]):
        self.canary_files = canary_files
        self.violations: List[dict] = []
        self._is_active = False

    def setup_canaries(self) -> Dict[tuple, str]:
        inode_map = {}
        for p in self.canary_files:
            p.parent.mkdir(parents=True, exist_ok=True)
            if not p.exists():
                p.write_text("TRIPWIRE_CANARY_ACTIVE")
            stat = p.stat()
            # Key: (st_dev, st_ino)
            inode_map[(stat.st_dev, stat.st_ino)] = str(p)
        return inode_map

    def poll_violations(self) -> List[dict]:
        """
        Polls ring buffer events (or fallback inode stat checks when eBPF is unavailable).
        """
        # Emulation fallback for macOS and environments without root CAP_BPF
        for p in self.canary_files:
            if not p.exists():
                self.violations.append({"type": "UNLINK", "path": str(p)})
            elif p.read_text() != "TRIPWIRE_CANARY_ACTIVE":
                self.violations.append({"type": "MUTATION", "path": str(p)})
        return self.violations

    def assert_no_breach(self):
        violations = self.poll_violations()
        if violations:
            raise AssertionError(f"Honeypot Syscall Tripwire Triggered: {violations}")
```

---

## 3. Edge Cases & Failure Modes

1. **Inode Recycling / Inode Collisions**: When a file is unlinked and a new file created in rapid succession on ext4 filesystems, the kernel allocator can reassign the exact same inode number.
   - *Mitigation*: Track both inode number and inode generation counter (`inode->i_generation`).
2. **OverlayFS Mount Inode Virtualization**: Inside Docker containers running OverlayFS, upper and lower layer inode numbers diverge, causing host/guest inode mismatch.
   - *Mitigation*: Resolve inodes directly against the container's private mount namespace (`/proc/<pid>/root`).
