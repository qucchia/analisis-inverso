$(function () {
  $("select").select2();
});

const options = {
    "adj cal": "Adjetivo calificativo",
    "adj rel": "Adjetivo relacional",
    "adj adv": "Adjetivo adverbial",
    "adv": "Adverbio",
    "adv mente": "Adverbio en -mente",
    "adv adj": "Adverbio adjetival",
    "adv dem": "Adverbio demostrativo",
    "adv foco": "Adverbio de foco",
    "adv int": "Adverbio interrogativo",
    atr: "Atributo",
    cag: "Complemento agente (CAg)",
    cd: "Complemento directo (CD)",
    ci: "Complemento indirecto (CI)",
    clocarg: "Complemento locativo argumental (CLocArg)",
    cmedarg: "Complemento de medida argumental (CMedArg)",
    cn: "Complemento del nombre (CN)",
    cpred: "Complemento predicativo (CPred)",
    crv: "Complemento de régimen (CRV)",
    "cpred cd": "Complemento predicativo orientado al CD",
    "cpred suj": "Complemento predicativo orientado al sujeto",
    "det dem": "Determinante demostrativo",
    "det int": "Determinante interrogativo",
    "det pos": "Determinante posesivo",
    "det rel": "Determinante relativo",
    "n col": "Nombre colectivo",
    "n no cont": "Nombre no contable",
    "n prop": "Nombre propio",
    "or adv": "Oración subordinada adverbial",
    "or rel": "Oración subordinada de relativo",
    "or sust": "Oración subordinada sustantiva",
    "or sust suj": "Oración sustantiva (en función de sujeto)",
    "n pt": "Pluralia tantum",
    "pron at": "Pronombre átono",
    "pron at cd": "Pronombre átono de CD",
    "pron at ci": "Pronombre átono de CI",
    "pas per": "Pasiva perifrásitca",
    "pron int": "Pronombre interrogativo",
    "pron num": "Pronombre numeral cardinal",
    "pron rel": "Pronombre relativo",
    "ter prep": "Término de la preposición",
    "n st": "Singularia tantum",
    suj_tacito: "Sujeto tácito",
    "v asp": "Verbo aspectual",
    "v cop": "Verbo copulativo",
    "v tr": "Verbo transitivo",
    "v inac": "Verbo inacusativo",
    "v inerg": "Verbo inergativo",
    "v mod": "Verbo modal",
};

Array.prototype.forEach.call(document.getElementsByClassName("element"), (element) => {
  element.appendChild(new Option("Escoge un elemento", "_"))
  Object.entries(options).forEach(([value, text]) =>
    element.appendChild(new Option(text, value))
  )
})

const form = document.getElementById("form");
form.addEventListener("submit", (e) => {
  e.preventDefault();

  document.getElementById("score").innerText = "Cargando...";
  fetch("/api/analisis?" + new URLSearchParams(new FormData(form)).toString())
    .then((res) => res.json())
    .then((data) => {
      if (!data) {
        document.getElementById("warning").innerText = `Error`;
        document.getElementById("alert").hidden = "";
        return;
      }
        
      const total = Object.entries(data.data).filter(([a]) => a != "_");
      const notGot = total.filter(([_, got]) => !got);
      document.getElementById("score").innerText = "Puntuación: " + (total.length - notGot.length) + "/" + total.length;
        
      const iframe = document.getElementById("render");
      iframe.src = `data:text/html,` + encodeURIComponent(`
        <meta charset="utf-8">
        <style>
          * { font-family: sans-serif; }
          @media (max-width: 600px) { * { font-size: 20px; } }
        </style>
      ` + data.render);
      document.getElementById("render2").src = `data:text/html,` + encodeURIComponent(`
        <meta charset="utf-8">
        <style>
          * {
            font-family: sans-serif;
          }
        </style>
      ` + data.render2);
        
      if (notGot.length) {
        document.getElementById("warning").innerText = `No he encontrado: ` + notGot.map(([a]) => options[a]).join(", ");
        document.getElementById("alert").hidden = "";
      } else {
        document.getElementById("alert").hidden = "hidden";
      }
    })
})

document.getElementById("random").addEventListener("click", (e) => {
  e.preventDefault();
  setRandom(Date.now())
})
function setRandom(seed) {
  const options = generate(seed);
  console.log(options);
  for (let i = 0; i < 4; i++) {
    $("#element-" + (i + 1)).val(options[i]).trigger('change');
  }
}

function daily() {
  setRandom(Math.floor(Date.now() / 86400000)) 
}
document.getElementById("today").addEventListener("click", (e) => {
       e.preventDefault();
  daily();
  
})

function generate(seed) {
  const rng = new Math.seedrandom(seed);
  const rlist = (list) => {
    return list[Math.floor(rng()*list.length)]
  };
  
  const options = [];
  if (rng() > 0.5) {
    options.push(rlist([
      "or sust", "or sust suj", "or rel",
      "or adv", "adv int", "adv rel", "pron int", "pron rel", "det rel", "det int"
    ]))
  } 

  let stuff = ["adjadv", "c", "n", "pron", "v", "otro"]
  while (options.length < 4) {
    console.log(stuff);
    const i = Math.floor(rng()*stuff.length);
    const thing = stuff[i];
    stuff = stuff.slice(0,i) .concat( stuff.slice(i+1));
    switch (thing) {
      case "adjadv":
        options.push(rlist(["adj cal", "adj rel", "adj adv",
        "adv", "adv adj", "adv dem", "adv foco", "adv int", "adv mente"]));
        break;
      case "c":
        options.push(rlist(["atr", "cag", "cd", "ci", "clocarg", "cmedarg", "cn", "cpred", "cpred cd", "cpred suj", "crv", "suj_tacito"]))
        break;
      case "n":
        options.push(rlist(["n col", "n no cont", "n prop", "n pt", "n st"]));
        break;
      case "pron":
        options.push(rlist(["pron at", "pron at cd", "pron at ci", "pron num"]));
        break;
      case "v":
        options.push(rlist(["pas per", "v tr", "v inac", "v inerg", "v cop", "v mod", "v asp"]));
        break;
      default:
        options.push(rlist(["ter prep", "det dem"]));
    }
  }
  return options;
}