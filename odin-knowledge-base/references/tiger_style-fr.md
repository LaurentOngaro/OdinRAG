---
title: "TigerStyle - Guide de style pour systemes critiques (traduction francaise)"
date: "2026-07-10"
tags: [OdinRAG, kb, reference, style, source/tigerbeetle, lang/fr]
type: reference
status: active
version: 1.0.0
lastUpdated: "2026-07-10"
updatedBy: "MiniMax-M3 (Kilo Code)"
summary: "Traduction francaise du TigerStyle de TigerBeetle pour lecture personnelle. Citations preservees en anglais (N.d.T.)."
exception: "french_translation_for_personal_reading"
---

# TigerStyle

source: [TIGER_STYLE](https://github.com/tigerbeetle/tigerbeetle/blob/main/docs/TIGER_STYLE.md)

> **Note du traducteur**: ce fichier est la traduction francaise du guide de style TigerStyle de TigerBeetle. Les citations de personnes reelles (Benjamin Franklin, Steve Jobs, Edsger Dijkstra, Gandalf, Gerard J. Holzmann, Phil Karlton, Rivacindela Hudsoni, John Carmack, Bilbo) sont preservees en anglais car elles sont la parole exacte de leurs auteurs. Les commentaires a l'interieur des blocs de code Zig sont traduits pour faciliter la comprehension, mais les identifiants, mots-cles et types restent en anglais.

## L'essence du style

> "There are three things extremely hard: steel, a diamond, and to know one's self." - Benjamin Franklin

Le style de code de TigerBeetle est en evolution. Un echange collectif a la frontiere de
l'ingenierie et de l'art. Les chiffres et l'intuition humaine. La raison et l'experience. Les
premiers principes et la connaissance. La precision et la poesie. Tout comme la musique. Un
rythme serre. Un groove rare. Des mots qui riment et des rimes qui se brisent. Du jazz
bionumerique. C'est ce que nous avons appris en chemin. Le meilleur reste a venir.

## Pourquoi avoir un style?

Un autre mot pour style est conception.

> "The design is not just what it looks like and feels like. The design is how it works." - Steve
> Jobs

Nos objectifs de conception sont la surete, la performance et l'experience developpeur. Dans cet
ordre. Les trois sont importants. Un bon style fait avancer ces objectifs. Le code rend-il la
surete, la performance ou l'experience developpeur meilleure ou pire? C'est pourquoi nous avons
besoin d'un style.

Ainsiformule, le style depasse la lisibilite, et la lisibilite est un acquis minimum, un moyen
plutot qu'une fin en soi.

> "...in programming, style is not something to pursue directly. Style is necessary only where
> understanding is missing." - [Let Over
> Lambda](https://letoverlambda.com/index.cl/guest/chap1.html)

Ce document explore comment nous appliquons ces objectifs de conception au style de code. D'abord,
un mot sur la simplicite, l'elegance et la dette technique.

## Sur la simplicite et l'elegance

La simplicite n'est pas un passe-droit. Elle n'entre pas en conflit avec nos objectifs de
conception. Elle n'a pas besoin d'etre une concession ou un compromis.

Bien au contraire, la simplicite est la facon dont nous reunissons nos objectifs de conception,
dont nous identifions la "super idee" qui resout les axes simultanement, pour obtenir quelque
chose d'elegant.

> "Simplicity and elegance are unpopular because they require hard work and discipline to achieve" -
> Edsger Dijkstra

Contrairement a l'opinion courante, la simplicite n'est pas non plus la premiere tentative mais
la revision la plus difficile. Il est facile de dire "faisons quelque chose de simple", mais le
faire en pratique exige de la reflexion, plusieurs passes, de nombreux croquis, et il nous faut
peut-etre encore ["jeter la premiere ebauche apres
l'autre"](https://en.wikipedia.org/wiki/The_Mythical_Man-Month).

La partie la plus difficile, alors, c'est toute la reflexion qu'on met dans chaque chose.

Nous depensons cette energie mentale en amont, proactivement plutot que reactivement, parce que
nous savons qu'une fois la reflexion faite, ce qui est depense sur la conception sera demesure
par l'implementation et les tests, et a nouveau par les couts d'operation et de maintenance.

Une heure ou un jour de conception vaut des semaines ou des mois en production:

> "the simple and elegant systems tend to be easier and faster to design and get right, more
> efficient in execution, and much more reliable" - Edsger Dijkstra

## La dette technique

Que pourrait-il mal tourner? Qu'est-ce qui ne va pas? Quelle question preferons-nous poser? La
premiere, parce que le code, comme l'acier, est moins couteux a modifier tant qu'il est chaud.
Un probleme resolu en production est beaucoup plus couteux qu'un probleme resolu en
implementation, ou qu'un probleme resolu en conception.

Comme il est deja assez difficile de decouvrir des obstacles majeurs, quand nous en trouvons,
nous les resolvons. Nous ne laissons pas passer des pics potentiels de latence memcpy, ou des
algorithmes de complexite exponentielle.

> "You shall not pass!" - Gandalf

Autrement dit, TigerBeetle a une politique de "zero dette technique". Nous faisons bien du
premier coup. C'est important parce que la deuxieme fois peut ne jamais arriver, et parce que
faire du bon travail, dont nous pouvons etre fiers, cree de l'elan.

Nous savons que ce que nous livrons est solide. Il peut nous manquer des fonctionnalites
essentielles, mais ce que nous avons repond a nos objectifs de conception. C'est la seule
facon de faire des progres incrementaux reguliers, en sachant que les progres que nous avons
faits en sont vraiment.

## Surete

> "The rules act like the seat-belt in your car: initially they are perhaps a little uncomfortable,
> but after a while their use becomes second-nature and not using them becomes unimaginable." -
> Gerard J. Holzmann

[Le Power of Ten de la NASA - Regles pour le developpement de code critique en
surete](https://spinroot.com/gerard/pdf/P10.pdf) changera votre facon de coder pour toujours. Pour
developper:

- Utilisez **uniquement un flot de controle tres simple et explicite** pour la clarte.
  **N'utilisez pas de recursion** pour vous assurer que toutes les executions qui doivent etre
  bornees le sont. Utilisez **un minimum d'excellentes abstractions** mais seulement si elles
  donnent le meilleur sens du domaine. Les abstractions ne sont [jamais a cout
  zero](https://isaacfreund.com/blog/2022-05/). Chaque abstraction introduit le risque d'une
  abstraction defectueuse.

- **Mettez une limite a tout** parce que, en realite, c'est ce que nous attendons-tout a une
  limite. Par exemple, toutes les boucles et toutes les files doivent avoir une borne superieure
  fixee pour empecher les boucles infinies ou les pics de latence en queue. Cela suit le
  principe ["fail-fast"](https://en.wikipedia.org/wiki/Fail-fast) pour que les violations soient
  detectees le plus tot possible. Quand une boucle ne peut pas se terminer (par ex. une boucle
  d'evenements), cela doit etre assure par une assertion.

- Utilisez des types de taille explicite comme `u32` pour tout, evitez `usize` dependant de
  l'architecture.

- **Les assertions detectent les erreurs du programmeur. Contrairement aux erreurs
  d'exploitation, qui sont attendues et doivent etre gerees, les echecs d'assertion sont
  inattendus. La seule facon correcte de gerer du code corrompu est de crasher. Les assertions
  degradent les bugs de correction catastrophiques en bugs de vivacite. Les assertions sont un
  multiplicateur de force pour decouvrir des bugs par le fuzzing.**

  - **Assurez tous les arguments et valeurs de retour des fonctions, les pre/postconditions et
    invariants.** Une fonction ne doit pas operer a l'aveugle sur des donnees qu'elle n'a pas
    verifiees. Le but d'une fonction est d'augmenter la probabilite qu'un programme soit
    correct. Les assertions au sein d'une fonction font partie de la facon dont les fonctions
    servent ce but. La densite d'assertions du code doit etre en moyenne au minimum deux
    assertions par fonction.

  - **[Appariez les assertions](https://tigerbeetle.com/blog/2023-12-27-it-takes-two-to-contract).**
    Pour chaque propriete que vous voulez faire respecter, essayez de trouver au moins deux
    chemins de code differents ou une assertion peut etre ajoutee. Par exemple, assurez la
    validite des donnees juste avant de les ecrire sur disque, et egalement immediatement apres
    les avoir lues depuis le disque.

  - A l'occasion, vous pouvez utiliser une assertion manifestement vraie au lieu d'un
    commentaire comme documentation plus forte quand la condition d'assertion est critique et
    surprenante.

  - Separer les assertions composees: preferer `assert(a); assert(b);` a `assert(a and b);`.
    La premiere est plus simple a lire et fournit une information plus precise si la condition
    echoue.

  - Utiliser un `if` mono-ligne pour assurer une implication: `if (a) assert(b)`.

  - **Assurez les relations entre constantes compile-time** comme controle sanitaire, et aussi
    pour documenter et faire respecter des
    [invariants subtils](https://github.com/coilhq/tigerbeetle/blob/db789acfb93584e5cb9f331f9d6092ef90b53ea6/src/vsr/journal.zig#L45-L47)
    ou des [tailles de
    types](https://github.com/coilhq/tigerbeetle/blob/578ac603326e1d3d33532701cb9285d5d2532fe7/src/ewah.zig#L41-L53).
    Les assertions compile-time sont extremement puissantes parce qu'elles peuvent verifier
    l'integrite de la conception d'un programme _avant_ meme que le programme ne s'execute.

  - **La regle d'or des assertions est d'assurer l'_espace positif_ que vous attendez ET
    d'assurer l'_espace negatif_ que vous n'attendez pas** parce que la ou les donnees
    traversent la frontiere valide/invalide entre ces espaces, on y trouve souvent des bugs
    interessants. C'est aussi pourquoi **les tests doivent tester exhaustivement**, non
    seulement avec des donnees valides mais aussi avec des donnees invalides, et quand des
    donnees valides deviennent invalides.

  - Les assertions sont un filet de securite, pas un substitut a la comprehension humaine.
    Avec la simulation par tests, il y a la tentation de faire confiance au fuzzer. Mais un
    fuzzer ne peut prouver que la presence de bugs, pas leur absence. Donc:
    - Construisez d'abord un modele mental precis du code,
    - encodez votre comprehension sous forme d'assertions,
    - ecrivez le code et les commentaires pour expliquer et justifier le modele mental a
      votre relecteur,
    - et utilisez VOPR comme dernier rempart, pour trouver des bugs dans votre comprehension
      et celle du relecteur du code.

- Toute la memoire doit etre allouee statiquement au demarrage. **Aucune memoire ne peut etre
  dynamiquement allouee (ou liberee et reallouee) apres l'initialisation.** Cela evite le
  comportement imprevisible qui peut significativement affecter la performance, et evite
  l'utilisation apres liberation. Comme effet de second ordre, il est de notre experience que cela
  conduit aussi a des conceptions plus efficaces et plus simples, qui sont plus performantes et
  plus faciles a maintenir et raisonner, par rapport aux conceptions qui ne considerent pas en
  amont tous les patterns d'usage memoire possibles comme partie de la conception.

- Declarez les variables dans la **plus petite portee possible**, et **minimisez le nombre de
  variables en portee**, pour reduire la probabilite que les variables soient mal utilisees.

- Il y a une discontinuite nette entre une fonction qui tient sur un ecran, et devoir derouler
  pour voir sa longueur. Pour cette raison physique, nous imposons une **limite stricte de
  70 lignes par fonction**. L'art nait des contraintes. Il y a plusieurs manieres de couper un
  mur de code en morceaux de 70 lignes, mais seuls quelques-decoupages paraissent justes.
  Quelques regles empiriques:

  - Une bonne forme de fonction est souvent l'inverse d'un sablier: quelques parametres, un
    type de retour simple, et beaucoup de logique consistante entre les accolades.
  - Centralisez le flot de controle. Quand vous fractionnez une grande fonction, essayez de
    garder toutes les instructions switch/if dans la fonction "parente", et deplacez les
    fragments de logique non branchue vers des fonctions auxiliaires. Divisez les responsabilites.
    Tout le flot de controle devrait etre gere par _une_ fonction, le reste ne devrait pas avoir
    a se soucier du flot de controle. En d'autres termes, ["poussez les `if` vers le haut et
    les `for` vers le bas"](https://matklad.github.io/2023/11/15/push-ifs-up-and-fors-down.html).
  - De meme, centralisez la manipulation d'etat. Laissez la fonction parente garder tout l'etat
    pertinent dans des variables locales, et utilisez des auxiliaires pour calculer ce qui doit
    changer, plutot que d'appliquer le changement directement. Gardez les fonctions feuilles
    pures.

- Appreliez, des le premier jour, **tous les avertissements du compilateur au reglage le plus
  strict du compilateur**.

- Quand votre programme doit interagir avec des entites externes, **ne faites pas de choses
  directement en reaction aux evenements externes**. Au lieu de cela, votre programme devrait
  tourner a son propre rythme. Non seulement cela rend votre programme plus sur en gardant
  sous votre controle le flot de controle de votre programme, mais cela ameliore aussi la
  performance pour la meme raison (vous pouvez batcher au lieu de commuter de contexte sur
  chaque evenement). De plus, cela facilite le maintien de bornes sur le travail effectue
  par periode de temps.

Au-dela de ces regles:

- Les conditions composees qui evaluent plusieurs booleens rendent difficile pour le lecteur
  de verifier que tous les cas sont geres. Separer les conditions composees en conditions
  simples via des branches `if/else` imbriquees. Separer les chaines `else if` complexes en
  arborescences `else { if { } }`. Cela rend les branches et cas clairs. A nouveau, considere
  si un seul `if` necessite egalement une branche `else` correspondante, pour assurer que
  les espaces positifs et negatifs sont geres ou assures.

- Les negations ne sont pas faciles! Statez les invariants de maniere positive. Quand vous
  travaillez avec des longueurs et indexes, cette forme est facile a obtenir juste (et a
  comprendre):

  ```zig
  if (index < length) {
    // L'invariant est tenu.
  } else {
    // L'invariant n'est pas tenu.
  }
  ```

  Cette forme est plus difficile, et va aussi a contre-courant de la facon dont `index` est
  typiquement compare a `length`, par exemple, dans une condition de boucle:

  ```zig
  if (index >= length) {
    // Ce n'est pas vrai que l'invariant est tenu.
  }
  ```

- Toutes les erreurs doivent etre gerees. Une [analyse des echecs en production dans les
  systemes distribues data-intensifs](https://www.usenix.org/system/files/conference/osdi14/osdi14-paper-yuan.pdf)
  a trouve que la majorite des echecs catastrophiques auraient pu etre evites par de simples
  tests du code de gestion d'erreurs.

> "Specifically, we found that almost all (92%) of the catastrophic system failures are the result
> of incorrect handling of non-fatal errors explicitly signaled in software."

- **Toujours motiver, toujours dire pourquoi**. N'oubliez jamais de dire pourquoi. Parce que si
  vous expliquez la rationale d'une decision, cela augmente non seulement la comprehension de
  l'auditeur, et le rend plus susceptible d'y adherer ou de s'y conformer, mais partage aussi
  avec lui des criteres avec lesquels evaluer la decision et son importance.

- **Passez explicitement les options aux fonctions de bibliotheque au site d'appel, au lieu de
  vous fier aux valeurs par defaut**. Par exemple, ecrivez
  `@prefetch(a, .{ .cache = .data, .rw = .read, .locality = 3 });` plutot que `@prefetch(a, .{});`.
  Cela ameliore la lisibilite mais surtout evite des bugs latents et potentiellement
  catastrophiques au cas ou la bibliotheque changerait un jour ses valeurs par defaut.

## Performance

> "The lack of back-of-the-envelope performance sketches is the root of all evil." - Rivacindela
> Hudsoni

- Pensez a la performance des le depart, depuis le debut. **Le meilleur moment pour resoudre la
  performance, pour obtenir les enormes gains de 1000x, est dans la phase de conception, qui
  est precisement quand nous ne pouvons pas mesurer ni profiler.** C'est aussi typiquement plus
  difficile de reparer un systeme apres implementation et profilage, et les gains sont moindres.
  Donc vous devez avoir de la sympathie mecanique. Comme un menuisier, travaillez avec le fil.

- **Faites des croquis de calcul a la louche par rapport aux quatre ressources (reseau,
  disque, memoire, CPU) et leurs deux caracteristiques principales (bande passante, latence).**
  Les croquis sont bon marche. Utilisez des croquis pour etre "approximativement juste" et
  atterrir dans les 90% du maximum global.

- Optimisez pour les ressources les plus lentes d'abord (reseau, disque, memoire, CPU) dans cet
  ordre, apres compensation de la frequence d'usage, parce que les ressources plus rapides
  peuvent etre utilisees beaucoup plus souvent. Par exemple, un defaut de cache memoire peut
  etre aussi couteux qu'un fsync disque, s'il arrive beaucoup plus souvent.

- Distinguer entre le plan de controle et le plan de donnees. Une delimitation claire entre
  plan de controle et plan de donnees par l'utilisation du batching permet un haut niveau de
  securite par assertions sans perdre en performance. Voir notre [talk de Zig SHOWTIME de
  juillet 2021](https://youtu.be/BH2jvJ74npM?t=1958) pour des exemples.

- Amortissez les couts reseau, disque, memoire et CPU en batchant les acces.

- Laissez le CPU etre un sprinteur faisant le 100m. Soyez previsible. Ne forcez pas le CPU a
  zigzaguer et changer de voie. Donnez au CPU des morceaux de travail assez gros. Cela revient
  au batching.

- Soyez explicite. Minimisez la dependance au compilateur pour qu'il fasse ce qu'il faut.

  En particulier, extrayez les boucles chaudes en fonctions autonomes avec des arguments
  primitifs sans `self` (voir [un
  exemple](https://github.com/tigerbeetle/tigerbeetle/blob/0.16.19/src/lsm/compaction.zig#L1932-L1937)).
  De cette facon, le compilateur n'a pas besoin de prouver qu'il peut mettre en cache les
  champs d'un struct dans des registres, et un lecteur humain peut reperer plus facilement des
  calculs redondants.

## Experience developpeur

> "There are only two hard things in Computer Science: cache invalidation, naming things, and
> off-by-one errors." - Phil Karlton

### Nommer les choses

- **Trouvez les justes noms et verbes.** Les grands noms sont l'essence d'un grand code, ils
  capturent ce qu'une chose est ou fait, et fournissent un modele mental net et intuitif. Ils
  montrent que vous comprenez le domaine. Prenez le temps de trouver le nom parfait, de trouver
  les noms et verbes qui fonctionnent ensemble, pour que le tout soit plus grand que la somme de
  ses parties.

- Utilisez `snake_case` pour les noms de fonctions, variables et fichiers. Le tiret bas est ce
  que nous avons de plus proche en tant que programmeurs d'un espace, et aide a separer les mots
  et a encourager des noms descriptifs. Nous n'utilisons pas le style de Zig `CamelCase.zig`
  pour les fichiers "struct" pour garder la convention simple et coherente.

- N'abregez pas les noms de variables, sauf si la variable est un type entier primitif utilise
  comme argument d'une fonction de tri ou de calcul matriciel. Utilisez des arguments de forme
  longue dans les scripts: `--force`, pas `-f`. Les flags a une seule lettre sont pour
  l'usage interactif.

- Utilisez la capitalisation correcte pour les acronymes (`VSRState`, pas `VsrState`).

- Pour le reste, suivez le guide de style de Zig.

- Ajoutez des unites ou qualificateurs aux noms de variables, et placez les unites ou
  qualificateurs en dernier, tries par ordre d'importance decroissant, pour que la variable
  commence par le mot le plus significatif, et finisse par le mot le moins significatif. Par
  exemple, `latency_ms_max` plutot que `max_latency_ms`. Cela s'alignera joliment quand
  `latency_ms_min` sera ajoute, tout en regroupant toutes les variables liees a la latence.

- Infusez les noms avec du sens. Par exemple, `allocator: Allocator` est un nom bon, bien que
  banal, mais `gpa: Allocator` et `arena: Allocator` sont excellents. Ils informent le lecteur
  si `deinit` doit etre appele explicitement.

- Quand vous choisissez des noms apparentes, efforcez-vous de trouver des noms avec le meme
  nombre de caracteres pour que les variables apparentees s'alignent toutes dans la source. Par
  exemple, comme arguments d'une fonction memcpy, `source` et `target` sont mieux que `src` et
  `dest` parce qu'ils ont l'effet de second ordre que toutes variables apparentees comme
  `source_offset` et `target_offset` s'aligneront dans les calculs et les slices. Cela rend
  le code symetrique, avec des blocs propres plus faciles a parcourir pour l'oeil et plus
  simples a verifier pour le lecteur.

- Quand une seule fonction appelle une fonction auxiliaire ou un callback, prefixez le nom de
  la fonction auxiliaire avec le nom de la fonction appelante pour montrer l'historique
  d'appel. Par exemple, `read_sector()` et `read_sector_callback()`.

- Les callbacks vont en dernier dans la liste des parametres. Cela reflete le flot de controle:
  les callbacks sont aussi _invoques_ en dernier.

- L'_ordre_ compte pour la lisibilite (meme s'il n'affecte pas la semantique). A la premiere
  lecture, un fichier est lu de haut en bas, donc mettez les choses importantes pres du haut. La
  fonction `main` va en premier.

  Il en va de meme pour les `structs`, l'ordre est champs puis types puis methodes:

  ```zig
  time: Time,
  process_id: ProcessID,

  const ProcessID = struct { cluster: u128, replica: u8 };
  const Tracer = @This(); // Cet alias conclut la section des types.

  pub fn init(gpa: std.mem.Allocator, time: Time) !Tracer {
      ...
  }
  ```

  Si un type imbrique est complexe, faites-en un struct de plus haut niveau.

  En meme temps, tout n'a pas un ordre unique. En cas de doute, considerer un tri alphabetique,
  en profitant du nommage big-endian.

- Ne surchargez pas les noms avec des significations multiples qui dependent du contexte. Par
  exemple, TigerBeetle a une fonctionnalite appelee _pending transfers_ ou un pending transfer
  peut ensuite etre _posted_ ou _voided_. Au debut, nous les appelions _two-phase commit
  transfers_, mais cela surchargait la terminologie _two-phase commit_ qui etait utilisee dans
  notre protocole de consensus, causant de la confusion.

- Pensez a comment les noms seront utilises en dehors du code, dans la documentation ou la
  communication. Par exemple, un nom est souvent un meilleur descripteur qu'un adjectif ou un
  participe present, parce qu'un nom peut etre directement utilise dans la correspondance sans
  avoir besoin d'etre reformule. Comparez `replica.pipeline` vs `replica.preparing`. Le premier
  peut etre utilise directement comme en-tete de section dans un document ou une conversation,
  tandis que le second doit etre clarifie. Les noms communs composent plus clairement pour les
  identifiants derives, par ex. `config.pipeline_max`.

- Zig a des arguments nommes via le pattern `options: struct`. Utilisez-le quand les arguments
  peuvent etre melanges. Une fonction prenant deux `u64` doit utiliser un struct d'options. Si
  un argument peut etre `null`, il devrait etre nomme pour que la signification du litteral
  `null` au site d'appel soit claire.

  Parce que les dependances comme un allocateur ou un tracer sont des singletons avec des
  types uniques, ils devraient etre passes a travers les constructeurs positionnellement, du
  plus general au plus specifique.

- **Ecrivez des messages de commit descriptifs** qui informent et enchantent le lecteur, parce
  que vos messages de commit sont lus. Notez qu'une description de pull request n'est pas
  stockee dans le depot git et est invisible dans `git blame`, et n'est donc pas un substitut
  a un message de commit.

- N'oubliez pas de dire pourquoi. Le code seul n'est pas de la documentation. Utilisez des
  commentaires pour expliquer pourquoi vous avez ecrit le code de cette facon. Montrez votre
  raisonnement.

- N'oubliez pas de dire comment. Par exemple, quand vous ecrivez un test, pensez a ecrire une
  description en haut pour expliquer le but et la methodologie du test, pour aider votre
  lecteur a se mettre a niveau, ou pour passer sur des sections, sans le forcer a plonger.

- Les commentaires sont des phrases, avec un espace apres la barre, avec une majuscule et un
  point, ou deux-points s'ils se rapportent a quelque chose qui suit. Les commentaires sont
  une prose bien ecrite decrivant le code, pas juste des gribouillages en marge. Les
  commentaires apres la fin d'une ligne _peuvent_ etre des phrases, sans ponctuation.

### Invalidation de cache

- Ne dupliquez pas les variables ou ne prenez pas d'alias sur elles. Cela reduira la
  probabilite que l'etat se desynchronise.

- Si vous ne voulez pas qu'un argument de fonction soit copie quand il est passe par valeur, et
  si le type de l'argument fait plus de 16 octets, alors passez l'argument comme `*const`. Cela
  attrapera les bugs ou l'appelant fait une copie accidentelle sur la pile avant d'appeler la
  fonction.

- Construisez des structs plus grands _en place_ en passant un _pointeur de sortie_ pendant
  l'initialisation.

  Les initialisations en place peuvent supposer la **stabilite du pointeur** et des **types
  immuables** tout en eliminant les allocations intermediaires de copie-deplacement, qui
  peuvent mener a une croissance indesirable de la pile.

  Gardez a l'esprit que les initialisations en place sont virales-si un champ est initialise en
  place, le struct conteneur entier devrait aussi etre initialise en place.

  **Preferer:**

  ```zig
  fn init(target: *LargeStruct) !void {
    target.* = .{
      // initialisation en place.
    };
  }

  fn main() !void {
    var target: LargeStruct = undefined;
    try target.init();
  }
  ```

  **Plutot que:**

  ```zig
  fn init() !LargeStruct {
    return LargeStruct {
      // deplacement de l'objet initialise.
    }
  }

  fn main() !void {
    var target = try LargeStruct.init();
  }
  ```

- **Reduire la portee** pour minimiser le nombre de variables en jeu et reduire la probabilite
  que la mauvaise variable soit utilisee.

- Calculez ou verifiez les variables pres de la ou/quand elles sont utilisees. **N'introduisez
  pas de variables avant qu'elles ne soient necessaires.** Ne les laissez pas trainer la ou
  elles ne sont pas. Cela reduira la probabilite d'un POCPOU (place-of-check to place-of-use),
  un cousin eloigne du fameux
  [TOCTOU](https://en.wikipedia.org/wiki/Time-of-check_to_time-of-use). La plupart des bugs
  reviennent a un fossé semantique, cause par un fossé en temps ou en espace, parce qu'il est
  plus dur de verifier du code qui n'est pas contenu selon ces dimensions.

- Utilisez des signatures de fonction et types de retour plus simples pour reduire la
  dimensionalite au site d'appel, le nombre de branches qui doivent etre gerees au site
  d'appel, parce que cette dimensionalite peut aussi etre virale, se propageant a travers la
  chaine d'appel. Par exemple, comme type de retour, `void` bat `bool`, `bool` bat `u64`, `u64`
  bat `?u64`, et `?u64` bat `!u64`.

- Assurez-vous que les fonctions s'executent jusqu'au bout sans suspension, pour que les
  assertions de precondition soient vraies pendant toute la duree de vie de la fonction. Ces
  assertions sont utiles comme documentation sans suspension, mais peuvent etre trompeuses
  sinon.

- Soyez sur vos gardes pour les **[fuites de
  tampon](https://en.wikipedia.org/wiki/Heartbleed)**. C'est un sous-debit de tampon,
  l'oppose d'un debordement de tampon, ou un tampon n'est pas pleinement utilise, avec du
  padding pas correctement mis a zero. Cela peut non seulement faire fuiter des informations
  sensibles, mais peut entrainer la violation des garanties deterministes requises par
  TigerBeetle.

- Utilisez des sauts de ligne pour **grouper l'allocation et la deallocation de ressources**,
  c.-a-d. avant l'allocation de la ressource et apres la declaration `defer` correspondante,
  pour rendre les fuites plus faciles a reperer.

### Erreurs de type off-by-one

- **Les suspects habituels pour les erreurs off-by-one sont les interactions occasionnelles
  entre un `index`, un `count` ou une `size`.** Ce sont tous des types entiers primitifs, mais
  devraient etre vus comme des types distincts, avec des regles claires pour la conversion. Pour
  aller d'un `index` a un `count`, vous devez ajouter un, puisque les indexes sont _bases sur
  0_ mais les counts sont _bases sur 1_. Pour aller d'un `count` a une `size`, vous devez
  multiplier par l'unite. A nouveau, c'est pourquoi inclure des unites et qualificateurs dans
  les noms de variables est important.

- Montrez votre intention en ce qui concerne la division. Par exemple, utilisez `@divExact()`,
  `@divFloor()` ou `div_ceil()` pour montrer au lecteur que vous avez reflechi a tous les
  scenarios interessants ou l'arrondi peut etre implique.

### Le style par les chiffres

- Lancez `zig fmt`.

- Utilisez 4 espaces d'indentation, plutot que 2 espaces, car cela est plus evident a l'oeil
  a distance.

- Limitez strictement toutes les longueurs de ligne, sans exception, a au plus 100 colonnes
  pour une bonne "mesure" typographique. Utilisez-la. Ne la depassez jamais. Rien ne devrait
  etre cache par une barre de defilement horizontale. Laissez votre editeur vous aider en
  definissant une regle de colonne. Pour envelopper une signature de fonction, un appel ou une
  structure de donnees, ajoutez une virgule de fin, fermez les yeux et laissez `zig fmt` faire
  le reste.

  Semblable a la longueur de fonction, la motivation derriere le nombre 100 est physique: juste
  assez pour faire tenir deux copies du code cote a cote sur un ecran.

- Ajoutez des accolades a l'instruction `if` sauf si elle tient sur une seule ligne pour la
  coherence et la defense en profondeur contre les bugs "goto fail;".

### Dependances

TigerBeetle a **une politique de "zero dependances"**, en dehors de la toolchain Zig. Les
dependances, en general, menent inevitablement a des attaques de la chaine d'approvisionnement,
au risque de surete et de performance, et a des temps d'installation lents. Pour les
infrastructures fondationnelles en particulier, le cout de toute dependance est amplifie dans
le reste de la stack.

### Outils

De meme, les outils ont des couts. Une petite boite a outils standardisee est plus simple a
operer qu'un ensemble d'instruments specialises chacun avec un manuel dedie. Notre outil
principal est Zig. Ce n'est peut-etre pas le meilleur pour tout, mais il est assez bon pour la
plupart des choses. Nous investissons dans notre outillage Zig pour nous assurer que nous pouvons
aborder rapidement de nouveaux problemes, avec un minimum de complexite accidentelle dans notre
environnement de developpement local.

> "The right tool for the job is often the tool you are already using-adding new tools has a higher
> cost than many people appreciate" - John Carmack

Par exemple, la prochaine fois que vous ecrivez un script, au lieu de `scripts/*.sh`, ecrivez
`scripts/*.zig`.

Cela rend non seulement votre script multiplateforme et portable, mais introduit la securite de
type et augmente la probabilite que l'execution de votre script reussisse pour tout le monde
dans l'equipe, au lieu de tomber sur un probleme specifique a Bash/Shell/OS.

La standardisation sur Zig pour l'outillage est importante pour s'assurer que nous reduisons la
dimensionalite, a mesure que l'equipe grandit, et donc la portee des gouts personnels. Cela peut
etre plus lent pour vous a court terme, mais cree plus de velocite pour l'equipe a long terme.

## La derniere etape

En fin de compte, continuez d'essayer des choses, amusez-vous, et souvenez-vous-c'est appelle
TigerBeetle, pas seulement parce que c'est rapide, mais parce que c'est petit!

> "You don't really suppose, do you, that all your adventures and escapes were managed by mere luck,
> just for your sole benefit? You are a very fine person, Mr. Baggins, and I am very fond of you;
> but you are only quite a little fellow in a wide world after all!"
>
> "Thank goodness!" said Bilbo laughing, and handed him the tobacco-jar.
