# this script takes output of ./spyder-data,
# adds all entries to a new bloomfilter
# and serializes the data of the bloomfilter into the output file
#
# usage: create_bloom_data.py <in> <out>

import sys
# this is our fork of pybloom to support PyQt bitset
# https://github.com/kiteco/python-bloomfilter
from pybloom_pyqt import BloomFilter

if len(sys.argv) != 3:
    print(f"usage: {sys.argv[0]} <input-file> <output-file>")
    sys.exit(-1)
input_path = sys.argv[1]
output_path = sys.argv[2]

with open(input_path, 'r') as f:
    lines = sum(1 for _ in f)
    print(f'bloom filter size: {lines}')
    f.seek(0)
    b = BloomFilter(capacity=lines)
    for line in f:
        b.add(line.strip('\n\r '))

b.tofile(output_path)
print(f'successfully saved bloom filter data to {output_path}')

checks = {
    "json.load",
    "json.loads",
    "json.dumps",
    "plt.figure",
    "pd.read_csv",
}
for check in checks:
    print(f'selftest: {check}? {check in b}')
