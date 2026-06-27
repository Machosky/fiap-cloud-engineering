#!/usr/bin/env python3
"""Publica 500 pedidos na API da Fase 2 (carga para a fila SQS).

Os 500 sao deterministicos: ciclam os 10 pedidos fixos de pedidos.json
(50 vezes), com pedido_id unico PED-0001..PED-0500. Assim o numero de
objetos no S3 (500) e o faturamento por cidade (50x o dos 10) sao iguais
para todos os alunos.

Uso (a variavel API vem do passo de captura do lab):
    python3 publicar_500.py "$API"
"""
import concurrent.futures
import json
import os
import sys
import time
import urllib.request

if len(sys.argv) < 2:
    print("uso: python3 publicar_500.py <API_URL>")
    sys.exit(1)

API = sys.argv[1].rstrip("/")
DIR = os.path.dirname(os.path.abspath(__file__))
base = json.load(open(os.path.join(DIR, "pedidos.json"), encoding="utf-8"))

TOTAL = 500


def envia(i):
    # cicla os 10 pedidos fixos; pedido_id unico por indice
    pedido = dict(base[i % len(base)])
    pedido["pedido_id"] = f"PED-{i + 1:04d}"
    data = json.dumps(pedido, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        f"{API}/pedidos", data=data,
        headers={"Content-Type": "application/json"}, method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=30).read()
        return True
    except Exception:
        return False


def main():
    t0 = time.time()
    ok = 0
    # 50 conexoes simultaneas: 500 POSTs em poucos segundos
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as ex:
        for r in ex.map(envia, range(TOTAL)):
            ok += 1 if r else 0
    dur = time.time() - t0
    print(f"{ok}/{TOTAL} pedidos publicados em {dur:.0f}s")
    if ok < TOTAL:
        print(f"ATENCAO: {TOTAL - ok} falharam. Rode de novo para completar.")


if __name__ == "__main__":
    main()
