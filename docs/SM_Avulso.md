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
| Telas | `JanelaSMAvulso`, `LinhasManobrasSM`, `LinhasConferenciaSM`, `JanelaListaSM` (GRID SM) |

Alterações em código **compartilhado** (todas aditivas; o comportamento de ATEIE, AI e MO não muda):
1. `_doc_lib_ultimo_numero`: ramo `tipo == "SM"` (numeração própria, como a MO);
2. `garantir_banco_doc_lib`: chama `_garantir_tabelas_doc_lib_sm`;
3. `JanelaListaAteie`: atributo `PERMITE_EMAIL = True` (a SM o desliga, pois não tem "Marcar e-mail enviado");
4. `cmd_click25_sm_avulso` deixou de ser "Página em Construção".

## Status e transições

`Reservado` -> `Em análise` -> `Aguarda Conferência` -> `Aprovado para Execução` -> `Em Execução` -> `Concluído`.
`Cancelado` vale de qualquer status, **menos Concluído**. Concluído e Cancelado não têm saída.

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
liberação (itens 6 e 7); Em Execução = reprogramações, data/hora e executantes da normalização (itens 8 e 9). Os itens 6 e 7
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
8. **Data e hora das manobras**: podem ser **corrigidas, não apagadas**; cada alteração vai para `doclib_sm_historico` (usuário e
   momento). Devem seguir a ordem das linhas e a normalização não pode ser anterior à última liberação. Os itens 6 e 7 só aceitam
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
15. **Sem Encaminhar por e-mail**: a SM não tem destinatário externo nem a coluna "Enviado e-mail".
16. **Permissões**: o Doc_Lib não distingue perfis (só exige usuário autenticado). Vale a mesma regra, e toda operação grava o usuário
    e o momento (`criado_*`, `atualizado_*`, `emitido_*`, `cancelada_*`, histórico).
17. **Frase solta no fim do pedido de alteração**: o texto "Tempo de Retorno à operação: ao invés de texto livre, colocar uma lista para
    selecionar o local de execução dos serviços" não trouxe lista e repete o pedido do 3.5. Foi lido como sobra de colagem; o 3.6 seguiu a
    instrução específica (igual ao AI). Se a intenção era outra, informar.
18. **PDF**: fiel ao formulário (12 itens, número no alto à direita, rodapé com página e número). O aviso vermelho
    "Aguardando a Conferência do documento" fica no cabeçalho enquanto a SM aguarda; o primeiro PDF gerado já o traz.

## Banco de dados

Tabelas novas, criadas por `garantir_banco_doc_lib` sem tocar nos dados existentes: `doclib_sm`, `doclib_sm_equipamentos`,
`doclib_sm_manobras`, `doclib_sm_conferencias`, `doclib_sm_historico`, `doclib_sm_transicoes`, `doclib_sm_pdfs`.

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
| `test_sm_avulso_pdf.py` | conteúdo, caixa alta, Indisponível, ausência de data/hora das manobras, paginação, quebra de texto, alinhamento, margens, reservada, cancelada, arquivamento |
| `test_regressao_doc_lib.py` | ATEIE, AI e MO (salvar, gerar, De acordo, reserva, MO-Referência, janelas, menu, GRID) e numerações independentes |

## Limites desta entrega

- Testado em Linux com tela virtual; a impressão (`os.startfile`/`lp`) e o Outlook não foram exercitados.
- Os testes de regressão de ATEIE, AI e MO foram rodados também contra o `main.py` original (mesmo resultado).
