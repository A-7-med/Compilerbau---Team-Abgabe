grammar Aufgabe2;

// Parserregeln

program
    : expr* EOF
    ;

expr
    : atom
    | listExpr
    ;

atom
    : INT
    | STRING
    | BOOL
    | IDENT
    ;

listExpr
    : LPAREN form RPAREN
    ;

form
    : ifExpr
    | doExpr
    | defExpr
    | defnExpr
    | letExpr
    | appExpr
    ;

ifExpr
    : IF expr expr expr?     // (if cond then [else])
    ;

doExpr
    : DO expr+               // (do e1 e2 ...)
    ;

defExpr
    : DEF IDENT expr         // (def name value)
    ;

defnExpr
    : DEFN IDENT LPAREN paramListOpt RPAREN expr
    ;

paramListOpt
    : paramList?
    ;

paramList
    : IDENT+
    ;

letExpr
    : LET LPAREN letBindingListOpt RPAREN expr
    ;

letBindingListOpt
    : letBindingList?
    ;

letBindingList
    : IDENT expr (IDENT expr)*
    ;

appExpr
    : operator argListOpt
    ;

argListOpt
    : argList?
    ;

argList
    : expr+
    ;

operator
    : PLUS
    | MINUS
    | STAR
    | SLASH
    | EQ
    | LT
    | GT
    | PRINT
    | STRFN
    | LISTFN
    | NTH
    | HEAD
    | TAIL
    | IDENT          // benutzerdefinierte Funktionen
    ;

// Lexerregeln

LPAREN  : '(' ;
RPAREN  : ')' ;

PLUS    : '+' ;
MINUS   : '-' ;
STAR    : '*' ;
SLASH   : '/' ;
EQ      : '=' ;
LT      : '<' ;
GT      : '>' ;

// Schlüsselwörter

IF      : 'if' ;
DO      : 'do' ;
DEF     : 'def' ;
DEFN    : 'defn' ;
LET     : 'let' ;
PRINT   : 'print' ;
STRFN   : 'str' ;
LISTFN  : 'list' ;
NTH     : 'nth' ;
HEAD    : 'head' ;
TAIL    : 'tail' ;

BOOL
    : 'true'
    | 'false'
    ;

INT
    : [0-9]+
    ;

STRING
    : '"' ( ~["\\] | '\\' . )* '"'
    ;

IDENT
    : [a-zA-Z_][a-zA-Z0-9_]*
    ;

// Kommentare und Whitespace

COMMENT
    : ';;' ~[\r\n]* -> skip
    ;

WS
    : [ \t\r\n]+ -> skip
    ;
