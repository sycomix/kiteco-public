import argparse

import kite.canonicalization.ontology as ontology


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input')
    parser.add_argument('--patterns')
    args = parser.parse_args()

    # Load regexes
    with open(args.patterns) as fd:
        x = ontology.Ontology(map(str.strip, open(args.patterns)))

    print('Loaded patterns for %d canonical errors' % len(x.patterns))

    # Apply to each line of text
    for line in open(args.input):
        line = line.strip()
        info = x.canonicalize(line)
        if info is not None:
            print(f'Matched: {line}')
            print(f'  Mapped to canonical error: {info.pattern.format_string}')
            for value in info.wildcards:
                print(f'    Wildcard: {value}')

if __name__ == '__main__':
    main()
