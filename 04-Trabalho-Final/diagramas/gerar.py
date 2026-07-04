#!/usr/bin/env python3
"""TEMPLATE de gerador de diagramas .excalidraw para aulas.

Copie este arquivo para <pasta-do-lab>/diagramas/gerar.py, ajuste a paleta
(cor da marca) e escreva uma funcao por diagrama montando nos + conexoes.
Os icones (PNG) devem estar em <pasta-do-lab>/diagramas/icones/ — baixe com
o script baixar-icones.sh desta skill.

Embute icones OFICIAIS como PNG. Layout pensado para UX: espacamento generoso,
sem sobreposicao, setas conectando bordas, rotulos abaixo dos icones.

API da classe Diagrama:
  no(icone, rotulo, cx, cy, destaque=False) -> dict(bbox)   # icone + rotulo
  seta(a, b, rotulo=None)                                   # horizontal
  seta_vertical(a, b, rotulo=None, tracejada=False)         # cima->baixo
  seta_diagonal(a, b, rotulo=None)                          # alturas diferentes
  fan_out(origem, [destinos], rotulo=None)                  # 1 -> N
  titulo(texto, x, y); nota(texto, x, y, w, cor)
  salvar(caminho)

LICOES DE UX (aplicar SEMPRE; a cada reprovacao do revisor, ADICIONE uma nova
aqui e nunca repita o erro em diagrama seguinte):
- L1 Acentuacao correta nos rotulos visiveis (portugues correto).
- L2 Sem redundancia entre titulo e subtitulo.
- L3 Direcao da seta casa com o verbo (sujeito = origem da seta).
- L4/L7 Layout proximo do topo e equilibrado; sem vazio vertical grande.
- L5 Rotulo de aresta explicito ("invoca (evento)" > "evento").
- L6 Deixar explicito o nome da empresa/contexto ficticio (senao parece typo).
- L8 Fluxo secundario (observabilidade/erro) com seta TRACEJADA.
- L9 Rotulo de seta nunca encosta na seta nem em icone (dar respiro).
- L10 Caminho de erro: tracejado + (so ele) cor de alerta.
- L11 Fan-out: setas de UM ponto; rotulo unico no ponto de divisao.
- L12 Mesmo icone em papeis diferentes -> papel em DESTAQUE no rotulo.
- L13 Cor tem semantica: magenta/vermelho = alerta. Rotulo informativo = cinza.
"""
import base64
import json
import sys
import os

DIR = os.path.dirname(os.path.abspath(__file__))
ICONES = os.path.join(DIR, "icones")

# Paleta FIAP + AWS
FIAP_MAGENTA = "#ED0973"
TEXTO = "#1e1e1e"
CINZA = "#495057"
AWS_LARANJA = "#ED7100"

# Geometria base (em px) — folgas largas evitam sobreposicao
ICON = 80          # tamanho do icone
LABEL_H = 50       # altura reservada para o rotulo (ate 2 linhas)
LABEL_GAP = 12     # espaco entre icone e rotulo
COL_PITCH = 260    # distancia horizontal entre centros de nos (bem largo)
ROW_PITCH = 230    # distancia vertical entre linhas


def _seed(n):
    return 1000 + n * 7


def carrega_icone_datauri(nome):
    # Usamos PNG (rasterizado dos SVGs oficiais): imagens PNG embutidas sao
    # renderizadas de forma confiavel pelo canvas headless; SVG-em-SVG nao e.
    with open(os.path.join(ICONES, f"{nome}.png"), "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return f"data:image/png;base64,{b64}"


class Diagrama:
    def __init__(self):
        self.elements = []
        self.files = {}
        self._n = 0

    def _id(self, prefix):
        self._n += 1
        return f"{prefix}{self._n}"

    def no(self, icone, rotulo, cx, cy, destaque=False):
        """Cria um no = icone centralizado em (cx,cy) + rotulo abaixo.
        Retorna o id do elemento-icone e seu bbox para ligar setas."""
        x = cx - ICON / 2
        y = cy - ICON / 2
        file_id = self._id("file")
        self.files[file_id] = {
            "mimeType": "image/png",
            "id": file_id,
            "dataURL": carrega_icone_datauri(icone),
            "created": 1,
        }
        img_id = self._id("img")
        self.elements.append({
            "id": img_id, "type": "image", "x": x, "y": y,
            "width": ICON, "height": ICON, "angle": 0,
            "strokeColor": "transparent", "backgroundColor": "transparent",
            "fillStyle": "solid", "strokeWidth": 1, "strokeStyle": "solid",
            "roughness": 0, "opacity": 100, "groupIds": [], "frameId": None,
            "roundness": None, "seed": _seed(self._n), "version": 1,
            "versionNonce": _seed(self._n), "isDeleted": False,
            "boundElements": [], "updated": 1, "link": None, "locked": False,
            "status": "saved", "fileId": file_id, "scale": [1, 1],
        })
        # rotulo abaixo do icone, largura = COL_PITCH (centralizado), 2 linhas ok
        lbl_w = COL_PITCH - 30
        lbl_x = cx - lbl_w / 2
        lbl_y = y + ICON + LABEL_GAP
        self.elements.append({
            "id": self._id("txt"), "type": "text", "x": lbl_x, "y": lbl_y,
            "width": lbl_w, "height": LABEL_H, "angle": 0,
            "strokeColor": FIAP_MAGENTA if destaque else TEXTO,
            "backgroundColor": "transparent", "fillStyle": "solid",
            "strokeWidth": 1, "strokeStyle": "solid", "roughness": 1,
            "opacity": 100, "groupIds": [], "frameId": None, "roundness": None,
            "seed": _seed(self._n), "version": 1, "versionNonce": _seed(self._n),
            "isDeleted": False, "boundElements": [], "updated": 1, "link": None,
            "locked": False, "fontSize": 16,
            "fontFamily": 2,  # 2 = fonte normal (Helvetica), legivel
            "text": rotulo, "textAlign": "center", "verticalAlign": "top",
            "containerId": None, "originalText": rotulo, "lineHeight": 1.25,
            "baseline": 14,
        })
        return {"x": x, "y": y, "w": ICON, "h": ICON, "cx": cx, "cy": cy}

    def seta(self, a, b, rotulo=None):
        """Liga o no a -> b por uma seta da borda direita de a a borda esq de b."""
        x1 = a["x"] + a["w"]
        y1 = a["cy"]
        x2 = b["x"]
        y2 = b["cy"]
        self.elements.append({
            "id": self._id("arr"), "type": "arrow", "x": x1, "y": y1,
            "width": x2 - x1, "height": y2 - y1, "angle": 0,
            "strokeColor": CINZA, "backgroundColor": "transparent",
            "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
            "roughness": 1, "opacity": 100, "groupIds": [], "frameId": None,
            "roundness": {"type": 2}, "seed": _seed(self._n), "version": 1,
            "versionNonce": _seed(self._n), "isDeleted": False,
            "boundElements": [], "updated": 1, "link": None, "locked": False,
            "points": [[0, 0], [x2 - x1, y2 - y1]],
            "lastCommittedPoint": None, "startBinding": None, "endBinding": None,
            "startArrowhead": None, "endArrowhead": "arrow",
        })
        if rotulo:
            # rotulo da seta ACIMA do meio do caminho, sem encostar nos nos
            mx = (x1 + x2) / 2
            my = (y1 + y2) / 2
            w = COL_PITCH - ICON - 20
            self.elements.append({
                "id": self._id("etxt"), "type": "text", "x": mx - w / 2,
                "y": my - 34, "width": w, "height": 22, "angle": 0,
                "strokeColor": CINZA, "backgroundColor": "transparent",
                "fillStyle": "solid", "strokeWidth": 1, "strokeStyle": "solid",
                "roughness": 1, "opacity": 100, "groupIds": [], "frameId": None,
                "roundness": None, "seed": _seed(self._n), "version": 1,
                "versionNonce": _seed(self._n), "isDeleted": False,
                "boundElements": [], "updated": 1, "link": None, "locked": False,
                "fontSize": 13, "fontFamily": 2, "text": rotulo,
                "textAlign": "center", "verticalAlign": "middle",
                "containerId": None, "originalText": rotulo, "lineHeight": 1.25,
                "baseline": 11,
            })

    def seta_vertical(self, a, b, rotulo=None, tracejada=False):
        """Liga a (em cima) -> b (embaixo) por seta vertical, borda a borda.
        tracejada=True marca fluxo secundario (ex: observabilidade)."""
        x1 = a["cx"]
        y1 = a["y"] + a["h"]
        x2 = b["cx"]
        y2 = b["y"]
        self.elements.append({
            "id": self._id("arr"), "type": "arrow", "x": x1, "y": y1,
            "width": x2 - x1, "height": y2 - y1, "angle": 0,
            "strokeColor": CINZA, "backgroundColor": "transparent",
            "fillStyle": "solid", "strokeWidth": 2,
            "strokeStyle": "dashed" if tracejada else "solid",
            "roughness": 1, "opacity": 100, "groupIds": [], "frameId": None,
            "roundness": {"type": 2}, "seed": _seed(self._n), "version": 1,
            "versionNonce": _seed(self._n), "isDeleted": False,
            "boundElements": [], "updated": 1, "link": None, "locked": False,
            "points": [[0, 0], [x2 - x1, y2 - y1]],
            "lastCommittedPoint": None, "startBinding": None, "endBinding": None,
            "startArrowhead": None, "endArrowhead": "arrow",
        })
        if rotulo:
            my = (y1 + y2) / 2
            # rotulo A ESQUERDA da seta (evita transbordar borda direita do canvas)
            lbl_w = 150
            self.elements.append({
                "id": self._id("vtxt"), "type": "text", "x": x1 - lbl_w - 14,
                "y": my - 11, "width": lbl_w, "height": 22, "angle": 0,
                "strokeColor": CINZA, "backgroundColor": "transparent",
                "fillStyle": "solid", "strokeWidth": 1, "strokeStyle": "solid",
                "roughness": 1, "opacity": 100, "groupIds": [], "frameId": None,
                "roundness": None, "seed": _seed(self._n), "version": 1,
                "versionNonce": _seed(self._n), "isDeleted": False,
                "boundElements": [], "updated": 1, "link": None, "locked": False,
                "fontSize": 13, "fontFamily": 2, "text": rotulo,
                "textAlign": "right", "verticalAlign": "middle",
                "containerId": None, "originalText": rotulo, "lineHeight": 1.25,
                "baseline": 11,
            })

    def seta_diagonal(self, a, b, rotulo=None):
        """Seta da borda direita de a ate a borda esquerda de b, mesmo em
        alturas diferentes (ex: 1 stream -> 2 consumidores acima/abaixo)."""
        x1 = a["x"] + a["w"]
        y1 = a["cy"]
        x2 = b["x"]
        y2 = b["cy"]
        self.elements.append({
            "id": self._id("arr"), "type": "arrow", "x": x1, "y": y1,
            "width": x2 - x1, "height": y2 - y1, "angle": 0,
            "strokeColor": CINZA, "backgroundColor": "transparent",
            "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
            "roughness": 1, "opacity": 100, "groupIds": [], "frameId": None,
            "roundness": {"type": 2}, "seed": _seed(self._n), "version": 1,
            "versionNonce": _seed(self._n), "isDeleted": False,
            "boundElements": [], "updated": 1, "link": None, "locked": False,
            "points": [[0, 0], [x2 - x1, y2 - y1]],
            "lastCommittedPoint": None, "startBinding": None, "endBinding": None,
            "startArrowhead": None, "endArrowhead": "arrow",
        })
        if rotulo:
            # rotulo a ~35% do caminho (perto da origem), deslocado para nao
            # encostar no no de destino nem na outra diagonal
            mx = x1 + (x2 - x1) * 0.35
            my = y1 + (y2 - y1) * 0.35
            self.elements.append({
                "id": self._id("dtxt"), "type": "text", "x": mx - 70,
                "y": my - 26, "width": 140, "height": 22, "angle": 0,
                "strokeColor": CINZA, "backgroundColor": "transparent",
                "fillStyle": "solid", "strokeWidth": 1, "strokeStyle": "solid",
                "roughness": 1, "opacity": 100, "groupIds": [], "frameId": None,
                "roundness": None, "seed": _seed(self._n), "version": 1,
                "versionNonce": _seed(self._n), "isDeleted": False,
                "boundElements": [], "updated": 1, "link": None, "locked": False,
                "fontSize": 13, "fontFamily": 2, "text": rotulo,
                "textAlign": "center", "verticalAlign": "middle",
                "containerId": None, "originalText": rotulo, "lineHeight": 1.25,
                "baseline": 11,
            })

    def fan_out(self, origem, destinos, rotulo=None):
        """1 origem -> N destinos (L11). Todas as setas partem do MESMO ponto
        (borda direita da origem); rotulo unico colocado nesse ponto."""
        px = origem["x"] + origem["w"]
        py = origem["cy"]
        for b in destinos:
            x2 = b["x"]
            y2 = b["cy"]
            self.elements.append({
                "id": self._id("arr"), "type": "arrow", "x": px, "y": py,
                "width": x2 - px, "height": y2 - py, "angle": 0,
                "strokeColor": CINZA, "backgroundColor": "transparent",
                "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
                "roughness": 1, "opacity": 100, "groupIds": [], "frameId": None,
                "roundness": {"type": 2}, "seed": _seed(self._n), "version": 1,
                "versionNonce": _seed(self._n), "isDeleted": False,
                "boundElements": [], "updated": 1, "link": None, "locked": False,
                "points": [[0, 0], [x2 - px, y2 - py]],
                "lastCommittedPoint": None, "startBinding": None,
                "endBinding": None, "startArrowhead": None,
                "endArrowhead": "arrow",
            })
        if rotulo:
            # L13: rotulo informativo = cinza (magenta seria lido como alerta).
            # L9: respiro maior do ponto de divisao para nao colar na seta.
            self.elements.append({
                "id": self._id("fotxt"), "type": "text", "x": px + 22,
                "y": py - 42, "width": 200, "height": 22, "angle": 0,
                "strokeColor": CINZA, "backgroundColor": "transparent",
                "fillStyle": "solid", "strokeWidth": 1, "strokeStyle": "solid",
                "roughness": 1, "opacity": 100, "groupIds": [], "frameId": None,
                "roundness": None, "seed": _seed(self._n), "version": 1,
                "versionNonce": _seed(self._n), "isDeleted": False,
                "boundElements": [], "updated": 1, "link": None, "locked": False,
                "fontSize": 13, "fontFamily": 2, "text": rotulo,
                "textAlign": "left", "verticalAlign": "middle",
                "containerId": None, "originalText": rotulo, "lineHeight": 1.25,
                "baseline": 11,
            })

    def titulo(self, texto, x, y, w=900):
        self.elements.append({
            "id": self._id("title"), "type": "text", "x": x, "y": y,
            "width": w, "height": 30, "angle": 0, "strokeColor": FIAP_MAGENTA,
            "backgroundColor": "transparent", "fillStyle": "solid",
            "strokeWidth": 1, "strokeStyle": "solid", "roughness": 1,
            "opacity": 100, "groupIds": [], "frameId": None, "roundness": None,
            "seed": _seed(self._n), "version": 1, "versionNonce": _seed(self._n),
            "isDeleted": False, "boundElements": [], "updated": 1, "link": None,
            "locked": False, "fontSize": 22, "fontFamily": 2, "text": texto,
            "textAlign": "left", "verticalAlign": "top", "containerId": None,
            "originalText": texto, "lineHeight": 1.25, "baseline": 19,
        })

    def nota(self, texto, x, y, w=900, cor=CINZA):
        self.elements.append({
            "id": self._id("nota"), "type": "text", "x": x, "y": y,
            "width": w, "height": 22, "angle": 0, "strokeColor": cor,
            "backgroundColor": "transparent", "fillStyle": "solid",
            "strokeWidth": 1, "strokeStyle": "solid", "roughness": 1,
            "opacity": 100, "groupIds": [], "frameId": None, "roundness": None,
            "seed": _seed(self._n), "version": 1, "versionNonce": _seed(self._n),
            "isDeleted": False, "boundElements": [], "updated": 1, "link": None,
            "locked": False, "fontSize": 14, "fontFamily": 2, "text": texto,
            "textAlign": "left", "verticalAlign": "top", "containerId": None,
            "originalText": texto, "lineHeight": 1.25, "baseline": 12,
        })

    def salvar(self, caminho):
        doc = {
            "type": "excalidraw", "version": 2, "source": "fiap-gerador",
            "elements": self.elements,
            "appState": {"gridSize": None, "viewBackgroundColor": "#ffffff"},
            "files": self.files,
        }
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)
        print(f"gerado: {caminho} ({len(self.elements)} elementos)")




# ---------------------------------------------------------------------------
# EXEMPLO — apague e escreva os seus diagramas (uma funcao por diagrama).
# Pre-requisito: diagramas/icones/{apigateway,lambda,s3}.png  (baixar-icones.sh)
# ---------------------------------------------------------------------------

def arquitetura_final():
    d = Diagrama()
    d.titulo("PedeJa - Trabalho Final: EFS -> S3 -> Lambda (Graviton) -> API", 60, 36)
    d.nota("Empresa: PedeJa (ficticia). Estado ao concluir o trabalho. "
           "Infra provisionada por Terraform; o aluno completa o miolo das Lambdas.",
           60, 74, w=1300)

    # ---- Faixa superior: ingestao + processamento (esquerda -> direita) ----
    y1 = 250
    x0 = 170
    efs = d.no("efs", "EFS (legado)\narquivos de pedido", x0, y1)
    ec2 = d.no("ec2", "EC2\n(sessao SSM)", x0 + COL_PITCH, y1)
    s3raw = d.no("s3", "S3 - data lake\nprefixo raw/", x0 + 2 * COL_PITCH, y1)
    lproc = d.no("lambda", "Lambda PROCESSA\n(Graviton arm64)", x0 + 3 * COL_PITCH, y1, destaque=True)
    s3res = d.no("s3", "S3 - data lake\nprefixo resumo/", x0 + 4 * COL_PITCH, y1)

    d.seta(efs, ec2, "aws s3 sync")
    d.seta(ec2, s3raw, "migra p/ raw/")
    d.seta(s3raw, lproc, "le pedidos")
    d.seta(lproc, s3res, "grava faturamento")

    # ---- Faixa inferior: API servindo o resumo ----
    # A Lambda API fica EXATAMENTE sob o S3 resumo/ (coluna 4) para a seta "le
    # resumo/" subir reta na vertical, sem cruzar outros nos. A API Gateway fica
    # a uma coluna a esquerda dela (coluna 3).
    y2 = y1 + 280
    api = d.no("apigateway", "API Gateway\nGET /faturamento", x0 + 3 * COL_PITCH, y2)
    lapi = d.no("lambda", "Lambda API\n(Graviton arm64)", x0 + 4 * COL_PITCH, y2, destaque=True)

    d.seta(api, lapi, "invoca (evento)")
    # L3: sujeito = origem da seta. A seta desce do S3 resumo/ (origem) para a
    # Lambda API (destino), reta na vertical (coluna 4) -> rotulo com sujeito S3.
    d.seta_vertical(s3res, lapi, "fornece resumo/")

    d.nota("Faturamento por cidade deterministico: R$ 596,70 somando os 10 pedidos do dataset.",
           x0, y2 + 150, w=900, cor=CINZA)

    d.salvar(os.path.join(DIR, "arquitetura-final.excalidraw"))


if __name__ == "__main__":
    arquitetura_final()
