grammar RSimple;

// =========== PARSER RULES ===========

program
    : statementList EOF
    ;

statementList
    : statement*
    ;

statement
    : assignment
    | outputStatement
    | ifStatement
    | whileStatement
    ;

assignment
    : ID assignOp expression
    ;

assignOp
    : '<-'
    | '='
    ;

outputStatement
    : 'print' '(' expressionList ')'
    ;

expressionList
    : expression (',' expression)*
    ;

ifStatement
    : 'if' '(' expression ')' statementBlock ('else' statementBlock)?
    ;

whileStatement
    : 'while' '(' expression ')' statementBlock
    ;

statementBlock
    : '{' statementList '}'
    | statement
    ;

expression
    : boolConst
    | arithmExpression (relOp arithmExpression)?
    ;

arithmExpression
    : term (('+' | '-') term)*
    ;

term
    : power (('*' | '/') power)*
    ;

power
    : factor ('^' power)?
    ;

factor
    : '-'? primary
    ;

primary
    : ID
    | INT
    | FLOAT
    | 'scan' '(' ')'
    | '(' arithmExpression ')'
    ;

relOp
    : '<' | '<=' | '>' | '>=' | '==' | '!='
    ;

boolConst
    : 'TRUE' | 'FALSE'
    ;

// =========== LEXER RULES ===========

// Keywords
IF      : 'if';
ELSE    : 'else';
WHILE   : 'while';
PRINT   : 'print';
SCAN    : 'scan';
TRUE    : 'TRUE';
FALSE   : 'FALSE';

// Identifiers and numbers
ID      : [a-zA-Z_][a-zA-Z0-9_.]*;
INT     : [0-9]+;
FLOAT   : [0-9]+ '.' [0-9]+;

// Operators (порядок важливий!)
ASSIGN  : '<-' | '=';
LE      : '<=';
GE      : '>=';
EQ      : '==';
NE      : '!=';
LT      : '<';
GT      : '>';
PLUS    : '+';
MINUS   : '-';
MULT    : '*';
DIV     : '/';
POWER   : '^';

// Delimiters
LPAREN  : '(';
RPAREN  : ')';
LBRACE  : '{';
RBRACE  : '}';
COMMA   : ',';

// Comments
COMMENT : '#' ~[\r\n]* -> skip;

// Whitespace
WS      : [ \t\r\n]+ -> skip;
