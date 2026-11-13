---
name: edicao-video-clinica
description: "Padrão de edição de Reels/TikTok verticais (clínica de estética e outros clientes, ex.: consórcio/imóveis) (meia tela com máscara suave, B-roll, legenda palavra a palavra, transições e efeitos sonoros sofisticados). Use SEMPRE que a usuária pedir para editar, cortar, legendar, enquadrar ou finalizar um vídeo, analisar vídeos de referência, ou mexer em B-roll/meia tela/transições/efeitos sonoros. Contém as preferências aprovadas, o registro de erros corrigidos e o pipeline (scripts) que gerou a versão aprovada."
---

# Padrão de edição — Reels da clínica de estética

Este arquivo é a **memória permanente** do padrão de edição da usuária. Ele vale para todo projeto
de vídeo, não só para o primeiro. Leia inteiro antes de editar.

## 0. Regras de trabalho (como colaborar)

1. **Toda correção da usuária vira regra aqui.** Ao receber uma correção que expresse preferência
   (não um ajuste pontual daquele vídeo), registre-a na seção 5 ("Registro de aprendizados") e,
   se mudar o padrão, atualize também a seção 2 ou 3. Faça commit no mesmo turno.
2. **Na dúvida sobre o padrão, pergunte antes de executar.** Exemplos de dúvida legítima: um tipo de
   vídeo novo (ex.: depoimento de paciente, antes/depois), material que não cabe nas regras
   (B-roll horizontal, foto estática), pedido que contradiz uma regra registrada. Não pergunte o que
   já está decidido aqui.
3. Nunca entregue sem a **verificação visual** da seção 4.
4. Responda em português, de forma direta.

## 1. Material de entrada (Google Drive)

- Pastas usadas: `Vídeo cortado` (vídeo bruto já com cortes secos), `Imagens` (B-roll), `Referência`.
- O conector do Drive **não baixa** arquivos grandes (estoura). Baixe por
  `https://drive.usercontent.google.com/download?id=<ID>&export=download&confirm=t`.
- Se vier HTML de login, a pasta está privada: peça à usuária para mover o arquivo para uma pasta
  pública **ou** compartilhar como "Qualquer pessoa com o link". Explique em passos curtos.

## 2. Padrão visual aprovado

**Estilo geral:** clean, elegante, adequado a clínica. Nada de glitch, flash, shake, zoom agressivo
ou excesso de transições. Inspiração = referências da pasta `Referência`, mas mais sóbrio.

**Formato:** 1080x1920, 30 fps, H.264 CRF 18, AAC 192k, `+faststart`.

**Três modos de quadro** (alternam ao longo do vídeo, corte a cada ~2–5 s):
- `talk` — apresentadora em tela cheia (enquadramento original).
- `split` — **meia tela**: B-roll em cima (1080x960), borda inferior **com máscara em degradê
  suave** (smoothstep de 300 px; nunca linha reta). A apresentadora **desce** (`presenter_shift`,
  470 px no vídeo aprovado) para que a cabeça comece onde o degradê termina — o rosto dela nunca
  fica coberto. Calcule o shift pela posição do rosto dela (faces.py no vídeo principal).
- `full` — B-roll em tela cheia, 1,5–2,6 s.

**Gancho:** título em caixa alta, 3 linhas, Inter ExtraBold 62, branco com sombra, nos primeiros
~6 s, sobre a meia tela (na faixa do degradê). Primeiro corte por volta de 3 s, título sai ~6 s.

**Legenda:** uma palavra por vez, minúscula (exceto nomes próprios via `keep_case`),
**Montserrat ExtraBold 78** (pedido de 2026-11-11; antes era Inter ExtraBold 76). A fonte não vem
instalada: baixe de `https://cdn.jsdelivr.net/gh/JulietaUla/Montserrat@master/fonts/ttf/Montserrat-ExtraBold.ttf`
(licença OFL) e passe a pasta em `ass=...:fontsdir=`. A palavra-chave do CTA (ex.: INVESTIR) vai
em caixa alta e dourada, branca, contorno preto 4 + sombra, sem pontuação. Posição **nunca sobre rostos**:
`talk` y=1250 (peito), `split` y=1580 (peito da apresentadora deslocada), `full` y=1640 (abaixo do
queixo do B-roll). Transcrição: faster-whisper `medium`, pt, word timestamps.

**Cartão de nome** no CTA: "Dra. Nome" (ExtraBold 74) + "ESPECIALIDADE" (SemiBold 42,
espaçado), centralizado y≈1640/1724, fade 0,3 s, ~5 s.

**Zoom:** só nos B-rolls `full`, push-in lento de **3%**, ancorado no rosto. Nenhum zoom no resto.

## 3. Enquadramento de B-roll (regra mais importante — ver aprendizado #1)

Cada B-roll é analisado e enquadrado **individualmente**. Nunca aplicar a mesma posição de corte em
todos.

1. Rode `faces.py` em todos os clipes (3 amostras/s) → posição e tamanho do rosto ao longo do clipe.
2. Escolha trechos que sejam **um único plano** (sem troca de cena dentro do trecho).
3. **Decida o modo pelo tamanho do rosto:**
   - Close / rosto grande (altura do rosto > ~230 px numa fonte 576 px de largura) → **`full`**,
     no enquadramento original. Close em meia tela sempre corta testa ou queixo.
   - Plano médio (tapete vermelho, corpo inteiro, meio corpo) → **`split`**.
4. No `split`, o corte vertical é calculado por clipe (`split_crop` em build.py):
   olhos no terço superior da área limpa (0–660 px), **≥40 px de respiro acima do cabelo
   (prioridade máxima)**, queixo no máximo 60 px dentro do degradê. Escala = mínima para cobrir
   (sem zoom extra, sem esticar, sem bordas).
5. Se a cabeça já encosta no topo no **próprio clipe original**, ele **não serve para meia tela**:
   use em `full` ou descarte. Nunca cortar cabeça/testa/queixo.
6. Evite trechos com texto queimado, setas, adesivos/emojis ou marca d'água do clipe de origem.
7. B-roll vertical estreito (9:16) não permite ajuste horizontal em meia tela sem zoom — ajuste só
   no eixo vertical e diga isso à usuária se for relevante.
8. Combine o B-roll com a fala (ex.: "por trás" → bastidores de maquiagem; "identidade" → cenas de
   épocas diferentes; "continuar parecendo você" → close sorrindo).

## 4. Transições e som (aprovados)

**Transições** (todas com tempo fixo, sem alterar a sincronia com o áudio):
- Entrada `talk→split`: apresentadora desliza para baixo (easeOutCubic 0,38 s) enquanto o B-roll
  entra com **focus pull** (desfocado → nítido) + fade de alfa. Saída `split→talk`: o inverso
  (smoothstep **0,18 s** — ver aprendizado #7), emendando perfeitamente no quadro seguinte.
  **A meia tela sai quando a voz termina a frase**: o fim do trecho `split` fica no início do
  silêncio real (silencedetect -33 dB, d=0,12) + 0,06 s, nunca no início da frase seguinte.
  Não use o fim de palavra do whisper (ele estica até a próxima palavra) e não confunda pausa no
  meio da frase com fim de frase.
- `split→split`: crossfade só do painel de cima, com foco; apresentadora parada.
- `full`: dissolve com desfoque (0,30 s entrada, 0,28 s saída) sobre o vídeo da apresentadora.

**Efeitos sonoros** — sintetizados em `sfx.py` (originais, sem direitos autorais):
- Abertura: impacto grave suave (-13) + brilho/cristal (-16) com o título.
- Entradas de `full`/`split`: whoosh de ar L→R (-13/-14), pico no corte; seeds diferentes por
  evento para não repetir. `split→split`: whoosh suave (-17). Saída de `split`: whoosh curto (-22).
- Cartão de nome: brilho/cristal (-17).
- Mix: voz com `loudnorm I=-14 TP=-2`; efeitos ~16 dB abaixo da voz (média do whoosh ≈ -34 dB vs
  voz ≈ -17 dB); limiter 0,92; fade-out 0,4 s no fim. **Sem trilha** (não foi pedida).

**Verificação obrigatória antes de entregar:**
- Folha de quadros (início/meio/fim) de **cada** B-roll: nenhuma cabeça cortada, nada importante
  fora do quadro, sem bordas pretas.
- Tiras quadro a quadro de cada tipo de transição.
- Legendas não cobrem rostos; nome próprio com acento correto.
- `ebur128` ≈ -14 LUFS; `volumedetect` dos efeitos vs voz.
- Envie o vídeo com `SendUserFile` + a imagem de verificação. Avise que o arquivo é grande demais
  para subir pelo conector do Drive.

## 4b. Corte de vídeo bruto + luz + velocidade (pedido de 2026-11-10)

Quando a usuária pedir "corta o bruto, melhora a luz e acelera": entregar **só isso** (sem
legenda, B-roll, título ou efeitos, a menos que peça).
- **Cortes:** transcreva (whisper) + `silencedetect n=-38dB d=0.25`. Remova silêncios, mantendo
  0,08 s antes e 0,14 s depois da fala; **junte trechos separados por pausas < 0,35 s** (evita
  micro-pulos na imagem); descarte respirações/ruídos soltos.
- **Repetições:** quando uma fala é gravada várias vezes, fique com a **última tomada completa**.
- **Ordem:** se um item foi gravado fora de lugar (ex.: depois do CTA), mova-o para o lugar
  lógico (antes da conclusão) e **avise** a usuária na entrega.
- Sem punch-in/zoom nos cortes (regra de zoom da seção 2); pequeno fade de áudio de 12–15 ms em
  cada corte para não estalar.
- **Luz:** compare 3 correções lado a lado no rosto e meça `signalstats YAVG` do rosto. Aprovada
  em gravação contra janela clara: `hqdn3d=1.5:1.5:3:3,curves=master='0/0.01 0.15/0.23 0.4/0.55
  0.7/0.81 1/0.96',colorbalance=rm=0.03:bm=-0.03:rh=-0.01:bh=0.01,eq=saturation=1.08:contrast=1.02`
  (rosto 79→104, fundo sem estourar). Não clarear a ponto de lavar o fundo.
- **Velocidade:** `setpts=PTS/1.2` + `atempo=1.2` (voz sem efeito de esquilo).
- **Áudio:** loudnorm + ajuste de ganho e limiter até medir ≈ -14 LUFS (o loudnorm de uma
  passada ficou em -16).
- **Verificação:** transcreva o resultado para confirmar que nenhuma palavra foi cortada no início
  ou no fim de um trecho ("Compartilha" virou "Partilha" com o corte 0,15 s tarde → abrir o corte
  no fim do silêncio anterior). Envie também a imagem antes/depois.

## 4c. Vídeos de outros clientes / sem B-roll fornecido (2026-11-11)

O padrão vale para **qualquer cliente**, não só a clínica (ex.: consultor de consórcio/imóveis).
- **Nunca reaproveite B-roll de outro projeto.** Os clipes que estão na pasta `Imagens` podem ser
  de um vídeo anterior. Se o tema não bate, não use e não pergunte se pode usar.
- **Sem B-roll do tema → busque você mesmo**, antes de perguntar. Neste ambiente só o
  **Wikimedia Commons** é acessível (Pexels, Pixabay, Mixkit, Coverr etc. são bloqueados).
  Os vídeos de lá raramente servem; use **fotos**, de preferência as que vieram do Unsplash ou do
  Pexels (busque "<tema> Unsplash"). Use `scripts/commons.py` para buscar e `scripts/dl.py` para
  baixar (com retry para erro 429). Thumbs só em larguras padrão (**960/1280/1920**; 2560 falha), e
  o host é upload.wikimedia.org (thumb.wikimedia.org é bloqueado). Prefira CC0/domínio público.
  Se usar CC BY ou BY-SA, passe os créditos à usuária para colocar na legenda do post.
- Monte uma folha de candidatas, escolha **por fala do roteiro** e prefira material do Brasil
  quando houver (ex.: placa "ALUGA-SE").
- **Foto em meia tela** (`scripts/build_photo.py`): escala mínima para cobrir, ponto focal
  (`fx,fy`) no meio da área limpa, deriva lenta de 3% ancorada no foco (para não ficar parada),
  `zoom` extra por foto só quando melhora a composição (ex.: céu demais acima da placa).
  As regras de respiro e de rosto da seção 3 também valem para fotos.
- **"Meia tela somente"** = só os modos `split` + `talk`: sem B-roll em tela cheia. Se ela pedir
  "sem legenda e sem título", tire também o brilho de abertura e o cartão de nome; mantenha as
  transições, os whooshes e o impacto suave.
- **Gráficos animados originais** (`scripts/graphics.py`): quando faltar imagem boa do tema, use
  painéis 1080x960 em azul-marinho com dourado, branco e vermelho/verde, fonte Inter, conteúdo
  só na área limpa (y<640) e elementos que entram **sincronizados com a palavra** (pegue o tempo
  em `words.json`). Modelos prontos: gráfico de juros subindo, renda × parcela estourando o limite,
  lista de motivos, barras de procura/oferta/aluguel, cards financiamento × consórcio (com
  "JUROS" riscado e "SEM JUROS"), balão de comentário com a palavra do CTA. Desenhe novos no
  mesmo estilo. No `plan`, o painel entra como `gfx/g_<nome>.mp4`. Gere uma prévia estática
  antes de renderizar.
- O Wikimedia também pode bloquear os **arquivos de vídeo** (429 "Too many requests" em
  upload.wikimedia.org): em 2026-11-11 foram 30 tentativas, uma por minuto, por 30 min, e nenhuma
  passou. Não insista além disso. Peça à usuária que coloque os vídeos na pasta **"Vídeos de apoio"**
  (pode ser pelo celular, no Pexels ou Mixkit) e dê a lista de termos de busca por fala do roteiro.
  Ela prefere **vídeos** a fotos ("não quero imagem de fotos, quero vídeos").
- Mixkit até libera o host, mas devolve 429 (anti-robô). **Não tente contornar.** Pexels e
  Pixabay ficam bloqueados. Se a usuária puder, peça que ela baixe vídeos no Pexels ou Mixkit e
  salve na pasta Imagens; se não puder, use gráficos + as melhores fotos.
- **"Totalmente meia tela"** = o vídeo inteiro em `split`, do primeiro ao último quadro
  (`start_split` / `end_split` no project.json). Só trocam os painéis de cima, com crossfade e
  foco. Quando não houver vídeos reais, use as cenas animadas de `scripts/graphics2.py`
  (fundo azul com bolhas subindo, sempre em movimento; copo de leite com nível animado, caixa,
  lupa, selos, listas sincronizadas com a fala), uma cena a cada 2–7 s, sincronizada com a
  transcrição. Exemplo: `project.leite.example.json` (vídeo do Nutri Alexandre, 17 cenas).
- Confira o volume final: a voz + `volume` pode passar de -14 LUFS (chegou a -12,7). Ajuste o
  ganho do mix e meça com `ebur128`.
- Ritmo: não deixe o apresentador mais de ~10 s seguidos na meia tela. Frases de impacto
  ("isso é uma grande oportunidade", "o juro não entra no consórcio") ficam com o rosto em tela
  cheia.
- `presenter_shift` é calculado para cada apresentador: topo da cabeça ≈ 840 px na meia tela
  (foi 470 para a Dra. Cíntia e 230 para o consultor).

## 4d. Pedido com zoom in/out, pop, ding, click (2026-11-12)

Quando o pedido listar explicitamente zoom in/out e efeitos estilo CapCut (whoosh, pop, click, ding,
swipe), o build.py aceita, por segmento `talk`, um 6.º campo no `plan`: `"in"` (aproximação lenta
até `zoom_max`, padrão 1,10), `"out"` (afastamento) ou `"punch"` (aproximação rápida em ~0,23 s,
para frases de impacto), ancorado em `presenter_face` [x,y]. Cada `in`/`punch` leva um whoosh
suave. Use `sfx_extra` para `ding` (informação importante), `click` (enumeração "primeiro",
"segundo") e `pop`. `sfx_gain` ajusta os ganhos. `cta_words` deixa a palavra do CTA em caixa
alta e dourada. `title_lines` e `name_card` são opcionais (sem nome informado → sem cartão).
- O título precisa sair **antes** da saída da meia tela (`title_end` ≤ fim do split − 0,3 s), senão
  cobre o rosto do apresentador durante a transição.
- B-roll sem pessoas (tour de apartamento): zere as detecções de `faces.json` desse clipe
  (falsos positivos deslocam o corte).
- Pessoa de cabeça baixa (ex.: assinando contrato) não é detectada e o corte central encosta a
  cabeça no topo: use em `full`.

## 4e. Alinhar ao take + transições e sons v2 (2026-11-12)

- **Todo limite de segmento do `plan` fica exatamente num corte de take do vídeo principal**
  (ou dentro de um take, nunca 1–5 quadros antes/depois de um corte). Detecte os cortes antes de
  montar o plano: `signalstats` YDIF no main (corte = YDIF > ~4× a mediana) ou
  `select='gt(scene,0.06)'`. Entrada de `full`/`split` começa no corte; a saída termina no corte
  ou no meio do mesmo take. Verifique no final: YDIF do `final.mp4` sem "lascas" (dois cortes
  separados por < 5 quadros que não sejam movimento de transição).
- `zoom_through` (ex.: 0.06) no project.json: na tela cheia o apresentador avança sob o dissolve
  e o B-roll pousa de 1,08 → 1,0; na saída, o inverso. Na meia tela o painel pousa com zoom suave
  e sai com um leve avanço.
- `sfx_style: "v2"` troca os sons por: `air` (whoosh de ar com doppler e reverb, mais macio),
  `air_soft`, `air_down`, `chime` (sino FM de duas notas, para palavras-chave), `boom` (impacto
  grave na abertura), `pluck` (nota de marimba quando o painel aparece). Ganhos aprovados para
  teste: air -12, air_soft -16 (só em zoom `punch`), air_down -18 (saída de split e de full), boom
  -12, pluck -21, chime -20. Todo som sintetizado precisa de fade no fim (`_tail`): sem isso o
  sino e o impacto estalam (dá para ver no `showspectrumpic` como uma linha vertical).
- `captions: false` remove a legenda; sem `title_lines`, sem título.

## 4f. Abertura direta + sons "comuns" (2026-11-12)

- `cold_open: true` → o vídeo **já abre em meia tela** no primeiro quadro: sem deslize, sem
  focus pull e sem fade de entrada no primeiro segmento. A saída continua normal. A usuária
  pediu assim ("não precisa dessa transição, já comece com a meia tela").
- `sfx_style: "common"` → sons no estilo dos clássicos do CapCut, curtos e secos, quase sem
  reverb: `whoosh_c` (entrada de B-roll e abertura), `swipe_c` (saídas e zoom punch), `pop_c`,
  `ding_c` (sino de notificação nas palavras-chave), `click`. Ganhos usados: whoosh -9, swipe
  -14/-15, abertura -11, pop -13, ding -15 (o v2 ficou "bonito" mas pouco familiar; para esta
  usuária, **prefira o estilo common**).
- `crop_y: {"<clip>@<início>": y}` força o corte vertical (px já escalados) na meia tela quando
  a detecção falha (pessoa de costas). Confira sempre a folha de quadros: o detector errou num
  B-roll com a moça de costas para a câmera e cortou a cabeça.

## 4g. B-roll com tarja preta ou flashes de fotógrafo (2026-11-13)

- **Tarja preta embutida** (vídeo baixado do TikTok com faixa em cima/embaixo): o modo `full`
  mostra as tarjas. Detecte com `cropdetect` e gere `br/<clip>c.mp4` já cortado; rode `faces.py`
  no clipe novo e junte ao `faces.json`.
- **Flashes de tapete vermelho** (quadro branco inteiro ou faixa branca do rolling shutter):
  troque o quadro com flash pelo anterior (detector: aumento de brilho numa faixa de 40 linhas
  vs. mediana de ±3 quadros vizinhos, limiar ~45; quadro inteiro: YAVG > mediana+30). Um quadro
  repetido não aparece; flash branco aparece muito.
- Pedido "meia tela e B-roll, sem exagero, sem efeito sonoro, sem legenda, sem título, dinâmico
  mas não exagerado": `cold_open`, `captions:false`, `sfx:false`, sem `title_lines` e sem cartão;
  em ~70 s ficaram 6 meias telas (2 com `split→split`) + 4 B-rolls em tela cheia, nada de zoom
  no `talk`, apresentadora no máximo ~10 s seguidos.

## 4h. B-roll no enquadramento original, take inteiro (2026-11-13)

- Pedido "pega os melhores takes das imagens de apoio sem cortar": B-roll **só em tela cheia**,
  no enquadramento original (clipes 9:16 entram inteiros, sem corte nem zoom: `"full_zoom": 0`).
  Meia tela sempre corta metade da altura do clipe, então **não use** quando ela pedir "sem cortar".
- Cada trecho fica **dentro de um único take** do clipe de apoio: detecte as trocas com
  `select='gt(scene,0.25)'` (flashes geram falsos cortes: confira numa folha com 6 quadros por
  trecho) e escolha os takes mais bonitos (rosto de frente, nítido, sem texto, sem flash forte).
- Clipe que não é 9:16 (ex.: 3:4 depois de tirar a tarja): `fit_clips` = clipe inteiro centralizado
  sobre uma cópia desfocada e escurecida dele mesmo, sem cortar nada.
- `cold_open` também vale para `full`: o vídeo abre direto no B-roll, sem dissolve de entrada.

## 5. Registro de aprendizados (erros e correções da usuária)

| # | Data | Erro | Correção / regra permanente |
|---|------|------|-----------------------------|
| 1 | 2026-11-10 | V1 cortou todos os B-rolls de meia tela com o mesmo deslocamento vertical fixo (30%). Closes de rosto ficaram com testa/queixo cortados e assunto mal posicionado. A usuária pediu "refinamento profissional dos cortes e enquadramentos". | Enquadramento individual guiado por detecção de rosto; closes vão para tela cheia; respiro acima da cabeça é prioridade; clipe com cabeça encostada no topo não entra em meia tela; um plano por trecho; conferir início/meio/fim de cada corte. (Seção 3) |
| 2 | 2026-11-10 | Na V1, a legenda saiu no centro da tela (sobre cabelo/testa) e o B-roll de meia tela cobria o rosto da apresentadora até ela ser deslocada. | Legenda sempre no peito/abaixo do queixo, por modo; apresentadora desce na meia tela. (Seção 2) |
| 3 | 2026-11-10 | Primeira mixagem dos efeitos ficou ~23 dB abaixo da voz (inaudível no celular). | Efeitos ~16 dB abaixo da voz; medir antes de entregar. (Seção 4) |
| 4 | 2026-11-10 | Pedido inicial: "não exagera nas transições nem nos zooms, vídeo bem clean". Depois: "transições e efeitos sonoros bem sofisticados". | Sofisticado = suave e discreto (focus pull, deslize, dissolve com desfoque, whoosh de ar), nunca chamativo. Zoom máximo 3% só em `full`. |
| 5 | 2026-11-11 | Num vídeo novo (consórcio/imóveis), perguntei se ela ia mandar B-roll ou se eu usava os da pasta, citando os clipes da Millie Bobby Brown do projeto anterior. Ela respondeu irritada: "não tem nada a ver com Millie Bobby Brown" e mandou o roteiro. | B-roll precisa casar com o roteiro do vídeo atual. Material de projeto anterior nunca é opção. Sem B-roll do tema, eu mesmo busco imagens adequadas (seção 4c) e entrego, sem fazer perguntas desnecessárias. |
| 6 | 2026-11-11 | No vídeo de consórcio ela não gostou das fotos do Commons (muitas fracas: fachada gasta, sala escura, calculadora pequena) e pediu "efeitos sonoros e transições", que já existiam mas estavam discretos demais para ela perceber. | Prefira gráficos animados sincronizados com a fala às fotos fracas; use só fotos fortes (arquitetura moderna, chaves, sala clara). Efeitos mais presentes para esse estilo: whoosh -10, suave -13, saída -18, impacto -11, mais um **pop** (-19) a cada elemento gráfico que aparece. Medido: whoosh ~13 dB abaixo da voz. |
| 7 | 2026-11-11 | "Arruma os atrasos na hora que a meia tela sai": o B-roll ficava na tela até o começo da frase seguinte e saía em 0,32 s, o que dava sensação de atraso (não havia quadro congelado; conferi com YDIF). | Saída em 0,18 s, terminando no fim real da voz (detectado na forma de onda). Vale para `build.py` e `build_photo.py`. |
| 8 | 2026-11-12 | V1 do vídeo do consórcio (consultor de imóveis): limites dos segmentos 2–3 quadros fora dos cortes do vídeo cortado; as transições começavam num take e terminavam em outro ("ultrapassando outro take"). Ela também achou que havia meia tela e B-roll demais, pediu efeitos "mais bonitos" e transições mais sofisticadas, e pediu sem legenda e sem título. | Alinhar todo limite aos cortes de take (seção 4e). Em vídeo de ~40 s: ~2 meias telas + ~2 B-rolls em tela cheia, o resto com o apresentador e zooms. Sons v2 + `zoom_through`. |
| 9 | 2026-11-12 | V2 do consórcio: ela trocou o B-roll de abertura (vídeo novo na pasta), pediu para começar já em meia tela, sem transição de entrada, e pediu "efeitos sonoros mais comuns" no lugar dos sons v2 (sintéticos/etéreos). | `cold_open` + `sfx_style: common` (seção 4f). Sons familiares (whoosh, swipe, pop, ding) em vez de designs elaborados. |
| 10 | 2026-11-12 | Na V3 do consórcio, depois de testar sons v2 e common, ela pediu para tirar todos os efeitos sonoros. | `"sfx": false` no project.json = só a voz. Para esta usuária, nos próximos vídeos, pergunte se ela quer efeitos sonoros antes de colocá-los (ou entregue sem e ofereça). |

## 6. Pipeline (scripts em `scripts/`)

Dependências: `ffmpeg` (libass), `pip install faster-whisper scipy "opencv-python-headless<4.11"`.
Para baixar o modelo whisper neste ambiente: `export HF_HUB_DISABLE_XET=1`.
Trabalhe no scratchpad, nunca na raiz do repositório.

```bash
WD=<scratchpad>/edit; mkdir -p $WD/br     # main.mov + br/b1.mp4 ...
ffmpeg -i $WD/main.mov -ac 1 -ar 16000 $WD/audio.wav
HF_HUB_DISABLE_XET=1 python3 -I scripts/transcribe.py $WD/audio.wav medium $WD/words.json
python3 -I scripts/faces.py $WD/faces.json $WD/br/*.mp4      # rode de dentro de $WD (caminhos br/...)
# rosto da apresentadora (para presenter_shift): reduza o main.mov e rode faces.py nele
# escreva $WD/project.json (modelo: project.example.json = vídeo aprovado da Dra. Cíntia)
python3 -I scripts/build.py $WD            # all | none (só re-mixa/legenda) | 3,5 (re-renderiza segmentos)
```

`project.json`: `end`, `presenter_shift`, `title_lines`, `title_end`, `name_card{name,role,start,end}`,
`keep_case`, `plan` = lista `[início, fim, modo, clipe, início_no_clipe]` cobrindo o vídeo inteiro
sem buracos. Monte o `plan` a partir da transcrição (frases) + `faces.json` (seção 3).
| 11 | 2026-11-13 | V1 do vídeo Dakota Johnson: meias telas cortavam os clipes de apoio e alguns trechos misturavam pedaços de takes diferentes. Ela disse "não ficou bom, pega os melhores takes das imagens de apoio sem cortar" e confirmou: take inteiro **e** enquadramento original. | Seção 4h: B-roll em tela cheia, sem corte nem zoom, um take bom por trecho. Para esta usuária, prefira mostrar o clipe inteiro a recortar para a meia tela. |
