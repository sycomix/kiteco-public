import click
import os
import json

from kite_metrics.loader import load_json_schema


@click.command()
@click.option('--out', type=click.Path())
@click.option('--full', default=False)
def main(out, full):
    for schema_name in ['kite_status', 'types']:
        if out:
            file = open(
                os.path.abspath(
                    os.path.join(out, f'{schema_name}.schema.json')
                ),
                'w',
            )
            writer = file.write
        else:
            writer = click.echo

        schema = load_json_schema(schema_name, {"full_validation": full})
        try:
            writer(json.dumps(schema, indent=2))
        except:
            click.echo(f"Error writing schema {schema}")


if __name__ == '__main__':
    main()
