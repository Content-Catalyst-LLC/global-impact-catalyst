# Global Impact Catalyst WordPress Plugin

Version 1.2.0 provides two shortcodes:

```text
[global_impact_catalyst_demo]
[global_impact_catalyst_workspace]
```

The demo is a stateless public canonical-contract builder. The workspace requires an authenticated user with `edit_posts` capability and adds persistent save, autosave recovery, search, duplicate, archive/restore, import, and export workflows.

Activation or automatic plugin-version upgrade creates prefixed contract, autosave, and audit tables. REST routes use the `global-impact-catalyst/v1` namespace, WordPress REST nonces, capability checks, and optimistic revision conflicts.

The package is v1.2.0. The embedded canonical contract engine remains v1.1.0 to preserve exact Python/browser calculation parity.
