## Language

### Data types

#### Booleans

- `True`
- `False`

#### Numbers

- `1234`
- `12.34`

#### Strings

`"A string"`  
`'Another string'`

#### None

`None` 

#### List

`[1, 2, 'can', "contain", "anything", False]`

#### Dictionary

`{'key': 'value', "like": "Python"}`

### Expressions

Produce a value

#### Arithmethic

- addition, `+`
- subtraction, `-`
- multiplication, `*`
- division, `/`

#### Comparison and equality

- `less < than`
- `greater > than`
- `lessthan <= orequal`
- `greaterthan >= orequal`

- `1 == 2`
- `"cat" != "dog"`

#### Logical operators

- `and`
- `or`
- `not`

#### Ternary operator

`1 if something_is_true else 2`

### Statements

Produce an effect

#### Variables

Assignment: `variable_name = "some value"`

#### Functions

Identifiers followed by parenthesis significes the calling of a builtin function provided by the host.

## Precedence

| Name       | Operators   | Associates
|------------|-------------|------------
| Equality   | `== !=`     | Left
| Comparison | `> >= < <=` | Left
| Term       | `- +`       | Left
| Factor     | `/ *`       | Left
| Unary      | `not -`     | Right

## Grammar

```
program             → declaration* EOF ;

declaration         → variableDeclaration | statement ;
statement           → expressionStatement ;

expressionStatement → expression "\n" ;
variableDeclaration → IDENTIFIER ( "=" expression )? "\n" ;

expression          → assignment ;
assignment          → IDENTIFIER "=" assignment | logic_or ;
logic_or            → logic_and ( "or" logic_and )* ;
logic_and           → equality ( "and" equality )* ;
equality            → comparison ( ( "!=" | "==" ) comparison )*;
comparison          → term ( ( ">" | ">=" | "<" | "<=" ) term )*;
term                → factor ( ( "-" | "+" ) factor )* ;
factor              → unary ( ( "/" | "*" ) unary )* ;
unary               → ( "not" | "-" ) unary | call ;
call                → primary ( "(" arguments? ")" )* ;
arguments           → expression ( ", " expression )* ;
primary             →  "True" | "False" | "None" 
                    | NUMBER | STRING 
                    | enclosure
                    | IDENTIFIER ;
enclosure           → "(" expression ")" | "[" expression "]" | "{" expression "}";
```

