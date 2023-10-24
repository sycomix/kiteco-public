from typing import List, Optional

import logging
import json

from kite.model.model import DataFeeder

from .raw_sample import RawSample


class FileFeeder(DataFeeder):
    def __init__(self, json_filename: str, count: int, start_offset: int=0):
        """
        Cycle through a file containing JSON-encoded samples

        :param json_filename: contains JSON-encoded RawSamples separated by newlines
        :param count: the number of records to read before restarting
        :param start_offset: the byte offset at which to start reading files
        """
        self._filename = json_filename
        self._count = count
        self._start_offset = start_offset
        self._file = None
        self._reset()

    def next(self) -> RawSample:
        if self._counter >= self._count:
            self._reset()
            return self.next()

        line = self._file.readline()
        if not line:
            if self._counter == 0:
                raise Exception(f"reached end of {self._filename} without reading lines")
            self._reset()
            return self.next()

        data = json.loads(line)
        self._counter += 1
        return RawSample.from_json(data)

    def count(self) -> int:
        return self._count

    def _reset(self):
        if self._file is not None:
            self._file.close()
        self._file = open(self._filename, 'r')
        self._file.seek(self._start_offset)
        self._counter = 0

    def stop(self):
        if self._file is not None:
            self._file.close()


class FileFeederSplit(object):
    def __init__(self, json_filename: str, val_fraction: float=0.2):
        """
        Create train/val FileFeeders which cycle through disjoint partitions of a file containing JSON-encoded samples

        :param json_filename: contains JSON-encoded RawSamples separated by newlines
        :param val_fraction: fraction of samples to use in the validation set
        """

        assert 0 < val_fraction < 1, f"val_fraction out of range: {val_fraction}"

        with open(json_filename, 'r') as f:
            lines = sum(1 for _ in f)
            num_train = int(lines * (1.0 - val_fraction))
            num_val = int(lines * val_fraction)

            assert (
                num_train > 0
            ), f"{json_filename} has too few samples ({lines}) to create train set"
            assert (
                num_val > 0
            ), f"{json_filename} has too few samples ({lines}) to create validation set"

            logging.info(
                f"{json_filename} has {lines} samples, will use {num_train} for train and {num_val} for validation"
            )

            # find the offset of the first validation sample
            f.seek(0)
            line = 0
            while True:
                if line == num_train:
                    val_offset = f.tell()
                    break
                f.readline()
                line += 1

        self._train_feeder = FileFeeder(json_filename, num_train)
        self._val_feeder = FileFeeder(json_filename, num_val, start_offset=val_offset)

    def train_feeder(self) -> FileFeeder:
        return self._train_feeder

    def val_feeder(self) -> FileFeeder:
        return self._val_feeder


class Batcher(DataFeeder):
    def __init__(self, feeder: DataFeeder, batch_size: int):
        self._feeder = feeder
        self._batch_size = batch_size
        self._samples: List[RawSample] = []

    def next(self) -> List[RawSample]:
        while len(self._samples) < self._batch_size:
            self._samples.append(self._feeder.next())
        ret = self._samples
        self._samples = []
        return ret

    def stop(self):
        self._feeder.stop()
