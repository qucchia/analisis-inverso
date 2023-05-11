from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import spacy
from spacy import displacy
from spacy.tokens import Span
import os
from os import listdir
from os.path import isfile, join

PALABRAS = {}

for f in listdir('lists'):
    if isfile(join('lists', f)):
        with open('lists/' + f, 'r') as file:
            PALABRAS[os.path.splitext(f)[0].replace("_", " ")] = file.read().split("\n") 
            file.close()

PALABRAS["adv int"] = ["dónde", "cuándo", "cómo", "cuánto"]
PALABRAS["adv rel"] = ["donde", "cuando", "como", "cuanto"]
PALABRAS["pron int"] = ["qué", "quién", "cuál"]
PALABRAS["pron rel"] = ["que", "quien", "cual"]
PALABRAS["det int"] = ["qué", "cuánto", "cuál"]
PALABRAS["det dem"] = ["este", "ese", "aquel"]
PALABRAS["det pos"] = ["mi", "tu", "su"]
PALABRAS["det rel"] = ["cuyo"]
PALABRAS["v cop"] = ["ser", "estar", "parecer"]
PALABRAS["pron at cd"] = ["lo", "la", "los", "las"]
PALABRAS["pron at ci"] = ["le", "les", "me", "te", "se", "nos", "os"]
    
nlp = spacy.load("es_core_news_md")

def analyse(sequence, el1, el2, el3, el4):
    doc = nlp(sequence)
    els = {}
    els[el1] = False
    els[el2] = False
    els[el3] = False
    els[el4] = False
    
    if "suj_tacito" in els: els["suj_tacito"] = True

    l = []
    def add_part(part, token, group=True):
        if not part in els: return
        els[part] = True
        if group:
            words = list(token.lefts) + [token] + list(token.rights)
            start = words[0].i
            if (part == "ter prep"): start += 1
            l.append(Span(doc, start, words[-1].i+1, part.upper()))
        elif (part == "pas per"):
            l.append(Span(doc, token.i, token.i+2, part.upper()))
        else:
            l.append(Span(doc, token.i, token.i+1, part.upper()))

    def is_it(type, token, condition=True):
        if token.lemma_ in PALABRAS[type] and condition:
            add_part(type, token, False)
            return True
        return False

    def cpred(token):
        add_part("cpred", token)
        if token.head.lemma_ in PALABRAS["v cpred cd"]:
            add_part("cpred cd", token)
        else:
            add_part("cpred suj", token)

    def crv(token):
        if len(doc) > token.head.i + 1 and \
                (token.head.lemma_ + " " + doc[token.head.i+1].lemma_) in PALABRAS["v cr"]:
            add_part("crv", token)      
            return True
        return False
        
    def clocarg(token):
        if token.head.lemma_ in PALABRAS["v loc"]:
            add_part("clocarg", token)      
            return True
        return False
    
    for token in doc:
        print(token.lemma_, token.pos_, token.tag_, token.dep_, token.morph)
        
        if token.dep_ == "obj" or token.dep_ == "ccomp" or token.dep_ == "xcomp":
            is_it("adv adj", token)
            if token.head.lemma_ in PALABRAS["v cop"] or \
                    token.head.lemma_ in PALABRAS["v semicop"]:
                add_part("atr", token)
            elif token.tag_ == "ADJ":
                cpred(token)
            elif token.head.lemma_ in PALABRAS["v med"]:
                add_part("cmedarg", token)
            elif not (crv(token) or clocarg(token)):
                lefts = list(token.lefts)
                if len(lefts) >= 1 and lefts[0].lemma_ == "por":
                    add_part("cag", token)
                else:
                    add_part("cd", token)
                
        if token.dep_ == "iobj":
            if token.tag_ == "ADJ":
                cpred(token)
            elif not (crv(token) or clocarg(token)):
                add_part("ci", token)

        if token.dep_ == "obl":
            if not crv(token):
                lefts = list(token.lefts)
                if len(lefts) >= 1 and lefts[0].lemma_ == "por":
                    add_part("cag", token)
                else:
                    clocarg(token)
        if token.dep_ == "cop": add_part("atr", token)
            
        if token.dep_ == "expl:pv":
            if token.text.lower() in PALABRAS["pron at cd"]:
                add_part("cd", token)
            if token.text.lower() in PALABRAS["pron at ci"]:
                add_part("ci", token)

        if token.head.tag_ == "NOUN" and token.dep_ != "case" and token.dep_ != "det":
            add_part("cn", token)

        if token.dep_ == "acl":
            add_part("or rel", token)

        if token.dep_ == "ccomp":
            add_part("or sust", token)
            
        if token.dep_ == "csubj":
            add_part("or sust suj", token)
            add_part("or sust", token)
            
        if token.dep_ == "advcl":
            children = list(token.children)
            if (len(children) and children[0].lemma_ in PALABRAS["adv int"]):
                add_part("or sust", token)
            else:
                add_part("or adv", token)
        
        if "suj_tacito" in els and token.dep_ == "nsubj":
            els["suj_tacito"] = False

        if token.tag_ == "NUM" and token.dep_ == "obj":
            add_part("pron num", token, False)
        
        if token.tag_ == "DET" or token.tag_ == "PRON":
            is_it("det rel", token)
            
        if token.tag_ == "DET":
            is_it("det dem", token)
            is_it("det int", token)
            
        if token.tag_ == "ADJ":
            print(1)
            if not is_it("adj rel", token):
                add_part("adj cal", token, False)
            is_it("adj adv", token)

        if token.tag_ == "ADP":
            add_part("ter prep", token.head)
            
        if token.tag_ == "ADV":
            add_part("adv", token, False)
            if token.lemma_.endswith("mente"):
                add_part("adv mente", token, False)
                
            is_it("adv dem", token)
            is_it("adv foc", token)
            is_it("adv rel", token)
        if token.tag_ == "ADV" or token.dep_ == "advmod":
            is_it("adv adj", token)

        if token.tag_ == "ADV" or token.tag_ == "PRON":
            is_it("adv int", token)
                
        if token.tag_ == "NOUN":
            is_it("n col", token)
            is_it("n no cont", token)
            is_it("n st", token)
            if token.lower_ in PALABRAS["n pt"]:
                add_part("n pt", token, False)
            
        if token.tag_ == "PRON":
            is_it("pron int", token)
            is_it("pron rel", token)

            if token.lower_ in PALABRAS["pron at ci"]:
                add_part("pron at ci", token, False)
                add_part("pron at", token, False)

            if token.lower_ in PALABRAS["pron at cd"]:
                add_part("pron at cd", token, False)
                add_part("pron at", token, False)
        
        if token.tag_ == "PROPN":
            if "n prop" in els:
                add_part("n prop", token, False)
                
        if token.tag_ == "VERB":
            is_it("v cop", token)
            is_it("v tr", token)
            is_it("v inac", token)
            is_it("v inerg", token)

        if token.tag_ == "VERB" or token.tag_ == "AUX":
            children = list(token.children)
            
            if len(doc) > token.i + 1 and \
                    ((doc[token.i+1].head == token and doc[token.i+1].tag_ == "VERB") or \
                    (len(doc) > token.i + 2 and \
                    doc[token.i+2].head == token and doc[token.i+2].tag_ == "VERB")):
                if (token.lemma_ == "tener"):
                    add_part("v mod", token, False)
                is_it("v mod", token)
                is_it("v asp", token)
            else:
                if (token.lemma_ == "tener"): add_part("v tr", token, False)
            
        if token.tag_ == "AUX":
            children = list(token.children)
            if len(children) and children[0].tag_ == "VERB":
                is_it("v mod", token)
                is_it("v asp", token)
            if token.lemma_ == "ser" and doc[token.i+1].morph.get("Tense") == ["Past"]:
                add_part("pas per", token, False)
            else:
                is_it("v cop", token)

    doc.spans["sc"] = l

    return {
        "render": displacy.render(doc, style="span"),
        "render2": displacy.render(doc, style="dep"),
        "data": els
    }

def serve(self):
    path = self.path
    if path == "/": path = "/index.html"
    try:
        self.send_response(200)
        extension = os.path.splitext(path)[1][1:]
        if extension == "png":
            with open('static' + path, 'rb') as f:
                content = f.read()
            self.send_header('Content-type', 'image/png')
            self.end_headers()
            self.wfile.write(content)
        else:
            with open('static' + path, 'r') as f:
                content = f.read()
            self.send_header('Content-type', 'text/' + extension)
            self.end_headers()
            self.wfile.write(bytes(content, 'utf8'))
    except:
        self.send_response(404)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write('404: File not found')

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print("OK")
        if (self.path.startswith("/api/analisis")):
            try:
                query = parse_qs(urlparse(self.path).query)
                object = analyse(query["secuencia"][0], \
                                query["1"][0], query["2"][0], query["3"][0], query["4"][0])
                
                self.send_response(200)
                self.send_header('Content-type', 'text/json')
                self.end_headers()
                self.wfile.write(bytes(json.dumps(object), 'utf8'))
            except Exception as e:
                print("ERROR", e)
                self.send_response(400)
                self.send_header('Content-type', 'text/json')
                self.end_headers()
                self.wfile.write(bytes(json.dumps(False), 'utf8'))
        else:
            serve(self)
            
httpd = HTTPServer(('', 8000), MyHandler)
print("READY")
httpd.serve_forever()

