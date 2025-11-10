# include-guard-convert

Converts C/C++ preprocessor
[include guards](http://en.wikipedia.org/wiki/Include_guard) from the 
`#ifndef XY_H`, `#define XY_H` to the `#pragma once` paradigm.

Header files have the problem that they should be included _once_ per compile
unit; thus, they usually deploy a scheme that looks like this

```c++
/*
 * some funky comment, doxygen, copyright info
 */
#ifndef MY_HEADERFILE_H
#define MY_HEADERFILE_H

class declare_and_define_whatever_you_want
{
...
};
#endif /* maybe a comment that this belongs to MY_HEADERFILE_H */
```

Since this lead to a few bugs (namely, sometimes there are `#define` naming
conflicts, or copy&paste errors), I've wrote a script to make the same file
look like this:

```c++
/*
 * some funky comment, doxygen, copyright info
 */
#pragma once

class declare_and_define_whatever_you_want
{
...
};
```

## Dependencies

- C preprocessor (only tested with the GCC `cpp`; clang's `clang-cpp` should
  work as well)
- Python 3 >= 3.10

## Installation

```shell
pip install include-guard-convert
```

or run directly using `uvx` or `pipx` (replace as wanted)

```shell
uvx include-guard-convert FILE1.H FILE2.HPP FILE3.HH
```

## Caveats

- The include guards should be the surround the _whole_ semantic content of the
  file. That means that `#ifndef` must be on the first non-comment,
  non-whitespace, non-empty line of your source code and that it must end with
  the matching `#ifndef` line, which may only be followed by empty or
  whitespace-only lines.
- The `#define` constants must be `UPPERCASE_UNDERSCORE_0_TO_9_ONLY` style.
