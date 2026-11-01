# Local review installation and rollback

Use the existing shared canonical portfolio installer linked in the [portfolio installation guide](https://michaeljabbour.github.io/reports/capability-installer/). Review its script and source provenance rather than downloading and running an unpinned command. The three README steps require an already available installer, a clean local checkout, full source commit, an explicit destination, a harness choice and the reviewed preview hash.

The preview describes files, hashes, target paths, permissions and dataflow. Installation copies tracked files under `skills/stories/` only. It does not run the checker, an LLM, an upstream recipe or a provider, install dependencies, grant trust, or publish. The installer’s transaction receipt supports `doctor`, `uninstall` and `rollback`; preserve it with the source commit. Review a fresh uninstall preview/hash before applying. Rollback uses the exact returned transaction, refuses edited installations and retains backups according to the shared installer contract.

The normal manual discovery alternative is to place the complete `skills/stories` folder in the host's supported skills-parent directory, including its LICENSE, references, schemas, checker and diagram. Manual copying has no shared transaction or hash receipt guarantee. Avoid overwriting another method named `stories`; inspect and resolve the conflict first.

There are no existing public Stories capability repository aliases to migrate. The old multi-agent bundle is not silently replaced: its recipes, namespaces, publishing behavior and document formats are not compatible surfaces of this small extraction. An existing bundle user should keep that installation until choosing this method separately. No active user installation is changed by the local review tests.

The optional checker works with Python 3.11+ and its standard library. Applying the written method requires a compatible caller; its provider/authentication/dataflow must already be authorized. No credentials are bundled or created.
