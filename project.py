#!/usr/bin/env python3
import sys
import os
import traceback


def main():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    debug = os.environ.get('DEBUG', 'false').lower() == 'true'

    if debug:
        print("[DEBUG] Starting project.py", file=sys.stderr)
        print(f"[DEBUG] Args: {sys.argv}", file=sys.stderr)

    try:
        from extensions import registry
        import transforms

        if debug:
            print(f"[DEBUG] transform_sets: {list(registry.transform_sets.keys())}", file=sys.stderr)
            for seed, transforms_list in registry.transform_sets.items():
                print(f"[DEBUG] Seed '{seed}' has {len(transforms_list)} transforms:", file=sys.stderr)
                for t in transforms_list:
                    print(f"[DEBUG]   - {t.display_name}", file=sys.stderr)

        args = sys.argv[1:]

        if len(args) >= 2:
            transform_name = args[0].strip('"').strip("'")
            input_value = args[1]

            if debug:
                print(f"[DEBUG] Looking for: {transform_name}", file=sys.stderr)

            transform_meta = None
            for seed, transforms_list in registry.transform_sets.items():
                for t in transforms_list:
                    if t.display_name == transform_name:
                        transform_meta = t
                        break
                if transform_meta:
                    break

            if not transform_meta:
                print(f"Error: Transform '{transform_name}' not found", file=sys.stderr)
                print("Available transforms:", file=sys.stderr)
                for seed, transforms_list in registry.transform_sets.items():
                    for t in transforms_list:
                        print(f"  - {t.display_name}", file=sys.stderr)
                sys.exit(1)

            class_name = transform_meta.class_name

            if class_name == 'fulldiscordosint':
                from transforms.FullDiscordOSINT import FullDiscordOSINT
                transform_class = FullDiscordOSINT
            else:
                print(f"Error: Unknown class {class_name}", file=sys.stderr)
                sys.exit(1)

            from maltego_trx.maltego import MaltegoMsg, MaltegoTransform
            request = MaltegoMsg()
            request.Value = input_value
            response = MaltegoTransform()

            transform_class.create_entities(request, response)
            print(response.returnOutput())

        else:
            print("Available transforms:")
            for seed, transforms_list in registry.transform_sets.items():
                for t in transforms_list:
                    print(f"  - {t.display_name}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if debug:
            traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()