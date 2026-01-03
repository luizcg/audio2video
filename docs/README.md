# Audio2Video - Website (GitHub Pages)

Este diretório contém o website estático do projeto, hospedado no GitHub Pages.

## Como Publicar

1. Vá em **Settings** do repositório no GitHub
2. Na seção **Pages**, selecione:
   - **Source:** Deploy from a branch
   - **Branch:** `main` (ou `master`)
   - **Folder:** `/docs`
3. Clique em **Save**
4. Aguarde alguns minutos e o site estará disponível em:
   `https://SEU-USUARIO.github.io/audio-converter/`

## Estrutura

```
docs/
├── index.html          # Página inicial
├── download.html       # Página de download
├── docs.html           # Documentação
├── faq.html            # Perguntas frequentes
├── contributing.html   # Guia de contribuição
├── licenses.html       # Licenças
├── README.md           # Este arquivo
└── assets/
    ├── css/
    │   └── styles.css  # Estilos
    ├── js/
    │   └── main.js     # JavaScript
    └── img/
        ├── app-main.png    # Screenshot principal (placeholder)
        ├── app-queue.png   # Screenshot da fila (placeholder)
        └── app-logs.png    # Screenshot dos logs (placeholder)
```

## Screenshots

Adicione screenshots do aplicativo na pasta `assets/img/`:

- `app-main.png` - Tela principal do aplicativo
- `app-queue.png` - Fila de conversão com progresso
- `app-logs.png` - Painel de logs expandido

**Tamanho recomendado:** 1280x720 ou similar (16:9)

## Personalização

### Alterar Links do GitHub

Em todos os arquivos HTML, substitua `SEU-USUARIO` pelo seu nome de usuário no GitHub:

```html
<!-- Exemplo -->
<a href="https://github.com/SEU-USUARIO/audio-converter">GitHub</a>
```

### Alterar Cores

Edite as variáveis CSS em `assets/css/styles.css`:

```css
:root {
  --color-primary: #4f46e5;      /* Cor principal (botões, links) */
  --color-secondary: #10b981;    /* Cor secundária (sucesso) */
  --color-bg: #ffffff;           /* Fundo */
  --color-text: #1e293b;         /* Texto */
}
```

## Desenvolvimento Local

Para testar localmente, use um servidor HTTP simples:

```bash
# Python 3
cd docs
python -m http.server 8000

# Acesse: http://localhost:8000
```

## Tecnologias

- HTML5
- CSS3 (sem frameworks)
- JavaScript vanilla
- Sem build step necessário
