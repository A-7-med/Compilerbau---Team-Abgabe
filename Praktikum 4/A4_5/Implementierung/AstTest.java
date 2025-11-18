import java.util.ArrayList;
import java.util.List;

// Dieses Programm zeigt, wie ein AST aus einem einfachen Parse-Tree gebaut wird
public class AstTest {

    /* ======================== Parse-Tree-Struktur ======================== */

    // Ein ParseNode repraesentiert einen Knoten im Baum, den der Parser liefert
    // Warum: Wir brauchen diese Struktur, um spaeter daraus den AST zu bauen
    static class ParseNode {
        public final String kind;     // Art des Knotens (z. B. "IntLiteral")
        public final String value;    // Zusatzinfo (z. B. Zahl oder Name)
        public final List<ParseNode> children; // Unterknoten

        public ParseNode(String kind, String value, List<ParseNode> children) {
            this.kind = kind;
            this.value = value;
            this.children = (children != null) ? children : new ArrayList<>(); // sorgt fuer eine leere Liste
        }

        public ParseNode(String kind, String value) {
            this(kind, value, new ArrayList<>()); // erstellt Node ohne Kinder
        }

        public ParseNode(String kind) {
            this(kind, null, new ArrayList<>()); // erstellt Node ohne value
        }
    }

    /* ======================== AST-Klassen ======================== */

    // Basis fuer alle AST-Knoten
    static abstract class AstNode { }

    // Basis fuer alle Ausdruecke im AST
    static abstract class Expr extends AstNode { }

    // Ein AST fuer ein ganzes Programm
    static class Program extends AstNode {
        private final List<Expr> body;

        // Warum: Ein Programm besteht aus mehreren Ausdruecken
        public Program(List<Expr> body) {
            this.body = body;
        }

        public List<Expr> getBody() {
            return body; // WICHTIG: gibt die oberste Ebene zurueck
        }

        @Override
        public String toString() {
            return "Program" + body;
        }
    }

    // Ganzzahl im AST
    static class IntLiteral extends Expr {
        private final int value;

        public IntLiteral(int value) {
            this.value = value; // speichert Beispielzahl
        }

        @Override
        public String toString() {
            return "Int(" + value + ")";
        }
    }

    // String im AST
    static class StringLiteral extends Expr {
        private final String value;

        public StringLiteral(String value) {
            this.value = value; // speichert Text wie "abc"
        }

        @Override
        public String toString() {
            return "String(\"" + value + "\")";
        }
    }

    // Boolean im AST
    static class BoolLiteral extends Expr {
        private final boolean value;

        public BoolLiteral(boolean value) {
            this.value = value; // speichert true oder false
        }

        @Override
        public String toString() {
            return "Bool(" + value + ")";
        }
    }

    // Variable im AST
    static class Var extends Expr {
        private final String name;

        public Var(String name) {
            this.name = name; // Name der Variable wie x oder n
        }

        @Override
        public String toString() {
            return "Var(" + name + ")";
        }
    }

    // (def name value)
    static class Def extends Expr {
        private final String name;
        private final Expr value;

        public Def(String name, Expr value) {
            this.name = name; // Name der neuen Variable
            this.value = value; // Wert der gespeichert wird
        }

        @Override
        public String toString() {
            return "Def(" + name + ", " + value + ")";
        }
    }

    // (defn name (params...) body)
    static class Defn extends Expr {
        private final String name;
        private final List<String> params;
        private final Expr body;

        public Defn(String name, List<String> params, Expr body) {
            this.name = name; // Funktionsname
            this.params = params; // Liste von Parametern
            this.body = body; // Rumpf der Funktion
        }

        @Override
        public String toString() {
            return "Defn(" + name + ", params=" + params + ", body=" + body + ")";
        }
    }

    // if-Ausdruck
    static class IfExpr extends Expr {
        private final Expr cond;
        private final Expr thenBranch;
        private final Expr elseBranch;

        public IfExpr(Expr cond, Expr thenBranch, Expr elseBranch) {
            this.cond = cond; // prueft Bedingung
            this.thenBranch = thenBranch; // wenn wahr
            this.elseBranch = elseBranch; // wenn falsch (kann fehlen)
        }

        @Override
        public String toString() {
            return "If(" + cond + ", " + thenBranch + ", " + elseBranch + ")";
        }
    }

    // Bindung in einem let-Ausdruck
    static class LetBinding {
        private final String name;
        private final Expr value;

        public LetBinding(String name, Expr value) {
            this.name = name; // Bezeichner
            this.value = value; // Wert
        }

        @Override
        public String toString() {
            return name + "=" + value;
        }
    }

    // let-Ausdruck
    static class LetExpr extends Expr {
        private final List<LetBinding> bindings;
        private final Expr body;

        public LetExpr(List<LetBinding> bindings, Expr body) {
            this.bindings = bindings; // Liste von Variablenbindungen
            this.body = body; // Ausdruck, der danach ausgewertet wird
        }

        @Override
        public String toString() {
            return "Let(" + bindings + ", body=" + body + ")";
        }
    }

    // do-Ausdruck
    static class DoExpr extends Expr {
        private final List<Expr> exprs;

        public DoExpr(List<Expr> exprs) {
            this.exprs = exprs; // Reihenfolge von Ausdruecken
        }

        @Override
        public String toString() {
            return "Do" + exprs;
        }
    }

    // Funktionsaufruf
    static class Call extends Expr {
        private final String func;
        private final List<Expr> args;

        public Call(String func, List<Expr> args) {
            this.func = func; // Name der Funktion wie hello
            this.args = args; // Liste der Argumente
        }

        @Override
        public String toString() {
            return "Call(" + func + ", args=" + args + ")";
        }
    }

    /* ======================== AST-Builder ======================== */

    // Diese Klasse wandelt einen Parse-Tree in einen AST um
    // Warum: Der AST ist spaeter fuer die Auswertung einfacher
    static class AstBuilder {

        public Program buildProgram(ParseNode root) {
            if (!"Program".equals(root.kind)) { // wenn es kein echtes Programm ist
                List<Expr> single = new ArrayList<>();
                single.add(buildExpr(root)); // packt den Ausdruck als einziges Element
                return new Program(single);
            }

            List<Expr> body = new ArrayList<>();
            for (ParseNode child : root.children) { // geht alle Kinder durch
                body.add(buildExpr(child)); // baut AST fuer jeden Ausdruck
            }
            return new Program(body); // WICHTIG: liefert komplettes Programm
        }

        private Expr buildExpr(ParseNode node) {
            switch (node.kind) {

                case "IntLiteral":
                    return new IntLiteral(Integer.parseInt(node.value)); // speichert Zahl

                case "StringLiteral":
                    return new StringLiteral(node.value); // speichert Text

                case "BoolLiteral":
                    return new BoolLiteral("true".equals(node.value)); // prueft true/false

                case "Identifier":
                    return new Var(node.value); // speichert Namen

                case "ListExpr":
                    return buildExpr(node.children.get(0)); // nimmt Inhalt der Klammer

                case "DefExpr": {
                    Expr valueExpr = buildExpr(node.children.get(0)); // baut Wert
                    return new Def(node.value, valueExpr);
                }

                case "DefnExpr": {
                    ParseNode paramListNode = node.children.get(0);
                    ParseNode bodyNode = node.children.get(1);

                    List<String> params = new ArrayList<>();
                    for (ParseNode p : paramListNode.children) {
                        params.add(p.value); // speichert Parametername
                    }

                    Expr body = buildExpr(bodyNode);
                    return new Defn(node.value, params, body);
                }

                case "IfExpr": {
                    Expr cond = buildExpr(node.children.get(0)); // liest Bedingung
                    Expr thenBranch = buildExpr(node.children.get(1)); // wenn wahr
                    Expr elseBranch = null;
                    if (node.children.size() > 2) {
                        elseBranch = buildExpr(node.children.get(2)); // wenn falsch
                    }
                    return new IfExpr(cond, thenBranch, elseBranch);
                }

                case "DoExpr": {
                    List<Expr> exprs = new ArrayList<>();
                    for (ParseNode c : node.children) {
                        exprs.add(buildExpr(c)); // fuegt jeden Ausdruck hinzu
                    }
                    return new DoExpr(exprs);
                }

                case "LetExpr": {
                    ParseNode bindingsNode = node.children.get(0);
                    ParseNode bodyNode = node.children.get(1);

                    List<LetBinding> bindings = new ArrayList<>();
                    for (ParseNode b : bindingsNode.children) {
                        String name = b.value;
                        Expr value = buildExpr(b.children.get(0)); // Wert der Bindung
                        bindings.add(new LetBinding(name, value));
                    }

                    Expr body = buildExpr(bodyNode);
                    return new LetExpr(bindings, body);
                }

                case "AppExpr": {
                    String func = node.value;
                    List<Expr> args = new ArrayList<>();
                    for (ParseNode c : node.children) {
                        args.add(buildExpr(c)); // liest alle Argumente
                    }
                    return new Call(func, args);
                }

                default:
                    throw new IllegalArgumentException("Unbekannter ParseNode-Typ: " + node.kind);
            }
        }
    }

    /* ======================== Test-Main ======================== */

    // Testet den AST, indem ein kleiner Parse-Tree per Hand gebaut wird
    public static void main(String[] args) {
        ParseNode five = new ParseNode("IntLiteral", "5"); // Beispielzahl 5

        List<ParseNode> callArgs = new ArrayList<>();
        callArgs.add(five); // fuegt Argument hinzu

        ParseNode app = new ParseNode("AppExpr", "hello", callArgs); // hello-Aufruf

        List<ParseNode> listChildren = new ArrayList<>();
        listChildren.add(app);

        ParseNode listExpr = new ParseNode("ListExpr", null, listChildren); // simuliert (hello 5)

        List<ParseNode> programChildren = new ArrayList<>();
        programChildren.add(listExpr);

        ParseNode programNode = new ParseNode("Program", null, programChildren);

        AstBuilder builder = new AstBuilder();
        Program ast = builder.buildProgram(programNode); // WICHTIG: baut finalen AST

        System.out.println(ast); // zeigt den AST
    }
}
