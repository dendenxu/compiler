# Nano C

The C programming language compiler with extremely limited functionality.

We'd only implement a subset of a subset of C. Don't even expect preprocessing.

And **do rememeber to delete those lines after this repo goes public**

## Language Specification

To be filled...

- Types: `int`, `double`, `float`, `char`, `unsigned`, `static`, `const`, `void`, `[]`
- Control Flow: `if`, `else`, `while`, `for`, `continue`, `break`
- Function: `return`, typed functions, scope(`{}` `;`)
- Aggregation: `struct`, `union`, `enum`
- Operator:
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
    13. `?`
        - `Expression1 ? Expression2 : Expression3`
        - `if (Expression1) Expression2;`
        - `else Expression3;`
    14. `=`
    15. `,`
- Comment: `//`

## Reference

- [PyCParser](https://github.com/eliben/pycparser)
- ...
