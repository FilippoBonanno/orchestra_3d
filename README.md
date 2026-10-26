# orchestra_3d — Orchestra 3D per Codex

Skill autonoma per seguire progetti di stampa 3D: brief e quote, Blender, mockup dal modello, STL, verifiche della mesh e preparazione nello slicer disponibile. Non modifica né richiede Orchestra originale. La repository si chiama `orchestra_3d`; il nome tecnico della skill è `orchestra-3d` per rispettare il validatore Codex.

## Installazione su un altro PC

Incolla in Codex:

> Usa skill-installer per installare la skill dalla repository https://github.com/FilippoBonanno/orchestra_3d, percorso skills/orchestra-3d. Non sovrascrivere una versione già installata senza controllarla.

Il pacchetto da installare è **solo `skills/orchestra-3d`**, non l'intera repository. Il tool skill-installer può installarlo nella directory skill personale di Codex; non servono modifiche globali ad AGENTS.md né hook Claude. Le directory personali supportate dipendono dall'ambiente: usa quella gestita dall'installer della tua installazione.

Dal turno successivo, richiama:

```text
$orchestra-3d
```

Oppure scrivi `orchestra_3d` e descrivi il progetto. Se la skill non compare ancora nell'elenco, riapri la chat/app per aggiornare la scoperta. Una chiamata senza progetto chiede quale oggetto creare. Rimane attiva per il lavoro 3D della chat fino a `stop orchestra_3d` o `normal mode`.

Esempio:

> $orchestra-3d Crea in Blender un distanziale di 30 × 20 × 5 mm con foro passante da 6 mm al centro. Voglio .blend, STL e anteprima. Non conosco ancora stampante e materiale.

## Requisiti e limiti

Codex deve avere accesso ai file e all'esecuzione locale. Blender va installato sul PC che genera i modelli; la skill lo cerca, non include un eseguibile. Il controllo visivo di Blender richiede strumenti di computer use disponibili. Lo slicer è opzionale: se manca, la skill consegna la mesh e dichiara la verifica slicer non eseguita. La delega è facoltativa e usa solo le capacità effettivamente disponibili.

La skill non installa software automaticamente, non abilita permessi, non configura server MCP e non avvia la stampante. I mockup non provano tolleranze o resistenza. L'audit incluso non certifica spessore minimo o assenza di autointersezioni.

## Verifica del pacchetto

```text
blender --background --factory-startup --python-exit-code 1 --python tests/test_blender.py
```

Il test genera un cubo in mm, esporta e reimporta l'STL e controlla dimensioni, topologia e volume; verifica mesh aperte, degeneri o con winding incoerente e la richiesta di revisione per gusci invertiti o cavità interne. Non esegue stampa fisica o slicer.

Riferimenti: [skill Codex](https://developers.openai.com/codex/skills/), [STL Blender](https://docs.blender.org/manual/en/latest/files/import_export/stl.html).
