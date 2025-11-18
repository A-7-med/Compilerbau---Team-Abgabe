from dataclasses import dataclass
from typing import List, Optional

from lexer import Lexer, TokenType, Token, LexerError


# AST-Knoten
@dataclass
class Node:
    kind: str
    value: Optional[str] = None
    children: List["Node"] = None

    def __post_init__(self):
        if self.children is None:
            self.children = []

    def __repr__(self):
        return f"Node({self.kind!r}, {self.value!r}, children={self.children})"


class ParserError(Exception):
    pass


class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        # Das nächste einzulesende Token (Lookahead)
        self.lookahead: Token = self.lexer.next_token()

    # ---------------------------------------------------------------
    # Grundfunktionen zum Arbeiten auf dem Tokenstrom
    # ---------------------------------------------------------------

    def consume(self):
        """Nimmt das aktuelle Token verbraucht und lädt das nächste."""
        self.lookahead = self.lexer.next_token()

    def match(self, expected_type: TokenType) -> Token:
        """
        Prüft, ob das aktuelle Token vom erwarteten Typ ist.
        Wenn ja, wird es konsumiert. Wenn nicht, -> Fehler.
        """
        if self.lookahead.type == expected_type:
            tok = self.lookahead
            self.consume()
            return tok
        self.error(f"erwartet {expected_type.name}", self.lookahead)

    def error(self, msg: str, token: Token):
        """Gibt eine kompakte Fehlermeldung aus und beendet den Parser."""
        raise ParserError(
            f"Parserfehler: {msg}, gefunden "
            f"{token.type.name}('{token.lexeme}') an {token.line}:{token.column}"
        )

    # ---------------------------------------------------------------
    # Startregel
    # ---------------------------------------------------------------

    def parse(self) -> Node:
        """
        program : expr* EOF
        Ein Programm besteht aus einer beliebigen Anzahl von Ausdrücken.
        """
        exprs = []
        while self.lookahead.type != TokenType.EOF:
            exprs.append(self.parse_expr())

        return Node("Program", children=exprs)

    # ---------------------------------------------------------------
    # Grammatik: Ausdrücke
    # ---------------------------------------------------------------

    def parse_expr(self) -> Node:
        """
        expr : atom | listExpr
        """
        t = self.lookahead.type

        # atom
        if t in (TokenType.INT, TokenType.STRING, TokenType.BOOL, TokenType.IDENT):
            return self.parse_atom()

        # ( ... )
        if t == TokenType.LPAREN:
            return self.parse_list_expr()

        self.error("Ausdruck erwartet", self.lookahead)

    def parse_atom(self) -> Node:
        """
        atom : INT | STRING | BOOL | IDENT
        """
        tok = self.lookahead

        if tok.type == TokenType.INT:
            self.consume()
            return Node("IntLiteral", tok.lexeme)

        if tok.type == TokenType.STRING:
            self.consume()
            return Node("StringLiteral", tok.lexeme)

        if tok.type == TokenType.BOOL:
            self.consume()
            return Node("BoolLiteral", tok.lexeme)

        if tok.type == TokenType.IDENT:
            self.consume()
            return Node("Identifier", tok.lexeme)

        self.error("Atom erwartet", tok)

    def parse_list_expr(self) -> Node:
        """
        listExpr : LPAREN form RPAREN
        """
        self.match(TokenType.LPAREN)
        inside = self.parse_form()
        self.match(TokenType.RPAREN)
        return Node("ListExpr", children=[inside])

    # ---------------------------------------------------------------
    # Grammatik: spezielle Formen
    # ---------------------------------------------------------------

    def parse_form(self) -> Node:
        """
        form : ifExpr | doExpr | defExpr | defnExpr | letExpr | appExpr
        """
        t = self.lookahead.type

        if t == TokenType.IF:
            return self.parse_if_expr()
        if t == TokenType.DO:
            return self.parse_do_expr()
        if t == TokenType.DEF:
            return self.parse_def_expr()
        if t == TokenType.DEFN:
            return self.parse_defn_expr()
        if t == TokenType.LET:
            return self.parse_let_expr()

        # Sonst Funktions- oder Operatoraufruf
        return self.parse_app_expr()

    def parse_if_expr(self) -> Node:
        """
        ifExpr : IF expr expr expr?
        """
        self.match(TokenType.IF)
        cond = self.parse_expr()
        then_branch = self.parse_expr()

        # optionaler else-Zweig
        if self.lookahead.type != TokenType.RPAREN:
            else_branch = self.parse_expr()
            return Node("IfExpr", children=[cond, then_branch, else_branch])

        return Node("IfExpr", children=[cond, then_branch])

    def parse_do_expr(self) -> Node:
        """
        doExpr : DO expr+
        Liest Ausdrücke bis ')' folgt.
        """
        self.match(TokenType.DO)

        exprs = []
        if self.lookahead.type == TokenType.RPAREN:
            self.error("mindestens einen Ausdruck erwartet", self.lookahead)

        while self.lookahead.type not in (TokenType.RPAREN, TokenType.EOF):
            exprs.append(self.parse_expr())

        return Node("DoExpr", children=exprs)

    def parse_def_expr(self) -> Node:
        """
        defExpr : DEF IDENT expr
        """
        self.match(TokenType.DEF)
        name = self.match(TokenType.IDENT)
        value = self.parse_expr()
        return Node("DefExpr", value=name.lexeme, children=[value])

    def parse_defn_expr(self) -> Node:
        """
        defnExpr : DEFN IDENT LPAREN paramListOpt RPAREN expr
        """
        self.match(TokenType.DEFN)
        name = self.match(TokenType.IDENT)

        self.match(TokenType.LPAREN)
        params = []
        while self.lookahead.type == TokenType.IDENT:
            params.append(Node("Param", self.lookahead.lexeme))
            self.consume()
        self.match(TokenType.RPAREN)

        body = self.parse_expr()

        param_node = Node("ParamList", children=params)
        return Node("DefnExpr", value=name.lexeme, children=[param_node, body])

    def parse_let_expr(self) -> Node:
        """
        letExpr :
            LET LPAREN (IDENT expr)* RPAREN expr
        """
        self.match(TokenType.LET)
        self.match(TokenType.LPAREN)

        bindings = []
        while self.lookahead.type == TokenType.IDENT:
            name = self.lookahead.lexeme
            self.consume()
            value = self.parse_expr()
            bindings.append(Node("LetBinding", value=name, children=[value]))

        self.match(TokenType.RPAREN)

        body = self.parse_expr()
        return Node("LetExpr", children=[Node("LetBindings", children=bindings), body])

    # ---------------------------------------------------------------
    # Funktions- und Operatoraufrufe
    # ---------------------------------------------------------------

    def parse_app_expr(self) -> Node:
        """
        appExpr : operator expr*
        Liest Operator oder Funktionsname + beliebig viele Argumente bis ')'.
        """
        op = self.lookahead

        if op.type not in (
            TokenType.PLUS, TokenType.MINUS, TokenType.STAR, TokenType.SLASH,
            TokenType.EQ, TokenType.LT, TokenType.GT,
            TokenType.PRINT, TokenType.STRFN, TokenType.LISTFN,
            TokenType.NTH, TokenType.HEAD, TokenType.TAIL,
            TokenType.IDENT
        ):
            self.error("Operator oder Funktionsname erwartet", op)

        self.consume()

        args = []
        while self.lookahead.type not in (TokenType.RPAREN, TokenType.EOF):
            args.append(self.parse_expr())

        return Node("AppExpr", value=op.lexeme, children=args)


# ---------------------------------------------------------------
# Kurzer Testlauf
# ---------------------------------------------------------------
if __name__ == "__main__":
    code = """
    (defn hello (n)
      (if (< n 10)
          (print (str "small: " n))
          (print (str "big: " n))))
    (hello 5)
    """

    lexer = Lexer(code)
    parser = Parser(lexer)

    try:
        tree = parser.parse()
        print(tree)
    except (ParserError, LexerError) as e:
        print("Fehler:", e)
