# 🔐 XRP Seed Manager

A lightweight encryption tool to safely store and manage your **XRP wallet seeds**, built with protection against malware in mind.

---

## 📦 Requirements

Install the only dependency using:

```bash
pip install pycryptodome==3.22.0
```

## 🔧 Integration Example
Easily integrate it into your project:
```python
from getpass import getpass
import xrp_seed_manager

password = getpass("Password: ")

seed_manager = xrp_seed_manager.XRPSeedManager()
try:
    seeds = seed_manager.decrypt_seeds(
        seed_file=".xrp_seeds/n_seeds.xrpseed",
        password=password
    )
except Exception:
    print("Wrong password")
    exit()

print(seeds)

```

## ⚠️ Warning
This tool does not store backups.

Keep copies of your encrypted seed file in a safe location.

I am not responsible for any data loss.
