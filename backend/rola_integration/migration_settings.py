"""Migration graph selection for upgrading pre-monorepo databases."""

LEGACY_MIGRATION_MODULES = {
    app: f"rola_integration.legacy_migrations.{app}"
    for app in ("core", "rating", "payment", "backup", "rola_integration")
}

PORTABLE_MIGRATIONS = {
    (app, "0001_portable")
    for app in ("core", "rating", "payment", "backup", "rola_integration")
}
