#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    (ROOT / path).write_text(text, encoding="utf-8")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"expected block not found: {label}")
    return text.replace(old, new, 1)


# ---------- install.sh ----------
s = read("install.sh")
s = replace_once(
    s,
    'REFLECTOR_HOST="127.0.0.1"\nCLIENT_CALLSIGN=""',
    'REFLECTOR_HOST="127.0.0.1"\nREFLECTOR_MODULE="B"\nDEXTRA_PORT="30001"\nCLIENT_MODULE="G"\nCLIENT_CALLSIGN=""',
    "installer defaults",
)
s = replace_once(
    s,
    "  --reflector-name NOME      Ex.: XLX026\n"
    "  --reflector-host HOST      IP/host do XLXD; padrao 127.0.0.1\n"
    "  --client-callsign CALL     Indicativo do cliente DExtra",
    "  --reflector-name NOME      Ex.: XLX123\n"
    "  --reflector-host HOST      IP/host do XLXD; padrao 127.0.0.1\n"
    "  --reflector-module LETRA   Modulo XLX monitorado; padrao B\n"
    "  --dextra-port PORTA        Porta DExtra do XLXD; padrao 30001\n"
    "  --client-module LETRA      Modulo do cliente DExtra; padrao G\n"
    "  --client-callsign CALL     Indicativo do cliente DExtra",
    "installer help",
)
s = replace_once(
    s,
    '        --reflector-host) REFLECTOR_HOST="${2:-}"; shift 2 ;;\n'
    '        --client-callsign)',
    '        --reflector-host) REFLECTOR_HOST="${2:-}"; shift 2 ;;\n'
    '        --reflector-module) REFLECTOR_MODULE="${2:-}"; shift 2 ;;\n'
    '        --dextra-port) DEXTRA_PORT="${2:-}"; shift 2 ;;\n'
    '        --client-module) CLIENT_MODULE="${2:-}"; shift 2 ;;\n'
    '        --client-callsign)',
    "installer option parser",
)
legacy_old = '''# Não permite instalar o novo serviço ao lado do legado ativo: dois gateways no módulo B
# poderiam duplicar conexões/atividade APRS.
if systemctl is-active --quiet xlx026-digital-lab.service 2>/dev/null; then
    fail "Servico legado xlx026-digital-lab esta ativo. Use um procedimento de migracao dedicado; este instalador nao executa coexistencia."
fi
'''
legacy_new = '''# Não permite instalar ao lado de um Digital Lab legado ativo. A detecção é
# genérica para evitar amarrar o instalador a um refletor específico.
LEGACY_SERVICE="$(systemctl list-units --type=service --state=active --no-legend --no-pager 2>/dev/null \\
    | awk '{print $1}' \\
    | grep -Ei '(^|-)digital-lab\\.service$' \\
    | grep -v '^xlx-aprs-dprs\\.service$' \\
    | head -n1 || true)"
if [ -n "$LEGACY_SERVICE" ]; then
    fail "Servico Digital Lab legado ativo: $LEGACY_SERVICE. Use migracao controlada; coexistencia nao e permitida."
fi
'''
s = replace_once(s, legacy_old, legacy_new, "legacy service guard")
s = replace_once(
    s,
    'REFLECTOR_NAME="$(printf \'%s\' "$REFLECTOR_NAME" | tr \'[:lower:]\' \'[:upper:]\' | tr -cd \'A-Z0-9_-\')"\n'
    'CLIENT_CALLSIGN=',
    'REFLECTOR_NAME="$(printf \'%s\' "$REFLECTOR_NAME" | tr \'[:lower:]\' \'[:upper:]\' | tr -cd \'A-Z0-9_-\')"\n'
    'REFLECTOR_MODULE="$(printf \'%s\' "$REFLECTOR_MODULE" | tr \'[:lower:]\' \'[:upper:]\' | tr -cd \'A-Z\' | cut -c1)"\n'
    'CLIENT_MODULE="$(printf \'%s\' "$CLIENT_MODULE" | tr \'[:lower:]\' \'[:upper:]\' | tr -cd \'A-Z\' | cut -c1)"\n'
    'CLIENT_CALLSIGN=',
    "installer normalization",
)
s = replace_once(
    s,
    '[ -n "$REFLECTOR_NAME" ] || fail "Nome do refletor invalido."\n',
    '[ -n "$REFLECTOR_NAME" ] || fail "Nome do refletor invalido."\n'
    '[[ "$REFLECTOR_MODULE" =~ ^[A-Z]$ ]] || fail "Modulo do refletor invalido; use uma letra A-Z."\n'
    '[[ "$CLIENT_MODULE" =~ ^[A-Z]$ ]] || fail "Modulo do cliente DExtra invalido; use uma letra A-Z."\n'
    '[[ "$DEXTRA_PORT" =~ ^[0-9]+$ ]] || fail "Porta DExtra invalida."\n'
    '[ "$DEXTRA_PORT" -ge 1 ] && [ "$DEXTRA_PORT" -le 65535 ] || fail "Porta DExtra fora do intervalo 1-65535."\n',
    "installer validation",
)
s = replace_once(
    s,
    'echo "Host XLXD       : $REFLECTOR_HOST"\n'
    'echo "Cliente DExtra',
    'echo "Host XLXD       : $REFLECTOR_HOST"\n'
    'echo "Modulo XLX      : $REFLECTOR_MODULE"\n'
    'echo "Porta DExtra    : $DEXTRA_PORT"\n'
    'echo "Modulo cliente  : $CLIENT_MODULE"\n'
    'echo "Cliente DExtra',
    "installer summary",
)
s = replace_once(
    s,
    '    "$REFLECTOR_HOST" \\\n    "$CLIENT_CALLSIGN" \\\n    "$APRS_LOGIN" \\\n    "$APRS_TX" <<\'PY\'\n'
    'import json, sys\n'
    'out, name, host, client, aprs, tx = sys.argv[1:]\n'
    'tx = tx == "1"',
    '    "$REFLECTOR_HOST" \\\n    "$REFLECTOR_MODULE" \\\n    "$DEXTRA_PORT" \\\n    "$CLIENT_MODULE" \\\n    "$CLIENT_CALLSIGN" \\\n    "$APRS_LOGIN" \\\n    "$APRS_TX" <<\'PY\'\n'
    'import json, sys\n'
    'out, name, host, module, dextra_port, client_module, client, aprs, tx = sys.argv[1:]\n'
    'tx = tx == "1"\n'
    'dextra_port = int(dextra_port)',
    "installer config arguments",
)
s = replace_once(
    s,
    '        "port": 30001,\n'
    '        "module": "B",\n'
    '        "client_callsign": client,\n'
    '        "client_module": "G"',
    '        "port": dextra_port,\n'
    '        "module": module,\n'
    '        "client_callsign": client,\n'
    '        "client_module": client_module',
    "installer reflector config",
)
s = replace_once(
    s,
    '        "reflector": name,\n'
    '        "module": "B"\n'
    '    }',
    '        "reflector": name,\n'
    '        "module": module\n'
    '    }',
    "installer site module",
)
write("install.sh", s)

# ---------- gateway + web ----------
s = read("gateway/xlx_aprs_dprs.py")
s = s.replace(
    "Read-only DExtra client for XLX module B + APRS-IS command service.",
    "Read-only DExtra client for a configured XLX module + APRS-IS command service.",
)
s = replace_once(s, 'VERSION = "1.1.1"', 'VERSION = "1.2.0"', "gateway version")
s = s.replace('super().__init__(name="dextra-b")', 'super().__init__(name="dextra-module")')
s = s.replace('self.db.set_status("module_b",', 'self.db.set_status("dextra_module",')
s = s.replace('"DPRS_MODULE_B"', '"DPRS_MODULE"')
write("gateway/xlx_aprs_dprs.py", s)

for name in [
    "web/assets/digital-lab.js",
    "web/assets/digital-lab-operator.js",
    "web/digital-lab-native.php",
    "web/api/digital-lab.php",
    "web/api/digital-lab-operator.php",
]:
    s = read(name).replace("module_b", "dextra_module").replace("DPRS_MODULE_B", "DPRS_MODULE")
    write(name, s)

# ---------- generic docs/service ----------
s = read("systemd/xlx-aprs-dprs.service").replace(
    "These controls are proven on the XLX026 workload.",
    "These controls are conservative defaults for an XLX reflector workload.",
)
write("systemd/xlx-aprs-dprs.service", s)

s = read("docs/ARCHITECTURE.md").replace("XLXD módulo B", "XLXD módulo configurado")
write("docs/ARCHITECTURE.md", s)

s = read("README.md")
s = s.replace(
    "Módulo opcional APRS / D-PRS para instalações XLX com o painel moderno.",
    "Componente independente APRS / D-PRS para refletores XLX e para o XLX Modern Dashboard.",
)
s = s.replace(
    "Este repositório mantém o gateway de dados separado do core do XLXD.",
    "Este é o repositório oficial e exclusivo do componente APRS/D-PRS. Ele mantém o gateway de dados separado do core do XLXD e separado do repositório do dashboard.",
)
s = s.replace("Exemplo com leitura do módulo B, APRS-IS e TX APRS:", "Exemplo com leitura do módulo C, APRS-IS e TX APRS:")
s = replace_once(
    s,
    "  --reflector-host 127.0.0.1 \\\n  --client-callsign",
    "  --reflector-host 127.0.0.1 \\\n  --reflector-module C \\\n  --dextra-port 30001 \\\n  --client-module G \\\n  --client-callsign",
    "README non-interactive example",
)
s = s.replace(
    "O instalador aborta se detectar o serviço legado `xlx026-digital-lab.service` ativo.",
    "O instalador procura genericamente por um serviço legado `*-digital-lab.service` ativo e aborta antes de instalar.",
)
insert = """
## Parâmetros do módulo XLX

Os valores padrão continuam compatíveis com a instalação tradicional:

```text
reflector module: B
DExtra port:      30001
client module:    G
```

Eles podem ser alterados sem editar código usando `--reflector-module`, `--dextra-port` e `--client-module`.

## Integração com o XLX Modern Dashboard

O código APRS/D-PRS não deve ser copiado para o repositório do dashboard. O instalador deste repositório publica a interface em `<dashboard>/aprs-dprs/`. O dashboard apenas aponta para essa rota quando o componente estiver instalado.

"""
marker = "## Conta administrativa inicial\n"
if "## Parâmetros do módulo XLX" not in s:
    s = replace_once(s, marker, insert + marker, "README module parameters")
write("README.md", s)

old = read("CHANGELOG.md")
if old.startswith("# Changelog\n\n"):
    old = old[len("# Changelog\n\n"):]
entry = """# Changelog

## 1.2.0 — 2026-09-01

- consolida `XLX-APRS-DPRS` como repositório exclusivo e independente do APRS/D-PRS;
- remove referências operacionais específicas de um refletor;
- torna módulo XLX, porta DExtra e módulo do cliente configuráveis pelo instalador;
- mantém B / 30001 / G como padrões compatíveis;
- generaliza a detecção de Digital Lab legado para impedir gateways duplicados;
- mantém o código APRS/D-PRS fora do repositório do dashboard e publica somente em `<dashboard>/aprs-dprs/`;
- atualiza gateway e interface para usar a chave genérica `dextra_module`.

"""
write("CHANGELOG.md", entry + old)
write("VERSION", "1.2.0\n")

# Keep the generic example explicit about defaults.
p = ROOT / "config/config.example.json"
data = json.loads(p.read_text(encoding="utf-8"))
data["reflector"]["port"] = 30001
data["reflector"]["module"] = "B"
data["reflector"]["client_module"] = "G"
data["site"]["module"] = "B"
p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# Final source-level assertion before shell/CI validation.
for path in ROOT.rglob("*"):
    if not path.is_file() or ".git" in path.parts or ".github" in path.parts:
        continue
    if path.suffix.lower() not in {".py", ".php", ".js", ".css", ".sh", ".md", ".json", ".service", ".txt", ""}:
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    if re.search(r"XLX026|XRF026|xlx026\.net|Santa\s+Isabel", text, re.I):
        raise SystemExit(f"reflector-specific identity remains in {path.relative_to(ROOT)}")

print("[OK] v1.2.0 source migration prepared")
