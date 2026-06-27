#!/usr/bin/env python3
"""Multilang (ShellBolt) word-count bolt for Apache Storm, wired via Flux.

It receives single-field "word" tuples emitted by the built-in
org.apache.storm.testing.TestWordSpout and keeps a running count per word,
logging every update to the Storm worker log. It is a terminal bolt (emits
nothing downstream), so no output fields are declared.

`import storm` resolves to resources/storm.py, the multilang protocol adapter
that is shipped inside the topology jar next to this file.
"""
import collections

import storm


class WordCountBolt(storm.BasicBolt):
    def initialize(self, conf, context):
        self._counts = collections.Counter()

    def process(self, tup):
        word = tup.values[0]
        self._counts[word] += 1
        # Visible in the worker log (see README for how to tail it).
        storm.log("WORDCOUNT %s = %d" % (word, self._counts[word]))


WordCountBolt().run()
