# Changelog

## 1.2.0 — 2026-09-01

- consolida `XLX-APRS-DPRS` como repositório exclusivo e independente do APRS/D-PRS;
- remove referências operacionais específicas de um refletor;
- torna módulo XLX, porta DExtra e módulo do cliente configuráveis pelo instalador;
- mantém B / 30001 / G como padrões compatíveis;
- generaliza a detecção de Digital Lab legado para impedir gateways duplicados;
- mantém o código APRS/D-PRS fora do repositório do dashboard e publica somente em `<dashboard>/aprs-dprs/`;
- atualiza gateway e interface para usar a chave genérica `dextra_module`.

## 1.1.1 — 2026-08-13

- separa o gateway APRS/D-PRS do repositório principal do XLX Modern Installer;
- mantém código, configuração, estado SQLite e serviço systemd em caminhos próprios;
- adiciona instalação, atualização, backup e remoção independentes;
- cria banco de autenticação vazio em instalações novas, sem copiar contas da produção;
- protege configuração, bancos, tokens, sessões, chaves e backups via `.gitignore` e validação;
- bloqueia coexistência acidental com um serviço Digital Lab legado ativo;
- permite integração opcional pelo XLX Modern Installer usando commit e SHA-256 fixados;
- adiciona validação automática de Bash, PHP, JavaScript, Python, manifesto e permissões executáveis.
