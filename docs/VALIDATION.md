# Validação do repositório

O XLX-APRS-DPRS possui validação automática e uma rotina local equivalente para impedir que arquivos incompletos, dados de runtime ou segredos sejam tratados como release.

## Commit pinado pelo XLX Modern Installer

A integração atualmente aprovada usa:

```text
commit: 771abaa0c1ea662f33f3fa0c4a59ec712b1e4fcb
install.sh SHA-256: 0c5c26adbf9b54fe803e3cbaf2ddc17e4ba737f7c9f3b5606231b67c9a9403f9
SOURCE-MANIFEST.sha256 SHA-256: b4a0e8f1e1fec7e894cff4c61b18c5891122278ecf5f2f666e5398b361c808d4
```

O pin continua válido mesmo que documentação ou desenvolvimento posterior avancem em `main`.

## O que o CI verifica

O workflow `.github/workflows/validate.yml` executa:

1. `sha256sum -c SOURCE-MANIFEST.sha256`;
2. sintaxe de todos os scripts Bash;
3. sintaxe PHP em `web/` e `scripts/`;
4. sintaxe JavaScript em `web/assets/`;
5. compilação do gateway Python;
6. `--check-config` com `config/config.example.json`;
7. bits executáveis de instaladores, validador e gateway;
8. `scripts/validate-source.sh`;
9. rejeição de bancos, configuração real, chaves privadas e padrões conhecidos de tokens.

## Validação local equivalente

Em um clone do repositório:

```bash
set -Eeuo pipefail
sha256sum -c SOURCE-MANIFEST.sha256

while IFS= read -r -d '' f; do
  bash -n "$f"
done < <(find . -type f -name '*.sh' -print0)

while IFS= read -r -d '' f; do
  php -l "$f" >/dev/null
done < <(find web scripts -type f -name '*.php' -print0)

if command -v node >/dev/null 2>&1; then
  while IFS= read -r -d '' f; do
    node --check "$f" >/dev/null
  done < <(find web/assets -type f -name '*.js' -print0)
fi

python3 - <<'PY'
from pathlib import Path
p = Path('gateway/xlx_aprs_dprs.py')
compile(p.read_text(encoding='utf-8'), str(p), 'exec')
PY

python3 gateway/xlx_aprs_dprs.py \
  --config config/config.example.json \
  --check-config

bash scripts/validate-source.sh
```

## Dados que não fazem parte da validação pública

A validação nunca depende de copiar dados reais de uma instalação. Permanecem fora do repositório:

- `/etc/xlx-aprs-dprs/config.json` real;
- bancos SQLite reais;
- tokens de sessão;
- credenciais administrativas;
- passcodes APRS reais;
- chaves privadas;
- logs e backups.
