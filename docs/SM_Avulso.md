# SM Avulso (Doc_Lib. - Click_25) - Sequência de Manobras

Documento novo do menu **DOC_LIB. > SM_Avulso**, implementado em `main.py` na seção
"SM AVULSO - SEQUÊNCIA DE MANOBRAS", logo antes de "JANELAS DO MENU Doc_Lib. (CLICK_25)".
Segue os padrões da MO (numeração, reserva, status, GRID, referência, PDF) e reaproveita os componentes do Doc_Lib.

## Onde está cada coisa

| Assunto | Funções / classes |
|---|---|
| Regras de dados e status | `DOC_LIB_TRANSICOES_SM`, `doc_lib_calcular_status_sm`, `doc_lib_diferencas_bloqueadas_sm`, `doc_lib_pendencias_transicao_sm` |
| Banco (tabelas e triggers) | `_garantir_tabelas_doc_lib_sm` (chamada por `garantir_banco_doc_lib`) |
| Normalização e validação | `doc_lib_normalizar_sm`, `doc_lib_validar_sm`, `doc_lib_erros_geracao_sm` |
| Gravação (uma transação) | `doc_lib_salvar_sm`, `doc_lib_cancelar_sm`, `doc_lib_reservar_sm`, `doc_lib_registrar_geracao_sm` |
| Sequência 1A/1B/2A e inversão | `doc_lib_identificar_sequencias_sm`, `doc_lib_inverter_acao_sm`, `doc_lib_inverter_manobras_sm` |
| SM-Referência | `doc_lib_dados_referencia_sm` e o botão em `JanelaSMAvulso.referencia` |
| PDF | `PDFSM`, `doc_lib_gerar_pdf_sm`, `doc_lib_registrar_e_arquivar_sm` |
| Ordem dos horários das manobras | `doc_lib_conflitos_horarios_sm` (chamada por `doc_lib_validar_sm`) |
| Antecedência da liberação (3 h) | `DOC_LIB_ANTECEDENCIA_MAXIMA_LIBERACAO_SM`, `doc_lib_inicio_vigente_sm` (usadas por `doc_lib_validar_sm`) |
| Prorrogar | `doc_lib_prefixo_vigente_sm`, `doc_lib_validar_prorrogacao_sm`, `doc_lib_dados_prorrogacao_sm`, `doc_lib_prorrogar_sm`, `DialogoProrrogarSM`, `JanelaSMAvulso.prorrogar` / `_aplicar_periodos` / `_atualizar_prorrogar` |
| Encaminhar SM por e-mail | `doc_lib_listar_contatos_sm`, `doc_lib_incluir_contato_sm`, `doc_lib_salvar_padroes_contatos_sm`, `doc_lib_enderecos_envio_sm`, `doc_lib_validar_envio_sm`, `doc_lib_pdf_para_envio_sm`, `doc_lib_registrar_envio_sm`, `doc_lib_definir_email_enviado_sm`, `DialogoEncaminharSM`, `JanelaSMAvulso.encaminhar` |
| Telas | `JanelaSMAvulso`, `LinhasManobrasSM`, `LinhasConferenciaSM`, `JanelaListaSM` (GRID SM) |

Alterações em código **compartilhado** (todas aditivas; o comportamento de ATEIE, AI e MO não muda):
1. `_doc_lib_ultimo_numero`: ramo `tipo == "SM"` (numeração própria, como a MO);
2. `garantir_banco_doc_lib`: chama `_garantir_tabelas_doc_lib_sm`;
3. `cmd_click25_sm_avulso` deixou de ser "Página em Construção".

O envio usa, sem alteração, `doc_lib_enviar_email`, `EMAIL_ATEIE_REMETENTES`, `config_email_ateie.json` e
`doc_lib_copiar_para_downloads` (os mesmos do ATEIE, do AI e da MO).

## Status e transições

`Reservado` -> `Em análise` -> `Aguarda Conferência` -> `Aprovado para Execução` -> `Em Execução` -> `Concluído`.
`Cancelado` vale de qualquer status, **menos Concluído**. Concluído e Cancelado não têm saída.
O e-mail da SM sai no status **Aguarda Conferência** (ver "Encaminhar SM por e-mail" abaixo); o envio não muda o status.

| Passagem | O que a provoca |
|---|---|
| (nova) -> Em análise | primeiro Salvar (consome o número) |
| Reservado -> Em análise | preencher e salvar a SM reservada (mantém o número) |
| Em análise -> Aguarda Conferência | botão **Gerar SM Avulso** (documento emitido; dados gerais protegidos) |
| Aguarda -> Aprovado | salvar ao menos **uma Conferência Manutenção E uma Conferência Operação** válidas |
| Aprovado -> Em Execução | salvar os Executantes da Liberação, com **todas** as manobras de liberação datadas (a partir daí os itens 6 e 7 ficam bloqueados) |
| Em Execução -> Concluído | salvar os Executantes da Normalização, com **todas** as manobras de normalização datadas |

O que cada status deixa alterar (`_DOC_LIB_GRUPOS_EDITAVEIS_SM`, vale na tela e no `doc_lib_salvar_sm`):
Em análise = edição geral; Aguarda = reprogramações e conferências; Aprovado = reprogramações, data/hora e executantes da
liberação (itens 6 e 7); Em Execução = nova reprogramação, **Prorrogar**, data/hora e executantes da normalização (itens 8 e 9). Os itens 6 e 7
**ficam inativos para qualquer lançamento depois de salvos** (a SM passa a Em Execução ao salvar os executantes); Concluído/Cancelado = nada.

## Decisões sobre pontos ambíguos do enunciado

1. **Repositório**: o `Completo` da sessão não tem AI nem MO; a SM foi feita no `Cod_completo` (que tem os três), em branch própria.
2. **Reserva do número**: igual à MO. A janela mostra o número **previsto**; ele é consumido (reservado e gravado) na transação
   de salvamento, com `BEGIN IMMEDIATE` e contador por tipo e ano em `doclib_numeracao`. O botão **SM-Reservado** grava números
   com status Reservado. Reservar ao abrir a janela queimaria um número a cada janela fechada sem salvar.
3. **"Em Análise"** usa a grafia do projeto (`Em análise`), para ter a mesma cor e o mesmo filtro dos outros documentos.
4. **Aprovação**: só a Conferência Manutenção não aprova, só a Conferência Operação não aprova (13.1); "impedir que conferências pelo
   sistema aprovem a SM" (item 18) foi lido como "sozinhas". Os botões e as modalidades do item 12 se chamam **Manutenção** (antes
   "Manual") e **Operação** (antes "Pelo Sistema"). No banco a coluna continua guardando `manual` e `sistema` (com `CHECK`), e a tela e o
   PDF mostram os nomes novos (`DOC_LIB_MODALIDADES_SM`). A Conferência Operação grava o nome completo e o login do usuário
   autenticado no `doc_lib_salvar_sm`, mesmo que os dados recebidos tragam outros.
   Não se exige que o conferente seja outra pessoa que o elaborador (regra não pedida; fica como sugestão).
5. **Executantes antes da aprovação** (ponto de atenção 13.2): não são aceitos. Os da Liberação só com a SM Aprovada para Execução e
   os da Normalização só Em Execução; assim a SM nunca pula de estado e não conclui com a execução pela metade.
6. **Cancelamento**: o enunciado manda permitir em qualquer status menos Concluído (a MO só cancela antes da execução). Foi seguido o
   enunciado; em **Em Execução** a janela avisa que cancelar não normaliza o equipamento. Justificativa obrigatória; número nunca reaproveitado.
7. **Reprogramações** são o único grupo de período editável depois de gerado o documento (até Concluído/Cancelado): prazo pode mudar
   até o fim. A programação original fica protegida. Cada reprogramação só é habilitada na ordem 1, 2, 3; a habilitação é gravada.
   Com a SM **Em Execução**, uma reprogramação já salva também fica protegida (só o botão Prorrogar muda o término dela); preencher uma
   reprogramação nova, ainda vazia, continua possível (ver item 19).
8. **Data e hora das manobras**: podem ser **corrigidas, não apagadas**; cada alteração vai para `doclib_sm_historico` (usuário e
   momento). A ordem segue o **número arábico da Sequência**, e a **letra não conta** (valem as duas tabelas, Liberação e
   Normalização):
   - número arábico maior não pode ter data e hora anteriores às de número menor: 2A não pode ser anterior a 1A, nem a 1B ou 1C
     (entende-se que 1A, 1B e 1C formam a etapa 1, que precisa terminar antes de a etapa 2 começar); o mesmo instante é aceito;
     a regra vale também quando falta um número no meio (3A não pode ser anterior a 1A, mesmo sem a etapa 2) e independe da
     posição das linhas na tabela;
   - com o mesmo número arábico o lançamento é livre: 2C pode ser anterior a 2A;
   - linha sem número válido ou sem data e hora não entra na comparação;
   - a mensagem aponta a linha em conflito (por exemplo "linha 3 (sequência 2A)") e a sequência de referência (a mais tardia entre as
     de número menor), e as caixas de data e hora da linha ficam em vermelho.
   A normalização continua sem poder ser anterior à última manobra de liberação. Os itens 6 e 7 só aceitam
   lançamento com a SM em Aprovado para Execução; ao salvar os executantes da liberação a SM vira Em Execução e eles ficam
   desabilitados na tela e recusados no banco. A correção de um horário já lançado na liberação, portanto, não é mais possível
   pelo sistema depois disso. O item 8 (normalização) continua corrigível até a SM ser Concluída.
9. **3.6 Tempo Retorno à Operação**, como no AI: duas opções, **Indisponível** ou **Tempo de Retorno** em `hh:mm`. O campo do tempo só
   é digitável com a opção do tempo escolhida (clicar nele a escolhe) e é limpo e travado com Indisponível. O tempo vai de 00:00
   a 23:59 e é normalizado ao sair do campo (`2:30`, `0230` e `2h30` viram `02:30`). Isto **substitui** a decisão da primeira
   entrega (duração com horas até 99): a regra agora é a mesma do AI. No banco e no PDF fica o texto `Indisponível` ou o `HH:MM`.
10. **Equipamento(s) a impedir**: a 1ª linha é obrigatória; a 2ª e a 3ª são opcionais, mas só por inteiro.
    - **3.1 Local, 3.2 Instalação e 3.3 Equipamento**: texto livre sempre em **caixa alta** (convertido ao digitar, ao salvar, ao
      carregar e ao imprimir; espaços repetidos são reduzidos).
    - **3.4 Caracterização**: lista de seleção com as **44 opções** informadas (`DOC_LIB_CARACTERIZACOES_SM`): 2 sem desligamento,
      21 "Com desligamento ..." e 21 "Com risco desligamento ...". Escolheu-se uma lista única, e não o seletor combinado,
      porque a relação já traz todas as combinações. A lista é somente de escolha (não aceita texto livre) e o banco recusa texto fora dela.
    - **3.5 Local da Execução dos Serviços**: lista de seleção com as **30 opções** informadas (`DOC_LIB_LOCAIS_EXECUCAO_SM`), também sem texto livre.
    - Os textos das listas foram mantidos **exatamente** como recebidos, inclusive "Com risco desligamento ..." sem "do/da" no início e a
      ausência de "UG-3 e 4" nos grupos de duas unidades. Se forem ajustados, basta editar as duas constantes.
    - SM antiga com texto livre em 3.4/3.5 (anterior a esta alteração) abre normalmente para consulta, mas exige escolher a opção
      da lista ao editar uma SM Em análise.
11. **Condições de segurança**: os cinco campos nascem em branco e são obrigatórios (escrever "Nenhuma" se não houver). O `CHECK` do
    banco recusa qualquer SM (fora Reservado e Cancelado) com uma delas vazia.
12. **Motivo**: no máximo 6 linhas **medidas como no PDF** (cerca de 600 caracteres); Condições (3 linhas) e Observações (6) têm só
    capacidade visual com rolagem, e o PDF imprime tudo, quebrando de página se preciso.
13. **Manobras**: número arábico 1-99, Local obrigatório de até 6 caracteres **em caixa alta** (itens 6 e 8), Ação obrigatória, pelo
    menos uma linha em cada tabela; linhas totalmente vazias são descartadas ao salvar. A letra é calculada pela ordem (1A, 1B, 2A;
    passa de Z para AA..AD).
14. **Inverter Manobras**: só inverte a ação em que o **único** verbo conhecido é a **primeira palavra**, sem outro verbo no
    infinitivo e sem negação, condição, verificação ou estado já descrito. Pares: abrir/fechar, bloquear/desbloquear, ligar/desligar,
    energizar/desenergizar, extrair/inserir, conectar/desconectar, habilitar/desabilitar, ativar/desativar, aterrar/desaterrar,
    travar/destravar. Nas demais, o original é mantido e a linha fica marcada (alerta laranja); **Gerar SM Avulso** só é aceito
    depois de conferir ou editar cada uma. Pede confirmação antes de substituir uma normalização já preenchida.
15. **Encaminhar SM por e-mail** (a primeira entrega não tinha e-mail; agora o envio é para conferência, com destinatários internos):
    - **Quando**: botão **Encaminhar SM** no rodapé da janela da SM, ativo só com a SM salva, sem alterações pendentes, emitida e no
      status **Aguarda Conferência** (`doc_lib_validar_envio_sm` recusa qualquer outro status). O envio não muda o status nem a
      revisão do documento.
    - **Remetente, método de envio e cópia na pasta Downloads**: os mesmos do ATEIE, do AI e da MO (remetentes
      `EMAIL_ATEIE_REMETENTES`, SMTP ou Outlook pelo `config_email_ateie.json`). O remetente escolhido por último vem sugerido.
    - **Destinatários**: não são por empresa. Há uma **lista única de e-mails da SM** (tabela `doclib_sm_contatos`, com nome opcional) e,
      para cada contato, as caixas **Para** e **Cc** (um contato não fica nos dois). Para o e-mail que não está na lista há o campo
      **Novo e-mail** (e nome opcional), com a opção Para ou Cc e o botão **Adicionar à lista**: o e-mail é gravado na lista (passa a
      aparecer nos próximos envios) e já vem marcado. Se o usuário digitar um e-mail e clicar direto em **Confirmar envio**, ele é
      incluído na lista e usado. E-mail repetido (sem diferenciar maiúsculas) não duplica; e-mail inválido é recusado. Cada contato tem
      o botão **Excluir** (com confirmação; os envios já registrados não mudam). A **última escolha de Para e Cc** fica gravada e vem
      marcada no envio seguinte. A lista inicial, criada junto com a tabela, tem só `nmaganha@alupar.com.br` e `jbarros@alupar.com.br`
      (endereços já citados no projeto): `DOC_LIB_CONTATOS_INICIAIS_SM`; o restante é cadastrado na própria janela de envio.
    - **Anexo**: o PDF da SM como está, **com** o aviso vermelho "Aguardando a Conferência do documento" (quem recebe é quem vai
      conferir). É arquivado em `SM/Enviados/<ano>` (tipo `envio` em `doclib_sm_pdfs`) e reaproveitado enquanto a revisão não muda; uma
      reprogramação ou conferência nova gera outro PDF.
    - **Assunto e texto**: constantes `EMAIL_SM_ASSUNTO` e `EMAIL_SM_TEXTO`. O assunto segue o padrão de teste dos demais documentos
      ("TESTE DE ENVIO DE E-MAIL - SM - Para Conferência"); troque a constante quando o texto definitivo for escolhido.
    - **Reenvio**: diferente de ATEIE, AI e MO, uma SM já encaminhada **pode** ser encaminhada de novo (por exemplo, esqueceram alguém ou
      houve reprogramação). Antes, uma pergunta mostra os envios anteriores (data, usuário, Para e Cc). Todos os envios ficam em
      `doclib_sm_emails`, que o banco não deixa alterar nem excluir.
    - **GRID SM**: coluna **Enviado e-mail** ("Não" ou "Sim, em dd/mm/aaaa" do envio mais recente) e botão **Marcar e-mail enviado**,
      para o caso de o envio automático falhar e o e-mail ser mandado à mão. Nesta marcação manual vale a regra dos demais documentos
      (SM com "Sim" não é marcada de novo; "Voltar para Não" corrige) e só vale para SM em Aguarda Conferência, Aprovado para Execução ou
      Em Execução. SM Concluída ou Cancelada não muda mais.
    - **Falhas**: se o e-mail não sair, a mensagem mostra o motivo e o arquivo para envio manual e nada é registrado; se o e-mail sair
      mas o registro no banco falhar, o aviso manda marcar no GRID. Se a SM mudar enquanto a janela de envio está aberta, o e-mail não é
      enviado.
16. **Permissões**: o Doc_Lib não distingue perfis (só exige usuário autenticado). Vale a mesma regra, e toda operação grava o usuário
    e o momento (`criado_*`, `atualizado_*`, `emitido_*`, `cancelada_*`, histórico).
17. **Frase solta no fim do pedido de alteração**: o texto "Tempo de Retorno à operação: ao invés de texto livre, colocar uma lista para
    selecionar o local de execução dos serviços" não trouxe lista e repete o pedido do 3.5. Foi lido como sobra de colagem; o 3.6 seguiu a
    instrução específica (igual ao AI). Se a intenção era outra, informar.
18. **PDF**: fiel ao formulário (12 itens, número no alto à direita, rodapé com página e número). O aviso vermelho
    "Aguardando a Conferência do documento" fica no cabeçalho enquanto a SM aguarda; o primeiro PDF gerado já o traz.
19. **Prorrogar** (SM em andamento): botão no quadro do **período em vigor** (a última reprogramação habilitada ou, se não houver, a
    Programação), no lugar do Habilitar: ao habilitar a Reprogramação-1, o Prorrogar sai do quadro 2.1 e passa para o 2.2, e assim por
    diante; o Habilitar segue para o quadro seguinte. O botão aparece sempre e só fica ativo quando:
    - a SM está **Em Execução** (liberação feita e executantes registrados; antes disso o instrumento é a Reprogramação);
    - não há alterações pendentes na janela (salvar antes, como em Gerar e Cancelar);
    - o período em vigor está preenchido e salvo (uma reprogramação habilitada e ainda vazia aponta o Prorrogar para o quadro dela,
      onde ele fica desativado até ela ser preenchida e salva).
    Ao clicar abre a janela **Prorrogar SM** com o período em vigor, o término atual, o número da prorrogação (P1, P2...) e os campos
    de data (com calendário) e hora do **novo término**, que **substitui** o término do período e passa a ser a data e hora válidas para
    o fim da atividade. Regras:
    - o novo término precisa ser **posterior** ao atual (igual ou anterior é recusado; para antecipar, use uma nova Reprogramação);
    - não há limite de prorrogações: P1, P2, P3, P4... A contagem é **por período**: a Programação prorrogada duas vezes mostra P2, e a
      Reprogramação-1, quando entra em vigor, começa de novo em P1 (cada término impresso leva o seu P);
    - **impresso**: ao lado do término prorrogado aparece o termo (P1, P2...) em fonte menor (6,5 pt, contra 9 pt da data e da hora);
      na tela o mesmo termo aparece ao lado da hora do término. Período sem prorrogação não mostra nada;
    - cada prorrogação fica em `doclib_sm_prorrogacoes` (período, número, término anterior, novo término, usuário e momento; o banco
      não deixa alterar nem excluir) e no histórico da SM, a revisão do documento avança e o status não muda. Gere o documento de
      novo para o PDF mostrar a prorrogação;
    - com a SM Em Execução o período **já salvo** não é mais editado direto (nem a Programação, que já era protegida, nem uma
      reprogramação salva): o término só muda pelo Prorrogar. Antes da execução (Aguarda, Aprovado) as reprogramações continuam
      editáveis como antes. O GRID SM mostra o término vigente.
20. **Antecedência das manobras de liberação**: a data e hora de cada manobra de liberação não pode ser **anterior a 3 horas do início
    programado**. O "programado" é o início do período em vigor (se houve reprogramação preenchida, vale o início dela). Exemplo: programado
    para 10/10/2026 14:00, a primeira manobra pode ser lançada a partir de 10/10/2026 11:00 (exatamente 3 horas antes é aceito; 10:59
    é recusado). A regra atravessa a meia-noite. Detalhes:
    - vale enquanto a liberação pode ser lançada (SM **Aprovada para Execução**). Depois de registrada a liberação ela fica bloqueada e
      não é conferida de novo: uma reprogramação posterior não invalida manobras já executadas;
    - se uma reprogramação for salva com a liberação já lançada em Aprovado e as manobras ficarem a mais de 3 horas do novo início, a
      gravação é recusada até as datas serem corrigidas **na mesma gravação**;
    - não há limite do outro lado (manobra depois do início) nem regra equivalente para a normalização;
    - a mensagem aponta a linha ("linha 1 (sequência 1A)"), o início programado e o primeiro horário permitido, e as caixas de data e
      hora ficam em vermelho. A dica do item 6 informa a regra.

## Banco de dados

Tabelas novas, criadas por `garantir_banco_doc_lib` sem tocar nos dados existentes: `doclib_sm`, `doclib_sm_equipamentos`,
`doclib_sm_manobras`, `doclib_sm_conferencias`, `doclib_sm_historico`, `doclib_sm_transicoes`, `doclib_sm_pdfs`,
`doclib_sm_prorrogacoes`, `doclib_sm_contatos` e `doclib_sm_emails`.

Proteções no banco (valem mesmo para quem alterar o `dados_turno.db` direto): `UNIQUE(numero)` e `UNIQUE(ano, sequencia)`;
`CHECK` do status, das condições, de 1 a 30 manobras, do Local (6 caracteres) e da modalidade; triggers que recusam transição de
status fora de `doclib_sm_transicoes`, qualquer alteração em SM concluída ou cancelada, mudança do número, exclusão da SM e
alteração ou exclusão de conferência registrada, e que gravam o histórico de status. Toda gravação é uma transação
(`BEGIN IMMEDIATE`) com conferência de revisão (`DocLibConflito` se outra pessoa salvou antes).

## Testes automatizados

Não havia testes no repositório; foi criada a pasta `tests/` (pytest). O sistema é carregado sem o `mainloop`, em pasta temporária
com banco próprio (o `dados_turno.db` real nunca é usado).

```
pip install pytest pymupdf          # além das bibliotecas do projeto (tkcalendar, fpdf2, pandas, matplotlib, requests...)
python -m pytest tests              # Windows
xvfb-run -a python -m pytest tests  # Linux sem tela (o conftest também inicia o Xvfb sozinho, se existir)
```

| Arquivo | O que cobre |
|---|---|
| `test_sm_avulso_dados.py` | numeração, reserva, reinício anual, criação simultânea (threads), programação/reprogramações, campos obrigatórios, listas 3.4/3.5, caixa alta, Indisponível/hh:mm, manobras, bloqueio dos itens 6 e 7, inversão, status, conferência, cancelamento, triggers, SM-Referência, listagem |
| `test_sm_avulso_concorrencia.py` | 4 processos separados salvando e reservando ao mesmo tempo no mesmo banco |
| `test_sm_avulso_interface.py` | janela real (Tk): número no alto à direita, padrões, listas de seleção, opção Indisponível/hh:mm, caixa alta ao digitar, reprogramações em ordem, tabelas de manobras, bloqueio dos itens 6 e 7, rótulos Manutenção/Operação, validações, fluxo completo até Concluído, inversão, referência, reserva, GRID, menu |
| `test_sm_avulso_email.py` | lista de contatos (incluir, repetido, inválido, ordem, última escolha), regras de status do envio, PDF para envio (arquivo, aviso, reaproveitamento, revisão), registro dos envios e imutabilidade, banco antigo, marcação manual no GRID, janela de envio (Para/Cc, novo e-mail, excluir, confirmar), botão da janela da SM, fluxo de envio com falha, reenvio e SM alterada durante o envio |
| `test_sm_avulso_prorrogacao.py` | Prorrogar: regras no banco (só Em Execução, novo término posterior, P1 a P5, conflito de revisão, imutabilidade), período em vigor e reprogramação, trava do período salvo, botão no quadro certo e alternando com o Habilitar, janela do Prorrogar, P no PDF (fonte menor, ao lado do término, margens) |
| `test_sm_avulso_pdf.py` | conteúdo, caixa alta, Indisponível, ausência de data/hora das manobras, paginação, quebra de texto, alinhamento, margens, reservada, cancelada, arquivamento |
| `test_regressao_doc_lib.py` | ATEIE, AI e MO (salvar, gerar, De acordo, reserva, MO-Referência, janelas, menu, GRID) e numerações independentes |

## Limites desta entrega

- Testado em Linux com tela virtual; a impressão (`os.startfile`/`lp`) e o Outlook não foram exercitados. O envio de e-mail foi
  testado com o envio real trocado por um registro das chamadas (destinatários, Cc, assunto, anexo); a conexão SMTP ou Outlook
  depende do `config_email_ateie.json` de cada computador, como nos demais documentos.
- Os testes de regressão de ATEIE, AI e MO foram rodados também contra o `main.py` original (mesmo resultado).
