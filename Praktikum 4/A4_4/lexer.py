from enum import Enum, auto
from dataclasses import dataclass


class TokenType(Enum):
    # Klammern
    LPAREN = auto()
    RPAREN = auto()

    # Operatoren
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    EQ = auto()
    LT = auto()
    GT = auto()

    # Schlüsselwörter
    IF = auto()
    DO = auto()
    DEF = auto()
    DEFN = auto()
    LET = auto()
    PRINT = auto()
    STRFN = auto()
    LISTFN = auto()
    NTH = auto()
    HEAD = auto()
    TAIL = auto()

    # Literale / Identifikatoren
    BOOL = auto()
    INT = auto()
    STRING = auto()
    IDENT = auto()

    # Ende
    EOF = auto()


@dataclass
class Token:
    type: TokenType
    lexeme: str
    line: int
    column: int

    def __repr__(self):
        return f"{self.type.name}('{self.lexeme}')@{self.line}:{self.column}"


class LexerError(Exception):
    pass


class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1

    def tokenize(self):
        tokens = []
        while True:
            tok = self.next_token()
            tokens.append(tok)
            if tok.type == TokenType.EOF:
                break
        return tokens

    def next_token(self) -> Token:
        self.skip_whitespace_and_comments()

        start_line = self.line
        start_col = self.column
        c = self.peek()

        if c == "\0":
            return Token(TokenType.EOF, "<EOF>", start_line, start_col)

        # Klammern
        if c == "(":
            self.consume()
            return Token(TokenType.LPAREN, "(", start_line, start_col)
        if c == ")":
            self.consume()
            return Token(TokenType.RPAREN, ")", start_line, start_col)

        # Operatoren
        if c == "+":
            self.consume()
            return Token(TokenType.PLUS, "+", start_line, start_col)
        if c == "-":
            self.consume()
            return Token(TokenType.MINUS, "-", start_line, start_col)
        if c == "*":
            self.consume()
            return Token(TokenType.STAR, "*", start_line, start_col)
        if c == "/":
            self.consume()
            return Token(TokenType.SLASH, "/", start_line, start_col)
        if c == "=":
            self.consume()
            return Token(TokenType.EQ, "=", start_line, start_col)
        if c == "<":
            self.consume()
            return Token(TokenType.LT, "<", start_line, start_col)
        if c == ">":
            self.consume()
            return Token(TokenType.GT, ">", start_line, start_col)

        # Zahl
        if c.isdigit():
            return self.number_token(start_line, start_col)

        # String
        if c == '"':
            return self.string_token(start_line, start_col)

        # Ident, Schlüsselwort, Bool
        if self.is_ident_start(c):
            return self.ident_or_keyword(start_line, start_col)

        # Alles andere ist ein Fehler
        raise LexerError(
            f"Unerwartetes Zeichen '{c}' bei {self.line}:{self.column}"
        )

    # Hilfsfunktionen

    def skip_whitespace_and_comments(self):
        while True:
            c = self.peek()
            if c in (" ", "\t", "\r", "\n"):
                self.consume()
            elif c == ";" and self.peek_next() == ";":
                # Kommentar bis Zeilenende
                self.consume()  # erstes ';'
                self.consume()  # zweites ';'
                while self.peek() not in ("\n", "\0"):
                    self.consume()
            else:
                break

    def number_token(self, start_line, start_col) -> Token:
        buf = []
        while self.peek().isdigit():
            buf.append(self.peek())
            self.consume()
        lexeme = "".join(buf)
        return Token(TokenType.INT, lexeme, start_line, start_col)

    def string_token(self, start_line, start_col) -> Token:
        buf = []
        self.consume()  # öffnendes "

        while True:
            c = self.peek()
            if c == "\0":
                raise LexerError(
                    f'String nicht abgeschlossen, erwartet " aber Eingabe zu Ende '
                    f'(Start bei {start_line}:{start_col})'
                )
            if c == '"':
                self.consume()  # schließendes "
                break
            # einfache Variante, keine Escape-Sonderbehandlung
            buf.append(c)
            self.consume()

        lexeme = "".join(buf)
        return Token(TokenType.STRING, lexeme, start_line, start_col)

    def ident_or_keyword(self, start_line, start_col) -> Token:
        buf = []
        buf.append(self.peek())
        self.consume()
        while self.is_ident_part(self.peek()):
            buf.append(self.peek())
            self.consume()

        text = "".join(buf)

        # Schlüsselwörter und Bool
        if text == "if":
            return Token(TokenType.IF, text, start_line, start_col)
        if text == "do":
            return Token(TokenType.DO, text, start_line, start_col)
        if text == "def":
            return Token(TokenType.DEF, text, start_line, start_col)
        if text == "defn":
            return Token(TokenType.DEFN, text, start_line, start_col)
        if text == "let":
            return Token(TokenType.LET, text, start_line, start_col)
        if text == "print":
            return Token(TokenType.PRINT, text, start_line, start_col)
        if text == "str":
            return Token(TokenType.STRFN, text, start_line, start_col)
        if text == "list":
            return Token(TokenType.LISTFN, text, start_line, start_col)
        if text == "nth":
            return Token(TokenType.NTH, text, start_line, start_col)
        if text == "head":
            return Token(TokenType.HEAD, text, start_line, start_col)
        if text == "tail":
            return Token(TokenType.TAIL, text, start_line, start_col)
        if text == "true" or text == "false":
            return Token(TokenType.BOOL, text, start_line, start_col)

        # sonst Identifikator
        return Token(TokenType.IDENT, text, start_line, start_col)

    def peek(self) -> str:
        if self.pos >= len(self.text):
            return "\0"
        return self.text[self.pos]

    def peek_next(self) -> str:
        if self.pos + 1 >= len(self.text):
            return "\0"
        return self.text[self.pos + 1]

    def consume(self):
        if self.pos >= len(self.text):
            return
        c = self.text[self.pos]
        self.pos += 1
        if c == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1

    @staticmethod
    def is_ident_start(c: str) -> bool:
        return c.isalpha() or c == "_"

    @staticmethod
    def is_ident_part(c: str) -> bool:
        return c.isalnum() or c == "_"


if __name__ == "__main__":
    code = """
    (defn hello (n)
      (if (< n 10)
          (print (str "small: " n))
          (print (str "big: " n))))

    ;; Kommentar
    (hello 5)
    """

    lexer = Lexer(code)
    try:
        tokens = lexer.tokenize()
        for t in tokens:
            print(t)
    except LexerError as e:
        print("Lexer-Fehler:", e)
