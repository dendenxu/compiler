# Nano C

The C programming language compiler with extremely limited functionality.

We'd only implement a subset of a subset of C. Don't even expect preprocessing.

And **do rememeber to delete these lines after this repo goes public**

## Language Specification

To be filled...

- Types: `int`, `double`, `float`, `char`, `void`, `unsigned`, `static`, `const`, `[]`
- Control Flow: `if`, `else`, `while`, `for`, `continue`, `break`
- Function: `return`, typed functions, scope(`{}` `;`)
- Aggregation: `struct`, `union`, `enum`
- Operators (with priorities):
    1. `()` `[]` `->` `.`
    2. `-` `++` `--` `!` `&` `*` `~` `(type)` `sizeof`
    3. `*` `/` `%`
    4. `+` `-`
    5. `<<` `>>`
    6. `<` `<=` `>` `<=`
    7. `==` `!=`
    8. `&`
    9. `^`
    10. `|`
    11. `&&`
    12. `||`
    13. `?:`
    14. `=`
    15. `,`
- Comment: `//` (one-line comment)

## References

- [PyCParser](https://github.com/eliben/pycparser)
- ...
