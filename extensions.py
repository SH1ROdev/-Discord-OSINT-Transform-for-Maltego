from maltego_trx.decorator_registry import TransformRegistry

registry = TransformRegistry(
    owner="sh1ro",
    author="Discord: shirov3_",
    host_url="http://localhost:8080",
    seed_ids=["discord"]
)

registry.version = "1.0"
registry.display_name_suffix = " [Discord Sensor]"
