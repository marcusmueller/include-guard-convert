#!/usr/bin/env python3
# SPDX-license-identifier: GPL-2.0-only
# Copyright: 2025 Marcus Müller and contributors
"""Tool to convert traditional include guards to #pragma once."""

__all__ = ["guarded_include", "main"]

import re
import os
import subprocess
import shlex

REGEXES = {
    "ifndef": r"^\s*# *(?:ifndef|IFNDEF)\s+([A-Za-z_0-9]{4,})\s*$",
    "define": r"^\s*# *(?:define|DEFINE)\s+([A-Za-z_0-9]{4,})\s*$",
    "endif": r"^\s*# *(?:endif|ENDIF)\s*(/\*.*\*/|//.*)?\s*$",
    "blank": r"^\s*(/\*.*\*/|//.*)?\s*$",
    "pragma": r"^\s*#(?:pragma|PRAGMA)\s+(?:once|ONCE)",
}
PATTERNS = dict([(key, re.compile(REGEXES[key])) for key in REGEXES.keys()])

CPP_COMMANDS = {
    "strip_comments": "cpp -w -dD  -fpreprocessed  -P -x c++ {file}",
    "test_if_guarded": "cpp -w -P -x c++ -D{define} {file}",
}


class guarded_include(object):
    """
    Class representing an #include'able file (a.k.a. a header).
    """

    def __init__(self, filename, autoconvert=False):
        self.filename = filename
        assert self._test_readable()
        if autoconvert and self.test_oldstyle_guarded():
            self.convert()

    def _test_readable(self) -> bool:
        return os.access(self.filename, os.R_OK)

    def test_oldstyle_guarded(self) -> re.Match | None:
        try:
            self._stripped = subprocess.check_output(
                shlex.split(CPP_COMMANDS["strip_comments"].format(file=self.filename)),
                stderr=subprocess.STDOUT,
                encoding="utf8",
            )
            lineend = self._stripped.find("\n")
            match_ifndef = PATTERNS["ifndef"].search(self._stripped[:lineend])
            if not match_ifndef:
                return None
            define = match_ifndef.group(1)
            with_define = subprocess.check_output(
                shlex.split(
                    CPP_COMMANDS["test_if_guarded"].format(
                        file=self.filename, define=define
                    )
                ),
                stderr=subprocess.STDOUT,
                encoding="utf8",
            )
            if not len(with_define) < 2:
                return None
            fh = open(self.filename, "r", encoding="utf8")
            line = fh.readline()
            while not PATTERNS["ifndef"].search(line):
                line = fh.readline()
                if not len(line):
                    fh.close()
                    return None

            line = fh.readline()
            fh.close()
            return PATTERNS["define"].search(line)

        except subprocess.CalledProcessError:
            return None

    def convert(self) -> None:
        freadh = open(self.filename, "r", encoding="utf8")
        lines = freadh.readlines()
        sep = "\r\n" if lines[0].endswith("\r\n") else "\n"
        freadh.close()
        fwriteh = open(self.filename, "w", encoding="utf8")
        for l_number in range(1, len(lines)):
            line = lines[-l_number]
            if PATTERNS["blank"].search(line):
                continue
            elif PATTERNS["endif"].search(line):
                lines.pop(-l_number)
                break
            else:
                raise SyntaxError(
                    f"encountered meaningful line after last #endif: \n{line}"
                )
        define = None
        done = False
        for l_number, line in enumerate(lines):
            if done:
                fwriteh.write(line)
                continue
            if define is None:
                pattern = PATTERNS["ifndef"]
            else:
                pattern = PATTERNS["define"]
            match = pattern.search(line)
            if match:
                newdefine = match.group(1)
                if define is None:
                    define = newdefine
                elif define == newdefine:
                    fwriteh.write("#pragma once" + sep)
                    done = True
            else:
                fwriteh.write(line)
        if define is None:
            raise SyntaxError("could not find #ifndef")
        elif define != newdefine:
            raise SyntaxError(
                f"found #ifndef {define}, does not match #define {newdefine}"
            )
        fwriteh.close()


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("filename", nargs="*")
    args = parser.parse_args()
    for filen in args.filename:
        try:
            gi = guarded_include(filen)
            if gi.test_oldstyle_guarded():
                gi.convert()
        except SyntaxError as e:
            print(filen)
            print(e)


if __name__ == "__main__":
    main()
