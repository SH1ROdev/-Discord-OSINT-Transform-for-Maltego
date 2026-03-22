import sys
import transforms
from extensions import registry
from maltego_trx.handler import handle_run
from maltego_trx.registry import register_transform_classes
from maltego_trx.server import app as application


def main():
    register_transform_classes(transforms)

    registry.write_transforms_config(include_output_entities=True)
    registry.write_settings_config()


if __name__ == '__main__':
    main()